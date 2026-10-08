"""Implement seqdb sequence service behavior for services.seq.upload_verify_batch."""

from collections import defaultdict
from typing import cast
from uuid import UUID

from gen_epix import fastapp
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.services import BatchUploader
from gen_epix.etl.enum import EtlStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.services.seq.upload_verify_batch_refdata import (
    _verify_batch_refdata_allele_profiles,
    _verify_batch_refdata_kmer_profiles,
    _verify_batch_refdata_mlva_profiles,
    _verify_batch_refdata_snp_profiles,
)


def _verify_sample_children(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Check child model existence and consistency."""
    success = True
    # Generic child model verifications
    success &= self.verify_children(
        cmd,
        batch_result,
        uow,
    )

    # Child model specific verifications, run seqs first so that seq_classifications
    # and seq_profiles can resolve their seq_id links (same dependency order as
    # SampleForUpload.CHILD_ORDER).
    success &= _verify_children_seqs(self, cmd, batch_result, uow)
    success &= _verify_children_seq_classifications(self, cmd, batch_result, uow)
    success &= _verify_children_seq_profiles(self, cmd, batch_result, uow)

    return success


def _verify_protocol(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
    child_model_class: type[model.Model],
) -> bool:
    """Verify and resolve child protocol IDs or codes in an upload batch.

    Args:
        self: Batch uploader providing linked-record validation.
        cmd: Upload command whose child records are validated.
        batch_result: Result collection updated with validation errors.
        uow: Active persistence unit of work.
        child_model_class: Child model type with protocol references.

    Returns:
        Whether all supplied protocol references are valid.

    Raises:
        ValueError: Child model metadata does not define a protocol field mapping.
    """
    children_field_name = model.SampleForUpload.CHILDREN_FIELD_NAME_MAP[
        child_model_class
    ]

    # Verify that all provided protocol IDs and codes exist and are consistent, and resolve codes to IDs in the upload batch when only codes are provided
    success = self.verify_link_id(
        list(self.parent_result_items(cmd, batch_result)),
        uow,
        cmd.user,
        children_field_name,
        "protocol_id",
        "protocol_code",
        model.Protocol,
    )

    # Get all protocol IDs
    protocol_ids = {x.protocol_id for x in cmd.sample_batch.get_all_children_for_upload(child_model_class)}  # type: ignore[attr-defined]
    protocol_ids.discard(None)
    protocol_ids.discard(NULL_ID)
    if not protocol_ids:
        # No protocol IDs provided, nothing left to verify
        return success

    # Get the provided protocols and check if their types are valid for this child model class
    valid_protocol_types = _get_valid_protocol_types(child_model_class)
    protocols: list[model.Protocol] = self.service.repository.crud(  # type: ignore[assignment]
        uow,
        cmd.user.id if cmd.user else None,
        model.Protocol,
        CrudOperation.READ_SOME,
        obj_ids=list(protocol_ids),
    )
    protocol_map = {cast(UUID, x.id): x for x in protocols}
    invalid_protocol_ids: set[UUID] = {
        cast(UUID, x.id)
        for x in protocols
        if x.protocol_type not in valid_protocol_types
    }
    if invalid_protocol_ids:
        success = False
        _add_invalid_protocol_errors(
            cmd,
            batch_result,
            children_field_name,
            invalid_protocol_ids,
            protocol_map,
            child_model_class,
        )
    return success


def _get_valid_protocol_types(
    child_model_class: type[model.Model],
) -> set[enum.ProtocolType]:
    """Return protocol types supported by a protocol-linked child model."""
    protocol_types_by_model = {
        model.ReadSet: enum.ProtocolTypeSet.SEQUENCING.value,
        model.Seq: enum.ProtocolTypeSet.ASSEMBLY.value,
        model.SeqClassification: enum.ProtocolTypeSet.CLASSIFICATION.value,
        model.SeqTaxonomy: enum.ProtocolTypeSet.TAXONOMY.value,
        model.SeqProfile: enum.ProtocolTypeSet.SEQ_PROFILE.value,
        model.SeqDistance: enum.ProtocolTypeSet.SEQ_DISTANCE.value,
    }
    try:
        return protocol_types_by_model[child_model_class]
    except KeyError as error:
        raise NotImplementedError(
            f"Unknown child model class {child_model_class} for protocol verification"
        ) from error


def _add_invalid_protocol_errors(
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    children_field_name: str,
    invalid_protocol_ids: set[UUID],
    protocol_map: dict[UUID, model.Protocol],
    child_model_class: type[model.Model],
) -> None:
    """Attach errors to non-skipped children using invalid protocol IDs."""
    for sample_for_upload, sample_result in zip(
        cmd.sample_batch.samples, batch_result.samples
    ):
        for child_for_upload, child_result in zip(
            getattr(sample_for_upload, children_field_name) or [],
            getattr(sample_result, children_field_name) or [],
        ):
            if child_result.status == EtlStatus.SKIPPED:
                # Child is already marked as skipped -> nothing left to do.
                continue
            if child_for_upload.protocol_id in invalid_protocol_ids:
                child_result.add_error(
                    "a4c9e18b",
                    f"Referenced protocol with ID {child_for_upload.protocol_id} has protocol_type {protocol_map[child_for_upload.protocol_id].protocol_type} that is not compatible with {child_model_class.__name__}",
                )


def _verify_children_seqs(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify Seq-specific rules.

    1. Replace protocol code by ID when only code is provided, and verify that the
       referenced Protocol exists and has the correct protocol_type.
    2. Verify that read_set_id and read_set2_id link to a ReadSet within the same
       sample.
    3. Detect existing Seqs by their natural key (sample_id, protocol_id, read_set_id,
       read_set2_id) so that a Seq with a different hash for the same key will be
       rejected.
    4. Replace within-batch temporary IDs by existing IDs when the natural key and hash
       match an existing Seq, and mark these as not new so that they will be updated
       instead of inserted. This allows users to link other entities within the batch
       to a Seq within that batch without knowing the actual ID.

    Assumptions:
    - The cmd.sample_batch enforces that Seqs do not link to read sets of different
      samples within the same batch, so it can rely on the fact that any Seq.read_set_id
      or Seq.read_set2_id that refers to a not yet existing ReadSet will nonetheless
      refer to a ReadSet that will be linked to the same sample.
    - The Seq model enforces that read_set2_id can be filled in only when read_set_id
      is filled in.
    - The generic verify_parents and verify_children methods have already been called to
      verify the existence of the sample and its children, so it can rely on any Sample
      ID and child ID to be valid and present in the database or otherwise having been
      annotated as is_new=True.
    """
    user_id = cmd.user.id if cmd.user else None
    samples_for_upload = cmd.sample_batch.samples
    sample_results = batch_result.samples
    success = True

    # Verify assembly protocols provided by ID and/or code
    success &= _verify_protocol(self, cmd, batch_result, uow, model.Seq)

    # Get dict[sample_id, dict[(protocol_id, read_set_id, read_set2_id), (seq_hash, id)]]
    natural_key_map: defaultdict[
        UUID, dict[tuple[UUID, UUID | None, UUID | None], tuple[UUID, UUID]]
    ] = defaultdict(dict)
    existing_sample_ids = frozenset(
        {
            cast(UUID, x.id)
            for x, y in zip(samples_for_upload, sample_results)
            if not y.is_new
        }
    )
    if not existing_sample_ids:
        # No existing samples, nothing more to verify
        return success
    result_iter = self.service.repository.read_fields(
        uow,
        user_id,
        model.Seq,
        [
            "sample_id",
            "protocol_id",
            "read_set_id",
            "read_set2_id",
            "seq_hash",
            "id",
        ],
        filter=UuidSetFilter(key="sample_id", members=existing_sample_ids),
    )
    for x in result_iter:
        # (protocol_id, read_set_id, read_set2_id) is the natural key for a Seq within a Sample, and should be unique in the database.
        natural_key_map[x[0]][(x[1], x[2], x[3])] = (x[4], x[5])

    # Get dict[read_set_id, sample_id] to verify that Seqs link to ReadSets within the same Sample
    existing_read_set_id_to_sample_id = (
        self.retrieve_parent_id_by_intra_parent_linked_child_id(
            uow,
            cmd,
            model.Seq,
            "read_set_id",
            model.ReadSet,
        )
        | self.retrieve_parent_id_by_intra_parent_linked_child_id(
            uow,
            cmd,
            model.Seq,
            "read_set2_id",
            model.ReadSet,
        )
    )

    # Verify each Seq
    for sample_for_upload, sample_result in zip(samples_for_upload, sample_results):
        existing_seq_data = natural_key_map.get(cast(UUID, sample_for_upload.id))
        for seq_for_upload, seq_result in zip(
            sample_for_upload.seqs or [], sample_result.seqs or []
        ):
            success &= _verify_one_seq(
                self,
                sample_for_upload,
                seq_for_upload,
                seq_result,
                existing_seq_data,
                existing_read_set_id_to_sample_id,
            )
    return success


def _verify_one_seq(
    self: BatchUploader,
    sample_for_upload: model.SampleForUpload,
    seq_for_upload: model.SeqForUpload,
    seq_result: model.UploadResult,
    existing_seq_data: (
        dict[tuple[UUID, UUID | None, UUID | None], tuple[UUID, UUID]] | None
    ),
    existing_read_set_id_to_sample_id: dict[UUID, UUID],
) -> bool:
    """Verify one sequence's read-set ownership and existing natural-key match."""
    if seq_result.status == EtlStatus.SKIPPED:
        return True
    success = _verify_seq_read_set_sample(
        seq_for_upload, seq_result, sample_for_upload, existing_read_set_id_to_sample_id
    )
    if not existing_seq_data:
        return success
    existing_seq_hash, existing_seq_id = _get_existing_seq_match(
        seq_for_upload, existing_seq_data
    )
    if existing_seq_hash is None:
        return success
    assert existing_seq_id is not None
    if existing_seq_hash != seq_for_upload.seq_hash:
        _add_seq_hash_mismatch_error(
            seq_for_upload, seq_result, existing_seq_hash, existing_seq_id
        )
        return False
    seq_result.add_info(
        "b6e14c9f",
        f"Existing Seq with same protocol_id ({seq_for_upload.protocol_id}) and seq_hash will have ReadSets set from None to (read_set_id: {seq_for_upload.read_set_id}, read_set2_id: {seq_for_upload.read_set2_id})",
    )
    seq_result.is_new = False
    seq_result.id = existing_seq_id
    if seq_for_upload.id is None:
        seq_for_upload.id = existing_seq_id
    elif seq_for_upload.id != existing_seq_id:
        seq_result.add_info(
            "4fa2d87c",
            f"Identical Seq with same protocol_id ({seq_for_upload.protocol_id}), read_set_id ({seq_for_upload.read_set_id}) and read_set2_id ({seq_for_upload.read_set2_id}) already exists with a different ID {existing_seq_id} than new ID {seq_for_upload.id}. New ID will be replaced in the batch with the existing one.",
        )
        sample_for_upload.replace_child_id(seq_for_upload, existing_seq_id)
    return success


def _verify_seq_read_set_sample(
    seq_for_upload: model.SeqForUpload,
    seq_result: model.UploadResult,
    sample_for_upload: model.SampleForUpload,
    read_set_id_to_sample_id: dict[UUID, UUID],
) -> bool:
    """Reject a sequence whose existing read set belongs to another sample."""
    if seq_for_upload.read_set_id is None or seq_for_upload.read_set_id == NULL_ID:
        return True
    existing_sample_id = read_set_id_to_sample_id.get(seq_for_upload.read_set_id)
    if existing_sample_id is None or existing_sample_id == sample_for_upload.id:
        return True
    seq_result.add_error(
        "e5a19c72",
        f"Seq has read_set_id {seq_for_upload.read_set_id} that links to an existing ReadSet coupled to a different Sample with ID {existing_sample_id}",
    )
    return False


def _get_existing_seq_match(
    seq_for_upload: model.SeqForUpload,
    existing_seq_data: dict[tuple[UUID, UUID | None, UUID | None], tuple[UUID, UUID]],
) -> tuple[UUID | None, UUID | None]:
    """Find a sequence by natural key, including the missing-read-set fallback."""
    natural_key = (
        seq_for_upload.protocol_id,
        seq_for_upload.read_set_id,
        seq_for_upload.read_set2_id,
    )
    existing_seq_hash, existing_seq_id = existing_seq_data.get(
        natural_key, (None, None)
    )
    if existing_seq_hash is None and seq_for_upload.read_set_id not in (None, NULL_ID):
        # Existing Seq without ReadSets can be updated with newly supplied ReadSet IDs.
        return existing_seq_data.get(
            (seq_for_upload.protocol_id, None, None), (None, None)
        )
    return existing_seq_hash, existing_seq_id


def _add_seq_hash_mismatch_error(
    seq_for_upload: model.SeqForUpload,
    seq_result: model.UploadResult,
    existing_seq_hash: UUID,
    existing_seq_id: UUID,
) -> None:
    """Record the correct mismatch error based on whether ReadSets are known."""
    if seq_for_upload.read_set_id is None or seq_for_upload.read_set_id == NULL_ID:
        seq_result.add_error(
            "7c1e9ab4",
            f"Different Seq with same protocol_id ({seq_for_upload.protocol_id}), read_set_id ({seq_for_upload.read_set_id}) and read_set2_id ({seq_for_upload.read_set2_id}) already exists with hash ({existing_seq_hash}) and ID {existing_seq_id}, but since the new Seq is derived from unknown ReadSets it cannot be verified if the actual ReadSets that were used were indeed different",
        )
        return
    seq_result.add_error(
        "7da16146",
        f"Seq with same protocol_id ({seq_for_upload.protocol_id}), read_set_id ({seq_for_upload.read_set_id}) and read_set2_id ({seq_for_upload.read_set2_id}) already exists with a different hash ({existing_seq_hash}) and ID {existing_seq_id}",
    )


def _verify_children_seq_classifications(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify SeqClassification-specific rules.

    1. Replace protocol code by ID when only code is provided, and verify that the
       referenced Protocol exists and has the correct protocol_type.
    2. Verify that seq_id links to a Seq within the same sample.
    3. Detect existing SeqClassifications by their natural key (sample_id, protocol_id,
       seq_id) so that a SeqClassification with a different primary_category_id for the
       same key will be rejected.

    Assumptions:
    - The cmd.sample_batch enforces that SeqClassifications do not link to Seqs of
      different samples within the same batch, so it can rely on the fact that any
      SeqClassification.seq_id that refers to a not yet existing Seq will nonetheless
      refer to a Seq that will be linked to the same sample.
    - The generic verify_parents and verify_children methods have already been called to
      verify the existence of the sample and its children, so it can rely on any Sample
      ID and child ID to be valid and present in the database or otherwise having been
      annotated as is_new=True.
    """
    user_id = cmd.user.id if cmd.user else None
    samples_for_upload = cmd.sample_batch.samples
    sample_results = batch_result.samples
    success = True

    # Verify assembly protocols provided by ID and/or code
    success &= _verify_protocol(self, cmd, batch_result, uow, model.SeqClassification)

    # Resolve and verify primary categories provided by ID and/or code
    success &= self.verify_link_id(
        list(self.parent_result_items(cmd, batch_result)),
        uow,
        cmd.user,
        "seq_classifications",
        "primary_category_id",
        "primary_category_code",
        model.SeqCategory,
    )

    # Get dict[sample_id, dict[(protocol_id, seq_id), (primary_category_id, id)]]
    natural_key_map: defaultdict[
        UUID, dict[tuple[UUID, UUID | None], tuple[UUID, UUID]]
    ] = defaultdict(dict)
    existing_sample_ids = frozenset(
        {
            cast(UUID, x.id)
            for x, y in zip(samples_for_upload, sample_results)
            if not y.is_new
        }
    )
    if not existing_sample_ids:
        # No existing samples, nothing more to verify
        return success
    result_iter = self.service.repository.read_fields(
        uow,
        user_id,
        model.SeqClassification,
        [
            "sample_id",
            "protocol_id",
            "seq_id",
            "primary_category_id",
            "id",
        ],
        filter=UuidSetFilter(key="sample_id", members=existing_sample_ids),
    )
    for x in result_iter:
        # (protocol_id, seq_id) is the natural key for a SeqClassification within a sample, and should be unique in the database.
        natural_key_map[x[0]][(x[1], x[2])] = (x[3], x[4])

    # Get dict[seq_id, sample_id] to verify that SeqClassifications link to Seqs within the same sample
    existing_seq_id_to_sample_id = (
        self.retrieve_parent_id_by_intra_parent_linked_child_id(
            uow,
            cmd,
            model.SeqClassification,
            "seq_id",
            model.Seq,
        )
    )

    # Verify each SeqClassification
    for sample_for_upload, sample_result in zip(samples_for_upload, sample_results):
        existing_seq_classification_data = natural_key_map.get(
            cast(UUID, sample_for_upload.id)
        )
        for seq_classification_for_upload, seq_classification_result in zip(
            sample_for_upload.seq_classifications or [],
            sample_result.seq_classifications or [],
        ):
            success &= _verify_one_seq_classification(
                self,
                sample_for_upload,
                seq_classification_for_upload,
                seq_classification_result,
                existing_seq_classification_data,
                existing_seq_id_to_sample_id,
            )
    return success


def _verify_one_seq_classification(
    self: BatchUploader,
    sample_for_upload: model.SampleForUpload,
    classification: model.SeqClassificationForUpload,
    result: model.UploadResult,
    existing_data: dict[tuple[UUID, UUID | None], tuple[UUID, UUID]] | None,
    seq_id_to_sample_id: dict[UUID, UUID],
) -> bool:
    """Verify one classification's linked sequence and natural-key match."""
    if result.status == EtlStatus.SKIPPED:
        return True
    success = _verify_classification_seq_sample(
        sample_for_upload, classification, result, seq_id_to_sample_id
    )
    if not existing_data:
        return success
    existing_category_id, existing_id = _get_existing_classification_match(
        self, classification, existing_data
    )
    if existing_category_id is None:
        return success
    assert existing_id is not None
    if existing_category_id != classification.primary_category_id:
        _add_classification_mismatch_error(
            classification, result, existing_category_id, existing_id
        )
        return False
    result.add_info(
        "8be3f4a1",
        f"Existing SeqClassification with same protocol_id ({classification.protocol_id}) and primary_category_id ({classification.primary_category_id}) will have seq_id set from None to ({classification.seq_id})",
    )
    result.is_new = False
    result.id = existing_id
    if classification.id is None:
        classification.id = existing_id
    elif classification.id != existing_id:
        result.add_info(
            "d91a7c4e",
            f"Identical SeqClassification with same protocol_id ({classification.protocol_id}) and seq_id ({classification.seq_id}) already exists with a different ID {existing_id} than new ID {classification.id}. New ID will be replaced in the batch with the existing one.",
        )
        sample_for_upload.replace_child_id(classification, existing_id)
    return success


def _verify_classification_seq_sample(
    sample_for_upload: model.SampleForUpload,
    classification: model.SeqClassificationForUpload,
    result: model.UploadResult,
    seq_id_to_sample_id: dict[UUID, UUID],
) -> bool:
    """Reject a classification linked to a sequence from another sample."""
    seq_id = classification.seq_id
    if seq_id is None or seq_id == NULL_ID:
        return True
    existing_sample_id = seq_id_to_sample_id.get(seq_id)
    if existing_sample_id is None or existing_sample_id == sample_for_upload.id:
        return True
    result.add_error(
        "c1d72e8a",
        f"SeqClassification has seq_id {seq_id} that links to an existing Seq coupled to a different sample with ID {existing_sample_id}",
    )
    return False


def _get_existing_classification_match(
    self: BatchUploader,
    classification: model.SeqClassificationForUpload,
    existing_data: dict[tuple[UUID, UUID | None], tuple[UUID, UUID]],
) -> tuple[UUID | None, UUID | None]:
    """Find an existing classification, including its no-sequence fallback."""
    key = (classification.protocol_id, classification.seq_id)
    category_id, existing_id = existing_data.get(key, (None, None))
    if category_id is None and not self.is_null(classification.seq_id):
        # An existing classification without seq_id may be updated with the supplied ID.
        return existing_data.get((classification.protocol_id, None), (None, None))
    return category_id, existing_id


def _add_classification_mismatch_error(
    classification: model.SeqClassificationForUpload,
    result: model.UploadResult,
    existing_category_id: UUID,
    existing_id: UUID,
) -> None:
    """Report category conflicts with specificity based on the supplied seq ID."""
    if classification.seq_id is None:
        result.add_error(
            "f2a84c91",
            f"Different SeqClassification with same protocol_id ({classification.protocol_id}), seq_id ({classification.seq_id}) already exists with primary_category_id ({existing_category_id}) and ID {existing_id}, but since the new seq classification is derived from an unknown seq_id it cannot be verified if the actual seq_id that was used was indeed different",
        )
        return
    result.add_error(
        "9d3a4f1b",
        f"SeqClassification with same protocol_id ({classification.protocol_id}) and seq_id ({classification.seq_id}) already exists with a different primary_category_id ({existing_category_id}) and ID {existing_id}",
    )


def _verify_children_seq_profiles(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify SeqProfile-specific rules.

    1. Replace protocol code by ID when only code is provided, and verify that the
       referenced Protocol exists and has the correct protocol_type.
    2. Verify that seq_id links to a Seq within the same sample.
    3. Detect existing SeqProfiles by their natural key (sample_id, protocol_id,
       seq_id) so that a SeqProfile with a different content_hash for the
       same key will be rejected.

    Assumptions:
    - The cmd.sample_batch enforces that SeqProfiles do not link to Seqs of
      different samples within the same batch, so it can rely on the fact that any
      SeqProfile.seq_id that refers to a not yet existing Seq will nonetheless
      refer to a Seq that will be linked to the same sample.
    - The generic verify_parents and verify_children methods have already been called to
      verify the existence of the sample and its children, so it can rely on any Sample
      ID and child ID to be valid and present in the database or otherwise having been
      annotated as is_new=True.
    """
    user_id = cmd.user.id if cmd.user else None
    samples_for_upload = cmd.sample_batch.samples
    sample_results = batch_result.samples
    success = True

    # Verify assembly protocols provided by ID and/or code
    success &= _verify_protocol(self, cmd, batch_result, uow, model.SeqProfile)

    # Retrieve and verify locus code maps provided by ID and/or code
    # TODO: 3034 this may have to be updated to allow specifying the protocol through a composite key
    success &= self.verify_link_id(
        list(self.parent_result_items(cmd, batch_result)),
        uow,
        cmd.user,
        "seq_profiles",
        "locus_code_map_id",
        "locus_code_map_code",
        model.LocusCodeMap,
    )

    # Get dict[sample_id, dict[(protocol_id, seq_id), (content_hash, id)]]
    natural_key_map: defaultdict[
        UUID, dict[tuple[UUID, UUID | None], tuple[UUID, UUID]]
    ] = defaultdict(dict)
    existing_sample_ids = frozenset(
        {
            cast(UUID, x.id)
            for x, y in zip(samples_for_upload, sample_results)
            if not y.is_new
        }
    )
    if not existing_sample_ids:
        # No existing samples, nothing more to verify
        return success
    result_iter = self.service.repository.read_fields(
        uow,
        user_id,
        model.SeqProfile,
        [
            "sample_id",
            "protocol_id",
            "seq_id",
            "content_hash",
            "id",
        ],
        filter=UuidSetFilter(key="sample_id", members=existing_sample_ids),
    )
    for x in result_iter:
        # (protocol_id, seq_id) is the natural key for a SeqProfile within a sample, and should be unique in the database.
        natural_key_map[x[0]][(x[1], x[2])] = (x[3], x[4])

    # Get dict[seq_id, sample_id] to verify that SeqProfiles link to Seqs within the same sample
    existing_seq_id_to_sample_id = (
        self.retrieve_parent_id_by_intra_parent_linked_child_id(
            uow,
            cmd,
            model.SeqProfile,
            "seq_id",
            model.Seq,
        )
    )

    # Verify each SeqProfile
    for sample_for_upload, sample_result in zip(samples_for_upload, sample_results):
        existing_seq_profile_data = natural_key_map.get(
            cast(UUID, sample_for_upload.id)
        )
        for seq_profile_for_upload, seq_profile_result in zip(
            sample_for_upload.seq_profiles or [],
            sample_result.seq_profiles or [],
        ):
            success &= _verify_one_seq_profile(
                self,
                sample_for_upload,
                seq_profile_for_upload,
                seq_profile_result,
                existing_seq_profile_data,
                existing_seq_id_to_sample_id,
            )
    return success


def _verify_one_seq_profile(
    self: BatchUploader,
    sample_for_upload: model.SampleForUpload,
    seq_profile: model.SeqProfileForUpload,
    result: model.UploadResult,
    existing_data: dict[tuple[UUID, UUID | None], tuple[UUID, UUID]] | None,
    seq_id_to_sample_id: dict[UUID, UUID],
) -> bool:
    """Verify one profile's linked sequence and existing natural-key match."""
    if result.status == EtlStatus.SKIPPED:
        return True
    success = _verify_profile_seq_sample(
        self, sample_for_upload, seq_profile, result, seq_id_to_sample_id
    )
    if not existing_data:
        return success
    existing_hash, existing_id = _get_existing_seq_profile_match(
        self, seq_profile, existing_data
    )
    if existing_hash is None:
        return success
    assert existing_id is not None
    if (
        seq_profile.content_hash != NULL_ID
        and existing_hash != seq_profile.content_hash
    ):
        _add_seq_profile_hash_mismatch_error(
            seq_profile, result, existing_hash, existing_id
        )
        return False
    if seq_profile.content_hash != NULL_ID:
        result.add_info(
            "1d7c9b53",
            f"Existing SeqProfile with same protocol_id ({seq_profile.protocol_id}) and content_hash ({seq_profile.content_hash}) will have seq_id set from None to ({seq_profile.seq_id})",
        )
    # NULL_ID hashes are computed during upsert and are matched by natural key here.
    result.is_new = False
    result.id = existing_id
    if seq_profile.id is None:
        seq_profile.id = existing_id
    elif seq_profile.id != existing_id:
        result.add_info(
            "a7f1c6d8",
            f"Identical SeqProfile with same protocol_id ({seq_profile.protocol_id}) and seq_id ({seq_profile.seq_id}) already exists with a different ID {existing_id} than new ID {seq_profile.id}. New ID will be replaced in the batch with the existing one.",
        )
        sample_for_upload.replace_child_id(seq_profile, existing_id)
    return success


def _verify_profile_seq_sample(
    self: BatchUploader,
    sample_for_upload: model.SampleForUpload,
    seq_profile: model.SeqProfileForUpload,
    result: model.UploadResult,
    seq_id_to_sample_id: dict[UUID, UUID],
) -> bool:
    """Reject a profile linked to a sequence from another sample."""
    if self.is_null(seq_profile.seq_id):
        return True
    existing_sample_id = seq_id_to_sample_id.get(cast(UUID, seq_profile.seq_id))
    if existing_sample_id is None or existing_sample_id == sample_for_upload.id:
        return True
    result.add_error(
        "0f4a9c3d",
        f"SeqProfile has seq_id {seq_profile.seq_id} that links to an existing Seq coupled to a different sample with ID {existing_sample_id}",
    )
    return False


def _get_existing_seq_profile_match(
    self: BatchUploader,
    seq_profile: model.SeqProfileForUpload,
    existing_data: dict[tuple[UUID, UUID | None], tuple[UUID, UUID]],
) -> tuple[UUID | None, UUID | None]:
    """Find a profile by natural key, including its no-sequence fallback."""
    key = (seq_profile.protocol_id, seq_profile.seq_id)
    content_hash, existing_id = existing_data.get(key, (None, None))
    if content_hash is None and not self.is_null(seq_profile.seq_id):
        return existing_data.get((seq_profile.protocol_id, None), (None, None))
    return content_hash, existing_id


def _add_seq_profile_hash_mismatch_error(
    seq_profile: model.SeqProfileForUpload,
    result: model.UploadResult,
    existing_hash: UUID,
    existing_id: UUID,
) -> None:
    """Record a known content-hash mismatch using the appropriate explanation."""
    if seq_profile.seq_id is None:
        result.add_error(
            "6b2f8e10",
            f"Different SeqProfile with same protocol_id ({seq_profile.protocol_id}), seq_id ({seq_profile.seq_id}) already exists with content_hash ({existing_hash}) and ID {existing_id}, but since the new seq classification is derived from an unknown seq_id it cannot be verified if the actual seq_id that was used was indeed different",
        )
        return
    result.add_error(
        "c4d8a2f7",
        f"SeqProfile with same protocol_id ({seq_profile.protocol_id}) and seq_id ({seq_profile.seq_id}) already exists with a different content_hash ({existing_hash}) and ID {existing_id}",
    )


def _verify_sample_refdata(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify and complete reference data."""
    success = True
    # Read sets: nothing to do
    # Sequences: nothing to do
    # Allele profiles
    success &= _verify_batch_refdata_allele_profiles(self, cmd, batch_result, uow)
    # MLVA profiles
    success &= _verify_batch_refdata_mlva_profiles(self, cmd, batch_result, uow)
    # SNP profiles
    success &= _verify_batch_refdata_snp_profiles(self, cmd, batch_result, uow)
    # K-mer profiles
    success &= _verify_batch_refdata_kmer_profiles(self, cmd, batch_result, uow)

    return success

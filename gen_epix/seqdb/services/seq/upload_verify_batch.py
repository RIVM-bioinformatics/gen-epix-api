from collections import defaultdict
from typing import cast
from uuid import UUID

from gen_epix import fastapp
from gen_epix.commondb.domain.enum import EtlStatus
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.services import BatchUploader
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
    """Check child model existence and consistency"""
    success = True
    # Generic child model verifications
    success &= self.verify_children(
        cmd,
        batch_result,
        uow,
    )

    # Child model specific verifications
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
    """Verify that protocols provided by ID or code exist, and resolve codes to IDs."""
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
    if child_model_class == model.ReadSet:
        valid_protocol_types = enum.ProtocolTypeSet.SEQUENCING.value
    elif child_model_class == model.Seq:
        valid_protocol_types = enum.ProtocolTypeSet.ASSEMBLY.value
    elif child_model_class == model.SeqClassification:
        valid_protocol_types = enum.ProtocolTypeSet.CLASSIFICATION.value
    elif child_model_class == model.SeqTaxonomy:
        valid_protocol_types = enum.ProtocolTypeSet.TAXONOMY.value
    elif child_model_class == model.SeqProfile:
        valid_protocol_types = enum.ProtocolTypeSet.SEQ_PROFILE.value
    elif child_model_class == model.SeqDistance:
        valid_protocol_types = enum.ProtocolTypeSet.SEQ_DISTANCE.value
    else:
        raise NotImplementedError(
            f"Unknown child model class {child_model_class} for protocol verification"
        )
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
        for sample_for_upload, sample_result in zip(
            cmd.sample_batch.samples, batch_result.samples
        ):
            for child_for_upload, child_result in zip(
                getattr(sample_for_upload, children_field_name) or [],
                getattr(sample_result, children_field_name) or [],
            ):
                if child_result.status == EtlStatus.SKIPPED:
                    # Child is already marked as skipped -> nothing left to do
                    continue
                if child_for_upload.protocol_id in invalid_protocol_ids:
                    child_result.add_error(
                        "a4c9e18b",
                        f"Referenced protocol with ID {child_for_upload.protocol_id} has protocol_type {protocol_map[child_for_upload.protocol_id].protocol_type} that is not compatible with {child_model_class.__name__}",
                    )
    return success


def _verify_children_seqs(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """
    Verify Seq specific rules:
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
            if seq_result.status == EtlStatus.SKIPPED:
                # Seq is already marked as skipped -> nothing left to do
                continue
            if not self.is_null(seq_for_upload.read_set_id):
                # Verify if read_set_id links to an existing ReadSet within the same Sample. If it links to a not yet existing ReadSet in this batch, this has already been verified by the SampleBatchForUpload model.
                existing_read_set_sample_id = existing_read_set_id_to_sample_id.get(
                    cast(UUID, seq_for_upload.read_set_id)
                )
                if (
                    existing_read_set_sample_id is not None
                    and existing_read_set_sample_id != sample_for_upload.id
                ):
                    success = False
                    seq_result.add_error(
                        "e5a19c72",
                        f"Seq has read_set_id {seq_for_upload.read_set_id} that links to an existing ReadSet coupled to a different Sample with ID {existing_read_set_sample_id}",
                    )
            if not existing_seq_data:
                # No existing Seqs for this Sample -> nothing left to do
                continue
            existing_seq_hash, existing_seq_id = existing_seq_data.get(
                (
                    seq_for_upload.protocol_id,
                    seq_for_upload.read_set_id,
                    seq_for_upload.read_set2_id,
                ),
                (None, None),
            )
            if existing_seq_hash is None:
                if (
                    seq_for_upload.read_set_id is not None
                    and seq_for_upload.read_set_id != NULL_ID
                ):
                    # New Seq has ReadSet(s) filled in -> check if an existing Seq with the same hash but no ReadSet(s) exists.
                    # In this case, it is assumed that it is (also) the ReadSet ID(s) that need to be set for this existing Seq.
                    # This behaviour is achieved by not assigning the existing_seq_hash so that the checks below classify it as an update.
                    existing_seq_hash, existing_seq_id = existing_seq_data.get(
                        (seq_for_upload.protocol_id, None, None), (None, None)
                    )
                if existing_seq_hash is None:
                    # No existing Seq for this (protocol_id, read_set_id, read_set2_id)
                    continue
            assert existing_seq_id is not None
            if existing_seq_hash != seq_for_upload.seq_hash:
                # New and corresponding existing Seq have different hash -> error since the same protocol and ReadSets should yield the same sequence
                success = False
                if (
                    seq_for_upload.read_set_id is None
                    or seq_for_upload.read_set_id == NULL_ID
                ):
                    # New and existing Seq both do not have ReadSets set -> error since it cannot be verified if the actual ReadSets were indeed identical (in which case a different Seq is an error)
                    seq_result.add_error(
                        "7c1e9ab4",
                        f"Different Seq with same protocol_id ({seq_for_upload.protocol_id}), read_set_id ({seq_for_upload.read_set_id}) and read_set2_id ({seq_for_upload.read_set2_id}) already exists with hash ({existing_seq_hash}) and ID {existing_seq_id}, but since the new Seq is derived from unknown ReadSets it cannot be verified if the actual ReadSets that were used were indeed different",
                    )
                else:
                    # Existing Seq has different hash -> error since the same protocol and ReadSets should yield the same sequence
                    seq_result.add_error(
                        "9d3a4f1b",
                        f"Seq with same protocol_id ({seq_for_upload.protocol_id}), read_set_id ({seq_for_upload.read_set_id}) and read_set2_id ({seq_for_upload.read_set2_id}) already exists with a different hash ({existing_seq_hash}) and ID {existing_seq_id}",
                    )
                continue
            else:
                seq_result.add_info(
                    "b6e14c9f",
                    f"Existing Seq with same protocol_id ({seq_for_upload.protocol_id}) and seq_hash will have ReadSets set from None to (read_set_id: {seq_for_upload.read_set_id}, read_set2_id: {seq_for_upload.read_set2_id})",
                )

            # At this point, an existing Seq with the same natural key and same hash has been found
            seq_result.is_new = False
            seq_result.id = existing_seq_id
            if seq_for_upload.id is None:
                # No ID set for the new Seq -> set equal to the existing Seq
                seq_for_upload.id = existing_seq_id
                continue
            if seq_for_upload.id != existing_seq_id:
                # Different ID for the new Seq -> treated as a temporary ID meant to create links to this Seq within the upload batch
                # Replace the temporary with the existing ID in all children within the batch that link to this Seq through the temporary ID, and replace the temporary ID by the existing ID for this Seq.
                seq_result.add_info(
                    "4fa2d87c",
                    f"Identical Seq with same protocol_id ({seq_for_upload.protocol_id}), read_set_id ({seq_for_upload.read_set_id}) and read_set2_id ({seq_for_upload.read_set2_id}) already exists with a different ID {existing_seq_id} than new ID {seq_for_upload.id}. New ID will be replaced in the batch with the existing one.",
                )
                sample_for_upload.replace_child_id(seq_for_upload, existing_seq_id)
    return success


def _verify_children_seq_classifications(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """
    Verify SeqClassification specific rules:
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
            if seq_classification_result.status == EtlStatus.SKIPPED:
                # Seq is already marked as skipped -> nothing left to do
                continue
            if (
                seq_classification_for_upload.seq_id is not None
                and seq_classification_for_upload.seq_id != NULL_ID
            ):
                # Verify if seq_id links to an existing Seq within the same sample. If it links to a not yet existing Seq in this batch, this has already been verified by the SampleBatchForUpload model.
                existing_seq_classification_sample_id = (
                    existing_seq_id_to_sample_id.get(
                        cast(UUID, seq_classification_for_upload.seq_id)
                    )
                )
                if (
                    existing_seq_classification_sample_id is not None
                    and existing_seq_classification_sample_id != sample_for_upload.id
                ):
                    success = False
                    seq_classification_result.add_error(
                        "c1d72e8a",
                        f"SeqClassification has seq_id {seq_classification_for_upload.seq_id} that links to an existing Seq coupled to a different sample with ID {existing_seq_classification_sample_id}",
                    )
            if not existing_seq_classification_data:
                # No existing SeqClassifications for this sample -> nothing left to do
                continue
            existing_primary_category_id, existing_seq_classification_id = (
                existing_seq_classification_data.get(
                    (
                        seq_classification_for_upload.protocol_id,
                        seq_classification_for_upload.seq_id,
                    ),
                    (None, None),
                )
            )
            if existing_primary_category_id is None:
                if not self.is_null(seq_classification_for_upload.seq_id):
                    # New SeqClassification has seq_id filled in -> check if an existing SeqClassification with the same primary_category_id but no linked Seq exists.
                    # In this case, it is assumed that it is (also) the seq_id that needs to be set for this existing SeqClassification.
                    # This behaviour is achieved by not assigning the existing_primary_category_id so that the checks below classify it as an update.
                    existing_primary_category_id, existing_seq_classification_id = (
                        existing_seq_classification_data.get(
                            (seq_classification_for_upload.protocol_id, None),
                            (None, None),
                        )
                    )
                if existing_primary_category_id is None:
                    # No existing seq classification for this (protocol_id, seq_id)
                    continue
            assert existing_seq_classification_id is not None
            if (
                existing_primary_category_id
                != seq_classification_for_upload.primary_category_id
            ):
                # New and corresponding existing seq classification have different primary_category_id -> error since the same protocol and seq_id should yield the same classification
                success = False
                if seq_classification_for_upload.seq_id is None:
                    # New and existing SeqClassification both do not have seq_id set -> error since it cannot be verified if the actual seq_ids were indeed identical (in which case a different seq classification is an error)
                    seq_classification_result.add_error(
                        "f2a84c91",
                        f"Different SeqClassification with same protocol_id ({seq_classification_for_upload.protocol_id}), seq_id ({seq_classification_for_upload.seq_id}) already exists with primary_category_id ({existing_primary_category_id}) and ID {existing_seq_classification_id}, but since the new seq classification is derived from an unknown seq_id it cannot be verified if the actual seq_id that was used was indeed different",
                    )
                else:
                    # Existing seq classification has different primary_category_id -> error since the same protocol and seq_id should yield the same classification
                    seq_classification_result.add_error(
                        "9d3a4f1b",
                        f"SeqClassification with same protocol_id ({seq_classification_for_upload.protocol_id}) and seq_id ({seq_classification_for_upload.seq_id}) already exists with a different primary_category_id ({existing_primary_category_id}) and ID {existing_seq_classification_id}",
                    )
                continue
            else:
                seq_classification_result.add_info(
                    "8be3f4a1",
                    f"Existing SeqClassification with same protocol_id ({seq_classification_for_upload.protocol_id}) and primary_category_id ({seq_classification_for_upload.primary_category_id}) will have seq_id set from None to ({seq_classification_for_upload.seq_id})",
                )

            # At this point, an existing SeqClassification with the same natural key and primary_category_id has been found
            seq_classification_result.is_new = False
            seq_classification_result.id = existing_seq_classification_id
            if seq_classification_for_upload.id is None:
                # No ID set for the new SeqClassification -> set equal to the existing SeqClassification
                seq_classification_for_upload.id = existing_seq_classification_id
                continue
            if seq_classification_for_upload.id != existing_seq_classification_id:
                # Different ID for the new SeqClassification -> treated as a temporary ID meant to create links to this SeqClassification within the upload batch
                # Replace the temporary with the existing ID in all children within the batch that link to this SeqClassification through the temporary ID, and replace the temporary ID by the existing ID for this SeqClassification.
                seq_classification_result.add_info(
                    "d91a7c4e",
                    f"Identical SeqClassification with same protocol_id ({seq_classification_for_upload.protocol_id}) and seq_id ({seq_classification_for_upload.seq_id}) already exists with a different ID {existing_seq_classification_id} than new ID {seq_classification_for_upload.id}. New ID will be replaced in the batch with the existing one.",
                )
                sample_for_upload.replace_child_id(
                    seq_classification_for_upload, existing_seq_classification_id
                )
    return success


def _verify_children_seq_profiles(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """
    Verify SeqProfile specific rules:
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
            if seq_profile_result.status == EtlStatus.SKIPPED:
                # Seq is already marked as skipped -> nothing left to do
                continue
            if not self.is_null(seq_profile_for_upload.seq_id):
                # Verify if seq_id links to an existing Seq within the same sample. If it links to a not yet existing Seq in this batch, this has already been verified by the SampleBatchForUpload model.
                existing_seq_profile_sample_id = existing_seq_id_to_sample_id.get(
                    cast(UUID, seq_profile_for_upload.seq_id)
                )
                if (
                    existing_seq_profile_sample_id is not None
                    and existing_seq_profile_sample_id != sample_for_upload.id
                ):
                    success = False
                    seq_profile_result.add_error(
                        "0f4a9c3d",
                        f"SeqProfile has seq_id {seq_profile_for_upload.seq_id} that links to an existing Seq coupled to a different sample with ID {existing_seq_profile_sample_id}",
                    )
            if not existing_seq_profile_data:
                # No existing SeqProfiles for this sample -> nothing left to do
                continue
            existing_content_hash, existing_seq_profile_id = (
                existing_seq_profile_data.get(
                    (
                        seq_profile_for_upload.protocol_id,
                        seq_profile_for_upload.seq_id,
                    ),
                    (None, None),
                )
            )
            if existing_content_hash is None:
                if not self.is_null(seq_profile_for_upload.seq_id):
                    # New SeqProfile has seq_id filled in -> check if an existing SeqProfile with the same content_hash but no linked Seq exists.
                    # In this case, it is assumed that it is (also) the seq_id that needs to be set for this existing SeqProfile.
                    # This behaviour is achieved by not assigning the existing_content_hash so that the checks below classify it as an update.
                    existing_content_hash, existing_seq_profile_id = (
                        existing_seq_profile_data.get(
                            (seq_profile_for_upload.protocol_id, None),
                            (None, None),
                        )
                    )
                if existing_content_hash is None:
                    # No existing seq classification for this (protocol_id, seq_id)
                    continue
            assert existing_seq_profile_id is not None
            if existing_content_hash != seq_profile_for_upload.content_hash:
                # New and corresponding existing seq classification have different content_hash -> error since the same protocol and seq_id should yield the same classification
                success = False
                if seq_profile_for_upload.seq_id is None:
                    # New and existing SeqProfile both do not have seq_id set -> error since it cannot be verified if the actual seq_ids were indeed identical (in which case a different seq classification is an error)
                    seq_profile_result.add_error(
                        "6b2f8e10",
                        f"Different SeqProfile with same protocol_id ({seq_profile_for_upload.protocol_id}), seq_id ({seq_profile_for_upload.seq_id}) already exists with content_hash ({existing_content_hash}) and ID {existing_seq_profile_id}, but since the new seq classification is derived from an unknown seq_id it cannot be verified if the actual seq_id that was used was indeed different",
                    )
                else:
                    # Existing seq classification has different content_hash -> error since the same protocol and seq_id should yield the same classification
                    seq_profile_result.add_error(
                        "c4d8a2f7",
                        f"SeqProfile with same protocol_id ({seq_profile_for_upload.protocol_id}) and seq_id ({seq_profile_for_upload.seq_id}) already exists with a different content_hash ({existing_content_hash}) and ID {existing_seq_profile_id}",
                    )
                continue
            else:
                seq_profile_result.add_info(
                    "1d7c9b53",
                    f"Existing SeqProfile with same protocol_id ({seq_profile_for_upload.protocol_id}) and content_hash ({seq_profile_for_upload.content_hash}) will have seq_id set from None to ({seq_profile_for_upload.seq_id})",
                )

            # At this point, an existing SeqProfile with the same natural key and content_hash has been found
            seq_profile_result.is_new = False
            seq_profile_result.id = existing_seq_profile_id
            if seq_profile_for_upload.id is None:
                # No ID set for the new SeqProfile -> set equal to the existing SeqProfile
                seq_profile_for_upload.id = existing_seq_profile_id
                continue
            if seq_profile_for_upload.id != existing_seq_profile_id:
                # Different ID for the new SeqProfile -> treated as a temporary ID meant to create links to this SeqProfile within the upload batch
                # Replace the temporary with the existing ID in all children within the batch that link to this SeqProfile through the temporary ID, and replace the temporary ID by the existing ID for this SeqProfile.
                seq_profile_result.add_info(
                    "a7f1c6d8",
                    f"Identical SeqProfile with same protocol_id ({seq_profile_for_upload.protocol_id}) and seq_id ({seq_profile_for_upload.seq_id}) already exists with a different ID {existing_seq_profile_id} than new ID {seq_profile_for_upload.id}. New ID will be replaced in the batch with the existing one.",
                )
                sample_for_upload.replace_child_id(
                    seq_profile_for_upload, existing_seq_profile_id
                )
    return success


def _verify_sample_refdata(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """
    Verify and complete reference data.
    """
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

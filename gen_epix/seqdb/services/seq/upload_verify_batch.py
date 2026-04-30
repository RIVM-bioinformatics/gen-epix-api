from collections import defaultdict
from uuid import UUID

from gen_epix import fastapp
from gen_epix.commondb.domain.enum import EtlStatus, UploadAction
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.services import BatchUploader
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import command, model
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


def _verify_children_seqs(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify seq specific rules"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = batch_result.samples
    success = True

    # Retrieve and verify assembly protocols provided by ID and/or code
    success &= self.verify_link_id(
        list(self.parent_result_items(cmd, batch_result)),
        uow,
        cmd.user,
        "seqs",
        "protocol_id",
        "protocol_code",
        model.Protocol,
    )

    # Get dict[(sample_id, seq_hash), [(read_set_id, read_set2_id, protocol_id, id)]
    sample_ids = list({sample.id for sample in samples if sample.id is not None})
    if not sample_ids:
        # No samples with ID, nothing to verify
        return success
    result_iter = self.service.repository.read_fields(
        uow,
        user_id,
        model.Seq,
        [
            "sample_id",
            "seq_hash",
            "read_set_id",
            "read_set2_id",
            "protocol_id",
            "id",
        ],
        filter=UuidSetFilter(key="sample_id", members=frozenset(sample_ids)),
    )
    key_map: defaultdict[tuple[UUID, UUID], list[tuple]] = defaultdict(list)
    for x in result_iter:
        key_map[(x[0], x[1])].append((x[2], x[3], x[4], x[5]))

    # Verify each seq
    has_existing_seqs = False
    for sample, sample_result in zip(samples, sample_results):
        if sample.id is None or sample.id == NULL_ID:
            # Sample does not exist
            continue
        for seq, seq_result in zip(sample.seqs or [], sample_result.seqs or []):
            if seq_result.status == EtlStatus.SKIPPED:
                # Seq is already marked as skipped, no need to verify
                continue
            existing_seq_data = key_map.get((sample.id, seq.seq_hash))
            if existing_seq_data is None:
                # No existing seq with this hash for this sample
                continue
            # Compare existing seqs with this hash
            for (
                read_set_id,
                read_set2_id,
                protocol_id,
                seq_id,
            ) in existing_seq_data:
                if seq.protocol_id != protocol_id:
                    # Different protocol, cannot give rise to an issue
                    continue
                if seq.read_set_id == read_set_id and seq.read_set2_id == read_set2_id:
                    # Same read sets -> skip since the seq is identical and there are
                    # no immutable parts
                    old_seq_id = seq.id
                    seq.id = seq_id
                    seq_result.add_warning(
                        "a2b3c4d5",
                        f"Seq with same hash ({seq.seq_hash}), read sets and protocol already exists",
                    )
                    seq_result.status = EtlStatus.SKIPPED
                    # Propagate the resolved DB ID to any child records that were
                    # pointing to the pre-assigned ID
                    if old_seq_id is not None and old_seq_id != seq_id:
                        for sc in sample.seq_classifications or []:
                            if sc.seq_id == old_seq_id:
                                sc.seq_id = seq_id
                        for st in sample.seq_taxonomies or []:
                            if st.seq_id == old_seq_id:
                                st.seq_id = seq_id
                        for sp in sample.seq_profiles or []:
                            if sp.seq_id == old_seq_id:
                                sp.seq_id = seq_id
                    break
                if seq.read_set_id is None and seq.read_set2_id is None:
                    # New seq with same hash but unknown read sets -> error since
                    # cannot verify if indeed it was derived from the same reads sets
                    success = False
                    seq_result.add_error(
                        "b9e4f8a1",
                        f"Seq with same hash ({seq.seq_hash}) and protocol already exists with ID {seq_id}, but new seq has no read sets no read sets are provided for the new seq to compare",
                    )
                    break
    return success


def _verify_children_seq_classifications(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """
    Detect existing SeqClassifications by their natural key (seq_id, protocol_id).

    verify_children only looks up children by their id field, which is None for
    SeqClassificationForUpload objects built from on-prem JSON. This function
    fills in the existing id and marks the result appropriately so that
    create_children does not attempt a duplicate INSERT.
    """
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = batch_result.samples
    success = True

    # Collect all seq_ids referenced by seq_classifications in this batch.
    seq_ids = list(
        {
            sc.seq_id
            for s in samples
            for sc in s.seq_classifications or []
            if sc.seq_id is not None and sc.seq_id != NULL_ID
        }
    )
    if not seq_ids:
        return success

    # Retrieve existing seq_classifications keyed by (seq_id, protocol_id).
    result_iter = self.service.repository.read_fields(
        uow,
        user_id,
        model.SeqClassification,
        ["seq_id", "protocol_id", "id"],
        filter=UuidSetFilter(key="seq_id", members=frozenset(seq_ids)),
    )
    existing_map: dict[tuple[UUID, UUID], UUID] = {
        (x[0], x[1]): x[2] for x in result_iter
    }
    if not existing_map:
        return success

    for sample, sample_result in zip(samples, sample_results):
        for sc, sc_result in zip(
            sample.seq_classifications or [],
            sample_result.seq_classifications or [],
        ):
            if sc_result.status != EtlStatus.PENDING:
                continue
            if sc.seq_id is None or sc.seq_id == NULL_ID:
                continue
            if sc.protocol_id is None or sc.protocol_id == NULL_ID:
                continue
            existing_id = existing_map.get((sc.seq_id, sc.protocol_id))
            if existing_id is None:
                continue
            # Existing SeqClassification found: fill in its id and mark as not new.
            sc.id = existing_id
            sc_result.id = existing_id
            sc_result.is_new = False
            if cmd.on_exists == UploadAction.ERROR:
                success = False
                sc_result.add_error(
                    "d4c5b6a7",
                    f"SeqClassification (seq_id={sc.seq_id}, protocol_id={sc.protocol_id}) already exists and on_exists={cmd.on_exists.value}",
                )
            elif cmd.on_exists == UploadAction.SKIP:
                sc_result.status = EtlStatus.SKIPPED
                sc_result.add_info(
                    "c3b4a5d6",
                    f"SeqClassification (seq_id={sc.seq_id}, protocol_id={sc.protocol_id}) already exists and on_exists={cmd.on_exists.value}",
                )

    return success


def _verify_children_seq_profiles(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify seq profile specific rules"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = batch_result.samples
    success = True

    # Get sample IDs
    sample_ids = list({x.id for x in samples if x.id is not None})
    if not sample_ids:
        # No existing samples, nothing to verify
        return success
    seq_profile_result_pairs = list(self.parent_result_items(cmd, batch_result))

    # Retrieve and verify locus detection protocols provided by ID and/or code
    # TODO: 3034 this may have to be updated to allow specifying the protocol through a composite key
    success &= self.verify_link_id(
        seq_profile_result_pairs,
        uow,
        cmd.user,
        "seq_profiles",
        "protocol_id",
        "protocol_code",
        model.Protocol,
    )

    # Retrieve and verify locus code maps provided by ID and/or code
    success &= self.verify_link_id(
        seq_profile_result_pairs,
        uow,
        cmd.user,
        "seq_profiles",
        "locus_code_map_id",
        "locus_code_map_code",
        model.LocusCodeMap,
    )

    # Get dict[(sample_id, content_hash), [(protocol_id, seq_id, id)]
    result_iter = self.service.repository.read_fields(
        uow,
        user_id,
        model.SeqProfile,
        [
            "sample_id",
            "content_hash",
            "protocol_id",
            "seq_id",
            "id",
        ],
        filter=UuidSetFilter(key="sample_id", members=frozenset(sample_ids)),
    )
    key_map: defaultdict[tuple[UUID, UUID], list[tuple]] = defaultdict(list)
    for x in result_iter:
        key_map[(x[0], x[1])].append((x[2], x[3], x[4]))

    # Verify each seq profile
    for sample, sample_result in zip(samples, sample_results):
        if sample.id is None or sample.id == NULL_ID:
            # Sample does not exist
            continue
        for seq_profile, seq_profile_result in zip(
            sample.seq_profiles or [], sample_result.seq_profiles or []
        ):
            if seq_profile_result.status == EtlStatus.SKIPPED:
                # Seq profile is already marked as skipped, no need to verify
                continue
            existing_seq_profile_data = key_map.get(
                (sample.id, seq_profile.content_hash)
            )
            if existing_seq_profile_data is None:
                # No existing seq profile with this hash for this sample
                continue
            # Compare existing seq profiles with this hash
            for (
                protocol_id,
                seq_id,
                seq_profile_id,
            ) in existing_seq_profile_data:
                if seq_profile.protocol_id != protocol_id:
                    # Different protocol, cannot give rise to an issue
                    continue
                if seq_profile.seq_id == seq_id:
                    # Same seq -> skip since the seq profile is identical and there are
                    # no immutable parts
                    seq_profile.id = seq_profile_id
                    seq_profile_result.id = seq_profile_id
                    seq_profile_result.add_warning(
                        "c7d8e9f0",
                        f"Seq profile with same hash ({seq_profile.content_hash}), seq and protocol already exists",
                    )
                    seq_profile_result.status = EtlStatus.SKIPPED
                    break
                if seq_profile.seq_id is None:
                    # New seq profile with same hash but unknown read sets -> error since
                    # cannot verify if indeed it was derived from the same seq
                    success = False
                    seq_profile_result.add_error(
                        "a8f3e7b2",
                        f"Seq profile with same hash ({seq_profile.content_hash}) and protocol already exists with ID {seq_profile_id}, but new seq profile has no seq ID provided for the new seq profile to compare",
                    )
                    break
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

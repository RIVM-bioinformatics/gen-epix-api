from collections import defaultdict
from uuid import UUID

from gen_epix import fastapp
from gen_epix.commondb.domain.enum import OnExistsUploadAction, UploadStatus
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.services import BatchUploader
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.services.seq.upload_verify_batch_refdata import (
    _verify_batch_refdata_allele_profiles,
)


def _verify_sample_children(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Check child model existence and consistency"""
    success = True
    # Generic child model verifications
    success &= self.verify_children(
        cmd,
        retval,
        uow,
    )

    # Child model specific verifications
    success &= _verify_children_seqs(self, cmd, retval, uow)
    success &= _verify_children_allele_profiles(self, cmd, retval, uow)

    return success


def _verify_children_seqs(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify seq specific rules"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Retrieve and verify assembly protocols provided by ID and/or code
    success &= self.verify_link_id(
        cmd,
        retval,
        uow,
        model.Seq,
        "assembly_protocol_id",
        "assembly_protocol_code",
        model.AssemblyProtocol,
    )

    # Get dict[(sample_id, seq_hash), [(read_set_id, read_set2_id, assembly_protocol_id, id)]
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
            "assembly_protocol_id",
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
            existing_seq_data = key_map.get((sample.id, seq.seq_hash))
            if existing_seq_data is None:
                # No existing seq with this hash for this sample
                continue
            # Compare existing seqs with this hash
            for (
                read_set_id,
                read_set2_id,
                assembly_protocol_id,
                seq_id,
            ) in existing_seq_data:
                if seq.assembly_protocol_id != assembly_protocol_id:
                    # Different assembly protocol, cannot give rise to an issue
                    continue
                if seq.read_set_id == read_set_id and seq.read_set2_id == read_set2_id:
                    # Same read sets -> skip since the seq is identical and there are
                    # no immutable parts
                    seq.id = seq_id
                    seq_result.add_warning(
                        "a2b3c4d5",
                        f"Seq with same hash ({seq.seq_hash}), read sets and assembly protocol already exists",
                    )
                    seq_result.status = UploadStatus.SKIPPED
                    if cmd.on_exists == OnExistsUploadAction.ERROR:
                        success = False
                        seq_result.add_error(
                            "b4c5d6e7",
                            f"{seq.__class__.NAME} already exists and on_exists={cmd.on_exists.value}",
                        )
                    elif cmd.on_exists == OnExistsUploadAction.SKIP:
                        seq_result.add_info(
                            "7a9f4c2e",
                            f"{seq.__class__.NAME} already exists and on_exists={cmd.on_exists.value}",
                        )
                    break
                if seq.read_set_id is None and seq.read_set2_id is None:
                    # New seq with same hash but unknown read sets -> error since
                    # cannot verify if indeed it was derived from the same reads sets
                    success = False
                    seq_result.add_error(
                        "f1e2d3c4",
                        f"Seq with same hash ({seq.seq_hash}) and assembly protocol already exists with ID {seq_id}, but new seq has no read sets no read sets are provided for the new seq to compare",
                    )
                    break
    return success


def _verify_children_allele_profiles(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify allele profile specific rules"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Get sample IDs
    sample_ids = list({x.id for x in samples if x.id is not None})
    if not sample_ids:
        # No existing samples, nothing to verify
        return success

    # Retrieve and verify locus detection protocols provided by ID and/or code
    success &= self.verify_link_id(
        cmd,
        retval,
        uow,
        model.AlleleProfile,
        "locus_detection_protocol_id",
        "locus_detection_protocol_code",
        model.LocusDetectionProtocol,
    )

    # Retrieve and verify locus sets provided by ID and/or code
    success &= self.verify_link_id(
        cmd,
        retval,
        uow,
        model.AlleleProfile,
        "locus_set_id",
        "locus_set_code",
        model.LocusSet,
    )

    # Retrieve and verify locus code maps provided by ID and/or code
    success &= self.verify_link_id(
        cmd,
        retval,
        uow,
        model.AlleleProfile,
        "locus_code_map_id",
        "locus_code_map_code",
        model.LocusCodeMap,
    )

    # Get dict[(sample_id, allele_profile_hash), [(locus_detection_protocol_id, locus_set_id, seq_id,id)]
    result_iter = self.service.repository.read_fields(
        uow,
        user_id,
        model.AlleleProfile,
        [
            "sample_id",
            "allele_profile_hash",
            "locus_detection_protocol_id",
            "locus_set_id",
            "seq_id",
            "id",
        ],
        filter=UuidSetFilter(key="sample_id", members=frozenset(sample_ids)),
    )
    key_map: defaultdict[tuple[UUID, UUID], list[tuple]] = defaultdict(list)
    for x in result_iter:
        key_map[(x[0], x[1])].append((x[2], x[3], x[4], x[5]))

    # Verify each allele profile
    for sample, sample_result in zip(samples, sample_results):
        if sample.id is None or sample.id == NULL_ID:
            # Sample does not exist
            continue
        for allele_profile, allele_profile_result in zip(
            sample.allele_profiles or [], sample_result.allele_profiles or []
        ):
            existing_allele_profile_data = key_map.get(
                (sample.id, allele_profile.allele_profile_hash)
            )
            if existing_allele_profile_data is None:
                # No existing allele profile with this hash for this sample
                continue
            # Compare existing allele profiles with this hash
            for (
                locus_detection_protocol_id,
                locus_set_id,
                seq_id,
                allele_profile_id,
            ) in existing_allele_profile_data:
                if (
                    allele_profile.locus_detection_protocol_id
                    != locus_detection_protocol_id
                ):
                    # Different locus detection protocol, cannot give rise to an issue
                    continue
                if allele_profile.locus_set_id != locus_set_id:
                    # Different locus set, cannot give rise to an issue
                    continue
                if allele_profile.seq_id == seq_id:
                    # Same seq -> skip since the allele profile is identical and there are
                    # no immutable parts
                    allele_profile.id = allele_profile_id
                    allele_profile_result.add_warning(
                        "c7d8e9f0",
                        f"Allele profile with same hash ({allele_profile.allele_profile_hash}), seq and assembly protocol already exists",
                    )
                    allele_profile_result.status = UploadStatus.SKIPPED
                    if cmd.on_exists == OnExistsUploadAction.ERROR:
                        success = False
                        allele_profile_result.add_error(
                            "d8a3b7f4",
                            f"{allele_profile.__class__.NAME} already exists and on_exists={cmd.on_exists.value}",
                        )
                    elif cmd.on_exists == OnExistsUploadAction.SKIP:
                        allele_profile_result.add_info(
                            "e4f2a1b3",
                            f"{allele_profile.__class__.NAME} already exists and on_exists={cmd.on_exists.value}",
                        )
                    break
                if allele_profile.seq_id is None:
                    # New allele profile with same hash but unknown read sets -> error since
                    # cannot verify if indeed it was derived from the same seq
                    success = False
                    allele_profile_result.add_error(
                        "a8f3e7b2",
                        f"Allele profile with same hash ({allele_profile.allele_profile_hash}) and assembly protocol already exists with ID {allele_profile_id}, but new allele profile has no seq ID provided for the new allele profile to compare",
                    )
                    break
    return success


def _verify_sample_refdata(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """
    Verify and complete reference data.
    """
    success = True
    # Read sets: nothing to do
    # Sequences: nothing to do
    # Allele profiles
    success &= _verify_batch_refdata_allele_profiles(self, cmd, retval, uow)

    return success

"""Implement seqdb sequence service behavior for services.seq.upload_verify_batch_refdata."""

from collections.abc import Collection
from typing import Any, cast
from uuid import UUID

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import UploadResult
from gen_epix.commondb.services import BatchUploader
from gen_epix.etl.enum import EtlStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.literal import MLVA_NO_LOCUS_REPEAT_NUMBER


def _verify_batch_refdata_allele_profiles(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: Any,
) -> bool:
    """Verify and complete reference data for allele profiles."""
    user_id = cmd.user.id if cmd.user else None
    profiles, profile_results = _collect_pending_allele_profiles(cmd, batch_result)
    if not profiles:
        # Nothing to do
        return True

    protocol_map, locus_set_map, reverse_locus_code_maps = _load_profile_reference_data(
        self, uow, user_id, profiles
    )
    success, unique_allele_ids = _convert_allele_profiles_to_ids(
        profiles, profile_results, protocol_map, locus_set_map, reverse_locus_code_maps
    )
    existing_allele_ids = _get_existing_allele_ids(
        self, uow, user_id, unique_allele_ids
    )
    new_allele_ids = unique_allele_ids - existing_allele_ids
    new_allele_locus_map = _prepare_allele_profiles_for_upload(
        profiles, profile_results, protocol_map, locus_set_map, new_allele_ids
    )
    if new_allele_locus_map:
        success &= _reconcile_provided_alleles(
            batch_result, cmd.sample_batch, new_allele_locus_map
        )
    else:
        # Every allele referenced in every profile is already stored. Any allele
        # sequences included in the upload payload are redundant — drop them so
        # _create_sample_refdata does not call UPSERT_SOME and trigger an
        # expensive full-row reload of up to 3004 immutable allele records.
        provided_alleles = cmd.sample_batch.alleles
        if provided_alleles:
            del provided_alleles[:]
    return success


def _collect_pending_allele_profiles(
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
) -> tuple[list[model.SeqProfileForUpload], list[UploadResult]]:
    """Collect pending allele profiles and their matching upload results."""
    profiles: list[model.SeqProfileForUpload] = []
    profile_results: list[UploadResult] = []
    for sample, sample_result in zip(cmd.sample_batch.samples, batch_result.samples):
        for profile, profile_result in zip(
            sample.seq_profiles or [], sample_result.seq_profiles or []
        ):
            if profile_result.status != EtlStatus.PENDING:
                continue
            if profile.seq_profile_type not in enum.SeqProfileTypeSet.ALLELE.value:
                continue
            profiles.append(profile)
            profile_results.append(profile_result)
    return profiles, profile_results


def _load_profile_reference_data(
    self: BatchUploader,
    uow: Any,
    user_id: UUID | None,
    profiles: list[model.SeqProfileForUpload],
) -> tuple[
    dict[UUID, model.Protocol],
    dict[UUID, model.LocusSet],
    dict[UUID, dict[UUID, str]],
]:
    """Load protocols, locus sets, and optional reverse locus-code maps."""
    uq_protocol_ids = {profile.protocol_id for profile in profiles}
    protocols: list[model.Protocol] = self.service.repository.crud(
        uow,
        user_id,
        model.Protocol,
        CrudOperation.READ_SOME,
        obj_ids=list(uq_protocol_ids),
    )
    protocol_map = {cast(UUID, protocol.id): protocol for protocol in protocols}
    locus_set_ids = {
        protocol_map[profile.protocol_id].locus_set_id for profile in profiles
    }
    locus_sets: list[model.LocusSet] = self.service.repository.crud(
        uow,
        user_id,
        model.LocusSet,
        CrudOperation.READ_SOME,
        obj_ids=list(locus_set_ids),
    )
    locus_set_map = {cast(UUID, locus_set.id): locus_set for locus_set in locus_sets}
    locus_code_map_ids = {
        profile.locus_code_map_id
        for profile in profiles
        if profile.locus_code_map_id is not None
        and profile.locus_code_map_id != NULL_ID
    }
    locus_code_maps: list[model.LocusCodeMap] = self.service.repository.crud(
        uow,
        user_id,
        model.LocusCodeMap,
        CrudOperation.READ_SOME,
        obj_ids=list(locus_code_map_ids),
    )
    reverse_locus_code_maps = {
        cast(UUID, locus_code_map.id): {
            locus_id: code for code, locus_id in locus_code_map.code_map.items()
        }
        for locus_code_map in locus_code_maps
    }
    return protocol_map, locus_set_map, reverse_locus_code_maps


def _convert_allele_profiles_to_ids(
    profiles: list[model.SeqProfileForUpload],
    profile_results: list[UploadResult],
    protocol_map: dict[UUID, model.Protocol],
    locus_set_map: dict[UUID, model.LocusSet],
    reverse_locus_code_maps: dict[UUID, dict[UUID, str]],
) -> tuple[bool, set[UUID]]:
    """Normalize allele profile inputs and collect referenced allele IDs."""
    success = True
    unique_allele_ids: set[UUID] = set()
    for profile, profile_result in zip(profiles, profile_results):
        if profile_result.status != EtlStatus.PENDING:
            continue
        locus_ids = locus_set_map[
            protocol_map[profile.protocol_id].locus_set_id
        ].locus_ids
        allele_ids = _get_allele_ids_for_profile(
            profile, profile_result, locus_ids, reverse_locus_code_maps
        )
        if allele_ids is None:
            success = False
            continue
        if len(allele_ids) != len(locus_ids):
            success = False
            profile_result.add_error(
                "b29dcaf6",
                f"Length of allele_ids ({len(allele_ids)}) does not match number of loci in locus set ({len(locus_ids)})",
            )
            continue
        unique_allele_ids.update(
            allele_id
            for allele_id in allele_ids
            if allele_id is not None and allele_id != NULL_ID
        )
    return success, unique_allele_ids


def _get_allele_ids_for_profile(
    profile: model.SeqProfileForUpload,
    profile_result: UploadResult,
    locus_ids: list[UUID],
    reverse_locus_code_maps: dict[UUID, dict[UUID, str]],
) -> list[UUID | None] | None:
    """Resolve one allele profile's supported input representation to IDs."""
    if profile.locus_allele_id_map is not None:
        # Convert locus_allele_id_map representation to allele_ids.
        reverse_locus_code_map = reverse_locus_code_maps[profile.locus_code_map_id]
        allele_ids = [
            profile.locus_allele_id_map.get(reverse_locus_code_map[locus_id])
            for locus_id in locus_ids
        ]
        profile.allele_ids = allele_ids
        profile.locus_allele_id_map = None
        return allele_ids
    if profile.content:
        if profile.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
            return profile.get_allele_ids()
        profile_result.add_error(
            "a6097022",
            f"Allele profile format {profile.format} is not supported for upload",
        )
        return None
    if profile.allele_ids is not None:
        return profile.allele_ids
    profile_result.add_error(
        "b4cb2ea0",
        "Allele profile must provide one of: content, allele_ids, or locus_allele_id_map",
    )
    return None


def _get_existing_allele_ids(
    self: BatchUploader,
    uow: Any,
    user_id: UUID | None,
    allele_ids: set[UUID],
) -> set[UUID]:
    """Retrieve existing allele IDs in bounded chunks."""
    allele_id_list = list(allele_ids)
    chunk_size = 1000  # TODO: make configurable
    existing_allele_ids: set[UUID] = set()
    for start in range(0, len(allele_id_list), chunk_size):
        current_ids = allele_id_list[start : start + chunk_size]
        is_existing: list[bool] = self.service.repository.crud(
            uow,
            user_id,
            model.Allele,
            CrudOperation.EXISTS_SOME,
            obj_ids=current_ids,
        )
        existing_allele_ids.update(
            allele_id for allele_id, exists in zip(current_ids, is_existing) if exists
        )
    return existing_allele_ids


def _prepare_allele_profiles_for_upload(
    profiles: list[model.SeqProfileForUpload],
    profile_results: list[UploadResult],
    protocol_map: dict[UUID, model.Protocol],
    locus_set_map: dict[UUID, model.LocusSet],
    new_allele_ids: set[UUID],
) -> dict[UUID, UUID]:
    """Record loci for new alleles and normalize profile content for storage."""
    new_allele_locus_map: dict[UUID, UUID] = {}
    for profile, profile_result in zip(profiles, profile_results):
        if profile_result.status != EtlStatus.PENDING:
            continue
        locus_ids = locus_set_map[
            protocol_map[profile.protocol_id].locus_set_id
        ].locus_ids
        assert profile.allele_ids is not None
        allele_ids = profile.allele_ids
        for allele_id, locus_id in zip(allele_ids, locus_ids):
            if allele_id not in new_allele_ids or allele_id in new_allele_locus_map:
                continue
            assert allele_id is not None
            new_allele_locus_map[allele_id] = locus_id
        if profile.content != "":
            continue
        profile.content = model.SeqProfile.get_ordered_allele_ids_representation(
            allele_ids
        )
        profile.format = enum.SeqProfileFormat.ORDERED_ALLELE_IDS
        if profile.content_hash == NULL_ID:
            profile.content_hash = model.SeqProfile.get_allele_profile_hash(allele_ids)
        profile.allele_ids = None
    return new_allele_locus_map


def _reconcile_provided_alleles(
    batch_result: model.SampleBatchUploadResult,
    sample_batch: model.SampleBatchForUpload,
    new_allele_locus_map: dict[UUID, UUID],
) -> bool:
    """Validate provided allele records and assign their expected locus IDs."""
    success = True
    provided_alleles = sample_batch.alleles or []
    # Deduplicate alleles in-place (keep first occurrence per ID). The batch
    # constructor may emit the same content-addressed allele once per sample;
    # the repository requires unique IDs.
    seen_allele_ids: set[UUID] = set()
    duplicate_indexes: list[int] = []
    for index, allele in enumerate(provided_alleles):
        assert allele.id is not None
        if allele.id in seen_allele_ids:
            duplicate_indexes.append(index)
        else:
            seen_allele_ids.add(allele.id)
    for index in sorted(duplicate_indexes, reverse=True):
        del provided_alleles[index]

    missing_allele_ids = set(new_allele_locus_map) - seen_allele_ids
    if missing_allele_ids:
        success = False
        missing_alleles_str = _format_allele_ids(missing_allele_ids)
        batch_result.add_error(
            "7eeced9e", f"Missing new alleles: {missing_alleles_str}"
        )
    extra_allele_ids = seen_allele_ids - set(new_allele_locus_map)
    if extra_allele_ids:
        extra_alleles_str = _format_allele_ids(extra_allele_ids)
        batch_result.add_warning(
            "dda74ae0", f"Superfluous new alleles provided: {extra_alleles_str}"
        )
    _set_provided_allele_loci(
        batch_result, provided_alleles, new_allele_locus_map, extra_allele_ids
    )
    provided_alleles[:] = [
        allele for allele in provided_alleles if allele.id not in extra_allele_ids
    ]
    return success


def _format_allele_ids(allele_ids: set[UUID]) -> str:
    """Format a bounded list of allele IDs for upload diagnostics."""
    sorted_ids = sorted(allele_ids)
    formatted_ids = ", ".join(str(allele_id) for allele_id in sorted_ids[:5])
    if len(sorted_ids) > 5:
        formatted_ids += f", ... (and {len(sorted_ids) - 5} more)"
    return formatted_ids


def _set_provided_allele_loci(
    batch_result: model.SampleBatchUploadResult,
    provided_alleles: list[model.AlleleForUpload],
    new_allele_locus_map: dict[UUID, UUID],
    extra_allele_ids: set[UUID],
) -> None:
    """Set provided alleles' loci and warn when the supplied locus disagrees."""
    for allele in provided_alleles:
        assert allele.id is not None
        if allele.id in extra_allele_ids:
            continue
        expected_locus_id = new_allele_locus_map[allele.id]
        locus_id = allele.locus_id
        if locus_id is None or locus_id == NULL_ID:
            allele.locus_id = expected_locus_id
            continue
        if locus_id != expected_locus_id:
            # The profile determines the locus ID; this is a warning, not a failure.
            allele.locus_id = expected_locus_id
            batch_result.add_warning(
                "e401b1bd",
                f"Different locus ID for new allele {allele.id}: expected {expected_locus_id}, got {locus_id}, used the former",
            )


def _handle_locus_allele_pair_mismatch(
    profile_result: UploadResult, invalid_locus_allele_pairs: list[tuple[UUID, UUID]]
) -> None:
    """Record a bounded diagnostic for locus and allele pairs absent from reference data."""
    if len(invalid_locus_allele_pairs) <= 5:
        invalid_pairs_str = ", ".join(
            [
                f"({locus_id},{allele_id})"
                for locus_id, allele_id in invalid_locus_allele_pairs
            ]
        )
    else:
        invalid_pairs_str = (
            ", ".join(
                [
                    f"({locus_id},{allele_id})"
                    for locus_id, allele_id in invalid_locus_allele_pairs[:5]
                ]
            )
            + f", ... (and {len(invalid_locus_allele_pairs) - 5} more)"
        )
    profile_result.add_error(
        "c9b8a7d6",
        f"Invalid (locus ID, allele ID) pairs: {invalid_pairs_str}",
    )


def _verify_batch_refdata_mlva_profiles(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: Any,
) -> bool:
    """Verify MLVA profile-specific rules."""
    success = True
    user_id = cmd.user.id if cmd.user else None
    profiles, profile_results = _collect_pending_profiles(
        cmd, batch_result, enum.SeqProfileTypeSet.MLVA.value
    )
    if not profiles:
        return success
    protocol_map, locus_set_map, reverse_locus_code_maps = _load_profile_reference_data(
        self, uow, user_id, profiles
    )
    for profile, profile_result in zip(profiles, profile_results):
        if profile_result.status != EtlStatus.PENDING:
            continue
        locus_ids = locus_set_map[
            protocol_map[profile.protocol_id].locus_set_id
        ].locus_ids
        repeat_numbers = _get_repeat_numbers_for_profile(
            profile,
            profile_result,
            locus_ids,
            reverse_locus_code_maps,
        )
        if repeat_numbers is None:
            success = False
            continue
        if len(repeat_numbers) != len(locus_ids):
            success = False
            profile_result.add_error(
                "f4b6a1c8",
                f"Length of repeat_numbers ({len(repeat_numbers)}) does not match number of loci in locus set ({len(locus_ids)})",
            )
            continue

        if profile.content != "":
            continue
        profile.content = model.SeqProfile.get_ordered_repeat_numbers_representation(
            repeat_numbers
        )
        profile.format = enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS
        profile.repeat_numbers = None

    return success


def _collect_pending_profiles(
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    profile_types: Collection[enum.SeqProfileType],
) -> tuple[list[model.SeqProfileForUpload], list[UploadResult]]:
    """Collect pending profiles of the requested types and their results."""
    profiles: list[model.SeqProfileForUpload] = []
    profile_results: list[UploadResult] = []
    for sample, sample_result in zip(cmd.sample_batch.samples, batch_result.samples):
        for profile, profile_result in zip(
            sample.seq_profiles or [], sample_result.seq_profiles or []
        ):
            if (
                profile_result.status == EtlStatus.PENDING
                and profile.seq_profile_type in profile_types
            ):
                profiles.append(profile)
                profile_results.append(profile_result)
    return profiles, profile_results


def _get_repeat_numbers_for_profile(
    profile: model.SeqProfileForUpload,
    profile_result: UploadResult,
    locus_ids: list[UUID],
    reverse_locus_code_maps: dict[UUID, dict[UUID, str]],
) -> list[int | None] | None:
    """Resolve a profile's supported MLVA representation to repeat numbers."""
    if profile.locus_repeat_number_map is not None:
        reverse_locus_code_map = reverse_locus_code_maps[profile.locus_code_map_id]
        repeat_numbers = [
            profile.locus_repeat_number_map.get(reverse_locus_code_map[locus_id])
            for locus_id in locus_ids
        ]
        profile.repeat_numbers = repeat_numbers
        profile.locus_repeat_number_map = None
        return repeat_numbers
    if profile.content:
        if profile.format == enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS:
            return [
                None if repeat_number == MLVA_NO_LOCUS_REPEAT_NUMBER else repeat_number
                for repeat_number in profile.get_repeat_numbers()
            ]
        profile_result.add_error(
            "d5e6f7a8",
            f"MLVA profile format {profile.format} is not supported for upload",
        )
        return None
    if profile.repeat_numbers is not None:
        return profile.repeat_numbers
    profile_result.add_error(
        "e6f7a8b9",
        "MLVA profile must provide one of: content, repeat_numbers, or locus_repeat_number_map",
    )
    return None


def _verify_batch_refdata_snp_profiles(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: Any,
) -> bool:
    """Verify SNP profiles specific rules."""
    # TODO: LSP-3268-Implement-SNP-profile-support-seqdb:
    #   - Load the 'real' ref_seq record.
    #   - Handle aligned_nucleotide_seq form.
    #   - Rebuild the full aligned sequence via nextclade_get_ref_alignment().

    user_id = cmd.user.id if cmd.user else None
    profiles, profile_results = _collect_pending_profiles(
        cmd, batch_result, enum.SeqProfileTypeSet.SNP.value
    )
    if not profiles:
        return True
    protocols = self.service.repository.crud(
        uow,
        user_id,
        model.Protocol,
        CrudOperation.READ_SOME,
        obj_ids=list({profile.protocol_id for profile in profiles}),
    )
    protocol_map = {x.id: x for x in protocols}
    success = _verify_snp_reference_sequences(
        self, uow, user_id, profiles, protocol_map, batch_result
    )
    for profile, profile_result in zip(profiles, profile_results):
        if profile_result.status != EtlStatus.PENDING:
            continue
        success &= _verify_one_snp_profile(profile, profile_result, protocol_map)
    return success


def _verify_snp_reference_sequences(
    self: BatchUploader,
    uow: Any,
    user_id: UUID | None,
    profiles: list[model.SeqProfileForUpload],
    protocol_map: dict[UUID, model.Protocol],
    batch_result: model.SampleBatchUploadResult,
) -> bool:
    """Verify all non-null reference-sequence IDs used by SNP profiles."""
    ref_seq_ids = {
        protocol_map[profile.protocol_id].ref_seq_id
        for profile in profiles
        if protocol_map[profile.protocol_id].ref_seq_id is not None
    }
    if not ref_seq_ids:
        return True
    ref_seq_exists: list[bool] = self.service.repository.crud(
        uow,
        user_id,
        model.RefSeq,
        CrudOperation.EXISTS_SOME,
        obj_ids=list(ref_seq_ids),
    )
    missing_ref_seqs = {
        ref_seq_id
        for ref_seq_id, exists in zip(ref_seq_ids, ref_seq_exists)
        if not exists
    }
    if not missing_ref_seqs:
        return True
    batch_result.add_error(
        "b7c6d5e4",
        f"Reference sequences not found: {sorted(missing_ref_seqs)}",
    )
    return False


def _verify_one_snp_profile(
    profile: model.SeqProfileForUpload,
    profile_result: UploadResult,
    protocol_map: dict[UUID, model.Protocol],
) -> bool:
    """Validate one pending SNP profile against its protocol and content."""
    ref_seq_id = protocol_map[profile.protocol_id].ref_seq_id
    if ref_seq_id is None:
        profile_result.add_error(
            "a6b5c4d3", "Protocol has no ref_seq_id for SNP profile"
        )
        return False
    content = profile.content
    if not content:
        profile_result.add_error("d3e2f1a0", "SNP profile content is empty")
        return False
    if profile.format == enum.SeqProfileFormat.NEXTCLADE:
        # TODO: Add more specific SNP profile validations as needed.
        pass
    return True


def _verify_batch_refdata_kmer_profiles(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    batch_result: model.SampleBatchUploadResult,
    uow: Any,
) -> bool:
    """Verify k-mer profile-specific rules."""
    success = True
    for sample, sample_result in zip(cmd.sample_batch.samples, batch_result.samples):
        for profile, profile_result in zip(
            sample.seq_profiles or [], sample_result.seq_profiles or []
        ):
            if profile_result.status != EtlStatus.PENDING:
                continue
            if profile.seq_profile_type not in enum.SeqProfileTypeSet.KMER.value:
                continue
            success = False
            profile_result.add_error(
                "a9b0c1d2",
                "Verification of k-mer profiles is not yet implemented",
            )
    return success

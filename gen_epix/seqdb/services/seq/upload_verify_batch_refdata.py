from typing import Any
from uuid import UUID

from gen_epix.commondb.domain.enum import EtlStatus
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import UploadResult
from gen_epix.commondb.services import BatchUploader
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.literal import MLVA_NO_LOCUS_REPEAT_NUMBER


def _verify_batch_refdata_allele_profiles(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: Any,
) -> bool:
    """
    Verify and complete reference data for allele profiles.
    """
    success = True
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples

    # Get all allele profiles that are to be processed
    profiles: list[model.SeqProfileForUpload] = []
    profile_results: list[UploadResult] = []
    profile_indices: list[tuple[int, int]] = (
        []
    )  # list of (sample index, profile index) tuples to be able to assign errors to the correct profile results
    for i, (sample, sample_result) in enumerate(zip(samples, sample_results)):
        curr_profiles = sample.seq_profiles or []
        curr_profile_results = sample_result.seq_profiles or []
        for j, (profile, profile_result) in enumerate(
            zip(curr_profiles, curr_profile_results)
        ):
            if profile_result.status != EtlStatus.PENDING:
                continue
            if profile.seq_profile_type not in enum.SeqProfileTypeSet.ALLELE.value:
                continue
            profiles.append(profile)
            profile_results.append(profile_result)
            profile_indices.append((i, j))
    if not profiles:
        # Nothing to do
        return success

    # Retrieve all protocols
    uq_protocol_ids = {x.protocol_id for x in profiles}
    protocols: list[model.Protocol] = self.service.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.Protocol,
        None,
        list(uq_protocol_ids),
        CrudOperation.READ_SOME,
    )
    protocol_map = {x.id: x for x in protocols}

    # Retrieve locus sets
    locus_set_ids = {
        protocol_map[x.protocol_id].locus_set_id
        for x in profiles
        if x.locus_code_map_id is not None and x.locus_code_map_id != NULL_ID
    }
    locus_sets: list[model.LocusSet] = self.service.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.LocusSet,
        None,
        list(locus_set_ids),
        CrudOperation.READ_SOME,
    )
    locus_set_map = {x.id: x for x in locus_sets}

    # Retrieve locus code maps
    locus_code_map_ids = {
        x.locus_code_map_id
        for x in profiles
        if x.locus_code_map_id is not None and x.locus_code_map_id != NULL_ID
    }
    locus_code_maps: list[model.LocusCodeMap] = self.service.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.LocusCodeMap,
        None,
        list(locus_code_map_ids),
        CrudOperation.READ_SOME,
    )
    locus_code_map_map = {x.id: x for x in locus_code_maps}

    # Initialize some data
    uq_allele_ids: set[UUID] = set()
    locus_code_map_locus_codes = {
        x.id: set(x.code_map) for x in locus_code_map_map.values()
    }
    rev_locus_code_map_map = {
        x.id: {y: x for x, y in x.code_map.items()} for x in locus_code_map_map.values()
    }
    allele_ids: list[UUID | None]

    # Convert to allele_profile representation and get unique allele IDs
    for profile, profile_result in zip(profiles, profile_results):
        if profile_result.status != EtlStatus.PENDING:
            continue
        locus_ids = locus_set_map[
            protocol_map[profile.protocol_id].locus_set_id
        ].locus_ids
        n_loci = len(locus_ids)
        locus_allele_id_map = profile.locus_allele_id_map
        if locus_allele_id_map is not None:
            # Convert locus_allele_id_map representation to allele_ids
            locus_code_map_id = profile.locus_code_map_id
            locus_code_map = locus_code_map_map[locus_code_map_id]
            rev_locus_code_map = rev_locus_code_map_map[locus_code_map_id]
            # TODO: 3034 this check is no longer needed since the locus_id is simply the first observed one rather than required to match. Remove once e.g. tests are updated as well.
            # invalid_locus_codes = (
            #     set(locus_allele_id_map.keys())
            #     - locus_code_map_locus_codes[locus_code_map_id]
            # )
            # if invalid_locus_codes:
            #     # Some locus codes are invalid
            #     success = False
            #     if len(invalid_locus_codes) <= 5:
            #         invalid_codes_str = ", ".join(sorted(list(invalid_locus_codes)))
            #     else:
            #         invalid_codes_str = (
            #             ", ".join(sorted(list(invalid_locus_codes)[:5]))
            #             + f", ... (and {len(invalid_locus_codes) - 5} more)"
            #         )
            #     profile_result.add_error(
            #         "e7a4b2d1",
            #         f"Invalid locus codes for locus code map {locus_code_map.code}: {invalid_codes_str}",
            #     )
            #     continue
            allele_ids = [
                locus_allele_id_map.get(rev_locus_code_map[x]) for x in locus_ids
            ]
            profile.allele_ids = allele_ids
            profile.locus_allele_id_map = None
        elif len(profile.content):
            # Convert content representation to allele_ids
            if profile.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
                allele_ids = profile.get_allele_ids()
            else:
                raise NotImplementedError(
                    f"Allele profile format {profile.format} not implemented"
                )
        elif profile.allele_ids is not None:
            allele_ids = profile.allele_ids
        else:
            raise AssertionError(
                "Either locus_allele_id_map, allele_profile or allele_ids must be provided"
            )
        # Verify allele_ids representation
        assert allele_ids is not None
        if len(allele_ids) != n_loci:
            success = False
            profile_result.add_error(
                "d3f5c6b2",
                f"Length of allele_ids ({len(allele_ids)}) does not match number of loci in locus set ({len(locus_ids)})",
            )
            continue
        uq_allele_ids.update(x for x in allele_ids if x is not None and x != NULL_ID)

    # TODO: 3034 no longer needed to retrieve (allele ID, locus ID) pairs since we no longer require the locus ID to match the existing one. Remove once e.g. tests are updated as well.
    # # Retrieve existing (allele ID, locus ID) pairs in chunks
    # uq_allele_ids_list = list(uq_allele_ids)
    # chunk_size = 1000  # TODO: make configurable
    # existing_allele_locus_map: dict[UUID, UUID] = {}
    # for i in range(0, len(uq_allele_ids_list), chunk_size):
    #     curr_allele_ids = uq_allele_ids_list[
    #         i : min(i + chunk_size, len(uq_allele_ids_list))
    #     ]
    #     result_iter = self.service.repository.read_fields(
    #         uow,
    #         user_id,
    #         model.Allele,
    #         ["id", "locus_id"],
    #         filter=UuidSetFilter(
    #             key="id",
    #             members=frozenset(curr_allele_ids),
    #         ),
    #     )
    #     existing_allele_locus_map.update({x[0]: x[1] for x in result_iter})

    # Retrieve existing allele IDs in chunks to avoid hitting parameter limits in the database
    uq_allele_ids_list = list(uq_allele_ids)
    chunk_size = 1000  # TODO: make configurable
    existing_allele_ids: set[UUID] = set()
    # existing_allele_locus_map: dict[UUID, UUID] = {}
    for i in range(0, len(uq_allele_ids_list), chunk_size):
        curr_allele_ids = uq_allele_ids_list[
            i : min(i + chunk_size, len(uq_allele_ids_list))
        ]
        is_existing: list[bool] = self.service.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Allele,
            None,
            curr_allele_ids,
            CrudOperation.EXISTS_SOME,
        )
        existing_allele_ids.update(
            allele_id
            for allele_id, exists in zip(curr_allele_ids, is_existing)
            if exists
        )
    new_allele_ids = uq_allele_ids - existing_allele_ids

    # Convert to content represent as ORDERED_ALLELE_IDS if not already the case
    # Record the first observed locus ID for each new allele ID to be able to set the locus ID for any new alleles
    new_allele_locus_map: dict[UUID, UUID] = {}
    for i, (profile, profile_result) in enumerate(zip(profiles, profile_results)):
        if profile_result.status != EtlStatus.PENDING:
            continue
        locus_ids = locus_set_map[
            protocol_map[profile.protocol_id].locus_set_id
        ].locus_ids
        assert profile.allele_ids is not None
        allele_ids = profile.allele_ids
        # Record the first observed locus ID for each new allele ID
        for allele_id, locus_id in zip(allele_ids, locus_ids):
            if allele_id not in new_allele_ids or allele_id in new_allele_locus_map:
                # Not a new allele or already observed
                continue
            assert allele_id is not None
            new_allele_locus_map[allele_id] = locus_id
        # TODO: 3034 no longer needed to check for mismatches between provided locus ID and existing locus ID since we no longer require the locus ID to match the existing one. Remove once e.g. tests are updated as well.
        # invalid_locus_allele_pairs: list[tuple[UUID, UUID]] = []
        # for locus_id, allele_id in zip(locus_ids, allele_ids):
        #     if allele_id is None or allele_id == NULL_ID:
        #         continue
        #     if allele_id not in existing_allele_locus_map:
        #         new_allele_locus_map[allele_id] = locus_id
        #         continue
        #     existing_locus_id = existing_allele_locus_map[allele_id]
        #     if existing_locus_id != locus_id:
        #         # Allele is associated with a different locus: add to invalid pairs
        #         invalid_locus_allele_pairs.append((locus_id, allele_id))
        # if invalid_locus_allele_pairs:
        #     # Some invalid (locus ID, allele ID) pairs found
        #     success = False
        #     _handle_locus_allele_pair_mismatch(
        #         profile_result, invalid_locus_allele_pairs
        #     )
        # Convert to allele profile representation if not already the case
        if profile.content != "":
            continue
        profile.content = model.SeqProfile.get_ordered_allele_ids_representation(
            allele_ids
        )
        profile.format = enum.SeqProfileFormat.ORDERED_ALLELE_IDS
        profile.allele_ids = None

    # Verify that any new alleles have been provided and set their locus IDs from the alleles in the sample data
    if new_allele_locus_map:
        provided_alleles = cmd.sample_batch.alleles or []
        provided_allele_ids = {x.id for x in provided_alleles}
        # Determine if any missing alleles
        missing_allele_ids = set(new_allele_locus_map.keys()) - provided_allele_ids
        if missing_allele_ids:
            # Some new alleles are missing
            success = False
            missing_allele_ids_list = sorted(missing_allele_ids)
            if len(missing_allele_ids_list) <= 5:
                missing_alleles_str = ", ".join(
                    [str(x) for x in missing_allele_ids_list]
                )
            else:
                missing_alleles_str = (
                    ", ".join([str(x) for x in missing_allele_ids_list[:5]])
                    + f", ... (and {len(missing_allele_ids_list) - 5} more)"
                )
            retval.add_error(
                "a9b8c7d6",
                f"Missing new alleles: {missing_alleles_str}",
            )
        # Determine if any extra alleles
        extra_allele_ids: set[UUID] = provided_allele_ids - set(
            new_allele_locus_map.keys()
        )  # type: ignore[assignment]
        if extra_allele_ids:
            # Some extra (superfluous) alleles provided
            extra_allele_ids_list = sorted(extra_allele_ids)
            if len(extra_allele_ids_list) <= 5:
                extra_alleles_str = ", ".join([str(x) for x in extra_allele_ids_list])
            else:
                extra_alleles_str = (
                    ", ".join([str(x) for x in extra_allele_ids_list[:5]])
                    + f", ... (and {len(extra_allele_ids_list) - 5} more)"
                )
            retval.add_warning(
                "f6e5d4c3",
                f"Superfluous new alleles provided: {extra_alleles_str}",
            )
        # Verify locus IDs of provided alleles
        extra_allele_indexes: list[int] = []
        for i, allele in enumerate(provided_alleles):
            assert allele.id is not None
            if allele.id in extra_allele_ids:
                # Superfluous allele: flag for deletion
                extra_allele_indexes.append(i)
                continue
            # Set allele locus ID if not already set
            expected_locus_id = new_allele_locus_map[allele.id]
            locus_id = allele.locus_id
            if locus_id is None or locus_id == NULL_ID:
                allele.locus_id = expected_locus_id
                continue
            if locus_id != expected_locus_id:
                # Different locus ID, put the one derived from the profile
                success = False
                retval.add_warning(
                    "e4f3g2h1",
                    f"Different locus ID for new allele {allele.id}: expected {expected_locus_id}, got {locus_id}, used the former",
                )
        # Remove any extra alleles
        for index in sorted(extra_allele_indexes, reverse=True):
            del provided_alleles[index]

    return success


def _handle_locus_allele_pair_mismatch(
    profile_result: UploadResult, invalid_locus_allele_pairs: list[tuple[UUID, UUID]]
) -> None:
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
    retval: model.SampleBatchUploadResult,
    uow: Any,
) -> bool:
    """Verify MLVA profiles specific rules"""
    success = True
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples

    profiles: list[model.SeqProfileForUpload] = []
    profile_results: list[UploadResult] = []
    for sample, sample_result in zip(samples, sample_results):
        curr_profiles = sample.seq_profiles or []
        curr_profile_results = sample_result.seq_profiles or []
        for profile, profile_result in zip(curr_profiles, curr_profile_results):
            if profile_result.status != EtlStatus.PENDING:
                continue
            if profile.seq_profile_type not in enum.SeqProfileTypeSet.MLVA.value:
                continue
            profiles.append(profile)
            profile_results.append(profile_result)
    if not profiles:
        return success

    protocol_ids = {profile.protocol_id for profile in profiles}
    protocols: list[model.Protocol] = self.service.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.Protocol,
        None,
        list(protocol_ids),
        CrudOperation.READ_SOME,
    )
    protocol_map = {protocol.id: protocol for protocol in protocols}

    locus_set_ids = {
        protocol_map[profile.protocol_id].locus_set_id
        for profile in profiles
        if profile.locus_code_map_id is not None
        and profile.locus_code_map_id != NULL_ID
    }
    locus_sets: list[model.LocusSet] = self.service.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.LocusSet,
        None,
        list(locus_set_ids),
        CrudOperation.READ_SOME,
    )
    locus_set_map = {locus_set.id: locus_set for locus_set in locus_sets}

    locus_code_map_ids = {
        profile.locus_code_map_id
        for profile in profiles
        if profile.locus_code_map_id is not None
        and profile.locus_code_map_id != NULL_ID
    }
    locus_code_maps: list[model.LocusCodeMap] = self.service.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.LocusCodeMap,
        None,
        list(locus_code_map_ids),
        CrudOperation.READ_SOME,
    )
    rev_locus_code_map_map = {
        locus_code_map.id: {
            locus_id: locus_code
            for locus_code, locus_id in locus_code_map.code_map.items()
        }
        for locus_code_map in locus_code_maps
    }

    repeat_numbers: list[int | None]
    for profile, profile_result in zip(profiles, profile_results):
        if profile_result.status != EtlStatus.PENDING:
            continue
        locus_ids = locus_set_map[
            protocol_map[profile.protocol_id].locus_set_id
        ].locus_ids
        n_loci = len(locus_ids)
        locus_repeat_number_map = profile.locus_repeat_number_map

        if locus_repeat_number_map is not None:
            locus_code_map_id = profile.locus_code_map_id
            rev_locus_code_map = rev_locus_code_map_map[locus_code_map_id]
            repeat_numbers = [
                locus_repeat_number_map.get(rev_locus_code_map[locus_id])
                for locus_id in locus_ids
            ]
            profile.repeat_numbers = repeat_numbers
            profile.locus_repeat_number_map = None
        elif len(profile.content):
            if profile.format == enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS:
                repeat_numbers = [
                    (
                        None
                        if repeat_number == MLVA_NO_LOCUS_REPEAT_NUMBER
                        else repeat_number
                    )
                    for repeat_number in profile.get_repeat_numbers()
                ]
            else:
                raise NotImplementedError(
                    f"MLVA profile format {profile.format} not implemented"
                )
        elif profile.repeat_numbers is not None:
            repeat_numbers = profile.repeat_numbers
        else:
            raise AssertionError(
                "Either locus_repeat_number_map, mlva_profile or repeat_numbers must be provided"
            )

        if len(repeat_numbers) != n_loci:
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


def _verify_batch_refdata_snp_profiles(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: Any,
) -> bool:
    """Verify SNP profiles specific rules"""
    if any(
        profile.seq_profile_type in enum.SeqProfileTypeSet.SNP.value
        for sample in cmd.sample_batch.samples
        for profile in sample.seq_profiles or []
    ):
        raise NotImplementedError("Verification of SNP profiles not implemented yet")

    return True


def _verify_batch_refdata_kmer_profiles(
    self: BatchUploader,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: Any,
) -> bool:
    """Verify k-mer profiles specific rules"""
    if any(
        profile.seq_profile_type in enum.SeqProfileTypeSet.KMER.value
        for sample in cmd.sample_batch.samples
        for profile in sample.seq_profiles or []
    ):
        raise NotImplementedError("Verification of k-mer profiles not implemented yet")

    return True

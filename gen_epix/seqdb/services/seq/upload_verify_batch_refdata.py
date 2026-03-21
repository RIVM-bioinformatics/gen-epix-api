from typing import Any
from uuid import UUID

from gen_epix.commondb.domain.enum import EtlStatus
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import UploadResult
from gen_epix.commondb.services import BatchUploader
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import command, enum, model


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
    allele_profiles: list[model.AlleleProfileForUpload] = []
    allele_profile_results: list[UploadResult] = []
    for i, (sample, sample_result) in enumerate(zip(samples, sample_results)):
        objs = sample.allele_profiles or []
        obj_results = sample_result.allele_profiles or []
        for j, (obj, obj_result) in enumerate(zip(objs, obj_results)):
            if obj_result.status != EtlStatus.PENDING:
                continue
            allele_profiles.append(obj)
            allele_profile_results.append(obj_result)
    if not allele_profiles:
        # Nothing to do
        return success

    # Retrieve locus sets
    locus_set_ids = {
        x.locus_set_id
        for x in allele_profiles
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
        for x in allele_profiles
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
    for profile, profile_result in zip(allele_profiles, allele_profile_results):
        if profile_result.status != EtlStatus.PENDING:
            continue
        locus_ids = locus_set_map[profile.locus_set_id].locus_ids
        n_loci = len(locus_ids)
        locus_allele_id_map = profile.locus_allele_id_map
        if locus_allele_id_map is not None:
            # Convert locus_allele_id_map representation to allele_ids
            locus_code_map_id = profile.locus_code_map_id
            locus_code_map = locus_code_map_map[locus_code_map_id]
            rev_locus_code_map = rev_locus_code_map_map[locus_code_map_id]
            invalid_locus_codes = (
                set(locus_allele_id_map.keys())
                - locus_code_map_locus_codes[locus_code_map_id]
            )
            if invalid_locus_codes:
                # Some locus codes are invalid
                success = False
                if len(invalid_locus_codes) <= 5:
                    invalid_codes_str = ", ".join(sorted(list(invalid_locus_codes)))
                else:
                    invalid_codes_str = (
                        ", ".join(sorted(list(invalid_locus_codes)[:5]))
                        + f", ... (and {len(invalid_locus_codes) - 5} more)"
                    )
                profile_result.add_error(
                    "e7a4b2d1",
                    f"Invalid locus codes for locus code map {locus_code_map.code}: {invalid_codes_str}",
                )
                continue
            allele_ids = [
                locus_allele_id_map.get(rev_locus_code_map[x]) for x in locus_ids
            ]
            profile.allele_ids = allele_ids
            profile.locus_allele_id_map = None
        elif profile.allele_profile is not None:
            # Convert allele_profile representation to allele_ids
            if (
                profile.allele_profile_format
                == enum.AlleleProfileFormat.ORDERED_ALLELE_IDS
            ):
                allele_ids = profile.get_allele_ids()
            else:
                raise NotImplementedError(
                    f"Allele profile format {profile.allele_profile_format} not implemented"
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

    # Retrieve existing (allele ID, locus ID) pairs in chunks
    uq_allele_ids_list = list(uq_allele_ids)
    chunk_size = 1000  # TODO: make configurable
    existing_allele_locus_map: dict[UUID, UUID] = {}
    for i in range(0, len(uq_allele_ids_list), chunk_size):
        result_iter = self.service.repository.read_fields(
            uow,
            user_id,
            model.Allele,
            ["id", "locus_id"],
            filter=UuidSetFilter(
                key="id",
                members=frozenset(
                    uq_allele_ids_list[i : min(i + chunk_size, len(uq_allele_ids_list))]
                ),
            ),
        )
        existing_allele_locus_map.update({x[0]: x[1] for x in result_iter})

    # Verify locus IDs of existing alleles and represent as allele_profile if not already the case
    new_allele_locus_map: dict[UUID, UUID] = {}
    for i, (profile, profile_result) in enumerate(
        zip(allele_profiles, allele_profile_results)
    ):
        if profile_result.status != EtlStatus.PENDING:
            continue
        locus_ids = locus_set_map[profile.locus_set_id].locus_ids
        assert profile.allele_ids is not None
        allele_ids = profile.allele_ids
        n_loci = len(locus_ids)
        invalid_locus_allele_pairs: list[tuple[UUID, UUID]] = []
        for locus_id, allele_id in zip(locus_ids, allele_ids):
            if allele_id is None or allele_id == NULL_ID:
                continue
            if allele_id not in existing_allele_locus_map:
                new_allele_locus_map[allele_id] = locus_id
                continue
            existing_locus_id = existing_allele_locus_map[allele_id]
            if existing_locus_id != locus_id:
                # Allele is associated with a different locus: add to invalid pairs
                invalid_locus_allele_pairs.append((locus_id, allele_id))
        if invalid_locus_allele_pairs:
            # Some invalid (locus ID, allele ID) pairs found
            success = False
            _handle_locus_allele_pair_mismatch(
                profile_result, invalid_locus_allele_pairs
            )
        # Convert to allele profile representation if not already the case
        if profile.allele_profile != "":
            continue
        profile.allele_profile = model.AlleleProfile.get_sorted_allele_ids_profile(
            allele_ids
        )
        profile.allele_profile_format = enum.AlleleProfileFormat.ORDERED_ALLELE_IDS
        profile.allele_ids = None
        # Reset n_loci to 0 so AlleleProfile validator will auto-compute it from the base64 string
        # (n_loci in AlleleProfile means "detected loci count", not total loci in set)
        profile.n_loci = 0

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
                # Incorrect locus ID
                success = False
                retval.add_error(
                    "e4f3g2h1",
                    f"Incorrect locus ID for new allele {allele.id}: expected {expected_locus_id}, got {locus_id}",
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

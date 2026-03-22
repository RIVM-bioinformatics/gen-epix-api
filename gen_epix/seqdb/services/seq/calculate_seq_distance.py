import json
from typing import cast
from uuid import UUID

import numpy as np

from gen_epix.commondb.domain.enum import EtlStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.number_set import NumberSetFilter
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_calculate_seq_distances_for_new_profiles(
    self: BaseSeqService,
    cmd: command.CalculateSeqDistancesForNewProfilesCommand,
) -> list[model.CalculateSeqDistancesResult]:
    """
    Method that takes batches of SeqProfiles and finds which SeqDistance type
    Protocols apply to each SeqProfile. For each applicable protocol it computes
    distances between every new SeqProfile and existing SeqProfiles and between new
    SeqProfiles themselves using type-specific distance rules. It updates any existing
    SeqDistance records to mirror the pairwise distance in the existing SeqDistance
    record, creates SeqDistance records for the new profiles, and returns a list of
    results describing the created distance records.
    """

    # TODO: to be refactored to lower both memory and computational complexity

    user_id = cmd.user.id if cmd.user else None
    seq_profiles = cmd.seq_profiles
    results: list[model.CalculateSeqDistancesResult] = []
    if not seq_profiles:
        # Special case: no profiles provided
        return results

    # Retrieve relevant seq profile protocols
    seq_profile_types = list(set(x.seq_profile_type for x in seq_profiles))
    with self.repository.uow() as uow:
        seq_profile_protocols: list[model.Protocol] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Protocol,
            None,
            None,
            CrudOperation.READ_ALL,
            filter=NumberSetFilter(
                key="seq_profile_type",
                members=frozenset({x.value for x in seq_profile_types}),
            ),
        )
    seq_profile_protocol_map = {
        x.id: x for x in seq_profile_protocols if x.id is not None
    }

    # Retrieve relevant seq distance protocols
    seq_distance_types = list(
        set.union(
            *[
                model.Protocol.SEQ_PROFILE_DISTANCE_TYPE_MAP[x].value
                for x in seq_profile_types
            ]
        )
    )
    with self.repository.uow() as uow:
        seq_distance_protocols: list[model.Protocol] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Protocol,
            None,
            None,
            CrudOperation.READ_ALL,
            filter=NumberSetFilter(
                key="seq_distance_type",
                members=frozenset({x.value for x in seq_distance_types}),
            ),
        )

    # Split profiles by type
    new_seq_profiles_by_type: dict[enum.SeqProfileType, list[model.SeqProfile]] = (
        dict.fromkeys(enum.SeqProfileType, [])
    )
    for profile in seq_profiles:
        new_seq_profiles_by_type[profile.seq_profile_type].append(profile)

    # For each profile type and calculate distances against existing profiles and between new profiles themselves
    for (
        seq_profile_type,
        new_seq_profiles_for_type,
    ) in new_seq_profiles_by_type.items():

        # Split new profiles by relevant subset (e.g. locus set for allele/MLVA profiles, ref seq for SNP profiles) if applicable, and find relevant seq distance protocols for each subset
        new_seq_profiles_by_subset: dict[UUID, list[model.SeqProfile]] = {}
        seq_distance_protocols_by_subset: dict[UUID, list[model.Protocol]] = {}
        if seq_profile_type == enum.SeqProfileType.KMER:
            raise NotImplementedError("K-mer distance calculation not implemented")
        elif seq_profile_type == enum.SeqProfileType.SNP:
            raise NotImplementedError("SNP distance calculation not implemented")
        elif seq_profile_type in enum.SeqProfileTypeSet.LOCUS_SET_BASED.value:
            # Split profiles by locus set, and find all seq distance protocols that apply to each locus set (if any)
            for profile in new_seq_profiles_for_type:
                assert profile.protocol_id is not None
                protocol = seq_profile_protocol_map[profile.protocol_id]
                assert protocol.locus_set_id is not None
                new_seq_profiles_by_subset.setdefault(protocol.locus_set_id, []).append(
                    profile
                )
            # Split seq distance protocols by locus set
            for protocol in seq_distance_protocols:
                locus_set_id = protocol.locus_set_id
                if (
                    locus_set_id is None
                    or locus_set_id not in seq_distance_protocols_by_subset
                ):
                    continue
                seq_distance_protocols_by_subset.setdefault(locus_set_id, []).append(
                    protocol
                )
        else:
            raise NotImplementedError(
                f"Unsupported seq profile type: {seq_profile_type}"
            )

        # For each subset, calculate distances for all seq distance protocols
        for (
            subset_id,
            seq_distance_protocols_for_subset,
        ) in seq_distance_protocols_by_subset.items():
            new_seq_profiles_for_subset = new_seq_profiles_by_subset[subset_id]
            for protocol in seq_distance_protocols_for_subset:
                # Calculate all distances for new_seq_profiles_for_subset for seq_distance_protocol
                max_stored_distance = protocol.max_stored_distance
                assert max_stored_distance is not None

                # Initialize distance maps for new profiles.
                new_profiles_list = [
                    x for x in new_seq_profiles_for_subset if x.id is not None
                ]
                new_profile_distance_maps: dict[UUID, dict[str, float]] = {
                    x.id: {} for x in new_profiles_list  # type: ignore[misc]
                }

                # Retrieve existing SeqDistances (for protocol) and profiles
                with self.repository.uow() as uow:
                    # TODO: instead of reading all SeqDistances in memory first, stream through them and calculate
                    existing_seq_distances: list[model.SeqDistance] = list(
                        self.repository.iter_seq_distances(uow, protocol.id)  # type: ignore[attr-defined]
                    )

                    # Retrieve existing profiles from db based on profile_ids in existing_seq_distances
                    existing_profile_ids: list[UUID] = list(
                        dict.fromkeys(x.seq_profile_id for x in existing_seq_distances)
                    )
                    existing_profiles_list: list[model.SeqProfile] = (
                        self.repository.crud(  # type: ignore[assignment]
                            uow,
                            user_id,
                            model.SeqProfile,
                            None,
                            existing_profile_ids,
                            CrudOperation.READ_SOME,
                        )
                        if existing_profile_ids
                        else []
                    )
                    existing_profile_map = {
                        x.id: x for x in existing_profiles_list if x.id is not None
                    }

                # Calculate distances of every existing profile against every new profile
                # TODO: currently assumes SeqDistanceFormat.PROFILE_DISTANCE_MAP format, should be refactored to support all formats as well
                modified_existing_seq_distances: list[model.SeqDistance] = []
                for existing_seq_distance in existing_seq_distances:
                    existing_profile = existing_profile_map[
                        existing_seq_distance.seq_profile_id
                    ]
                    existing_distance_map = json.loads(existing_seq_distance.content)
                    modified = False
                    for new_profile in new_profiles_list:
                        assert new_profile.id is not None
                        distance = _calculate_profile_distance(
                            seq_profile_type,
                            existing_profile,
                            new_profile,
                        )
                        if distance <= max_stored_distance:
                            # Update existing profile's distance map with new profile
                            existing_distance_map[str(new_profile.id)] = distance
                            # Update new profile's distance map with existing profile
                            new_profile_distance_maps[new_profile.id][
                                str(existing_profile.id)
                            ] = distance
                            modified = True

                    if modified:
                        existing_seq_distance.content = json.dumps(
                            existing_distance_map
                        )
                        modified_existing_seq_distances.append(existing_seq_distance)

                # Calculate distances of new profiles against each other profile (inter-batch pairs)
                for i in range(len(new_profiles_list)):
                    for j in range(i + 1, len(new_profiles_list)):
                        n_i = new_profiles_list[i]
                        n_j = new_profiles_list[j]
                        distance = _calculate_profile_distance(
                            seq_profile_type,
                            n_i,
                            n_j,
                        )
                        if distance <= max_stored_distance:
                            new_profile_distance_maps[n_i.id][str(n_j.id)] = distance  # type: ignore[index]
                            new_profile_distance_maps[n_j.id][str(n_i.id)] = distance  # type: ignore[index]

                # Update modified existing SeqDistances
                if modified_existing_seq_distances:
                    with self.repository.uow() as uow:
                        self.repository.crud(
                            uow,
                            user_id,
                            model.SeqDistance,
                            modified_existing_seq_distances,
                            None,
                            CrudOperation.UPDATE_SOME,
                        )
                    results.extend(
                        [
                            model.CalculateSeqDistancesResult(
                                id=updated_seq_distance.id,
                                status=EtlStatus.UPDATED,
                                seq_distance_profile_id=updated_seq_distance.seq_profile_id,
                            )
                            for updated_seq_distance in modified_existing_seq_distances
                        ]
                    )

                # Create all new SeqDistances objects and store them
                new_seq_distances: list[model.SeqDistance] = [
                    model.SeqDistance(  # type: ignore[call-arg]
                        id=cast(UUID, self.generate_id()),
                        sample_id=cast(UUID, new_profile.sample_id),
                        seq_profile_id=cast(UUID, new_profile.id),
                        protocol_id=cast(UUID, protocol.id),
                        format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
                        content=json.dumps(
                            new_profile_distance_maps[cast(UUID, new_profile.id)]
                        ),
                    )
                    for new_profile in new_profiles_list
                ]
                with self.repository.uow() as uow:
                    created_new_seq_distances: list[model.SeqDistance] = self.repository.crud(  # type: ignore[assignment]
                        uow,
                        user_id,
                        model.SeqDistance,
                        new_seq_distances,
                        None,
                        CrudOperation.CREATE_SOME,
                    )

                # Create results for created SeqDistances
                for created_new_seq_distance in created_new_seq_distances:
                    results.append(
                        model.CalculateSeqDistancesResult(
                            id=created_new_seq_distance.id,
                            status=EtlStatus.CREATED,
                            seq_distance_profile_id=created_new_seq_distance.seq_profile_id,  # type : ignore[arg-type]
                        )
                    )

    return results


def _calculate_profile_distance(
    seq_profile_model_type: enum.SeqProfileType,
    profile1: model.SeqProfile,
    profile2: model.SeqProfile,
    ref_seq: model.RefSeq | None = None,
    locus_set: model.LocusSet | None = None,
) -> float:
    """Return the distance between two profiles of the same type"""
    if seq_profile_model_type == enum.SeqProfileType.SNP:
        # TODO: this implementation is not correct as the aligned sequences may contain different gaps in the reference sequence between both. Instead, the differences versus the reference sequence should be enumerated and compared.
        seq1 = profile1.get_aligned_nucleotide_seq(ref_seq=ref_seq)
        seq2 = profile2.get_aligned_nucleotide_seq(ref_seq=ref_seq)
        return float(np.count_nonzero(np.array(list(seq1)) != np.array(list(seq2))))
    elif seq_profile_model_type == enum.SeqProfileType.ALLELE:
        # Parse allele profiles to get allele IDs, and calculate Hamming distance
        # between allele IDs, ignoring missing loci (i.e. where one or both profiles
        # have None as allele ID)
        ids1: list[UUID | None] = profile1.get_allele_ids(locus_set=locus_set)
        ids2: list[UUID | None] = profile2.get_allele_ids(locus_set=locus_set)
        return float(
            sum(
                1
                for x, y in zip(ids1, ids2)
                if x != y and x is not None and y is not None
            )
        )
    elif seq_profile_model_type == enum.SeqProfileType.MLVA:
        # Parse MLVA profiles to get repeat numbers
        repeat_numbers1 = profile1.get_repeat_numbers(locus_set=locus_set)
        repeat_numbers2 = profile2.get_repeat_numbers(locus_set=locus_set)
        # Hamming distance: count loci where repeat numbers differ
        return float(sum(1 for x, y in zip(repeat_numbers1, repeat_numbers2) if x != y))
    else:
        raise NotImplementedError(
            f"Distance calculation not implemented for {seq_profile_model_type}"
        )


# def calculate_allele_profile_distance(
#     calculate_distance: Callable[[list[Hashable], list[Hashable]], float],
#     allele_profile_format1: enum.SeqProfileFormat,
#     allele_ids1: list[Hashable],
#     allele_profile_format2: enum.SeqProfileFormat,
#     allele_ids2: list[Hashable],
# ) -> float:
#     """
#     Calculate the distance between two allele profiles
#     """
#     if allele_profile_format1 == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
#         if allele_profile_format2 == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
#             distance = calculate_distance(allele_ids1, allele_ids2)
#         else:
#             raise NotImplementedError()
#     else:
#         raise NotImplementedError()
#     return distance

# def calculate_hamming_distance(ids1: list[Hashable], ids2: list[Hashable]) -> float:
#     """
#     Calculate Hamming distance between allele or snp profiles: per locus, add 1
#     to the distance if the alleles are different. In case one of the two loci are
#     missing, the distance is not increased and neither is it if both are missing
#     """
#     return float(
#         sum(
#             1
#             for x, y in zip(ids1, ids2)
#             if x != y and x is not None and y is not None
#         )
#     )

# def calculate_pairwise_allele_profile_distances(
#     protocols: Iterable[model.Protocol],
#     allele_profiles: Iterable[model.SeqProfile],
# ) -> list[model.SeqDistance]:
#     """
#     Calculate all distances for a set of allele profiles between themselves for all
#     the given distance protocols.
#     """
#     seq_distances: list[model.SeqDistance] = []
#     # Go over each distance protocol
#     for protocol in protocols:
#         assert protocol.id is not None
#         locus_set_id = protocol.locus_set_id
#         if locus_set_id is None:
#             raise exc.InvalidArgumentsError("Protocol must have a locus_set_id")
#         max_stored_distance = protocol.max_stored_distance
#         assert max_stored_distance is not None
#         # Get distance calculation function
#         if protocol.seq_distance_type == enum.SeqDistanceType.ALLELE_HAMMING:
#             calculate_distance = SeqService.calculate_hamming_distance
#         else:
#             raise NotImplementedError()
#         # Select only allele profiles for this locus set that are of usable quality
#         curr_allele_profiles: list[model.SeqProfile] = [
#             x
#             for x in allele_profiles
#             if x.locus_set_id == locus_set_id
#             and x.qc_result
#             and x.qc_result.is_usable()
#         ]
#         # Convert allele_profile from json to object
#         allele_profile_allele_ids = [
#             json.loads(x.allele_profile) for x in curr_allele_profiles
#         ]
#         allele_profile_str_seq_ids = [str(x.seq_id) for x in curr_allele_profiles]
#         # Go over each unique pair of allele profiles
#         curr_seq_distances: dict[int, dict[str, float]] = {
#             i: dict() for i in range(len(curr_allele_profiles))
#         }
#         for i, allele_profile1 in enumerate(curr_allele_profiles):
#             # First allele profile
#             allele_profile_format1 = allele_profile1.allele_profile_format
#             allele_ids1 = allele_profile_allele_ids[i]
#             seq_id1 = allele_profile_str_seq_ids[i]
#             for j in range(i + 1, len(curr_allele_profiles)):
#                 # Second allele profile
#                 allele_profile2 = curr_allele_profiles[j]
#                 allele_profile_format2 = allele_profile2.allele_profile_format
#                 allele_ids2 = allele_profile_allele_ids[j]
#                 seq_id2 = allele_profile_str_seq_ids[j]
#                 # Calculate distance depending on format of each allele profile
#                 distance = SeqService.calculate_allele_profile_distance(
#                     calculate_distance,
#                     allele_profile_format1,
#                     allele_ids1,
#                     allele_profile_format2,
#                     allele_ids2,
#                 )
#                 # Keep only distances up to the maximum
#                 if distance > max_stored_distance:
#                     continue
#                 # Add to seq_distances
#                 curr_seq_distances[i][seq_id2] = distance
#                 curr_seq_distances[j][seq_id1] = distance

#         # Create SeqDistance objects from distances
#         for i, allele_profile in enumerate(curr_allele_profiles):
#             # Calculate SeqDistance.id as 128 bit hash of sample_id, so that it is always the same
#             seq_distance_id = UUID(
#                 bytes=hashlib.sha256(allele_profile.sample_id.bytes).digest()[:16]
#             )
#             # Create seq_distance and add to dict_db
#             seq_distance = model.SeqDistance(
#                 id=seq_distance_id,
#                 sample_id=cast(UUID, allele_profile.sample_id),
#                 protocol_id=cast(UUID, protocol.id),
#                 allele_profile_id=cast(UUID, allele_profile.id),
#                 format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
#                 content=json.dumps(curr_seq_distances[i]),
#             )
#             seq_distances.append(seq_distance)

#     return seq_distances

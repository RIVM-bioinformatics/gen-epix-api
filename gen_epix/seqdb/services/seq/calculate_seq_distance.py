import json
from collections.abc import Iterable
from datetime import datetime
from typing import Any, cast
from uuid import UUID

import numpy as np

from gen_epix.commondb.domain.enum import EtlStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.exc import ConcurrentModificationError
from gen_epix.filter.string_set import StringSetFilter
from gen_epix.seqdb.domain import command, enum, exc, model
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_retrieve_seq_distance_last_modified(
    self: BaseSeqService,
    cmd: command.RetrieveSeqDistanceLastModifiedCommand,
) -> datetime | None:

    with self.repository.uow() as uow:
        seq_distance_protocol: model.Protocol = self.repository.crud(  # type: ignore[assignment]
            uow,
            cmd.user.id if cmd.user else None,
            model.Protocol,
            CrudOperation.READ_ONE,
            obj_ids=cmd.protocol_id,
        )
        if seq_distance_protocol.protocol_type != enum.ProtocolType.SEQ_DISTANCE:
            raise exc.InvalidArgumentsError(
                "ad28ab0f", f"Protocol {cmd.protocol_id} is not a SeqDistance protocol"
            )
        return self.repository.get_max_seq_distance_modified_at(  # type: ignore[attr-defined]
            uow, cmd.protocol_id
        )


def seq_service_calculate_seq_distances_for_new_profiles(
    self: BaseSeqService,
    cmd: command.CalculateSeqDistancesForNewProfilesCommand,
) -> list[model.CalculateSeqDistancesResult]:
    """
    For each new SeqProfile find applicable SeqDistance protocols, compute distances
    between every new profile and all existing profiles (plus between new profiles
    themselves), update existing SeqDistance records to mirror the pairwise distance,
    create SeqDistance records for the new profiles, and return results.records for the
    new profiles, and return results.

    Uses a streaming approach: existing SeqDistances are NOT fully materialized. Profile
    IDs are collected first via a lightweight query, profiles are fetched, then
    distances are streamed one-by-one.
    """
    user_id = cmd.user.id if cmd.user else None
    seq_profiles = cmd.seq_profiles
    results: list[model.CalculateSeqDistancesResult] = []
    if not seq_profiles:
        return results

    # Retrieve relevant seq profile protocols
    seq_profile_types = list(set(x.seq_profile_type for x in seq_profiles))
    with self.repository.uow() as uow:
        seq_profile_protocols: list[model.Protocol] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Protocol,
            CrudOperation.READ_ALL,
            # TODO: this should be an enum set filter
            filter=StringSetFilter(
                key="seq_profile_type",
                members=frozenset({x.name for x in seq_profile_types}),
                case_sensitive=True,
            ),
        )
    seq_profile_protocol_map = {
        x.id: x for x in seq_profile_protocols if x.id is not None
    }

    # Retrieve relevant seq distance protocols
    seq_distance_types = list(
        set(
            [
                next(iter(model.Protocol.SEQ_PROFILE_DISTANCE_TYPE_MAP[x].value))
                for x in seq_profile_types
            ]
        )
    )
    with self.repository.uow() as uow:
        seq_distance_protocols: list[model.Protocol] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Protocol,
            CrudOperation.READ_ALL,
            # TODO: this should be an enum set filter
            filter=StringSetFilter(
                key="seq_distance_type",
                members=frozenset({x.name for x in seq_distance_types}),
                case_sensitive=True,
            ),
        )

    # Split profiles by type
    new_seq_profiles_by_type: dict[enum.SeqProfileType, list[model.SeqProfile]] = {
        seq_profile_type: [] for seq_profile_type in enum.SeqProfileType
    }
    for profile in seq_profiles:
        new_seq_profiles_by_type[profile.seq_profile_type].append(profile)

    # For each profile type calculate distances
    for (
        seq_profile_type,
        new_seq_profiles_for_type,
    ) in new_seq_profiles_by_type.items():
        if not new_seq_profiles_for_type:
            continue

        # Split by relevant subset
        new_seq_profiles_by_subset: dict[UUID, list[model.SeqProfile]] = {}
        seq_distance_protocols_by_subset: dict[UUID, list[model.Protocol]] = {}
        if seq_profile_type == enum.SeqProfileType.KMER:
            raise NotImplementedError("K-mer distance calculation not implemented")
        elif seq_profile_type == enum.SeqProfileType.SNP:
            raise NotImplementedError("SNP distance calculation not implemented")
        elif seq_profile_type in enum.SeqProfileTypeSet.LOCUS_SET_BASED.value:
            for profile in new_seq_profiles_for_type:
                assert profile.protocol_id is not None
                protocol = seq_profile_protocol_map[profile.protocol_id]
                assert protocol.locus_set_id is not None
                new_seq_profiles_by_subset.setdefault(protocol.locus_set_id, []).append(
                    profile
                )
            for protocol in seq_distance_protocols:
                locus_set_id = protocol.locus_set_id
                if (
                    locus_set_id is None
                    or locus_set_id not in new_seq_profiles_by_subset
                ):
                    continue
                seq_distance_protocols_by_subset.setdefault(locus_set_id, []).append(
                    protocol
                )
        else:
            raise NotImplementedError(
                f"Unsupported seq profile type: {seq_profile_type}"
            )

        # For each subset, calculate distances
        for (
            subset_id,
            protocols_for_subset,
        ) in seq_distance_protocols_by_subset.items():
            new_profiles = new_seq_profiles_by_subset[subset_id]
            for protocol in protocols_for_subset:
                _calculate_and_store_distances(
                    self,
                    user_id,
                    protocol,
                    seq_profile_type,
                    new_profiles,
                    results,
                    cmd.seq_distance_last_modified_at,
                    existing_chunk_size=cmd.existing_chunk_size,
                )

    return results


def seq_service_update_seq_distances(
    self: BaseSeqService,
    cmd: command.UpdateSeqDistancesCommand,
) -> list[model.CalculateSeqDistancesResult]:
    """
    For a given distance protocol, find all profiles that don't yet have a SeqDistance
    record, compute the missing distances and create the records while maintaining the
    symmetry invariant.
    """
    user_id = cmd.user.id if cmd.user else None
    results: list[model.CalculateSeqDistancesResult] = []

    # Get the distance protocol
    with self.repository.uow() as uow:
        protocol: model.Protocol = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Protocol,
            CrudOperation.READ_ONE,
            obj_ids=cmd.protocol_id,
        )
    assert protocol.max_stored_distance is not None
    assert protocol.seq_distance_type is not None

    # Determine which profile type this distance protocol applies to.
    profile_type = _profile_type_for_distance_protocol(
        protocol,
    )
    if profile_type is None:
        raise ValueError(
            f"No profile type maps to distance type" f" {protocol.seq_distance_type}"
        )

    # Get profile IDs that already have SeqDistances
    with self.repository.uow() as uow:
        existing_distance_profile_ids: set[UUID] = set(
            self.repository.iter_seq_distance_profile_ids(  # type: ignore[attr-defined]
                uow, protocol.id
            )
        )

    # Get profiling protocols that match the distance protocol's subset criteria.
    with self.repository.uow() as uow:
        profiling_protocols: list[model.Protocol] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Protocol,
            CrudOperation.READ_ALL,
            # TODO: this should be an enum set filter
            filter=StringSetFilter(
                key="seq_profile_type",
                members=frozenset({profile_type.name}),
                case_sensitive=True,
            ),
        )

    # Filter to protocols with matching subset
    matching_protocol_ids = _matching_profiling_protocol_ids(
        profile_type,
        profiling_protocols,
        protocol,
    )
    if not matching_protocol_ids:
        return results

    # Get all profiles for matching profiling protocols
    with self.repository.uow() as uow:
        all_profiles: list[model.SeqProfile] = (
            self.repository.get_profiles_by_protocol_ids(  # type: ignore[attr-defined]
                uow,
                matching_protocol_ids,
            )
        )

    # Determine profiles that are missing distances
    missing_profiles: list[model.SeqProfile] = [
        x
        for x in all_profiles
        if x.id is not None and x.id not in existing_distance_profile_ids
    ]
    if not missing_profiles:
        return results
    if cmd.max_new_profiles is not None:
        missing_profiles = missing_profiles[: cmd.max_new_profiles]

    _calculate_and_store_distances(
        self,
        user_id,
        protocol,
        profile_type,
        missing_profiles,
        results,
        known_existing_profile_ids=list(existing_distance_profile_ids),
        existing_chunk_size=cmd.existing_chunk_size,
    )

    return results


def _chunk_profile_ids(
    ids: list[UUID], chunk_size: int | None
) -> list[list[UUID]]:
    """Split *ids* into sub-lists of at most *chunk_size*.

    Returns ``[ids]`` when *chunk_size* is ``None`` (no
    chunking). Returns ``[]`` when *ids* is empty so
    callers can skip the loop entirely.
    """
    if not ids:
        return []
    if chunk_size is None:
        return [ids]
    return [ids[i : i + chunk_size] for i in range(0, len(ids), chunk_size)]


def _decode_profile(
    seq_profile_type: enum.SeqProfileType,
    profile: model.SeqProfile,
) -> Any:
    """Return pre-decoded profile data for distance computation.

    ALLELE → list[bytes | None] (16-byte chunks, one per locus)
    MLVA   → list[int] (repeat numbers)
    SNP    → str (aligned nucleotide sequence)
    """
    if seq_profile_type == enum.SeqProfileType.ALLELE:
        return profile.get_allele_id_bytes()
    if seq_profile_type == enum.SeqProfileType.MLVA:
        return profile.get_repeat_numbers()
    if seq_profile_type == enum.SeqProfileType.SNP:
        return profile.get_aligned_nucleotide_seq()
    raise NotImplementedError(
        f"Distance calculation not implemented for {seq_profile_type}"
    )


def _distance_from_decoded(
    seq_profile_type: enum.SeqProfileType,
    data1: Any,
    data2: Any,
) -> float:
    """Compute distance from pre-decoded profile data.

    Accepts the values produced by ``_decode_profile``; avoids
    repeated b64decode / json.loads inside tight comparison loops.
    """
    if seq_profile_type == enum.SeqProfileType.ALLELE:
        return float(
            sum(
                1
                for x, y in zip(data1, data2)
                if x != y and x is not None and y is not None
            )
        )
    if seq_profile_type == enum.SeqProfileType.MLVA:
        return float(sum(1 for x, y in zip(data1, data2) if x != y))
    if seq_profile_type == enum.SeqProfileType.SNP:
        return float(
            np.count_nonzero(np.array(list(data1)) != np.array(list(data2)))
        )
    raise NotImplementedError(
        f"Distance calculation not implemented for {seq_profile_type}"
    )


def _calculate_and_store_distances(
    service: BaseSeqService,
    user_id: UUID | None,
    protocol: model.Protocol,
    seq_profile_type: enum.SeqProfileType,
    new_seq_profiles: list[model.SeqProfile],
    results: list[model.CalculateSeqDistancesResult],
    seq_distance_last_modified_at: datetime | None = None,
    known_existing_profile_ids: list[UUID] | None = None,
    existing_chunk_size: int | None = None,
) -> None:
    """
    Calculate distances between new_seq_profiles and all
    existing profiles for protocol, then persist updates
    and new records.

    Existing profiles are processed in chunks of
    ``existing_chunk_size`` (all at once when ``None``).
    Within each chunk, SeqProfiles and their SeqDistance
    records are loaded, distances computed, and modified
    records persisted before moving to the next chunk.
    New SeqDistance records are created once after all
    chunks complete, so their maps accumulate contributions
    from every existing profile.
    """
    max_stored_distance = protocol.max_stored_distance
    assert max_stored_distance is not None

    new_profiles_list = [x for x in new_seq_profiles if x.id is not None]
    new_profile_distance_maps: dict[UUID, dict[str, float]] = {
        x.id: {} for x in new_profiles_list  # type: ignore[misc]
    }
    # Pre-decode new profiles once; reused across all chunks and the
    # intra-batch pass to avoid repeated b64decode / json.loads per
    # comparison.
    new_profiles_decoded: list[Any] = [
        _decode_profile(seq_profile_type, p) for p in new_profiles_list
    ]

    # Collect profile IDs + concurrency check
    with service.repository.uow() as uow:
        if seq_distance_last_modified_at is not None:
            max_modified = service.repository.get_max_seq_distance_modified_at(  # type: ignore[attr-defined]
                uow, protocol.id
            )
            if (
                max_modified is not None
                and max_modified > seq_distance_last_modified_at
            ):
                raise ConcurrentModificationError(
                    "SeqDistance records were modified after the provided seq_distance_last_modified_at timestamp. "
                    "Aborting to prevent conflicts."
                )

        if known_existing_profile_ids is not None:
            existing_profile_ids = known_existing_profile_ids
        else:
            existing_profile_ids: list[UUID] = list(  # type: ignore[no-redef]
                dict.fromkeys(
                    service.repository.iter_seq_distance_profile_ids(  # type: ignore[attr-defined]
                        uow, protocol.id
                    )
                )
            )

    # Process existing profiles in chunks to cap peak memory use.
    # SQL Server caps parameterized queries at 2100 parameters; chunks of
    # ≤2000 keep READ_SOME safe without optimize_parameter_handling.
    # TODO: make read_some auto-select optimize_parameter_handling when
    #   len(obj_ids) > 2000 so callers don't need to know about this limit.
    for chunk_ids in _chunk_profile_ids(existing_profile_ids, existing_chunk_size):
        with service.repository.uow() as uow:
            existing_profiles_list: list[model.SeqProfile] = (
                service.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id,
                    model.SeqProfile,
                    CrudOperation.READ_SOME,
                    obj_ids=chunk_ids,
                    optimize_parameter_handling=len(chunk_ids) > 2000,
                )
            )
        existing_profile_map = {
            x.id: x for x in existing_profiles_list if x.id is not None
        }

        modified_existing: list[model.SeqDistance] = []
        with service.repository.uow() as uow:
            for existing_seq_distance in service.repository.iter_seq_distances(  # type: ignore[attr-defined]
                uow, protocol.id, profile_ids=chunk_ids
            ):
                assert isinstance(existing_seq_distance, model.SeqDistance)
                profile = existing_profile_map.get(
                    existing_seq_distance.seq_profile_id
                )
                if profile is None:
                    continue
                existing_decoded = _decode_profile(seq_profile_type, profile)
                updates: dict[str, float] = {}
                for new_profile, new_decoded in zip(
                    new_profiles_list, new_profiles_decoded
                ):
                    assert new_profile.id is not None
                    distance = _distance_from_decoded(
                        seq_profile_type,
                        existing_decoded,
                        new_decoded,
                    )
                    if distance <= max_stored_distance:
                        updates[str(new_profile.id)] = distance
                        new_profile_distance_maps[new_profile.id][
                            str(profile.id)
                        ] = distance
                if updates:
                    distance_map = json.loads(existing_seq_distance.content)
                    distance_map.update(updates)
                    existing_seq_distance.content = json.dumps(distance_map)
                    modified_existing.append(existing_seq_distance)

        if modified_existing:
            with service.repository.uow() as uow:
                service.repository.crud(
                    uow,
                    user_id,
                    model.SeqDistance,
                    CrudOperation.UPDATE_SOME,
                    objs=modified_existing,
                )
            results.extend(
                model.CalculateSeqDistancesResult(
                    id=sd.id,
                    status=EtlStatus.UPDATED,
                    seq_distance_profile_id=(sd.seq_profile_id),
                )
                for sd in modified_existing
            )

    # Intra-batch distances (new - new)
    _compute_intra_batch_distances(
        seq_profile_type,
        new_profiles_list,
        new_profile_distance_maps,
        max_stored_distance,
    )

    # Create new SeqDistance records once, after all chunks complete.
    # Each new profile's map has accumulated distances from every existing
    # profile processed above.
    new_seq_distances: list[model.SeqDistance] = [
        model.SeqDistance(  # type: ignore[call-arg]
            id=cast(UUID, service.generate_id()),
            sample_id=x.sample_id,
            seq_profile_id=cast(UUID, x.id),
            protocol_id=cast(UUID, protocol.id),
            format=(enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP),
            content=json.dumps(new_profile_distance_maps[cast(UUID, x.id)]),
        )
        for x in new_profiles_list
    ]
    with service.repository.uow() as uow:
        created_new: list[model.SeqDistance] = service.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.SeqDistance,
            CrudOperation.CREATE_SOME,
            objs=new_seq_distances,
        )

    for created_seq_distance in created_new:
        results.append(
            model.CalculateSeqDistancesResult(
                id=created_seq_distance.id,
                status=EtlStatus.CREATED,
                seq_distance_profile_id=(created_seq_distance.seq_profile_id),
            )
        )


def _compute_intra_batch_distances(
    seq_profile_type: enum.SeqProfileType,
    profiles: list[model.SeqProfile],
    distance_maps: dict[UUID, dict[str, float]],
    max_stored_distance: float,
) -> None:
    """
    Compute pairwise distances between profiles within
    a single batch and populate *distance_maps*.
    """
    decoded = [_decode_profile(seq_profile_type, p) for p in profiles]
    for i in range(len(profiles)):
        for j in range(i + 1, len(profiles)):
            p_i = profiles[i]
            p_j = profiles[j]
            distance = _distance_from_decoded(
                seq_profile_type,
                decoded[i],
                decoded[j],
            )
            if distance <= max_stored_distance:
                distance_maps[p_i.id][str(p_j.id)] = distance  # type: ignore[index]
                distance_maps[p_j.id][str(p_i.id)] = distance  # type: ignore[index]


def _profile_type_for_distance_protocol(
    protocol: model.Protocol,
) -> enum.SeqProfileType | None:
    """
    Given a distance protocol, return the SeqProfileType it applies to, or None.
    """
    for (
        profile_type,
        distance_type_set,
    ) in model.Protocol.SEQ_PROFILE_DISTANCE_TYPE_MAP.items():
        if protocol.seq_distance_type in distance_type_set.value:
            return profile_type
    return None


def _matching_profiling_protocol_ids(
    profile_type: enum.SeqProfileType,
    profiling_protocols: list[model.Protocol],
    distance_protocol: model.Protocol,
) -> list[UUID]:
    """
    Return IDs of profiling protocols whose subset
    (locus_set or ref_seq) matches distance_protocol.
    """
    if profile_type in enum.SeqProfileTypeSet.LOCUS_SET_BASED.value:
        return [
            x.id
            for x in profiling_protocols
            if x.locus_set_id == distance_protocol.locus_set_id and x.id is not None
        ]
    if profile_type in enum.SeqProfileTypeSet.REF_SEQ_BASED.value:
        return [
            x.id
            for x in profiling_protocols
            if x.ref_seq_id == distance_protocol.ref_seq_id and x.id is not None
        ]
    return []


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
        # Parse allele profiles as raw bytes and
        # calculate Hamming distance, ignoring missing
        # loci (where one or both are None).
        ids1 = profile1.get_allele_id_bytes()
        ids2 = profile2.get_allele_id_bytes()
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

import json
from datetime import datetime
from functools import lru_cache
from typing import Any, cast
from uuid import UUID

import numpy as np
from pydantic import BaseModel, ConfigDict

from gen_epix.commondb.domain.enum import EtlStatus
from gen_epix.fastapp import BaseUnitOfWork
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.exc import ConcurrentModificationError
from gen_epix.filter import StringSetFilter
from gen_epix.seqdb.domain import command, enum, exc, model
from gen_epix.seqdb.domain.literal import (
    NEXTCLADE_NON_ACGTN_PATTERN,
    NEXTCLADE_POSITION_RANGE_PATTERN,
    NEXTCLADE_SUBSTITUTION_PATTERN,
)
from gen_epix.seqdb.domain.service import BaseSeqService


class _ParsedNextcladeProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    substitutions: dict[int, str]
    deletions: set[int]
    insertions: dict[int, str]
    missing: set[int]
    non_acgtns: dict[int, str]
    variant_states: dict[int, tuple[str, str | None]]
    alignment_start: int
    alignment_end: int


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
    create SeqDistance records for the new profiles, and return results.
    """
    user_id = cmd.user.id if cmd.user else None
    seq_profiles = cmd.seq_profiles
    results: list[model.CalculateSeqDistancesResult] = []
    if not seq_profiles:
        return results

    # Execute in a single transaction
    seq_profile_types = list(set(x.seq_profile_type for x in seq_profiles))
    with self.repository.uow() as uow:
        # Retrieve relevant seq profile protocols
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

        # Calculate distances for each profile type
        for (
            seq_profile_type,
            new_seq_profiles_for_type,
        ) in new_seq_profiles_by_type.items():
            if not new_seq_profiles_for_type:
                continue

            # Split by relevant subset (ref_seq or locus_set) so that distances are
            # only computed between profiles that share the same reference.
            new_seq_profiles_by_subset: dict[UUID, list[model.SeqProfile]] = {}
            seq_distance_protocols_by_subset: dict[UUID, list[model.Protocol]] = {}
            if seq_profile_type == enum.SeqProfileType.KMER:
                raise NotImplementedError("K-mer distance calculation not implemented")
            elif seq_profile_type in enum.SeqProfileTypeSet.REF_SEQ_BASED.value:
                for profile in new_seq_profiles_for_type:
                    assert profile.protocol_id is not None
                    protocol = seq_profile_protocol_map[profile.protocol_id]
                    assert protocol.ref_seq_id is not None
                    new_seq_profiles_by_subset.setdefault(
                        protocol.ref_seq_id, []
                    ).append(profile)
                for protocol in seq_distance_protocols:
                    ref_seq_id = protocol.ref_seq_id
                    if (
                        ref_seq_id is None
                        or ref_seq_id not in new_seq_profiles_by_subset
                    ):
                        continue
                    seq_distance_protocols_by_subset.setdefault(ref_seq_id, []).append(
                        protocol
                    )
            elif seq_profile_type in enum.SeqProfileTypeSet.LOCUS_SET_BASED.value:
                for profile in new_seq_profiles_for_type:
                    assert profile.protocol_id is not None
                    protocol = seq_profile_protocol_map[profile.protocol_id]
                    assert protocol.locus_set_id is not None
                    new_seq_profiles_by_subset.setdefault(
                        protocol.locus_set_id, []
                    ).append(profile)
                for protocol in seq_distance_protocols:
                    locus_set_id = protocol.locus_set_id
                    if (
                        locus_set_id is None
                        or locus_set_id not in new_seq_profiles_by_subset
                    ):
                        continue
                    seq_distance_protocols_by_subset.setdefault(
                        locus_set_id, []
                    ).append(protocol)
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
                        uow,
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
        seq_distance_protocol: model.Protocol = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Protocol,
            CrudOperation.READ_ONE,
            obj_ids=cmd.protocol_id,
        )
        assert seq_distance_protocol.max_stored_distance is not None
        assert seq_distance_protocol.seq_distance_type is not None

        # Get profile IDs that already have SeqDistances
        existing_distance_profile_ids: set[UUID] = set(
            self.repository.iter_seq_distance_profile_ids(  # type: ignore[attr-defined]
                uow, seq_distance_protocol.id
            )
        )

        # Get SeqProfile protocols that match the distance protocol's subset criteria.
        seq_profile_type = (
            seq_distance_protocol.get_seq_profile_type_for_distance_protocol()
        )
        seq_profile_protocols: list[model.Protocol] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Protocol,
            CrudOperation.READ_ALL,
            # TODO: this should be an enum set filter
            filter=StringSetFilter(
                key="seq_profile_type",
                members=frozenset({seq_profile_type.name}),
                case_sensitive=True,
            ),
        )

        # Filter to protocols with matching subset
        matching_protocol_ids = _get_matching_seq_profile_protocol_ids(
            seq_profile_type,
            seq_distance_protocol,
            seq_profile_protocols,
        )
        if not matching_protocol_ids:
            return results

        # Get all profiles for the corresponding protocols
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
        # max_new_profiles caps the work per call so lsp-data can loop
        # incrementally rather than timing out on a single giant request.
        if cmd.max_new_profiles is not None:
            missing_profiles = missing_profiles[: cmd.max_new_profiles]

        _calculate_and_store_distances(
            self,
            uow,
            user_id,
            seq_distance_protocol,
            seq_profile_type,
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

    Decodes profile content once so the inner comparison loop can call
    ``_distance_from_decoded`` without repeating expensive parsing on
    every pair.

    Return types by profile type:
      ALLELE  → list[bytes | None]  (16-byte UUID chunks, one per locus)
      MLVA    → list[int]           (repeat numbers)
      SNP     → _ParsedNextcladeProfile (only NEXTCLADE format supported)
    """
    if seq_profile_type == enum.SeqProfileType.ALLELE:
        return profile.get_allele_id_bytes()
    if seq_profile_type == enum.SeqProfileType.MLVA:
        return profile.get_repeat_numbers()
    if seq_profile_type == enum.SeqProfileType.SNP:
        # _parse_nextclade_profile_content is lru_cache-decorated, so the
        # cost of parsing is paid at most once per unique content string.
        return _parse_nextclade_profile(profile)
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

    Performance note: with N existing profiles and M new profiles per
    chunk, using _decode_profile + _distance_from_decoded reduces
    decode calls from N×M to N+M.
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
        return _nextclade_hamming_from_parsed(data1, data2)
    raise NotImplementedError(
        f"Distance calculation not implemented for {seq_profile_type}"
    )


def _calculate_and_store_distances(
    service: BaseSeqService,
    uow: BaseUnitOfWork,
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
    Calculate pairwise distances between new_seq_profiles and all existing
    profiles for protocol, then persist updates and new SeqDistance records.

    ALGORITHM OVERVIEW
    ------------------
    1. Optional concurrency guard: abort if SeqDistance records were modified
       after seq_distance_last_modified_at (prevents lost-update races).

    2. Collect existing_profile_ids — either the caller-supplied
       known_existing_profile_ids (set by UpdateSeqDistancesCommand, which
       already knows who has a record) or a lightweight query via
       iter_seq_distance_profile_ids.

    3. Pre-decode all new profiles once into new_profiles_decoded. This pays
       the b64decode / json.loads cost M times (one per new profile) instead
       of N×M times (once per existing×new pair) — a major saving when N is
       large.

    4. Process existing profiles in chunks of existing_chunk_size:
       a. READ_SOME: fetch up to chunk_size SeqProfile objects.
       b. iter_seq_distances: fetch only the SeqDistance records for this
          chunk (temp-table JOIN on mssql avoids the ODBC 07002 error from
          IN() on uniqueidentifier FK columns).
       c. For each existing SeqDistance:
          - decode the existing profile once (existing_decoded).
          - compare against every new profile using _distance_from_decoded
            (pre-decoded), collecting updates.
          - if any distance ≤ max_stored_distance: json.loads the content
            blob ONLY NOW (deferred parse avoids cost for non-matching
            records, which are the vast majority when max_stored_distance
            is tight), update the map, mark as modified.
       d. UPDATE_SOME: flush modified records for this chunk before moving
          to the next — caps peak memory and write-batch size.

    5. Intra-batch: compute pairwise distances among new_profiles themselves.

    6. CREATE_SOME: write all new SeqDistance records once at the end.
       Deferred until all chunks complete so each new profile's map
       accumulates contributions from every existing profile.

    MEMORY BOUNDS (with existing_chunk_size = C)
    ----------------------------------------------
    SeqProfile objects    : ≤ C at a time (freed after each chunk)
    SeqDistance objects   : ≤ C at a time (freed after each chunk)
    new_profiles_decoded  : M entries, held for the duration of the call
    new_profile_distance_maps : M dicts, grown incrementally across chunks

    uow is the caller's unit of work, used for initial reads (concurrency
    check, profile ID collection) and for the final CREATE_SOME write.
    Per-chunk READ_SOME / iter_seq_distances / UPDATE_SOME each open their
    own unit of work so they can be committed independently.
    """
    max_stored_distance = protocol.max_stored_distance
    assert max_stored_distance is not None

    # Filter out any profiles that somehow arrived without a persisted ID.
    # In practice all profiles should have IDs at this point, but the type
    # allows None and skipping them is safer than an assertion crash.
    new_profiles = [x for x in new_seq_profiles if x.id is not None]

    # Accumulator for each new profile's distance map. Keyed by new profile
    # ID; values grow incrementally as the chunk loop processes existing
    # profiles. The final maps are written to SeqDistance.content in step 6.
    new_profile_distance_maps: dict[UUID, dict[str, float]] = {
        x.id: {} for x in new_profiles  # type: ignore[misc]
    }

    # Step 3 — Pre-decode new profiles once.
    # Each comparison would otherwise call get_allele_id_bytes() /
    # get_repeat_numbers() / _parse_nextclade_profile() on the new profile,
    # paying the decode cost N times (once per existing profile). Decoding
    # upfront reduces that to M (once per new profile), so total decode
    # calls drop from N×M to N+M across the whole chunk loop.
    new_profiles_decoded: list[Any] = [
        _decode_profile(seq_profile_type, p) for p in new_profiles
    ]

    # Step 1 — Concurrency guard (uses caller's uow — read-only).
    # Only active when the caller passes seq_distance_last_modified_at, which
    # is the timestamp the caller read before starting this operation. If
    # another process has written a newer SeqDistance record in the meantime
    # we abort rather than risk a lost-update: our distance maps would be
    # based on a stale view of who is already close to whom.
    if seq_distance_last_modified_at is not None:
        max_modified = service.repository.get_max_seq_distance_modified_at(  # type: ignore[attr-defined]
            uow, protocol.id
        )
        if max_modified is not None and max_modified > seq_distance_last_modified_at:
            raise ConcurrentModificationError(
                "9f3b2d7a",
                message="SeqDistance records were modified after the provided "
                "seq_distance_last_modified_at timestamp.",
            )

    # Step 2 — Collect existing profile IDs (uses caller's uow — read-only).
    # UpdateSeqDistancesCommand supplies known_existing_profile_ids directly
    # (it already has the set of profiles-with-records from the caller), so
    # we avoid a redundant query in that path. Otherwise we query the DB.
    # dict.fromkeys preserves iteration order while deduplicating — the DB
    # can return duplicate profile IDs if the index is non-unique.
    existing_profile_ids: list[UUID]
    if known_existing_profile_ids is not None:
        existing_profile_ids = known_existing_profile_ids
    else:
        existing_profile_ids = list(
            dict.fromkeys(
                service.repository.iter_seq_distance_profile_ids(  # type: ignore[attr-defined]
                    uow, protocol.id
                )
            )
        )

    # Steps 4a-4d — Process existing profiles in chunks.
    # Without chunking the original algorithm loaded all N SeqProfile objects
    # and all N SeqDistance records simultaneously, causing OOM crashes for
    # large datasets. Chunking bounds peak memory to chunk_size profiles and
    # their distance records at a time.
    # Each chunk opens its own unit of work so it can be committed
    # independently — see the TODO below for the atomicity trade-off.
    # SQL Server caps parameterised IN() at 2100 tokens; chunks of ≤2000
    # keep READ_SOME within that limit without optimize_parameter_handling.
    for chunk_ids in _chunk_profile_ids(existing_profile_ids, existing_chunk_size):

        # Step 4a — Fetch SeqProfile objects for this chunk only.
        # TODO: chunk_uow is a separate unit of work from the caller's uow,
        #   which means each chunk runs in its own transaction. This is
        #   intentional — it keeps READ_SOME, iter_seq_distances, and
        #   UPDATE_SOME bounded per chunk — but it means the chunked writes
        #   are not atomic with the final CREATE_SOME. Unclear if there is a
        #   better alternative without materialising all chunks first.
        with service.repository.uow() as chunk_uow:
            existing_profiles_list: list[model.SeqProfile] = (
                service.repository.crud(  # type: ignore[assignment]
                    chunk_uow,
                    user_id,
                    model.SeqProfile,
                    CrudOperation.READ_SOME,
                    obj_ids=chunk_ids,
                    optimize_parameter_handling=len(chunk_ids) > 2000,
                )
            )

        # Build an O(1) lookup map for use in the SeqDistance loop below.
        # Profiles with no ID are excluded (same defensive filter as above).
        existing_profile_map = {
            x.id: x for x in existing_profiles_list if x.id is not None
        }

        # Step 4b-4c — Stream SeqDistance records for this chunk and compute.
        # iter_seq_distances filters to profile_ids=chunk_ids, which on mssql
        # uses a temp-table JOIN instead of IN() — avoiding the SQL Server
        # ODBC 07002 error that IN() on uniqueidentifier FK columns triggers
        # regardless of list size. This is the fix that replaced the earlier
        # workaround of passing profile_ids=None and filtering in Python,
        # which caused a full-table scan on every chunk (O(N×chunks) reads).
        modified_existing: list[model.SeqDistance] = []
        with service.repository.uow() as chunk_uow:
            for existing_seq_distance in service.repository.iter_seq_distances(  # type: ignore[attr-defined]
                chunk_uow, protocol.id, profile_ids=chunk_ids
            ):
                assert isinstance(existing_seq_distance, model.SeqDistance)
                profile = existing_profile_map.get(
                    existing_seq_distance.seq_profile_id
                )
                # Should not happen with a correct chunk filter, but the DB
                # could return a record whose profile was deleted between the
                # READ_SOME and this query — skip it rather than crash.
                if profile is None:
                    continue

                # Decode the existing profile's content once per SeqDistance
                # record, not once per new-profile comparison. Together with
                # new_profiles_decoded (decoded before the loop) this reduces
                # total decode calls from N×M to N+M per call.
                existing_decoded = _decode_profile(seq_profile_type, profile)

                # Compare this existing profile against every new profile.
                # Collect matching pairs in `updates` before touching
                # existing_seq_distance.content — this lets us skip
                # json.loads entirely for the common case where no new
                # profile is close enough to record (see below).
                updates: dict[str, float] = {}
                for new_profile, new_decoded in zip(new_profiles, new_profiles_decoded):
                    assert new_profile.id is not None
                    distance = _distance_from_decoded(
                        seq_profile_type,
                        existing_decoded,
                        new_decoded,
                    )
                    if distance <= max_stored_distance:
                        updates[str(new_profile.id)] = distance
                        # Symmetry invariant: if A's map records distance to
                        # B, then B's map must also record it. Write the
                        # reverse entry into new_profile_distance_maps now;
                        # it will be serialised into the new SeqDistance
                        # record at step 6 after all chunks complete.
                        new_profile_distance_maps[new_profile.id][
                            str(profile.id)
                        ] = distance

                # Deferred json.loads — only parse the content blob when at
                # least one new profile is close enough to warrant an update.
                # With a tight max_stored_distance (e.g. 20 on cgMLST with
                # thousands of loci) the vast majority of existing records
                # produce no updates, so this skips almost all JSON parsing.
                if updates:
                    distance_map = json.loads(existing_seq_distance.content)
                    distance_map.update(updates)
                    existing_seq_distance.content = json.dumps(distance_map)
                    modified_existing.append(existing_seq_distance)

        # Step 4d — Flush modified records for this chunk before moving on.
        # Committing per chunk bounds the UPDATE_SOME write-batch size and
        # releases the modified SeqDistance objects from memory, keeping
        # peak RSS proportional to chunk_size rather than to N.
        if modified_existing:
            with service.repository.uow() as chunk_uow:
                service.repository.crud(
                    chunk_uow,
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

    # Step 5: intra-batch distances (new-new pairs).
    _calculate_pairwise_profile_distances(
        seq_profile_type,
        new_profiles,
        new_profile_distance_maps,
        max_stored_distance,
    )

    # Step 6: create new SeqDistance records once, after all chunks complete.
    # Each new profile's distance map has now accumulated contributions from
    # every existing profile processed in the chunk loop above.
    new_seq_distances: list[model.SeqDistance] = [
        model.SeqDistance(  # type: ignore[call-arg]
            id=cast(UUID, service.generate_id()),
            sample_id=x.sample_id,  # type: ignore[arg-type]
            seq_profile_id=cast(UUID, x.id),
            protocol_id=cast(UUID, protocol.id),  # type: ignore[arg-type]
            format=(enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP),  # type: ignore[arg-type]
            content=json.dumps(new_profile_distance_maps[cast(UUID, x.id)]),  # type: ignore[arg-type]
        )
        for x in new_profiles
    ]
    created_seq_distances: list[model.SeqDistance] = service.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.SeqDistance,
        CrudOperation.CREATE_SOME,
        objs=new_seq_distances,
    )

    for created_seq_distance in created_seq_distances:
        results.append(
            model.CalculateSeqDistancesResult(
                id=created_seq_distance.id,
                status=EtlStatus.CREATED,
                seq_distance_profile_id=(created_seq_distance.seq_profile_id),
            )
        )


def _calculate_pairwise_profile_distances(
    seq_profile_type: enum.SeqProfileType,
    profiles: list[model.SeqProfile],
    distance_maps: dict[UUID, dict[str, float]],
    max_stored_distance: float,
) -> None:
    """
    Compute pairwise distances between profiles within a single batch and
    populate *distance_maps* (upper-triangle only; both directions stored).

    Profiles are decoded once into a ``decoded`` list, then the O(N²/2)
    loop calls ``_distance_from_decoded`` on pre-decoded data — avoiding
    repeated b64decode / json.loads across the N² comparisons.
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


def _get_matching_seq_profile_protocol_ids(
    profile_type: enum.SeqProfileType,
    seq_distance_protocol: model.Protocol,
    seq_profile_protocols: list[model.Protocol],
) -> list[UUID]:
    """
    Return IDs of SeqProfile protocols whose subset (locus_set or ref_seq)
    matches the SeqDistance protocol.
    """
    if profile_type in enum.SeqProfileTypeSet.LOCUS_SET_BASED.value:
        return [
            x.id
            for x in seq_profile_protocols
            if x.locus_set_id == seq_distance_protocol.locus_set_id and x.id is not None
        ]
    if profile_type in enum.SeqProfileTypeSet.REF_SEQ_BASED.value:
        return [
            x.id
            for x in seq_profile_protocols
            if x.ref_seq_id == seq_distance_protocol.ref_seq_id and x.id is not None
        ]
    return []


def _split_nextclade_field(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_nextclade_position_token(token: str) -> set[int]:
    match = NEXTCLADE_POSITION_RANGE_PATTERN.fullmatch(token)
    if match is None:
        raise ValueError(f"Invalid Nextclade position token: {token}")
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        raise ValueError(f"Invalid Nextclade position range: {token}")
    return set(range(start, end + 1))


def _parse_nextclade_substitutions(value: str) -> dict[int, str]:
    substitutions: dict[int, str] = {}
    for token in _split_nextclade_field(value):
        match = NEXTCLADE_SUBSTITUTION_PATTERN.fullmatch(token)
        if match is None:
            raise ValueError(f"Invalid Nextclade substitution token: {token}")
        substitutions[int(match.group(1))] = match.group(2).lower()
    return substitutions


def _parse_nextclade_ranges(value: str) -> set[int]:
    positions: set[int] = set()
    for token in _split_nextclade_field(value):
        positions.update(_parse_nextclade_position_token(token))
    return positions


def _parse_nextclade_non_acgtns(value: str) -> dict[int, str]:
    non_acgtns: dict[int, str] = {}
    for token in _split_nextclade_field(value):
        match = NEXTCLADE_NON_ACGTN_PATTERN.fullmatch(token)
        if match is None:
            raise ValueError(f"Invalid Nextclade non_acgtns token: {token}")
        base = match.group(1).lower()
        for position in _parse_nextclade_position_token(match.group(2)):
            non_acgtns[position] = base
    return non_acgtns


@lru_cache(maxsize=4096)
def _parse_nextclade_profile_content(content: str) -> _ParsedNextcladeProfile:
    nextclade_fields = json.loads(content)
    if not isinstance(nextclade_fields, dict):
        raise ValueError("Nextclade SNP profile content must be a JSON object")

    if "substitutions" not in nextclade_fields:
        raise ValueError("Nextclade SNP profile content must contain 'substitutions'")
    substitutions = _parse_nextclade_substitutions(
        str(nextclade_fields["substitutions"])
    )
    deletions = _parse_nextclade_ranges(str(nextclade_fields.get("deletions", "")))
    missing = _parse_nextclade_ranges(str(nextclade_fields.get("missings", "")))
    non_acgtns = _parse_nextclade_non_acgtns(
        str(nextclade_fields.get("non_acgtns", ""))
    )

    alignment_start = int(nextclade_fields.get("alignment_start", 0))
    _all_positions = set(substitutions) | deletions | missing | set(non_acgtns)
    _default_end = max(_all_positions) if _all_positions else 0
    alignment_end = int(nextclade_fields.get("alignment_end", _default_end))
    if alignment_end < alignment_start:
        raise ValueError(
            "Invalid Nextclade alignment range: " f"{alignment_start}-{alignment_end}"
        )

    variant_states: dict[int, tuple[str, str | None]] = {
        position: ("base", base) for position, base in substitutions.items()
    }
    variant_states.update({position: ("deletion", None) for position in deletions})
    variant_states.update(
        {position: ("non_acgtn", base) for position, base in non_acgtns.items()}
    )
    variant_states.update({position: ("missings", None) for position in missing})

    return _ParsedNextcladeProfile(
        substitutions=substitutions,
        deletions=deletions,
        # Insertions do not affect SNP Hamming over reference positions.
        insertions={},
        missing=missing,
        non_acgtns=non_acgtns,
        variant_states=variant_states,
        alignment_start=alignment_start,
        alignment_end=alignment_end,
    )


def _parse_nextclade_profile(profile: model.SeqProfile) -> _ParsedNextcladeProfile:
    if profile.format != enum.SeqProfileFormat.NEXTCLADE:
        raise NotImplementedError(
            "SNP distance calculation currently supports only Nextclade profiles"
        )
    return _parse_nextclade_profile_content(profile.content)


def _nextclade_position_state(
    profile: _ParsedNextcladeProfile,
    position: int,
) -> tuple[str, str | None]:
    if position < profile.alignment_start or position > profile.alignment_end:
        return ("outside", None)
    return profile.variant_states.get(position, ("reference", None))


def _nextclade_hamming_from_parsed(
    parsed_profile1: _ParsedNextcladeProfile,
    parsed_profile2: _ParsedNextcladeProfile,
) -> float:
    """
    Compute the Nextclade SNP Hamming distance from two already-parsed profiles.

    Separated from ``_calculate_nextclade_snp_hamming_distance`` so the
    pre-decode path (``_distance_from_decoded``) can call it without
    re-parsing profiles that were already decoded by ``_decode_profile``.
    """
    overlap_start = max(
        parsed_profile1.alignment_start,
        parsed_profile2.alignment_start,
    )
    overlap_end = min(
        parsed_profile1.alignment_end,
        parsed_profile2.alignment_end,
    )
    overlap_length = max(0, overlap_end - overlap_start + 1)
    profile1_length = (
        parsed_profile1.alignment_end - parsed_profile1.alignment_start + 1
    )
    profile2_length = (
        parsed_profile2.alignment_end - parsed_profile2.alignment_start + 1
    )

    mismatches = profile1_length + profile2_length - (2 * overlap_length)
    if overlap_length == 0:
        return float(mismatches)

    default_state = ("reference", None)
    get_state1 = parsed_profile1.variant_states.get
    get_state2 = parsed_profile2.variant_states.get
    relevant_positions = {
        position
        for position in parsed_profile1.variant_states
        if overlap_start <= position <= overlap_end
    }
    relevant_positions.update(
        position
        for position in parsed_profile2.variant_states
        if overlap_start <= position <= overlap_end
    )

    for position in relevant_positions:
        if get_state1(position, default_state) != get_state2(position, default_state):
            mismatches += 1

    return float(mismatches)


def _calculate_nextclade_snp_hamming_distance(
    profile1: model.SeqProfile,
    profile2: model.SeqProfile,
) -> float:
    parsed_profile1 = _parse_nextclade_profile(profile1)
    parsed_profile2 = _parse_nextclade_profile(profile2)
    return _nextclade_hamming_from_parsed(parsed_profile1, parsed_profile2)


def _calculate_profile_distance(
    seq_profile_model_type: enum.SeqProfileType,
    profile1: model.SeqProfile,
    profile2: model.SeqProfile,
    ref_seq: model.RefSeq | None = None,
    locus_set: model.LocusSet | None = None,
) -> float:
    """Return the distance between two profiles of the same type"""
    # TODO: LSP-3268 This function forces both profile representations (i.e. ready for distance calculation) to be calculated each time for each pair. More efficient would be to calculate all representations just once and then loop over the pairs.
    if seq_profile_model_type == enum.SeqProfileType.SNP:
        if (
            profile1.format == enum.SeqProfileFormat.NEXTCLADE
            and profile2.format == enum.SeqProfileFormat.NEXTCLADE
        ):
            return _calculate_nextclade_snp_hamming_distance(profile1, profile2)
        assert ref_seq is not None
        ref_seq_str = ref_seq.get_nucleotide_seq()
        seq1 = profile1.get_aligned_nucleotide_seq(ref_seq_str=ref_seq_str)
        seq2 = profile2.get_aligned_nucleotide_seq(ref_seq_str=ref_seq_str)
        seq_bytes1 = np.frombuffer(seq1.encode("ascii"), dtype=np.uint8)
        seq_bytes2 = np.frombuffer(seq2.encode("ascii"), dtype=np.uint8)
        # TODO: LSP-3268 Avoid magic strings by putting this in an enum. Also, N must be lowercase (already adjusted here)
        _N = ord("n")
        _DASH = ord("-")
        skip = (
            (seq_bytes1 == _N)
            | (seq_bytes1 == _DASH)
            | (seq_bytes2 == _N)
            | (seq_bytes2 == _DASH)
        )
        return float(np.count_nonzero((seq_bytes1 != seq_bytes2) & ~skip))
    elif seq_profile_model_type == enum.SeqProfileType.ALLELE:
        # Parse allele profiles as raw bytes and
        # calculate Hamming distance, ignoring missing
        # loci (where one or both are None).
        id_bytes1 = profile1.get_allele_id_bytes()
        id_bytes2 = profile2.get_allele_id_bytes()
        return float(
            sum(
                1
                for x, y in zip(id_bytes1, id_bytes2)
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

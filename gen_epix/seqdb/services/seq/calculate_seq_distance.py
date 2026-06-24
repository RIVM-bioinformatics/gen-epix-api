import json
import time
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
from gen_epix.seqdb.domain.repository.seq import BaseSeqRepository
from gen_epix.seqdb.domain.service import BaseSeqService
from gen_epix.util import chunk_list


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


# Numpy has no uint128 type; allele UUIDs are stored as S16 (16-byte byte
# strings). All-zero bytes = NULL_ID (missing locus). S16 byte-wise equality
# gives correct UUID identity — see SeqProfile.get_allele_array() for details.
_NULL_ALLELE = b"\x00" * 16

# Lightweight accumulator for the row-per-pair path: (profile_id_a, profile_id_b,
# distance). SeqDistancePair objects are materialised in bulk at step 6, keeping
# Pydantic validation and uuid4() calls out of the inner comparison loop.
_RawPair = tuple[UUID, UUID, float]


def _hamming_allele_numpy(arr1: np.ndarray, arr2: np.ndarray) -> float:
    """
    Hamming distance between two (n_loci,) S16 allele arrays.

    S16 is a no-uint128 workaround (see SeqProfile.get_allele_array). Elements
    equal to _NULL_ALLELE are missing loci; pairs where either side is missing
    are excluded, matching the Python fallback.
    """
    null1 = arr1 == _NULL_ALLELE
    null2 = arr2 == _NULL_ALLELE
    return float(np.sum((arr1 != arr2) & ~null1 & ~null2))


def _hamming_allele_numpy_batch(
    existing_arr: np.ndarray,
    new_matrix: np.ndarray,
    null_new: np.ndarray,
) -> np.ndarray:
    """
    Hamming distances from one existing S16 profile to all M new profiles.

    existing_arr: (n_loci,) S16 — one existing profile.
    new_matrix:   (M, n_loci) S16 — all M new profiles stacked.
    null_new:     (M, n_loci) bool — precomputed missing-locus mask for new.
    Returns:      (M,) float array of distances.

    Broadcasting replaces M Python-loop calls to _hamming_allele_numpy.
    null_new is precomputed before the chunk loop so it is not recomputed
    for every existing profile.
    """
    null_existing = existing_arr == _NULL_ALLELE
    diff = new_matrix != existing_arr[None, :]
    missing = null_new | null_existing[None, :]
    return np.sum(diff & ~missing, axis=1).astype(float)


def _encode_to_int32(
    new_s16: np.ndarray,
    chunk_s16: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build a shared vocabulary from new + chunk S16 matrices and encode both to int32.

    new_s16:   (M, n_loci) S16 — pre-stacked new profiles.
    chunk_s16: (C, n_loci) S16 — all existing profiles in this chunk, stacked.
    Returns:   (new_int32, chunk_int32), shapes (M, n_loci) and (C, n_loci) int32.

    np.unique collects the sorted set of distinct S16 allele tokens across both
    matrices; np.searchsorted maps every cell to its position in that sorted list
    (a vectorised dict lookup). This reduces each cell from 16 bytes (S16) to 4 bytes
    (int32), cutting matrix memory by 4x and replacing 16-byte byte-string comparisons
    with 4-byte integer comparisons in the Hamming step.

    The vocabulary is rebuilt per chunk so codes are consistent within one
    _hamming_allele_int32_batch call but not comparable across chunks.
    """
    combined = np.concatenate([new_s16, chunk_s16])
    unique_vals = np.unique(combined)
    new_int32 = np.searchsorted(unique_vals, new_s16).astype(np.int32)
    chunk_int32 = np.searchsorted(unique_vals, chunk_s16).astype(np.int32)
    return new_int32, chunk_int32


def _hamming_allele_int32_batch(
    existing_row: np.ndarray,
    new_matrix: np.ndarray,
    null_existing: np.ndarray,
    null_new: np.ndarray,
) -> np.ndarray:
    """
    Hamming distances from one existing int32 profile to all M new int32 profiles.

    existing_row:  (n_loci,) int32 — one row from chunk_int32 produced by _encode_to_int32.
    new_matrix:    (M, n_loci) int32 — new profiles encoded with the same per-chunk vocab.
    null_existing: (n_loci,) bool — True where existing allele is NULL_ID.
    null_new:      (M, n_loci) bool — True where new allele is NULL_ID; precomputed
                   from the S16 new_matrix before encoding, stable across chunks.
    Returns:       (M,) int32 — mismatch count per new profile.

    Null masks are derived from the S16 stage (before encoding) because the null
    allele maps to whichever integer the per-chunk vocab assigns it, not to a fixed
    sentinel, so the int32 codes alone cannot identify null loci.
    """
    diff = new_matrix != existing_row[None, :]
    missing = null_new | null_existing[None, :]
    return np.sum(diff & ~missing, axis=1, dtype=np.int32)


def seq_service_retrieve_seq_distance_last_modified(
    self: BaseSeqService,
    cmd: command.RetrieveSeqDistanceLastModifiedCommand,
) -> datetime | None:

    with self.repository.uow() as uow:
        seq_distance_protocol: model.Protocol = self.repository.crud(
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
        seq_profile_protocols: list[model.Protocol] = self.repository.crud(
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
        seq_distance_protocols: list[model.Protocol] = self.repository.crud(
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
                        use_row_per_pair=cmd.use_row_per_pair,
                        use_numpy_allele=cmd.use_numpy_allele,
                        use_batch_new_profiles=cmd.use_batch_new_profiles,
                        use_bulk_insert=cmd.use_bulk_insert,
                        use_int32_vocab=cmd.use_int32_vocab,
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
    repository: BaseSeqRepository = self.repository  # type: ignore[assignment]
    log = self.logger
    user_id = cmd.user.id if cmd.user else None
    results: list[model.CalculateSeqDistancesResult] = []

    t0 = time.perf_counter()
    if log:
        log.debug(
            "UpdateSeqDistances start: protocol_id=%s chunk_size=%s limit=%s",
            cmd.protocol_id,
            cmd.existing_chunk_size,
            cmd.limit,
        )

    # Get the distance protocol
    with repository.uow() as uow:
        seq_distance_protocol: model.Protocol = repository.crud(
            uow,
            user_id,
            model.Protocol,
            CrudOperation.READ_ONE,
            obj_ids=cmd.protocol_id,
        )
        assert seq_distance_protocol.max_stored_distance is not None
        assert seq_distance_protocol.seq_distance_type is not None

        # Get SeqProfile protocols that match the distance protocol's subset criteria.
        seq_profile_type = (
            seq_distance_protocol.get_seq_profile_type_for_distance_protocol()
        )
        seq_profile_protocols: list[model.Protocol] = repository.crud(
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

        # Single SQL query: profiles with no SeqDistance record for this
        # protocol (NOT EXISTS), capped at limit via SQL LIMIT /
        # TOP.  This replaces the previous approach of loading all profiles
        # and all distance-profile-ids into Python and computing the set
        # difference there, which timed out as both sets grew large.
        missing_profiles: list[model.SeqProfile] = (
            repository.get_profiles_without_seq_distance(
                uow,
                distance_protocol_id=cast(UUID, seq_distance_protocol.id),
                seq_profile_protocol_ids=matching_protocol_ids,
                limit=cmd.limit,
            )
        )
        if log:
            log.debug(
                "UpdateSeqDistances: %d profiles missing distances (after limit cap) (%.3fs)",
                len(missing_profiles),
                time.perf_counter() - t0,
            )
        if not missing_profiles:
            return results

        _calculate_and_store_distances(
            self,
            uow,
            user_id,
            seq_distance_protocol,
            seq_profile_type,
            missing_profiles,
            results,
            existing_chunk_size=cmd.existing_chunk_size,
            use_row_per_pair=cmd.use_row_per_pair,
            use_numpy_allele=cmd.use_numpy_allele,
            use_batch_new_profiles=cmd.use_batch_new_profiles,
            use_int32_vocab=cmd.use_int32_vocab,
        )

    return results


def _decode_profile(
    seq_profile_type: enum.SeqProfileType,
    profile: model.SeqProfile,
    use_numpy_allele: bool = False,
) -> Any:
    """Return pre-decoded profile data for distance computation.

    Decodes profile content once so the inner comparison loop can call
    ``_distance_from_decoded`` without repeating expensive parsing on
    every pair.

    Return types by profile type:
      ALLELE  → np.ndarray (S16, shape (n_loci,)) if use_numpy_allele,
                else list[bytes | None] (16-byte UUID chunks, one per locus)
      MLVA    → list[int]           (repeat numbers)
      SNP     → _ParsedNextcladeProfile (only NEXTCLADE format supported)
    """
    if seq_profile_type == enum.SeqProfileType.ALLELE:
        if use_numpy_allele:
            return profile.get_allele_array()
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


def _calculate_distance_for_decoded_profile_pair(
    seq_profile_type: enum.SeqProfileType,
    data1: Any,
    data2: Any,
) -> float:
    """Compute distance from pre-decoded profile data.

    Accepts the values produced by ``_decode_profile``; avoids
    repeated b64decode / json.loads inside tight comparison loops.

    Performance note: with N existing profiles and M new profiles per
    chunk, using _decode_profile + _calculate_distance_for_decoded_profile_pair reduces
    decode calls from N×M to N+M.
    """
    if seq_profile_type == enum.SeqProfileType.ALLELE:
        if isinstance(data1, np.ndarray):
            return _hamming_allele_numpy(data1, data2)
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
    use_row_per_pair: bool = False,
    use_numpy_allele: bool = False,
    use_batch_new_profiles: bool = False,
    use_bulk_insert: bool = False,
    use_int32_vocab: bool = False,
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
       d. Accumulate modified records in all_modified_existing (no write
          yet — all writes are deferred to step 6).

    5. Intra-batch: compute pairwise distances among new_profiles themselves.

    6. Single-transaction write using the caller's uow:
       - UPDATE_SOME: all modified existing SeqDistance records at once.
       - CREATE_SOME: all new SeqDistance records at once.
       Both share the same transaction, ensuring atomicity.

    MEMORY BOUNDS (with existing_chunk_size = C)
    ----------------------------------------------
    SeqProfile objects    : ≤ C at a time (freed after each chunk)
    SeqDistance objects   : up to all modified (held until step 6 write)
    new_profiles_decoded  : M entries, held for the duration of the call
    new_profile_distance_maps : M dicts, grown incrementally across chunks

    uow is the caller's unit of work, used for initial reads (concurrency
    check, profile ID collection) and for the step 6 writes.
    Per-chunk READ_SOME / iter_seq_distances open their own read-only unit
    of work so reads stay bounded without holding a transaction open across
    the full chunk loop.
    """
    logger = service.logger
    repository: BaseSeqRepository = service.repository  # type: ignore[assignment]
    t_fn = time.perf_counter()
    max_stored_distance = protocol.max_stored_distance
    assert max_stored_distance is not None

    if use_batch_new_profiles and not use_numpy_allele:
        raise ValueError("use_batch_new_profiles requires use_numpy_allele=True")
    if use_int32_vocab and not use_numpy_allele:
        raise ValueError("use_int32_vocab requires use_numpy_allele=True")
    if use_int32_vocab and use_batch_new_profiles:
        raise ValueError("use_int32_vocab and use_batch_new_profiles are mutually exclusive")

    # Check if any profiles do not have an ID.
    if not all(x.id is not None for x in new_seq_profiles):
        if logger:
            logger.error("_calculate_and_store_distances: some new profiles have no ID")
        raise exc.InvalidArgumentsError(
            "fbb3c9e7", "All new profiles must have an ID before distance calculation"
        )

    # Accumulator for each new profile's distance map. Keyed by new profile
    # ID; values grow incrementally as the chunk loop processes existing
    # profiles. The final maps are written to SeqDistance.content in step 6.
    new_profile_distance_maps: dict[UUID, dict[str, float]] = {
        x.id: {} for x in new_seq_profiles  # type: ignore[misc]
    }

    # Step 1 — Concurrency guard (uses caller's uow — read-only).
    # Only active when the caller passes seq_distance_last_modified_at and we
    # are writing to SeqDistance blobs. In row-per-pair mode we do not touch
    # blobs, so a concurrent blob modification does not affect our write.
    # TODO: row-per-pair mode still requires serialized runs. Two concurrent
    # calls each process their own new-profile set but never compare the two
    # sets against each other, leaving cross-set pairs uncalculated. A
    # separate concurrency guard is needed (e.g. an advisory lock or a
    # seq_distance_pair row count / last-inserted-at check) before this path
    # can be used safely in production.
    if seq_distance_last_modified_at is not None and not use_row_per_pair:
        max_modified = repository.get_max_seq_distance_modified_at(
            uow, cast(UUID, protocol.id)
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
                repository.iter_seq_distance_profile_ids(uow, cast(UUID, protocol.id))
            )
        )

    chunks = chunk_list(existing_profile_ids, existing_chunk_size)
    n_chunks = len(chunks)
    if logger:
        logger.debug(
            "_calculate_and_store_distances: n_new=%d n_existing=%d n_chunks=%d chunk_size=%s (%.3fs)",
            len(new_seq_profiles),
            len(existing_profile_ids),
            n_chunks,
            existing_chunk_size,
            time.perf_counter() - t_fn,
        )

    # Step 3 — Pre-decode new profiles once.
    # Each comparison would otherwise call get_allele_id_bytes() /
    # get_repeat_numbers() / _parse_nextclade_profile() on the new profile,
    # paying the decode cost N times (once per existing profile). Decoding
    # upfront reduces that to M (once per new profile), so total decode
    # calls drop from N×M to N+M across the whole chunk loop.
    decoded_new_profiles: list[Any] = [
        _decode_profile(seq_profile_type, p, use_numpy_allele=use_numpy_allele)
        for p in new_seq_profiles
    ]

    # Pre-stack for batch mode (ALLELE + numpy only).
    # new_matrix: (M, n_loci) S16; null_new: (M, n_loci) bool mask.
    # Precomputed here so the chunk loop does not reallocate per existing
    # profile. Both stay None when batch mode is off or for non-ALLELE types.
    # use_int32_vocab also needs new_matrix (S16) to build the per-chunk vocab.
    new_matrix: np.ndarray | None = None
    null_new: np.ndarray | None = None
    if (
        (use_batch_new_profiles or use_int32_vocab)
        and seq_profile_type == enum.SeqProfileType.ALLELE
        and decoded_new_profiles
        and isinstance(decoded_new_profiles[0], np.ndarray)
    ):
        new_matrix = np.stack(decoded_new_profiles)
        # null_new is derived from the S16 bytes, not from int32 codes, because
        # the per-chunk vocab assigns the null allele an arbitrary integer.
        # Precomputing here keeps it stable and avoids recomputing per chunk.
        null_new = new_matrix == _NULL_ALLELE

    # all_modified_existing accumulates updated SeqDistance records across
    # all chunks (blob path only). all_new_pairs accumulates raw (_RawPair)
    # tuples across all chunks (row-per-pair path only); SeqDistancePair
    # objects are materialised from them in step 6. Both are written
    # atomically in step 6 using the caller's uow.
    all_modified_existing: list[model.SeqDistance] = []
    all_new_pairs: list[_RawPair] = []

    # Steps 4a-4d — Process existing profiles in chunks.
    # Chunking bounds peak memory for reads: each chunk loads at most
    # chunk_size SeqProfile objects. Modified SeqDistance objects accumulate
    # in all_modified_existing (blob path) or SeqDistancePair objects in
    # all_new_pairs (row-per-pair path). Both are written in step 6.
    # optimize_parameter_handling=True uses a temp-table JOIN on mssql
    # instead of IN() — required because IN() on UNIQUEIDENTIFIER FK
    # columns via pyodbc raises ODBC 07002 regardless of list size.
    for chunk_no, chunk_ids in enumerate(chunks, start=1):

        t_chunk = time.perf_counter()

        # Step 4a — Fetch SeqProfile objects for this chunk only.
        with repository.uow() as chunk_uow:
            existing_profiles_list: list[model.SeqProfile] = repository.crud(
                chunk_uow,
                user_id,
                model.SeqProfile,
                CrudOperation.READ_SOME,
                obj_ids=chunk_ids,
                optimize_parameter_handling=True,
            )
        t_read = time.perf_counter()
        if logger:
            logger.debug(
                "  chunk %d/%d: READ_SOME %d profiles (%.3fs)",
                chunk_no,
                n_chunks,
                len(existing_profiles_list),
                t_read - t_chunk,
            )

        # int32 vocab path: build a per-chunk shared vocab from new + chunk S16
        # matrices and encode both to int32.  new_int32 and profile_int32_map are
        # only populated when use_int32_vocab=True, new_matrix is available, and
        # the chunk is non-empty; otherwise the existing paths (S16 batch or Python
        # loop) are used unchanged.
        new_int32: np.ndarray | None = None
        profile_int32_map: dict[UUID, tuple[np.ndarray, np.ndarray]] = {}
        if (
            use_int32_vocab
            and new_matrix is not None
            and null_new is not None
            and seq_profile_type == enum.SeqProfileType.ALLELE
        ):
            valid_for_int32 = [p for p in existing_profiles_list if p.id is not None]
            if valid_for_int32:
                chunk_s16 = np.stack([p.get_allele_array() for p in valid_for_int32])
                null_chunk = chunk_s16 == _NULL_ALLELE  # (C, n_loci) bool
                new_int32, chunk_int32 = _encode_to_int32(new_matrix, chunk_s16)
                profile_int32_map = {
                    p.id: (chunk_int32[i], null_chunk[i])
                    for i, p in enumerate(valid_for_int32)
                }

        if use_row_per_pair:
            # Row-per-pair path: compute distances and collect SeqDistancePair
            # objects; no SeqDistance blobs are read or written this chunk.
            for existing_profile in existing_profiles_list:
                if existing_profile.id is None:
                    continue
                pid_b = existing_profile.id  # narrowed by `is None` check above
                int32_entry = profile_int32_map.get(pid_b)
                if new_int32 is not None and null_new is not None and int32_entry is not None:
                    int32_row, null_existing_row = int32_entry
                    distances_arr = _hamming_allele_int32_batch(
                        int32_row, new_int32, null_existing_row, null_new
                    )
                    for i in np.where(distances_arr <= max_stored_distance)[0]:
                        pid_a = cast(UUID, new_seq_profiles[i].id)
                        d = float(distances_arr[i])
                        all_new_pairs.append((pid_a, pid_b, d))
                        all_new_pairs.append((pid_b, pid_a, d))
                else:
                    decoded_existing = _decode_profile(
                        seq_profile_type, existing_profile, use_numpy_allele
                    )
                    if new_matrix is not None and null_new is not None:
                        distances_arr = _hamming_allele_numpy_batch(
                            decoded_existing, new_matrix, null_new
                        )
                        # np.where avoids a per-pair Python if-check; beneficial
                        # when few pairs pass the max_stored_distance filter.
                        for i in np.where(distances_arr <= max_stored_distance)[0]:
                            pid_a = cast(UUID, new_seq_profiles[i].id)
                            d = float(distances_arr[i])
                            all_new_pairs.append((pid_a, pid_b, d))
                            all_new_pairs.append((pid_b, pid_a, d))
                    else:
                        for new_profile, decoded_new in zip(
                            new_seq_profiles, decoded_new_profiles
                        ):
                            assert new_profile.id is not None
                            distance = _calculate_distance_for_decoded_profile_pair(
                                seq_profile_type, decoded_existing, decoded_new
                            )
                            if distance <= max_stored_distance:
                                pid_a = new_profile.id  # narrowed by assert above
                                all_new_pairs.append((pid_a, pid_b, distance))
                                all_new_pairs.append((pid_b, pid_a, distance))
        else:
            # Blob path: read SeqDistance records and update content.
            # Build an O(1) lookup map for use in the SeqDistance loop below.
            existing_profile_map = {
                x.id: x for x in existing_profiles_list if x.id is not None
            }

            # Step 4b-4c — Stream SeqDistance records for this chunk and compute.
            # iter_seq_distances filters to profile_ids=chunk_ids, which on mssql
            # uses a temp-table JOIN to avoid the ODBC 07002 error that IN() on
            # uniqueidentifier FK columns triggers regardless of list size.
            modified_existing: list[model.SeqDistance] = []
            n_distances_seen = 0
            with repository.uow() as chunk_uow:
                for existing_seq_distance in repository.iter_seq_distances(
                    chunk_uow, cast(UUID, protocol.id), profile_ids=chunk_ids
                ):
                    assert isinstance(existing_seq_distance, model.SeqDistance)
                    n_distances_seen += 1
                    existing_profile = existing_profile_map.get(
                        existing_seq_distance.seq_profile_id
                    )
                    # Should not happen with a correct chunk filter, but the DB
                    # could return a record whose profile was deleted between the
                    # READ_SOME and this query — skip it rather than crash.
                    if existing_profile is None:
                        continue

                    # Compare this existing profile against every new profile.
                    updates: dict[str, float] = {}
                    int32_entry = profile_int32_map.get(existing_seq_distance.seq_profile_id)
                    if new_int32 is not None and null_new is not None and int32_entry is not None:
                        int32_row, null_existing_row = int32_entry
                        distances_arr = _hamming_allele_int32_batch(
                            int32_row, new_int32, null_existing_row, null_new
                        )
                        for new_profile, dist in zip(new_seq_profiles, distances_arr):
                            assert new_profile.id is not None
                            if float(dist) <= max_stored_distance:
                                updates[str(new_profile.id)] = float(dist)
                                new_profile_distance_maps[new_profile.id][
                                    str(existing_profile.id)
                                ] = float(dist)
                    else:
                        decoded_existing_profile = _decode_profile(
                            seq_profile_type, existing_profile, use_numpy_allele
                        )
                        if new_matrix is not None and null_new is not None:
                            distances_arr = _hamming_allele_numpy_batch(
                                decoded_existing_profile, new_matrix, null_new
                            )
                            for new_profile, dist in zip(new_seq_profiles, distances_arr):
                                assert new_profile.id is not None
                                if float(dist) <= max_stored_distance:
                                    updates[str(new_profile.id)] = float(dist)
                                    new_profile_distance_maps[new_profile.id][
                                        str(existing_profile.id)
                                    ] = float(dist)
                        else:
                            for new_profile, decoded_new_profile in zip(
                                new_seq_profiles, decoded_new_profiles
                            ):
                                assert new_profile.id is not None
                                distance = _calculate_distance_for_decoded_profile_pair(
                                    seq_profile_type,
                                    decoded_existing_profile,
                                    decoded_new_profile,
                                )
                                if distance <= max_stored_distance:
                                    updates[str(new_profile.id)] = distance
                                    # Symmetry: write the reverse entry now; it will
                                    # be serialised into the new SeqDistance record
                                    # at step 6 after all chunks complete.
                                    new_profile_distance_maps[new_profile.id][
                                        str(existing_profile.id)
                                    ] = distance

                    # Deferred json.loads — only parse the content blob when at
                    # least one new profile is close enough to warrant an update.
                    if updates:
                        distance_map = json.loads(existing_seq_distance.content)
                        distance_map.update(updates)
                        existing_seq_distance.content = json.dumps(distance_map)
                        modified_existing.append(existing_seq_distance)

            t_iter = time.perf_counter()
            if logger:
                logger.debug(
                    "  chunk %d/%d: iter+compute %d distances, %d modified (%.3fs)",
                    chunk_no,
                    n_chunks,
                    n_distances_seen,
                    len(modified_existing),
                    t_iter - t_read,
                )

            # Step 4d — Accumulate modified records for the single write in step 6.
            all_modified_existing.extend(modified_existing)

    # Step 5: intra-batch distances (new-new pairs).
    t_step5 = time.perf_counter()
    if use_row_per_pair:
        _calculate_pairwise_profile_distances_to_pairs(
            seq_profile_type,
            new_seq_profiles,
            decoded_new_profiles,
            max_stored_distance,
            all_new_pairs,
        )
    else:
        _calculate_pairwise_profile_distances(
            seq_profile_type,
            new_seq_profiles,
            new_profile_distance_maps,
            max_stored_distance,
            decoded_profiles=decoded_new_profiles,
        )
    if logger:
        logger.debug(
            "_calculate_and_store_distances step 5 (pairwise new-new): %.3fs",
            time.perf_counter() - t_step5,
        )

    # Step 6: single-transaction write using the caller's uow (atomic).
    t_step6 = time.perf_counter()
    if use_row_per_pair:
        proto_id = cast(UUID, protocol.id)
        if use_bulk_insert:
            # Core executemany path: bypasses Pydantic construction and ORM
            # session tracking. Falls back to NotImplementedError on DICT repos
            # (caught below and re-raised), so only SA repos benefit.
            try:
                repository.bulk_insert_seq_distance_pairs(
                    uow, user_id, all_new_pairs, proto_id
                )
            except NotImplementedError:
                # DICT repository: fall through to ORM path below.
                use_bulk_insert = False
        if not use_bulk_insert:
            # ORM path: model_construct bypasses validation — values are
            # internally computed so no external input is present;
            # profile_a/profile_b default to None.
            pair_objects: list[model.SeqDistancePair] = [
                model.SeqDistancePair.model_construct(
                    id=cast(UUID, service.generate_id()),
                    protocol_id=proto_id,
                    profile_id_a=a,
                    profile_id_b=b,
                    distance=d,
                )
                for a, b, d in all_new_pairs
            ]
            if pair_objects:
                repository.crud(
                    uow,
                    user_id,
                    model.SeqDistancePair,
                    CrudOperation.CREATE_SOME,
                    objs=pair_objects,
                )
        # Coverage markers: SeqDistance rows with empty content so that
        # get_profiles_without_seq_distance (NOT EXISTS on seq_distance) still
        # correctly identifies unprocessed profiles on subsequent calls.
        new_seq_distances: list[model.SeqDistance] = [
            model.SeqDistance(  # type: ignore[call-arg]
                id=cast(UUID, service.generate_id()),
                sample_id=x.sample_id,  # type: ignore[arg-type]
                seq_profile_id=cast(UUID, x.id),
                protocol_id=cast(UUID, protocol.id),  # type: ignore[arg-type]
                format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,  # type: ignore[arg-type]
                content="{}",
            )
            for x in new_seq_profiles
        ]
        created_seq_distances: list[model.SeqDistance] = repository.crud(
            uow,
            user_id,
            model.SeqDistance,
            CrudOperation.CREATE_SOME,
            objs=new_seq_distances,
        )
        for created in created_seq_distances:
            results.append(
                model.CalculateSeqDistancesResult.model_construct(
                    id=created.id,
                    status=EtlStatus.CREATED,
                    seq_distance_profile_id=created.seq_profile_id,
                )
            )
    else:
        # Blob write path: UPDATE_SOME modified existing + CREATE_SOME new.
        if all_modified_existing:
            repository.update_some_seq_distance_content(
                uow, user_id, all_modified_existing
            )
            results.extend(
                model.CalculateSeqDistancesResult.model_construct(
                    id=sd.id,
                    status=EtlStatus.UPDATED,
                    seq_distance_profile_id=sd.seq_profile_id,
                )
                for sd in all_modified_existing
            )
        new_seq_distances = [
            model.SeqDistance(  # type: ignore[call-arg]
                id=cast(UUID, service.generate_id()),
                sample_id=x.sample_id,  # type: ignore[arg-type]
                seq_profile_id=cast(UUID, x.id),
                protocol_id=cast(UUID, protocol.id),  # type: ignore[arg-type]
                format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,  # type: ignore[arg-type]
                content=json.dumps(new_profile_distance_maps[cast(UUID, x.id)]),  # type: ignore[arg-type]
            )
            for x in new_seq_profiles
        ]
        created_seq_distances = repository.crud(
            uow,
            user_id,
            model.SeqDistance,
            CrudOperation.CREATE_SOME,
            objs=new_seq_distances,
        )
        for created_seq_distance in created_seq_distances:
            results.append(
                model.CalculateSeqDistancesResult.model_construct(
                    id=created_seq_distance.id,
                    status=EtlStatus.CREATED,
                    seq_distance_profile_id=created_seq_distance.seq_profile_id,
                )
            )
    n_pairs = len(all_new_pairs)
    n_created = len(new_seq_distances)
    n_updated = len(all_modified_existing)
    if logger:
        logger.debug(
            "_calculate_and_store_distances step 6 "
            "(pairs=%d UPDATE_SOME %d CREATE_SOME %d): %.3fs — total: %.3fs",
            n_pairs,
            n_updated,
            n_created,
            time.perf_counter() - t_step6,
            time.perf_counter() - t_fn,
        )


def _calculate_pairwise_profile_distances(
    seq_profile_type: enum.SeqProfileType,
    profiles: list[model.SeqProfile],
    distance_maps: dict[UUID, dict[str, float]],
    max_stored_distance: float,
    decoded_profiles: list[Any] | None = None,
) -> None:
    """
    Compute pairwise distances between profiles within a single batch and
    populate *distance_maps* (upper-triangle only; both directions stored).

    decoded_profiles may be supplied from step 3 (already decoded with
    use_numpy_allele=True) to avoid redundant decoding and to keep numpy
    arrays in use, which hits _hamming_allele_numpy instead of the slow
    Python fallback in _calculate_distance_for_decoded_profile_pair.
    """
    if decoded_profiles is None:
        decoded_profiles = [_decode_profile(seq_profile_type, p) for p in profiles]
    profile_ids = [cast(UUID, x.id) for x in profiles]
    str_profile_ids = [str(x) for x in profile_ids]
    for i in range(len(profiles)):
        id1 = profile_ids[i]
        str_id1 = str_profile_ids[i]
        decoded_profile1 = decoded_profiles[i]
        for j in range(i + 1, len(profiles)):
            id2 = profile_ids[j]
            str_id2 = str_profile_ids[j]
            decoded_profile2 = decoded_profiles[j]
            distance = _calculate_distance_for_decoded_profile_pair(
                seq_profile_type,
                decoded_profile1,
                decoded_profile2,
            )
            if distance <= max_stored_distance:
                distance_maps[id1][str_id2] = distance
                distance_maps[id2][str_id1] = distance


def _calculate_pairwise_profile_distances_to_pairs(
    seq_profile_type: enum.SeqProfileType,
    profiles: list[model.SeqProfile],
    decoded_profiles: list[Any],
    max_stored_distance: float,
    pairs_out: list[_RawPair],
) -> None:
    """
    Compute intra-batch pairwise distances for the row-per-pair path and
    append raw _RawPair tuples (both directions) to pairs_out.

    decoded_profiles must be pre-decoded with the same use_numpy_allele
    setting that was used for the chunk loop, so numpy arrays are handled
    correctly by _calculate_distance_for_decoded_profile_pair.
    SeqDistancePair objects are materialised from raw tuples in step 6.
    """
    profile_ids = [cast(UUID, x.id) for x in profiles]
    for i in range(len(profiles)):
        for j in range(i + 1, len(profiles)):
            distance = _calculate_distance_for_decoded_profile_pair(
                seq_profile_type, decoded_profiles[i], decoded_profiles[j]
            )
            if distance <= max_stored_distance:
                pairs_out.append((profile_ids[i], profile_ids[j], distance))
                pairs_out.append((profile_ids[j], profile_ids[i], distance))


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

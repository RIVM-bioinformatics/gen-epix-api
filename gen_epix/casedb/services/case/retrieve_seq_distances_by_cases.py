"""Retrieve stored sequence distances under case and column access checks."""

import json
from collections import defaultdict
from typing import cast
from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.enum as seqdb_enum
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.retrieve_seq import _retrieve_case_profile_map
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.contains_string import ContainsStringFilter
from gen_epix.filter.equals_uuid import EqualsUuidFilter


def case_service_retrieve_seq_distances_by_cases(
    self: BaseCaseService, cmd: command.RetrieveSeqDistancesByCasesCommand
) -> list[model.CaseSeqDistance]:
    """Return distances within the casedb protocol maximum to permitted profiles.

    Requested cases require a populated, readable distance column. External
    targets additionally require sequence-column access when included. Each
    result is keyed by its requested case ID, and distances are keyed by target
    case IDs.

    Args:
        self: Service handling the request.
        cmd: Requested cases, distance column, and external-target filtering flag.

    Returns:
        CaseSeqDistance for each requested Case.

    Raises:
        InvalidArgumentsError: If the column has the wrong case or column type.
        InitializationServiceError: If the linked sequence column is missing.
        UnauthorizedAuthError: If requested distance content is unavailable, or
            no case for an external target permits reading the distance column.
        RequestLimitExceededAuthError: If requested cases exceed configured limits.
    """
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None
    with repository.uow() as uow:
        # @ABAC: Retrieve the case profile map with access control checks
        genetic_distance_protocol, case_seq_profile_map, dist_col = (
            _retrieve_case_profile_map(self, uow, cmd)
        )

        # Special case: no case IDs provided, return an empty list
        if not cmd.case_ids:
            return []

        # Special case: no accessible sequence profiles, return a list with empty distances
        seq_profile_ids = list(
            set(case_seq_profile_map.values())
        )  # take unique as more than one Case may map to the same SeqProfile
        if not seq_profile_ids:
            return [
                model.CaseSeqDistance(id=case_id, distances={})
                for case_id in cmd.case_ids
            ]

        # Retrieve the SeqDistances for the accessible profiles
        seqdb_seq_distance_protocol_id = (
            genetic_distance_protocol.seqdb_seq_distance_protocol_id
        )
        seq_profile_additional_cases_map: dict[UUID, set[tuple[UUID, UUID]]] = (
            defaultdict(set)
        )
        seq_profile_case_map: dict[UUID, UUID] = {}
        for case_id, seq_profile_id in case_seq_profile_map.items():
            if seq_profile_id in seq_profile_case_map:
                # More than one case with this seq_profile ID exists, keep track of additional cases as well as the first case found
                seq_profile_additional_cases_map[seq_profile_id].add(
                    (seq_profile_case_map[seq_profile_id], case_id)
                )
            else:
                seq_profile_case_map[seq_profile_id] = case_id
        seq_distances: list[seqdb_model.SeqDistance] = self.app.handle(
            seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand(
                user=cmd.user,
                seq_profile_ids=seq_profile_ids,
                protocol_id=seqdb_seq_distance_protocol_id,
            )
        )

        # Unpack content (distances) from the retrieved SeqDistances, storing them in a map keyed by seq_profile_id and removing too large distances
        max_stored_distance = genetic_distance_protocol.seqdb_max_stored_distance
        if max_stored_distance is None:
            max_stored_distance = float("inf")
        seq_profile_distances_map: dict[UUID, dict[UUID, float]] = {}
        for seq_distance in seq_distances:
            if seq_distance.format == seqdb_enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP:
                seq_profile_distances_map[seq_distance.seq_profile_id] = {
                    UUID(x): y
                    for x, y in json.loads(seq_distance.content).items()
                    if y is not None and y <= max_stored_distance
                }
            else:
                raise AssertionError(
                    f"Unexpected SeqDistance format: {seq_distance.format}"
                )

        # Determine which other cases are readable, in case other cases are not to be filtered out, by adding them to seq_profile_case_map
        all_distance_seq_profile_ids: set[UUID] = set()
        for distances in seq_profile_distances_map.values():
            all_distance_seq_profile_ids.update(distances)
        all_distance_seq_profile_ids_str = {
            str(seq_profile_id) for seq_profile_id in all_distance_seq_profile_ids
        }
        if not cmd.filter_other_cases:
            # Do not filter out other cases, except those that are not readable
            case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
            user_id = None if cmd.user is None else cmd.user.id
            dist_col_id = cast(UUID, dist_col.id)
            dist_col_id_str = str(dist_col_id)
            if case_abac is None or case_abac.is_full_access:
                # @ABAC: not applied, use more efficient query
                for row in self.repository.read_fields(
                    uow,
                    user_id,
                    model.Case,
                    ["id", "content"],
                    filter=CompositeFilter(
                        filters=[
                            EqualsUuidFilter(
                                key="case_type_id", value=cmd.case_type_id
                            ),
                            ContainsStringFilter(key="content", value=dist_col_id_str),
                        ]
                    ),
                ):
                    content: dict[str, str | None] = json.loads(row[1])
                    seq_profile_id_str = content.get(dist_col_id_str)
                    if (
                        seq_profile_id_str is not None
                        and seq_profile_id_str in all_distance_seq_profile_ids_str
                    ):
                        # Map the sequence profile ID to the corresponding case ID
                        seq_profile_id = UUID(seq_profile_id_str)
                        case_id = UUID(row[0])
                        if seq_profile_id in seq_profile_case_map:
                            # More than one case with this seq_profile ID exists, keep track of additional cases as well as the first case found
                            seq_profile_additional_cases_map[seq_profile_id].add(
                                (seq_profile_case_map[seq_profile_id], case_id)
                            )
                        else:
                            seq_profile_case_map[seq_profile_id] = case_id
            else:
                # @ABAC: remove all cases with non-readable dist_col from distances
                assert user_id is not None
                cases, _ = self._retrieve_cases_with_content_right(uow, user_id, case_abac, enum.CaseRight.READ_CASE, cmd.case_type_id, case_ids=None, filter_content=True, apply_max_n_cases=False)  # type: ignore[assignment]
                for case in cases:
                    seq_profile_id_str = case.content.get(dist_col_id)
                    if seq_profile_id_str is not None:
                        seq_profile_id = UUID(seq_profile_id_str)
                        if seq_profile_id in all_distance_seq_profile_ids:
                            if seq_profile_id in seq_profile_case_map:
                                # More than one case with this seq_profile ID exists, keep track of additional cases as well as the first case found
                                seq_profile_additional_cases_map[seq_profile_id].add(
                                    (
                                        seq_profile_case_map[seq_profile_id],
                                        cast(UUID, case.id),
                                    )
                                )
                            else:
                                seq_profile_case_map[seq_profile_id] = cast(
                                    UUID, case.id
                                )
        else:
            # Keep only distances to requested cases, nothing to do as seq_profile_case_map is already filtered
            pass

        # Derive CaseSeqDistances
        case_seq_distances: list[model.CaseSeqDistance] = []
        for case_id in cmd.case_ids:
            seq_profile_id_or_none = case_seq_profile_map.get(case_id)
            if seq_profile_id_or_none is None:
                # No SeqDistance existed for the requested Case ID -> add empty CaseSeqDistance
                case_seq_distance = model.CaseSeqDistance(
                    id=case_id,
                    distances={},
                )
            else:
                # Create CaseSeqDistance containing only distances for SeqProfiles in seq_profile_case_map, plus any additional cases mapping to the same SeqProfile
                distances_or_none = seq_profile_distances_map.get(
                    seq_profile_id_or_none
                )
                assert distances_or_none is not None
                case_distances: dict[UUID, float] = {}
                for target_seq_profile_id, distance in distances_or_none.items():
                    if target_seq_profile_id not in seq_profile_case_map:
                        continue
                    case_distances[seq_profile_case_map[target_seq_profile_id]] = (
                        distance
                    )
                    for _, additional_case_id in seq_profile_additional_cases_map.get(
                        target_seq_profile_id, set()
                    ):
                        case_distances[additional_case_id] = distance
                case_seq_distance = model.CaseSeqDistance(
                    id=case_id,
                    distances=case_distances,
                )
            case_seq_distances.append(case_seq_distance)

        return case_seq_distances

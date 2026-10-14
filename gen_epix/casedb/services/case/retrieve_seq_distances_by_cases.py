"""Retrieve stored sequence distances under case and column access checks."""

import json
from collections import defaultdict
from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.equals_uuid import EqualsUuidFilter


def case_service_retrieve_seq_distances_by_cases(
    self: BaseCaseService, cmd: command.RetrieveSeqDistancesByCasesCommand
) -> list[seqdb_model.SeqDistance]:
    """Return distances within the casedb protocol maximum to permitted profiles.

    Requested cases require a populated, readable distance column. External
    targets additionally require sequence-column access when included. Returned
    rows are copies, with case IDs as row IDs and profile IDs as map keys.

    Args:
        self: Service handling the request.
        cmd: Requested cases, distance column, and external-target filtering flag.

    Returns:
        Stored source rows for each requested case, including empty filtered maps.

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
        dist_col: model.Col = repository.crud(
            uow,
            user.id,
            model.Col,
            CrudOperation.READ_ONE,
            obj_ids=cmd.genetic_distance_col_id,
        )
        if dist_col.case_type_id != cmd.case_type_id:
            raise exc.InvalidArgumentsError(
                "bac042b3", "The genetic-distance column belongs to another case type."
            )
        ref_col: model.RefCol = repository.crud(
            uow,
            user.id,
            model.RefCol,
            CrudOperation.READ_ONE,
            obj_ids=dist_col.ref_col_id,
        )
        if ref_col.col_type != enum.ColType.GENETIC_DISTANCE:
            raise exc.InvalidArgumentsError(
                "7684d8a9", "The selected column is not a genetic-distance column."
            )
        protocol: model.GeneticDistanceProtocol = repository.crud(
            uow,
            user.id,
            model.GeneticDistanceProtocol,
            CrudOperation.READ_ONE,
            obj_ids=ref_col.genetic_distance_protocol_id,
        )
        seq_col_id = dist_col.genetic_sequence_col_id
        if seq_col_id is None:
            raise exc.InitializationServiceError(
                "0ac987fb",
                "The genetic-distance column has no linked genetic-sequence column.",
            )
        if not cmd.case_ids:
            return []
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
        assert case_abac is not None
        cases, is_max_results_exceeded = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            enum.CaseRight.READ_CASE,
            cmd.case_type_id,
            case_ids=cmd.case_ids,
            filter_content=False,
        )
        if is_max_results_exceeded:
            raise exc.RequestLimitExceededAuthError(
                "e783e7bb", "Requested cases exceed the configured result limit."
            )
        collections = self._retrieve_case_data_collections_map(uow, user.id)
        rights_cache: dict[UUID, model.CaseRights] = {}

        def can_read(case: model.Case, col_id: UUID) -> bool:
            if case_abac.is_full_access:
                return True
            assert case.id is not None
            if case.id not in rights_cache:
                rights_cache[case.id] = case_abac.get_case_rights(
                    case.id,
                    case.case_type_id,
                    case.created_in_data_collection_id,
                    collections.get(case.id, set())
                    | {case.created_in_data_collection_id},
                )
            rights = rights_cache[case.id]
            return rights.is_full_access or col_id in rights.read_col_ids

        profile_cases: dict[UUID, list[UUID]] = defaultdict(list)
        for case in cases:
            profile_value = case.content.get(cmd.genetic_distance_col_id)
            if not can_read(case, cmd.genetic_distance_col_id) or not profile_value:
                raise exc.UnauthorizedAuthError(
                    "a7dcb11a",
                    "The requested genetic-distance content is not readable.",
                )
            assert case.id is not None
            profile_cases[UUID(profile_value)].append(case.id)
        if not profile_cases:
            return []
        seq_distances: list[seqdb_model.SeqDistance] = self.app.handle(
            seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand(
                user=cmd.user,
                seq_profile_ids=list(profile_cases),
                protocol_id=protocol.seqdb_seq_distance_protocol_id,
            )
        )
        distance_maps = [
            {
                target: distance
                for target, distance in row.get_profile_distance_map().items()
                if protocol.seqdb_max_stored_distance is None
                or distance <= protocol.seqdb_max_stored_distance
            }
            for row in seq_distances
        ]
        allowed_profiles = set(profile_cases)
        if not cmd.filter_other_cases:
            external_profiles = {
                target
                for distances in distance_maps
                for target in distances
                if target not in profile_cases
            }
            if external_profiles:
                all_cases: list[model.Case] = repository.crud(
                    uow,
                    user.id,
                    model.Case,
                    CrudOperation.READ_ALL,
                    filter=EqualsUuidFilter(key="case_type_id", value=cmd.case_type_id),
                )
                candidates: dict[UUID, list[model.Case]] = defaultdict(list)
                requested_ids = set(cmd.case_ids)
                for case in all_cases:
                    value = case.content.get(cmd.genetic_distance_col_id)
                    if not value or case.id in requested_ids:
                        continue
                    profile_id = UUID(value)
                    if profile_id in external_profiles:
                        candidates[profile_id].append(case)
                for profile_id, matching_cases in candidates.items():
                    readable_cases = [
                        case
                        for case in matching_cases
                        if can_read(case, cmd.genetic_distance_col_id)
                    ]
                    if not readable_cases:
                        raise exc.UnauthorizedAuthError(
                            "bc4b754d",
                            "Matching genetic-distance content is not readable.",
                        )
                    if any(can_read(case, seq_col_id) for case in readable_cases):
                        allowed_profiles.add(profile_id)

        retval: list[seqdb_model.SeqDistance] = []
        for row, distances in zip(seq_distances, distance_maps):
            content = json.dumps(
                {
                    str(target): distance
                    for target, distance in distances.items()
                    if target in allowed_profiles
                }
            )
            for case_id in profile_cases.get(row.seq_profile_id, []):
                retval.append(
                    row.model_copy(
                        deep=True, update={"id": case_id, "content": content}
                    )
                )
        return retval

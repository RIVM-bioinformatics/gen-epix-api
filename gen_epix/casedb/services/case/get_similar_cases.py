from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp.enum import CrudOperation


def case_service_get_similar_cases(
    self: BaseCaseService, cmd: command.GetSimilarCasesCommand
) -> list[UUID]:
    case_type_id = cmd.case_type_id
    dist_case_type_col_id = cmd.genetic_distance_case_type_col_id
    case_ids = cmd.case_ids
    max_distance = cmd.max_distance
    user: model.User
    user, repository = self._get_user_and_repository(cmd)  # type: ignore[assignment]
    assert isinstance(user, model.User) and user.id is not None
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    if len(case_ids) == 0:
        raise exc.InvalidArgumentsError("At least one case ID must be provided")

    with repository.uow() as uow:
        # Get distance column data
        dist_case_type_col: model.CaseTypeCol = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.CaseTypeCol,
            None,
            dist_case_type_col_id,
            CrudOperation.READ_ONE,
        )
        if dist_case_type_col.case_type_id != case_type_id:
            raise exc.InvalidArgumentsError(
                f"Case type column {dist_case_type_col_id} does not belong to case type {case_type_id}"
            )
        dist_col: model.Col = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            dist_case_type_col.col_id,
            CrudOperation.READ_ONE,
        )
        if dist_col.col_type != enum.ColType.GENETIC_DISTANCE:
            raise exc.InvalidArgumentsError(
                f"Case type column {dist_case_type_col_id} is not of type {enum.ColType.GENETIC_DISTANCE.value}"
            )

        # Get genetic distance protocol
        genetic_distance_protocol: model.GeneticDistanceProtocol = (
            self.repository.crud(  # type: ignore[assignment]
                uow,
                user.id,
                model.GeneticDistanceProtocol,
                None,
                dist_col.genetic_distance_protocol_id,
                CrudOperation.READ_ONE,
            )
        )
        seqdb_seq_distance_protocol_id = (
            genetic_distance_protocol.seqdb_seq_distance_protocol_id
        )

        # @ABAC: Get cases
        all_cases = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            enum.CaseRight.READ_CASE,
            case_type_id,
            case_ids=None,
            filter_content=True,
        )

        # Get profile_ids from dist_case_type_col
        case_id_profile_id_map: dict[UUID, UUID] = {}
        for case in all_cases:
            profile_id = case.content.get(dist_case_type_col_id)
            if profile_id:
                case_id_profile_id_map[case.id] = UUID(profile_id)

        profile_ids: list[UUID] = []
        for case_id, profile_id in case_id_profile_id_map.items():
            if case_id in case_ids:
                profile_ids.append(profile_id)

        similar_profile_ids: list[UUID] = self.app.handle(
            seqdb_command.GetSimilarProfilesCommand(
                seq_distance_protocol_id=seqdb_seq_distance_protocol_id,
                profile_ids=profile_ids,
                max_distance=max_distance,
            )
        )

        # Normalize result ids and include seed profile_ids; map back to case ids
        unique_similar_profile_ids: set[UUID] = {UUID(str(x)) for x in similar_profile_ids}
        norm_seed_profile_ids: set[UUID] = {UUID(str(x)) for x in profile_ids}
        lookup_ids: set[UUID] = unique_similar_profile_ids | norm_seed_profile_ids
        similar_case_ids: list[UUID] = [
            case_id for case_id, profile_id in case_id_profile_id_map.items() if profile_id in lookup_ids
        ]

    return similar_case_ids

from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp.enum import CrudOperation


def case_service_retrieve_similar_cases(
    self: BaseCaseService, cmd: command.RetrieveSimilarCasesCommand
) -> list[UUID]:
    case_type_id = cmd.case_type_id
    dist_col_id = cmd.genetic_distance_col_id
    case_ids = cmd.case_ids
    max_distance = cmd.max_distance
    user: model.User
    user, repository = self._get_user_and_repository(cmd)  # type: ignore[assignment]
    assert isinstance(user, model.User) and user.id is not None
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    # Special case: zero query cases
    if len(case_ids) == 0:
        return []

    with repository.uow() as uow:
        # Get distance column data
        dist_col: model.Col = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            dist_col_id,
            CrudOperation.READ_ONE,
        )
        if dist_col.case_type_id != case_type_id:
            raise exc.InvalidArgumentsError(
                f"Col {dist_col_id} does not belong to CaseType {case_type_id}"
            )
        dist_ref_col: model.RefCol = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.RefCol,
            None,
            dist_col.ref_col_id,
            CrudOperation.READ_ONE,
        )
        if dist_ref_col.col_type != enum.ColType.GENETIC_DISTANCE:
            raise exc.InvalidArgumentsError(
                f"Column {dist_col_id} is not of type {enum.ColType.GENETIC_DISTANCE.value}"
            )

        # Get genetic distance protocol
        genetic_distance_protocol: model.Protocol = (
            self.repository.crud(  # type: ignore[assignment]
                uow,
                user.id,
                model.Protocol,
                None,
                dist_ref_col.protocol_id,
                CrudOperation.READ_ONE,
            )
        )
        seqdb_seq_distance_protocol_id = genetic_distance_protocol.seqdb_protocol_id

        # @ABAC: Get all cases
        all_cases = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            enum.CaseRight.READ_CASE,
            case_type_id,
            case_ids=None,
            filter_content=True,
            apply_max_n_cases=False,
        )

        # Get profile_ids from dist_ref_col
        case_id_profile_id_map: dict[UUID, str | None] = {
            x.id: x.content.get(dist_col_id) for x in all_cases
        }
        case_ids_set = set(case_ids)
        profile_ids: list[UUID] = [
            UUID(profile_id)
            for case_id, profile_id in case_id_profile_id_map.items()
            if profile_id is not None and case_id in case_ids_set
        ]

        # Get similar profile IDs from seqdb, expected not to include the query profile ids
        similar_profile_ids: list[UUID] = self.app.handle(
            seqdb_command.RetrieveSimilarProfilesCommand(
                protocol_id=seqdb_seq_distance_protocol_id,
                profile_ids=profile_ids,
                max_distance=max_distance,
            )
        )

        # Retrieve cases for similar profiles
        # TODO: theoretically two cases could have the same profile as content. If this detected, then an alternate (slower) process should be chosen to map profile ID back to case ID.
        profile_id_case_id_map = {
            y: x for x, y in case_id_profile_id_map.items() if y is not None
        }
        similar_profile_ids_str = [str(x) for x in similar_profile_ids]
        similar_case_ids = [
            profile_id_case_id_map[x]
            for x in similar_profile_ids_str
            if x in profile_id_case_id_map
        ]

    return similar_case_ids

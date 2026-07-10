from uuid import UUID

import gen_epix.seqdb.domain.command as seqdb_command
from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp.enum import CrudOperation


def case_service_retrieve_similar_cases(
    self: BaseCaseService, cmd: command.RetrieveSimilarCasesCommand
) -> command.RetrieveSimilarCasesReturnValue:
    case_type_id = cmd.case_type_id
    dist_col_id = cmd.genetic_distance_col_id
    case_ids = cmd.case_ids
    user: model.User
    user, repository = self._get_user_and_repository(cmd)  # type: ignore[assignment]
    assert isinstance(user, model.User) and user.id is not None
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    # Special case: zero query cases
    if len(case_ids) == 0:
        return command.RetrieveSimilarCasesReturnValue(cases=[])

    with repository.uow() as uow:
        # Get distance column data
        dist_col: model.Col = repository.crud(
            uow,
            user.id,
            model.Col,
            CrudOperation.READ_ONE,
            obj_ids=dist_col_id,
        )
        if dist_col.case_type_id != case_type_id:
            raise exc.InvalidArgumentsError(
                "331bf264",
                f"Col {dist_col_id} does not belong to CaseType {case_type_id}",
            )
        dist_ref_col: model.RefCol = repository.crud(
            uow,
            user.id,
            model.RefCol,
            CrudOperation.READ_ONE,
            obj_ids=dist_col.ref_col_id,
        )
        if dist_ref_col.col_type != enum.ColType.GENETIC_DISTANCE:
            raise exc.InvalidArgumentsError(
                "ebf33e88",
                f"Column {dist_col_id} is not of type {enum.ColType.GENETIC_DISTANCE.value}",
            )

        # Get genetic distance protocol
        genetic_distance_protocol: model.GeneticDistanceProtocol = self.repository.crud(
            uow,
            user.id,
            model.GeneticDistanceProtocol,
            CrudOperation.READ_ONE,
            obj_ids=dist_ref_col.genetic_distance_protocol_id,
        )
        seqdb_seq_distance_protocol_id = (
            genetic_distance_protocol.seqdb_seq_distance_protocol_id
        )

        # @ABAC: Get all cases
        all_cases = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            enum.CaseRight.READ_CASE,
            case_type_id,
            case_ids=None,
            filter_content=True,
            calculate_case_date=False,
            apply_max_n_cases=False,
        )

        # Get profile_ids from dist_ref_col
        case_id_profile_id_map: dict[UUID, str | None] = {  # type: ignore[assignment]
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
                max_distance=cmd.max_distance,
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
            if profile_id_case_id_map[x]
            not in case_ids_set  # Exclude query cases if they appear as similar
        ]

        # Retrieve similar cases with ABAC applied to case date
        similar_cases = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            enum.CaseRight.READ_CASE,
            case_type_id,
            case_ids=similar_case_ids,
            filter_content=True,
            calculate_case_date=True,
            apply_max_n_cases=False,
        )

        # early return if there are now no similar cases after ABAC filtering
        if len(similar_cases) == 0:
            return command.RetrieveSimilarCasesReturnValue(cases=[])

        case_type_access_abacs = case_abac.case_type_access_abacs.get(case_type_id, {})
        private_data_collection_ids = {
            x.data_collection_id
            for x in case_type_access_abacs.values()
            if x.is_private
        }
        case_data_collections_map = self._retrieve_case_data_collections_map(
            uow, user.id, case_ids=similar_case_ids
        )

        # Construct return value
        retval = command.RetrieveSimilarCasesReturnValue(
            cases=[
                model.SimilarCase(
                    id=x.id,
                    case_date=x.case_date,
                    is_own_case=bool(
                        (
                            case_data_collections_map.get(x.id, set())
                            | {x.created_in_data_collection_id}
                        )
                        & private_data_collection_ids
                    ),
                )
                for x in similar_cases
                if x.id is not None
            ]
        )
    return retval

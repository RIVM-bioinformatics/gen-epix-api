from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService


def case_service_retrieve_is_own_cases(
    self: BaseCaseService, cmd: command.RetrieveIsOwnCasesCommand
) -> dict[UUID, bool]:
    case_type_id = cmd.case_type_id
    user: model.User
    user, repository = self._get_user_and_repository(cmd)  # type: ignore[assignment]
    assert isinstance(user, model.User) and user.id is not None
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None
    right = enum.CaseRight.READ_CASE

    with repository.uow() as uow:

        is_full_access = case_abac.is_full_access
        has_case_read = case_abac.get_combinations_with_access_right(right)
        if case_type_id not in has_case_read and not is_full_access:
            raise exc.UnauthorizedAuthError(
                "b4c3caa5", f"Unauthorized CaseType: {case_type_id}"
            )

        all_cases = self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            right,
            case_type_id,
            case_ids=cmd.case_ids,
            filter_content=True,
            calculate_case_date=False,
            apply_max_n_cases=False,
            on_invalid_case_id="ignore",
        )

        case_type_access_abacs = case_abac.case_type_access_abacs.get(case_type_id, {})
        private_data_collection_ids = {
            x.data_collection_id
            for x in case_type_access_abacs.values()
            if x.is_private
        }
        case_data_collections_map = self._retrieve_case_data_collections_map(
            uow, user.id, case_ids={x.id for x in all_cases if x is not None}  # type: ignore[misc]
        )

        is_own_cases_map = {
            x.id: bool(
                (
                    case_data_collections_map.get(x.id, set())
                    | {x.created_in_data_collection_id}
                )
                & private_data_collection_ids
            )
            for x in all_cases
            if x.id is not None
        }

    return is_own_cases_map

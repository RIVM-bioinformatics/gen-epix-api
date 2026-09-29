"""Update the creating data collection for existing cases."""

from typing import cast
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import is_app_admin_or_above
from gen_epix.fastapp import CrudOperation


def case_service_update_case_created_in_data_collection(
    self: BaseCaseService,
    cmd: command.UpdateCaseCreatedInDataCollectionCommand,
) -> list[UUID]:
    """Update the created_in_data_collection_id for existing cases.

    All cases are read before any mutations are persisted, so an invalid case ID
    prevents the update batch from being applied.

    Args:
        self: Case service handling the command.
        cmd: Case IDs and the replacement data collection ID.

    Returns:
        The IDs of the updated cases. If a case's created_in_data_collection_id was
        already set to the target value, it will not be included.

    Raises:
        AssertionError: If the command user is not an app administrator or above.
    """
    user, repository = self._get_user_and_repository(cmd)
    assert user.id is not None
    assert is_app_admin_or_above(self, user)  # type: ignore[arg-type]

    with repository.uow() as uow:
        cases: list[model.Case] = repository.crud(
            uow,
            user.id,
            model.Case,
            CrudOperation.READ_SOME,
            obj_ids=cmd.case_ids,
        )
        cases_to_update: list[model.Case] = []
        for case in cases:
            if (
                case.created_in_data_collection_id
                == cmd.target_created_in_data_collection_id
            ):
                continue
            case.created_in_data_collection_id = (
                cmd.target_created_in_data_collection_id
            )
            cases_to_update.append(case)
        if not cases_to_update:
            return []
        updated_cases = repository.crud(
            uow,
            user.id,
            model.Case,
            CrudOperation.UPDATE_SOME,
            objs=cases_to_update,
        )
        return [cast(UUID, x.id) for x in updated_cases]

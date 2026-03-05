"""
CRUD operations for Case entities.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete, get_case_abac_from_command, is_app_admin_or_above)
from gen_epix.fastapp import CrudOperation, CrudOperationSet
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_case(
    self: BaseCaseService, cmd: command.CaseCrudCommand
) -> list[model.Case] | model.Case | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for Case entities."""

    # Start unit of work
    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_app_admin_or_above(self, cmd.user):
            return _crud_case_without_abac(self, uow, cmd)
        return _crud_case_with_abac(self, uow, cmd)


def _crud_case_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseCrudCommand,
) -> list[model.Case] | model.Case | list[UUID] | UUID | list[bool] | bool | None:
    """Case admin command handling, no ABAC applied."""
    return self.crud(cmd)  # type: ignore[return-value]


def _crud_case_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseCrudCommand,
) -> list[model.Case] | model.Case | list[UUID] | UUID | list[bool] | bool | None:
    """Case user command handling, ABAC applied."""
    # @ABAC: get case abac
    case_abac = get_case_abac_from_command(cmd)

    # Special case: no policy, allows for internal commands to retrieve all
    if case_abac is None:
        # No policy: allows for internal commands to retrieve all
        return self.crud(cmd)  # type: ignore[return-value]

    # Initialise some
    is_create = cmd.operation in CrudOperationSet.CREATE.value
    is_read = cmd.operation in CrudOperationSet.READ_OR_EXISTS.value
    is_update = cmd.operation in CrudOperationSet.UPDATE.value
    is_delete = cmd.operation in CrudOperationSet.DELETE.value
    is_delete_all = cmd.operation == CrudOperation.DELETE_ALL
    assert cmd.user is not None and cmd.user.id is not None

    # Determine valid case types and data collections
    case_ids: list[UUID] = cmd.get_obj_ids()  # type: ignore[assignment]
    if is_create | is_read | is_update:
        # Implemented through separate create case set command
        raise AssertionError("Unexpected operation")
    elif is_delete:
        # All linked data collections have remove right
        if is_delete_all:
            # Delete all not allowed due to potential large number of case
            raise exc.UnauthorizedAuthError(
                f"Operation {cmd.operation.value} not allowed for cases for this user"
            )
        # Get all cases and data collection links
        assert case_ids is not None
        cases: list[model.Case] = self.repository.crud(  # type: ignore[assignment]
            uow,
            cmd.user.id,
            model.Case,
            None,
            case_ids,
            CrudOperation.READ_SOME,
        )
        case_data_collection_map = self._retrieve_case_data_collections_map(
            uow,
            cmd.user.id,
            case_ids=case_ids,
        )
        # Check if the user has access to all data collections of all requested
        # cases
        for case in cases:
            data_collection_ids = case_data_collection_map.get(
                case.id, set()  # type: ignore[arg-type]
            )
            is_allowed = case_abac.is_allowed(
                case.case_type_id,
                case.created_in_data_collection_id,
                enum.CaseRight.REMOVE_CASE,
                True,
                current_data_collection_ids=data_collection_ids,
            )
            if not is_allowed:
                raise exc.UnauthorizedAuthError(
                    f"User {cmd.user.id} is not allowed to delete case {case.id}"
                )
        # Delete with cascade
        _crud_cascade_delete(self, uow, cmd)
        return self.crud(cmd)  # type: ignore[return-value]
    else:
        raise AssertionError("Unexpected operation")

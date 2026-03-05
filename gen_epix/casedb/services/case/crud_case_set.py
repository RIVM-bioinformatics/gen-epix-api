"""
CRUD operations for CaseSet entities.
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


def case_service_crud_case_set(
    self: BaseCaseService, cmd: command.CaseSetCrudCommand
) -> list[model.CaseSet] | model.CaseSet | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for CaseSet entities."""

    # Start unit of work
    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_app_admin_or_above(self, cmd.user):
            return _crud_case_set_without_abac(self, uow, cmd)
        return _crud_case_set_with_abac(self, uow, cmd)


def _crud_case_set_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetCrudCommand,
) -> list[model.CaseSet] | model.CaseSet | list[UUID] | UUID | list[bool] | bool | None:
    """CaseSet admin command handling, no ABAC applied."""
    # Any other operation
    return self.crud(cmd)  # type: ignore[return-value]


def _crud_case_set_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetCrudCommand,
) -> list[model.CaseSet] | model.CaseSet | list[UUID] | UUID | list[bool] | bool | None:
    """CaseSet user command handling, ABAC applied."""
    # @ABAC: get case abac
    case_abac: model.CaseAbac | None = get_case_abac_from_command(cmd)

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
    case_set_ids: list[UUID] = cmd.get_obj_ids()  # type: ignore[assignment]
    if is_create:
        # Implemented through separate create case set command
        raise AssertionError("Unexpected operation")
    elif is_read:
        # At least one data collection with read access is required
        retval = self._retrieve_case_sets_with_content_right(
            uow,
            cmd.user.id,
            case_abac,
            enum.CaseRight.READ_CASE_SET,
            case_set_ids=case_set_ids,
            filter=cmd.query_filter,
        )
        return retval[0] if cmd.operation == CrudOperation.READ_ONE else retval
    elif is_update:
        # At least one data collection with write access is required
        self._retrieve_case_sets_with_content_right(
            uow,
            cmd.user.id,
            case_abac,
            enum.CaseRight.WRITE_CASE_SET,
            case_set_ids=case_set_ids,
        )
        return self.crud(cmd)  # type: ignore[return-value]
    elif is_delete:
        # All linked data collections have remove right
        _validate_case_set_deletion(
            self, uow, cmd, case_abac, is_delete_all, case_set_ids
        )
        # Delete with cascade
        return self.crud(cmd)  # type: ignore[return-value]
    else:
        raise AssertionError("Unexpected operation")


def _validate_case_set_deletion(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetCrudCommand,
    case_abac: model.CaseAbac,
    is_delete_all: bool,
    case_set_ids: list[UUID] | None,
) -> None:
    if is_delete_all:
        # Delete all not allowed due to potential large number of case sets
        raise exc.UnauthorizedAuthError(
            f"Operation {cmd.operation.value} not allowed for case sets for this user"
        )
        # Get all case sets and data collection links
    assert case_set_ids is not None
    case_sets: list[model.CaseSet] = self.repository.crud(  # type: ignore[assignment]
        uow,
        cmd.user.id,  # type: ignore[union-attr]
        model.CaseSet,
        None,
        case_set_ids,
        CrudOperation.READ_SOME,
    )
    case_set_data_collection_map: dict[UUID, set[UUID]] = (
        self._retrieve_case_set_data_collections_map(
            uow,
            cmd.user.id,  # type: ignore[arg-type,union-attr]
            case_set_ids=case_set_ids,
        )
    )
    # Check if the user has access to all data collections of all requested
    # case sets
    for case_set in case_sets:
        assert case_set.id is not None
        data_collection_ids: set[UUID] = case_set_data_collection_map.get(
            case_set.id, set()
        )
        is_allowed = case_abac.is_allowed(
            case_set.case_type_id,
            case_set.created_in_data_collection_id,
            enum.CaseRight.REMOVE_CASE_SET,
            True,
            current_data_collection_ids=data_collection_ids,
        )
        if not is_allowed:
            raise exc.UnauthorizedAuthError(
                f"User {cmd.user.id} is not allowed to delete case set {case_set.id}"  # type: ignore[union-attr]
            )

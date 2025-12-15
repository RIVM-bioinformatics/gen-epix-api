"""
CRUD operations for CaseSetDataCollectionLink entities.
Complex association entity with extensive ABAC logic.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    get_case_abac_from_command,
    is_app_admin_or_above,
)
from gen_epix.fastapp import CrudOperation, CrudOperationSet
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_case_set_data_collection_link(
    self: BaseCaseService, cmd: command.CaseSetDataCollectionLinkCrudCommand
) -> (
    list[model.CaseSetDataCollectionLink]
    | model.CaseSetDataCollectionLink
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseSetDataCollectionLink entities."""

    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_app_admin_or_above(self, cmd.user):
            return _crud_case_set_data_collection_link_without_abac(self, uow, cmd)
        return _crud_case_set_data_collection_link_with_abac(self, uow, cmd)


def _crud_case_set_data_collection_link_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetDataCollectionLinkCrudCommand,
) -> (
    list[model.CaseSetDataCollectionLink]
    | model.CaseSetDataCollectionLink
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseSetDataCollectionLink admin command handling."""
    _crud_cascade_delete(self, uow, cmd)
    return self.crud(cmd)  # type:ignore[return-value]


def _crud_case_set_data_collection_link_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetDataCollectionLinkCrudCommand,
) -> (
    list[model.CaseSetDataCollectionLink]
    | model.CaseSetDataCollectionLink
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseSetDataCollectionLink user command handling, ABAC applied."""
    case_abac = get_case_abac_from_command(cmd)

    if case_abac is None:
        return self.crud(cmd)  # type:ignore[return-value]

    # Initialize some
    is_read_all = cmd.operation == CrudOperation.READ_ALL
    is_delete_all = cmd.operation == CrudOperation.DELETE_ALL
    is_update = cmd.operation in CrudOperationSet.UPDATE.value

    # Read all without filter and delete all not allowed due to potential large
    # number of case set data collection links
    if (is_read_all and not cmd.query_filter) or is_delete_all or is_update:
        raise exc.UnauthorizedAuthError(
            f"Operation {cmd.operation.value} not allowed for case set data collection links for this user"
        )

    # For now, delegate to the main crud method with extensive logic
    # TODO: Implement the complex ABAC logic from the main crud.py file
    # This includes checking case set access rights, data collection rights, etc.
    from gen_epix.casedb.services.case.crud import _crud_data_by_non_admin

    return _crud_data_by_non_admin(self, uow, cmd)  # type: ignore[return-value]

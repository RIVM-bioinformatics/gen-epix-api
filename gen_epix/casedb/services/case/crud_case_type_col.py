"""
CRUD operations for CaseTypeCol entities.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    crud_with_access_filter,
    get_case_abac_from_command,
    is_metadata_admin_or_above,
)
from gen_epix.fastapp import CrudOperationSet
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_case_type_col(
    self: BaseCaseService, cmd: command.CaseTypeColCrudCommand
) -> (
    list[model.CaseTypeCol]
    | model.CaseTypeCol
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseTypeCol entities."""

    # Start unit of work
    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_metadata_admin_or_above(self, cmd.user):
            return _crud_case_type_col_by_admin(self, uow, cmd)
        return _crud_case_type_col_by_non_admin(self, uow, cmd)


def _crud_case_type_col_by_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeColCrudCommand,
) -> (
    list[model.CaseTypeCol]
    | model.CaseTypeCol
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeCol admin command handling, no ABAC applied."""
    return self.crud(cmd)  # type:ignore[return-value]


def _crud_case_type_col_by_non_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeColCrudCommand,
) -> (
    list[model.CaseTypeCol]
    | model.CaseTypeCol
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeCol user command handling, ABAC applied."""
    # @ABAC: get case abac
    case_abac = get_case_abac_from_command(cmd)

    # Special case: no policy, allows for internal commands to retrieve all
    if not case_abac:
        # No policy: allows for internal commands to retrieve all
        return self.crud(cmd)  # type:ignore[return-value]

    # Initialize some
    is_read = cmd.operation in CrudOperationSet.READ_OR_EXISTS.value

    if not is_read:
        # Only read operations are allowed for metadata commands for these
        # users
        raise AssertionError("Unexpected operation")

    valid_case_type_col_ids = case_abac.get_case_type_cols_with_any_rights()
    access_filter = self._compose_id_filter(("id", valid_case_type_col_ids))
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]

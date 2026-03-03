"""
CRUD operations for CaseType entities.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    crud_with_access_filter,
    get_case_abac_from_command,
    get_readable_reference_data_from_command,
    is_metadata_admin_or_above,
)
from gen_epix.fastapp import CrudOperationSet
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_case_type(
    self: BaseCaseService, cmd: command.CaseTypeCrudCommand
) -> (
    list[model.CaseType] | model.CaseType | list[UUID] | UUID | list[bool] | bool | None
):
    """Handle CRUD operations for CaseType entities."""

    # Start unit of work
    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_metadata_admin_or_above(self, cmd.user):
            result = _crud_case_type_without_abac(self, uow, cmd)
        else:
            result = _crud_case_type_with_abac(self, uow, cmd)

    if cmd.operation not in CrudOperationSet.READ_OR_EXISTS.value:
        # Clear retrieve_complete_case_type cache as data has changed, to prevent stale data in subsequent calls
        self._RETRIEVE_COMPLETE_CASE_TYPE_CACHE.clear()  # type: ignore[attr-defined]

    return result


def _crud_case_type_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeCrudCommand,
) -> (
    list[model.CaseType] | model.CaseType | list[UUID] | UUID | list[bool] | bool | None
):
    """CaseType admin command handling, no ABAC applied."""
    return self.crud(cmd)  # type: ignore[return-value]


def _crud_case_type_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeCrudCommand,
) -> (
    list[model.CaseType] | model.CaseType | list[UUID] | UUID | list[bool] | bool | None
):
    """CaseType user command handling, ABAC applied."""
    # Special case: no policy, allows for internal commands to retrieve all
    if not get_case_abac_from_command(cmd):
        return self.crud(cmd)  # type: ignore[return-value]

    is_read = cmd.operation in CrudOperationSet.READ_OR_EXISTS.value
    if not is_read:
        # Only read operations are allowed for metadata commands for these
        # users
        raise AssertionError("Unexpected operation")

    readable_reference_data = get_readable_reference_data_from_command(cmd)
    assert readable_reference_data is not None
    valid_case_type_ids = readable_reference_data.case_type_ids
    access_filter = self._compose_id_filter(("id", valid_case_type_ids))
    # No cascade delete to force conscious decision to delete from other models
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]

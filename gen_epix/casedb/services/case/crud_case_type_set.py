"""
CRUD operations for CaseTypeSet entities.
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


def case_service_crud_case_type_set(
    self: BaseCaseService, cmd: command.CaseTypeSetCrudCommand
) -> (
    list[model.CaseTypeSet]
    | model.CaseTypeSet
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseTypeSet entities."""

    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_metadata_admin_or_above(self, cmd.user):
            return _crud_case_type_set_without_abac(self, uow, cmd)
        return _crud_case_type_set_with_abac(self, uow, cmd)


def _crud_case_type_set_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeSetCrudCommand,
) -> (
    list[model.CaseTypeSet]
    | model.CaseTypeSet
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeSet admin command handling, no ABAC applied."""
    retval = self.crud(cmd)
    return retval  # type: ignore[return-value]


def _crud_case_type_set_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeSetCrudCommand,
) -> (
    list[model.CaseTypeSet]
    | model.CaseTypeSet
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeSet user command handling, ABAC applied."""
    if not get_case_abac_from_command(cmd):
        return self.crud(cmd)  # type: ignore[return-value]

    is_read = cmd.operation in CrudOperationSet.READ_OR_EXISTS.value
    if not is_read:
        raise AssertionError("Unexpected operation")

    readable_reference_data = get_readable_reference_data_from_command(cmd)
    assert readable_reference_data is not None
    access_filter = self._compose_id_filter(
        ("id", readable_reference_data.case_type_set_ids)
    )
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]

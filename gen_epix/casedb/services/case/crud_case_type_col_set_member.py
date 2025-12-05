"""
CRUD operations for CaseTypeColSetMember entities.
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


def case_service_crud_case_type_col_set_member(
    self: BaseCaseService, cmd: command.CaseTypeColSetMemberCrudCommand
) -> (
    list[model.CaseTypeColSetMember]
    | model.CaseTypeColSetMember
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseTypeColSetMember entities."""

    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_metadata_admin_or_above(self, cmd.user):
            return _crud_case_type_col_set_member_by_admin(self, uow, cmd)
        return _crud_case_type_col_set_member_by_non_admin(self, uow, cmd)


def _crud_case_type_col_set_member_by_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeColSetMemberCrudCommand,
) -> (
    list[model.CaseTypeColSetMember]
    | model.CaseTypeColSetMember
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeColSetMember admin command handling, no ABAC applied."""
    return self.crud(cmd)  # type:ignore[return-value]


def _crud_case_type_col_set_member_by_non_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeColSetMemberCrudCommand,
) -> (
    list[model.CaseTypeColSetMember]
    | model.CaseTypeColSetMember
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeColSetMember user command handling, ABAC applied."""
    case_abac = get_case_abac_from_command(cmd)

    if not case_abac:
        return self.crud(cmd)  # type:ignore[return-value]

    is_read = cmd.operation in CrudOperationSet.READ_OR_EXISTS.value

    if not is_read:
        raise AssertionError("Unexpected operation")

    valid_case_type_col_ids = case_abac.get_case_type_cols_with_any_rights()
    access_filter = self._compose_id_filter(
        ("case_type_col_id", valid_case_type_col_ids)
    )
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]

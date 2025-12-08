"""
CRUD operations for CaseTypeColSet entities.
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


def case_service_crud_case_type_col_set(
    self: BaseCaseService, cmd: command.CaseTypeColSetCrudCommand
) -> (
    list[model.CaseTypeColSet]
    | model.CaseTypeColSet
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseTypeColSet entities."""

    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_metadata_admin_or_above(self, cmd.user):
            return _crud_case_type_col_set_by_admin(self, uow, cmd)
        return _crud_case_type_col_set_by_non_admin(self, uow, cmd)


def _crud_case_type_col_set_by_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeColSetCrudCommand,
) -> (
    list[model.CaseTypeColSet]
    | model.CaseTypeColSet
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeColSet admin command handling, no ABAC applied."""
    return self.crud(cmd)  # type:ignore[return-value]


def _crud_case_type_col_set_by_non_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeColSetCrudCommand,
) -> (
    list[model.CaseTypeColSet]
    | model.CaseTypeColSet
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeColSet user command handling, ABAC applied."""
    case_abac = get_case_abac_from_command(cmd)

    if not case_abac:
        return self.crud(cmd)  # type:ignore[return-value]

    is_read = cmd.operation in CrudOperationSet.READ_OR_EXISTS.value
    is_delete = cmd.operation in CrudOperationSet.DELETE.value

    if not is_read:
        raise AssertionError("Unexpected operation")

    # Determine valid case type cols as those with any rights
    valid_case_type_col_ids = case_abac.get_case_type_cols_with_any_rights()
    valid_case_type_col_set_ids: set[UUID] = (
        self._read_association_with_valid_ids(  # type:ignore[assignment]
            command.CaseTypeColSetMemberCrudCommand,
            "case_type_col_set_id",
            "case_type_col_id",
            valid_ids2=valid_case_type_col_ids,
            match_all2=is_delete,
            return_type="ids1",
            uow=uow,
            user=cmd.user,
        )
    )
    access_filter = self._compose_id_filter(("id", valid_case_type_col_set_ids))
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]

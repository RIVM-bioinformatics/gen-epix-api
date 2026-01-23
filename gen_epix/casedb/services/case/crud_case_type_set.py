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
    is_metadata_admin_or_above,
)
from gen_epix.fastapp import CrudOperationSet
from gen_epix.fastapp.enum import CrudOperation
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
    return retval  # type:ignore[return-value]


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
    case_abac = get_case_abac_from_command(cmd)

    if not case_abac:
        return self.crud(cmd)  # type:ignore[return-value]

    is_read = cmd.operation in CrudOperationSet.READ_OR_EXISTS.value
    if not is_read:
        raise AssertionError("Unexpected operation")

    # Get all case type sets and members
    user = cmd.user
    assert user is not None and user.id is not None
    all_case_type_set_ids: list[UUID] = self.repository.crud(  # type:ignore[assignment]
        uow,
        user.id,
        model.CaseTypeSet,
        None,
        None,
        CrudOperation.READ_ALL,
        return_id=True,
    )
    all_case_type_set_members: list[model.CaseTypeSetMember] = (
        self.repository.crud(  # type:ignore[assignment]
            uow,
            user.id,
            model.CaseTypeSetMember,
            None,
            None,
            CrudOperation.READ_ALL,
        )
    )

    # Get empty case type sets
    empty_case_type_set_ids: set[UUID] = set(all_case_type_set_ids) - {
        x.case_type_set_id for x in all_case_type_set_members
    }

    # Get valid case type sets
    valid_case_type_ids = case_abac.get_case_types_with_any_rights()
    valid_case_type_set_ids = empty_case_type_set_ids | {
        x.case_type_set_id
        for x in all_case_type_set_members
        if x.case_type_id in valid_case_type_ids
    }

    # Read data with access filter
    access_filter = self._compose_id_filter(("id", valid_case_type_set_ids))
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]

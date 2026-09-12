"""Handle CRUD operations for case-type-set entities."""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    _verify_is_read_operation,
    crud_with_access_filter,
    get_ref_data_access_from_command,
)
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
        return _crud_case_type_set_without_abac(self, uow, cmd)

        # Currently not in use. Left here for future reference if we want to add ABAC for CaseTypeSet.
        # if is_refdata_admin_or_above(self, cmd.user):
        #     return _crud_case_type_set_without_abac(self, uow, cmd)
        # return _crud_case_type_set_with_abac(self, uow, cmd)


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


# Currently not in use. Left here for future reference if we want to add ABAC for CaseTypeSet.
# Adding ABAC for CaseTypeSet would need to be complex: the user should see all CaseTypeSets that contain at least one CaseType that the organization has access to.
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
    ref_data_access = get_ref_data_access_from_command(cmd)
    if ref_data_access is None or ref_data_access.is_full_access:
        # Special case: no policy (implies full access) or explicit full access
        return self.crud(cmd)  # type: ignore[return-value]
    _verify_is_read_operation(cmd)
    # Perform CRUD with access filter applied
    access_filter = ref_data_access.get_case_type_set_filter("id")
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]

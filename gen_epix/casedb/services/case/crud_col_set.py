"""Handle CRUD operations for column-set entities."""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.policies.pdp import PolicyDecisionPoint
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    crud_with_access_filter,
)
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_col_set(
    self: BaseCaseService, cmd: command.ColSetCrudCommand
) -> list[model.ColSet] | model.ColSet | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for ColSet entities."""
    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)

        return _crud_col_set_without_abac(self, uow, cmd)

        # Currently not in use. Left here for future reference if we want to add ABAC for ColSet.
        # if is_refdata_admin_or_above(self, cmd.user):
        #     return _crud_col_set_without_abac(self, uow, cmd)
        # return _crud_col_set_with_abac(self, uow, cmd)


def _crud_col_set_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.ColSetCrudCommand,
) -> list[model.ColSet] | model.ColSet | list[UUID] | UUID | list[bool] | bool | None:
    """ColSet admin command handling, no ABAC applied."""
    return self.crud(cmd)  # type: ignore[return-value]


# Currently not in use. Left here for future reference if we want to add ABAC for ColSet.
# Adding ABAC for ColSet would need to be complex: the user should see all ColSets that contain at least one ColSets that the organization has access to.
def _crud_col_set_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.ColSetCrudCommand,
) -> list[model.ColSet] | model.ColSet | list[UUID] | UUID | list[bool] | bool | None:
    """ColSet user command handling, ABAC applied."""
    pdp: PolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
    access_filter = pdp.get_col_set_id_filter(cmd, col_set_id_field_name="id")
    # No cascade delete to force conscious decision to delete from other models
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]

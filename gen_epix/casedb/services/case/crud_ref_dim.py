"""
CRUD operations for RefDim entities.
This is a simple metadata entity with no ABAC restrictions.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    crud_with_access_filter,
    get_ref_data_access_from_command,
    is_refdata_admin_or_above,
)
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_ref_dim(
    self: BaseCaseService, cmd: command.RefDimCrudCommand
) -> list[model.RefDim] | model.RefDim | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for RefDim entities."""

    # Start unit of work
    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_refdata_admin_or_above(self, cmd.user):
            result = _crud_ref_dim_without_abac(self, uow, cmd)
        else:
            result = _crud_ref_dim_with_abac(self, uow, cmd)

    return result


def _crud_ref_dim_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.RefDimCrudCommand,
) -> list[model.RefDim] | model.RefDim | list[UUID] | UUID | list[bool] | bool | None:
    """RefDim admin command handling, no ABAC applied."""
    return self.crud(cmd)  # type: ignore[return-value]


def _crud_ref_dim_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.RefDimCrudCommand,
) -> list[model.RefDim] | model.RefDim | list[UUID] | UUID | list[bool] | bool | None:
    """RefDim user command handling, ABAC applied."""
    ref_data_access = get_ref_data_access_from_command(cmd)
    if ref_data_access is None or ref_data_access.is_full_access:
        # Special case: no policy (implies full access) or explicit full access
        return self.crud(cmd)  # type: ignore[return-value]
    access_filter = ref_data_access.get_ref_dim_filter("id")
    # No cascade delete to force conscious decision to delete from other models
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]

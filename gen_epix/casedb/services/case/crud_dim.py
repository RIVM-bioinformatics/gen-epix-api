"""
CRUD operations for Dim entities.
This is a simple metadata entity with no ABAC restrictions.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    crud_with_access_filter,
    get_readable_reference_data_from_command,
)
from gen_epix.fastapp import CrudOperation, CrudOperationSet


def case_service_crud_dim(
    self: BaseCaseService, cmd: command.DimCrudCommand
) -> list[model.Dim] | model.Dim | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for Dim entities."""
    # Dim entities have no ABAC restrictions - use direct crud

    with self.repository.uow() as uow:
        if cmd.operation in CrudOperationSet.READ.value:
            readable_reference_data = get_readable_reference_data_from_command(cmd)
            assert readable_reference_data is not None
            valid_dim_ids = readable_reference_data.dim_ids
            access_filter = self._compose_id_filter(("id", valid_dim_ids))
            # No cascade delete to force conscious decision to delete from other models
            return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]
    return self.crud(cmd)  # type: ignore[return-value]

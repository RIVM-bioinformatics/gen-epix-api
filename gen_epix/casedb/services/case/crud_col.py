"""
CRUD operations for Col entities.
This is a simple metadata entity with no ABAC restrictions.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService


def case_service_crud_col(
    self: BaseCaseService, cmd: command.ColCrudCommand
) -> list[model.Col] | model.Col | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for Col entities."""
    # Col entities have no ABAC restrictions - use direct crud
    return self.crud(cmd)  # type: ignore[return-value]

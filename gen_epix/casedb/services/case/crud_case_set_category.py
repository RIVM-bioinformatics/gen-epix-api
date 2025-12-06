"""
CRUD operations for CaseSetCategory entities.
This is a simple metadata entity with no ABAC restrictions.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import _crud_cascade_delete


def case_service_crud_case_set_category(
    self: BaseCaseService, cmd: command.CaseSetCategoryCrudCommand
) -> (
    list[model.CaseSetCategory]
    | model.CaseSetCategory
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseSetCategory entities."""
    # CaseSetCategory entities have no ABAC restrictions, only RBAC - use direct crud
    with self.repository.uow() as uow:
        _crud_cascade_delete(self, uow, cmd)
        return self.crud(cmd)  # type: ignore[return-value]

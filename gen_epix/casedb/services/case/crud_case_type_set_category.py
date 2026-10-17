"""Handle CRUD operations for case-type-set-category entities.

This metadata entity has no ABAC restrictions. The public handler runs cascade
deletion and generic CRUD delegation inside a repository unit of work; shared
CRUD and cascade behavior remain in the case service framework.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import _crud_cascade_delete


def case_service_crud_case_type_set_category(
    self: BaseCaseService, cmd: command.CaseTypeSetCategoryCrudCommand
) -> (
    list[model.CaseTypeSetCategory]
    | model.CaseTypeSetCategory
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseTypeSetCategory entities.

    The handler opens a repository unit of work, processes configured linked
    deletes, and delegates the command to the case service's generic CRUD
    handler. No service-level ABAC filtering is applied.

    Args:
        self: Case service handling the command.
        cmd: CRUD command to execute.

    Returns:
        The result returned by generic CRUD handling.

    Raises:
        AssertionError: If a configured cascade requires a user identity and
            the command has none.
    """
    with self.repository.uow() as uow:
        _crud_cascade_delete(self, uow, cmd)
        return self.crud(cmd)  # type: ignore[return-value]

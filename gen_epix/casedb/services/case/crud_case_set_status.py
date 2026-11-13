"""Handle case-set-status CRUD through the case service.

This metadata entity has no ABAC restrictions. The public handler delegates
linked-record cleanup and persistence to the shared case service utilities.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import _crud_cascade_delete


def case_service_crud_case_set_status(
    self: BaseCaseService, cmd: command.CaseSetStatusCrudCommand
) -> (
    list[model.CaseSetStatus]
    | model.CaseSetStatus
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Execute a CaseSetStatus CRUD command in one repository unit of work.

    Linked records are cascade-deleted before the command is delegated to the
    case service's CRUD handler.

    Args:
        self: Case service handling the command.
        cmd: CRUD command to execute.

    Returns:
        Result returned by the case service's CRUD handler.
    """
    # CaseSetStatus entities have no ABAC restrictions, only RBAC - use direct crud
    with self.repository.uow() as uow:
        _crud_cascade_delete(self, uow, cmd)
        return self.crud(cmd)  # type: ignore[return-value]

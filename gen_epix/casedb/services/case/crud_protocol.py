"""
CRUD operations for Protocol entities.
This is a simple metadata entity with no ABAC restrictions.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService


def case_service_crud_protocol(
    self: BaseCaseService, cmd: command.ProtocolCrudCommand
) -> (
    list[model.Protocol] | model.Protocol | list[UUID] | UUID | list[bool] | bool | None
):
    """Handle CRUD operations for Protocol entities."""
    # Protocol entities have no ABAC restrictions - use direct crud
    return self.crud(cmd)  # type: ignore[return-value]

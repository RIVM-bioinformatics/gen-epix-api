"""Handle CRUD operations for genetic-distance protocol entities.

This is a simple metadata entity with no ABAC restrictions.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService


def case_service_crud_genetic_distance_protocol(
    self: BaseCaseService, cmd: command.GeneticDistanceProtocolCrudCommand
) -> (
    list[model.GeneticDistanceProtocol]
    | model.GeneticDistanceProtocol
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for GeneticDistanceProtocol entities."""
    # GeneticDistanceProtocol entities have no ABAC restrictions - use direct crud
    return self.crud(cmd)  # type: ignore[return-value]

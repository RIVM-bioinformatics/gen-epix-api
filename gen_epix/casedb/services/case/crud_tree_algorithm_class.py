"""Handle CRUD operations for tree-algorithm-class entities.

This is a simple metadata entity with no ABAC restrictions.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.services.case.base import BaseCaseService


def case_service_crud_tree_algorithm_class(
    self: BaseCaseService, cmd: command.TreeAlgorithmClassCrudCommand
) -> (
    list[model.TreeAlgorithmClass]
    | model.TreeAlgorithmClass
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for TreeAlgorithmClass entities."""
    # TreeAlgorithmClass entities have no ABAC restrictions - use direct crud
    return self.crud(cmd)  # type: ignore[return-value]

"""Tests for entity relationship ordering."""

from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel

from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import OnException


class ParentModel(BaseModel):
    """Model used as a dependency in the entity-ordering test."""

    id: UUID
    NAME: ClassVar[str] = "Parent"
    ENTITY: ClassVar[Entity | None] = None


class ChildModel(BaseModel):
    """Model linked to its parent in the entity-ordering test."""

    id: UUID
    parent_id: UUID | None = None
    NAME: ClassVar[str] = "Child"
    ENTITY: ClassVar[Entity | None] = None


def test_topological_sort_places_linked_entities_before_dependents() -> None:
    """Order linked entities before entities that depend on them."""
    parent = Entity(persistable=True).set_model_class(ParentModel)
    ParentModel.ENTITY = parent
    child = Entity(
        persistable=True,
        links={1: ("parent_id", ParentModel, None)},
    ).set_model_class(ChildModel)
    ChildModel.ENTITY = child

    assert Entity.topological_sort([child, parent], OnException.RAISE) == [
        parent,
        child,
    ]

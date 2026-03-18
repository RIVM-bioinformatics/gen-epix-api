# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later
from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.case.ref_data import (
    Protocol,
    TreeAlgorithm,
)
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity


class PhylogeneticTree(Model):
    """
    A phylogenetic tree, including a description of the leaves and how it was
    generated.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="phylogenetic_trees",
        persistable=False,
    )
    tree_algorithm_id: UUID | None = Field(
        default=None, description="The ID of the tree algorithm. FOREIGN KEY"
    )
    tree_algorithm: TreeAlgorithm | None = Field(
        default=None, description="The tree algorithm"
    )
    tree_algorithm_code: enum.TreeAlgorithmType = Field(
        description="The tree algorithm"
    )
    protocol_id: UUID | None = Field(
        default=None, description="The ID of the genetic distance protocol. FOREIGN KEY"
    )
    protocol: Protocol | None = Field(
        default=None, description="The genetic distance protocol"
    )
    leaf_ids: list[UUID] | None = Field(
        default=None,
        description="The list of unique identifiers of the leaves of the phylogenetic tree.",
    )
    profile_ids: list[UUID] | None = Field(
        default=None,
        description="The list of unique identifiers of the profile of each leaf of the phylogenetic tree.",
    )
    newick_repr: str = Field(
        description="The Newick representation of the phylogenetic tree."
    )

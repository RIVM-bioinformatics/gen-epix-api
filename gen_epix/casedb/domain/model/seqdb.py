# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_serializer

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.case.case import (
    GeneticDistanceProtocol,
    TreeAlgorithm,
)
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp import Entity


class GeneticSequence(Model):
    """
    A genetic sequence. Temporary implementation.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="genetic_sequences",
    )
    nucleotide_sequence: str | None = Field(
        default=None, description="The nucleotide sequence"
    )
    distances: dict[UUID, float] | None = Field(
        default=None, description="The distances to other sequences"
    )

    @field_serializer("distances", mode="plain")
    def _serialize_distances(
        self, value: dict[UUID, float] | None
    ) -> dict[str, float] | None:
        return None if value is None else {str(x): y for x, y in value.items()}


class AlleleProfile(Model):
    """
    An allele profile. Temporary implementation.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="allele_profiles",
    )
    # TODO: add link to sequence and gene set
    allele_profile: str | None = Field(default=None, description="The allele profile")


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
    tree_algorithm: TreeAlgorithm = Field(
        default=None, description="The tree algorithm"
    )
    tree_algorithm_code: enum.TreeAlgorithmType = Field(
        description="The tree algorithm"
    )
    genetic_distance_protocol_id: UUID | None = Field(
        default=None, description="The ID of the genetic distance protocol. FOREIGN KEY"
    )
    genetic_distance_protocol: GeneticDistanceProtocol = Field(
        default=None, description="The genetic distance protocol"
    )
    leaf_ids: list[UUID] | None = Field(
        default=None,
        description="The list of unique identifiers of the leaves of the phylogenetic tree.",
    )
    sequence_ids: list[UUID] | None = Field(
        default=None,
        description="The list of unique identifiers of the sequence of each leaf of the phylogenetic tree.",
    )
    newick_repr: str = Field(
        description="The Newick representation of the phylogenetic tree."
    )

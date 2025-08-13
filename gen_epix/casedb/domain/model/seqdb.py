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
from gen_epix.common.domain.model.base import Model
from gen_epix.fastapp import Entity

_SERVICE_TYPE = enum.ServiceType.SEQDB
_ENTITY_KWARGS = {
    "schema_name": _SERVICE_TYPE.value.lower(),
}


class GeneticSequence(Model):
    """
    A class representing a genetic sequence. Temporary implementation.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="genetic_sequences",
        table_name="genetic_sequence",  # TODO: temporarily added for extraction of seqdb demo data
        persistable=False,
        **_ENTITY_KWARGS,
    )
    nucleotide_sequence: str | None = Field(
        default=None, description="The nucleotide sequence"
    )
    distances: dict[UUID, float] | None = Field(
        default=None, description="The distances to other sequences"
    )

    @field_serializer("distances")
    def serialize_distances(self, value: dict[UUID, float], _info):
        return {str(x): y for x, y in value.items()}


class AlleleProfile(Model):
    """
    A class representing an allele profile. Temporary implementation.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="allele_profiles",
        **_ENTITY_KWARGS,
    )
    # TODO: add link to sequence and gene set
    allele_profile: str | None = Field(default=None, description="The allele profile")


class PhylogeneticTree(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="phylogenetic_trees",
        persistable=False,
        **_ENTITY_KWARGS,
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

from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model import Model
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.protocol import Protocol


class TreeAlgorithmClass(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="tree_algorithm_classes",
        table_name="tree_algorithm_class",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
    )
    code: str = Field(
        description="The code of the tree algorithm class", max_length=255
    )
    name: str = Field(
        description="The name of the tree algorithm class", max_length=255
    )
    is_seq_based: bool = Field(
        description="Whether the sequence or alignment is needed as input"
    )
    is_dist_based: bool = Field(
        description="Whether the distance between sequences is needed as input"
    )
    rank: int | None = Field(
        default=None,
        description="The rank of the tree algorithm class, if relevant.",
    )


class TreeAlgorithm(Model):
    """
    See https://en.wikipedia.org/wiki/Hierarchical_clustering,
    https://en.wikipedia.org/wiki/Neighbor_joining,
     https://en.wikipedia.org/wiki/Computational_phylogenetics,
     https://en.wikipedia.org/wiki/Spanning_tree
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="tree_algorithms",
        table_name="tree_algorithm",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        links=create_links(
            {
                1: (
                    "tree_algorithm_class_id",
                    TreeAlgorithmClass,
                    "tree_algorithm_class",
                ),
            }
        ),
    )
    code: enum.TreeAlgorithm = Field(description="The code of the tree algorithm")
    name: str = Field(description="The name of the tree algorithm", max_length=255)
    description: str | None = Field(
        default=None, description="The description of the tree algorithm"
    )
    tree_algorithm_class_id: UUID = Field(
        description="The ID of the tree algorithm class. FOREIGN KEY"
    )
    tree_algorithm_class: TreeAlgorithmClass | None = Field(
        default=None, description="The class of algorithm"
    )
    is_ultrametric: bool = Field(description="Whether the tree is ultrametric")
    rank: int | None = Field(
        default=None,
        description="The rank of the tree algorithm, if relevant.",
    )


# Non-persistable models


class PhylogeneticTree(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="phylogenetic_trees",
        persistable=False,
    )
    tree_algorithm: enum.TreeAlgorithm = Field(description="The tree algorithm")
    protocol_id: UUID = Field(description="The ID of the protocol. FOREIGN KEY")
    protocol: Protocol | None = Field(default=None, description="The protocol")
    leaf_names: list[str] | None = Field(
        default=None,
        description="The list of names of the leaves of the phylogenetic tree to be put in the tree representation instead of seq_ids. Must have the same length as seq_ids.",
    )
    profile_ids: list[UUID] | None = Field(
        default=None,
        description="The list of unique identifiers of the sequence of each leaf of the phylogenetic tree.",
    )
    newick_repr: str = Field(
        description="The Newick representation of the phylogenetic tree."
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if self.leaf_names:
            if len(set(self.leaf_names)) < len(self.leaf_names):
                raise ValueError("Duplicate leaf_codes")
        if self.profile_ids:
            if len(set(self.profile_ids)) < len(self.profile_ids):
                raise ValueError("Duplicate seq_ids")
            if self.leaf_names and len(self.profile_ids) != len(self.leaf_names):
                raise ValueError(
                    "seq_ids and leaf_codes must have the same length if leaf_codes is provided."
                )
        return self

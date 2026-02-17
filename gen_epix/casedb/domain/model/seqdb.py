# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later
from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_serializer

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.case.persistable import (
    GeneticDistanceProtocol,
    TreeAlgorithm,
)
from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.util import copy_model_field
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity
from gen_epix.fastapp.domain.util import create_keys, create_links
from gen_epix.seqdb.domain.model import AssemblyProtocol as SeqdbAssemblyProtocol
from gen_epix.seqdb.domain.model import File as SeqdbFile
from gen_epix.seqdb.domain.model import LibraryPrepProtocol as SeqdbLibraryPrepProtocol
from gen_epix.seqdb.domain.model import RawSeq as SeqdbRawSeq
from gen_epix.seqdb.domain.model import ReadSet as SeqdbReadSet
from gen_epix.seqdb.domain.model import Sample as SeqdbSample
from gen_epix.seqdb.domain.model import Seq as SeqdbSeq


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


class LibraryPrepProtocol(SeqdbLibraryPrepProtocol):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="library_prep_protocols",
        table_name="library_prep_protocol",
        persistable=False,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class File(SeqdbFile):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="files",
        table_name="file",
        persistable=False,
    )


class ReadSet(SeqdbReadSet):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="read_sets",
        table_name="read_set",
        persistable=False,
        keys=create_keys({1: "code"}),
        links=create_links(
            {
                1: (
                    "library_prep_protocol_id",
                    LibraryPrepProtocol,
                    "library_prep_protocol",
                ),
            }
        ),
    )
    library_prep_protocol: LibraryPrepProtocol | None = copy_model_field(
        SeqdbReadSet, "library_prep_protocol"
    )


class AssemblyProtocol(SeqdbAssemblyProtocol):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="assembly_protocols",
        table_name="assembly_protocol",
        persistable=False,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class RawSeq(SeqdbRawSeq):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="raw_seqs",
        table_name="raw_seq",
        persistable=False,
    )


class Sample(SeqdbSample):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="samples",
        table_name="sample",
        persistable=False,
        keys=create_keys({1: "code"}),
    )


class Seq(SeqdbSeq):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seqs",
        table_name="seq",
        persistable=False,
        keys=create_keys(
            {
                1: "code",
            }
        ),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("read_set_id", ReadSet, "read_set"),
                3: ("read_set2_id", ReadSet, "read_set2"),
                4: ("assembly_protocol_id", AssemblyProtocol, "assembly_protocol"),
                5: ("raw_seq_id", RawSeq, "raw_seq"),
            }
        ),
    )
    sample: Sample | None = copy_model_field(SeqdbSeq, "sample")
    read_set: ReadSet | None = copy_model_field(SeqdbSeq, "read_set")
    read_set2: ReadSet | None = copy_model_field(SeqdbSeq, "read_set2")
    assembly_protocol: AssemblyProtocol | None = copy_model_field(
        SeqdbSeq, "assembly_protocol"
    )
    raw_seq: RawSeq | None = copy_model_field(SeqdbSeq, "raw_seq")

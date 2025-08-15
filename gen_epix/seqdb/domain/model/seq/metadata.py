# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


import json
from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_serializer, field_validator

from gen_epix.common.domain.model import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import ProtocolMixin, SeqMixin

_SERVICE_TYPE = enum.ServiceType.SEQ
_ENTITY_KWARGS = {
    "service_type": _SERVICE_TYPE,
    "schema_name": _SERVICE_TYPE.value.lower(),
}


class TreeAlgorithmClass(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="tree_algorithm_classes",
        table_name="tree_algorithm_class",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        **_ENTITY_KWARGS,
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
        **_ENTITY_KWARGS,
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


class LibraryPrepProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="library_prep_protocols",
        table_name="library_prep_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
        **_ENTITY_KWARGS,
    )


class AssemblyProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="assembly_protocols",
        table_name="assembly_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
        **_ENTITY_KWARGS,
    )
    has_manual_curation: bool = Field(
        default=False,
        description="Whether the assembly has a, potentially optional, manual curation step.",
    )


class LocusDetectionProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_detection_protocols",
        table_name="locus_detection_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
        **_ENTITY_KWARGS,
    )


class SnpDetectionProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="snp_detection_protocols",
        table_name="snp_detection_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
        **_ENTITY_KWARGS,
    )


class KmerDetectionProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="kmer_detection_protocols",
        table_name="kmer_detection_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
        **_ENTITY_KWARGS,
    )


class AlignmentProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="alignment_protocols",
        table_name="alignment_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
        **_ENTITY_KWARGS,
    )
    is_multiple: bool = Field(
        description="Whether the alignment protocol can be used for more than two sequences"
    )


class TaxonomyProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxonomy_protocols",
        table_name="taxonomy_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
        **_ENTITY_KWARGS,
    )


class SeqClassificationProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_classification_protocols",
        table_name="seq_classification_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
        **_ENTITY_KWARGS,
    )
    is_taxonomic: bool = Field(
        description="Whether the category is based on phylogeny or not"
    )


class PcrProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="pcr_protocols",
        table_name="pcr_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
        **_ENTITY_KWARGS,
    )
    target_names: list[str]

    @field_validator("target_names", mode="before")
    def _validate_target_names(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            return json.loads(value)
        return value


class AstProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ast_protocols",
        table_name="ast_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
        **_ENTITY_KWARGS,
    )
    is_predicted: bool
    antimicrobial_names: list[str]

    @field_validator("antimicrobial_names", mode="before")
    def _validate_antimicrobial_names(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            return json.loads(value)
        return value


class SeqCategorySet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_category_sets",
        table_name="seq_category_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        **_ENTITY_KWARGS,
    )
    code: str = Field(description="The code of the category set", max_length=255)
    name: str = Field(description="The name of the category set", max_length=255)


class SeqCategory(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_categories",
        table_name="seq_category",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        links=create_links(
            {
                1: (
                    "seq_category_set_id",
                    SeqCategorySet,
                    "seq_category_set",
                )
            }
        ),
        **_ENTITY_KWARGS,
    )
    code: str = Field(description="The code of the category", max_length=255)
    name: str = Field(description="The name of the category", max_length=255)
    seq_category_set_id: UUID = Field(
        description="The ID of the sequence category set. FOREIGN KEY"
    )
    seq_category_set: SeqCategorySet = Field(description="The sequence category set")


class SubtypingScheme(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="subtyping_schemes",
        table_name="subtyping_scheme",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        **_ENTITY_KWARGS,
    )
    code: str = Field(description="The code of the subtyping scheme", max_length=255)
    name: str = Field(description="The name of the subtyping scheme", max_length=255)
    description: str | None = Field(
        default=None, description="The description of the subtyping scheme"
    )


class Taxon(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxa",
        table_name="taxon",
        persistable=True,
        keys=create_keys({1: "code"}),
        links=create_links(
            {
                1: ("subtyping_scheme_id", SubtypingScheme, "subtyping_scheme"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    code: str = Field(description="The code of the taxon", max_length=255)
    name: str = Field(description="The name of the taxon", max_length=255)
    rank: enum.TaxonRank = Field(description="The rank of the taxon")
    ncbi_taxid: int | None = Field(
        default=None, description="The NCBI Taxonomy ID of the taxon"
    )
    ictv_ictv_id: str | None = Field(
        default=None, description="The ICTV ID of the taxon", max_length=255
    )
    snomed_sctid: int | None = Field(
        default=None, description="The Snomed CT ID of the taxon"
    )
    subtyping_scheme_id: UUID | None = Field(
        default=None, description="The ID of the subtyping scheme, if any. FOREIGN KEY"
    )
    subtyping_scheme: SubtypingScheme | None = Field(
        default=None, description="The subtyping scheme"
    )
    ncbi_ancestor_taxids: list[int] | None = Field(
        default=None,
        description="The NCBI taxon IDs of the ancestors, sorted from highest to lowest rank",
    )
    ancestor_taxon_ids: list[UUID] = Field(
        description="The IDs of the ancestor taxa, sorted from highest to lowest rank"
    )

    @field_validator("ncbi_ancestor_taxids", mode="before")
    @classmethod
    def _validate_ncbi_ancestor_taxids(cls, value: list[int] | str) -> list[int]:
        if isinstance(value, str):
            return [int(x) for x in json.loads(value)]
        return value

    @field_validator("ancestor_taxon_ids", mode="before")
    @classmethod
    def _validate_ancestor_taxon_ids(cls, value: list[UUID] | str) -> list[UUID]:
        if isinstance(value, str):
            return [UUID(x) for x in json.loads(value)]
        return value

    @field_serializer("ancestor_taxon_ids")
    def serialize_ancestor_taxon_ids(self, value: list[UUID], _info):
        return [str(x) for x in value]


class TaxonSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxon_sets",
        table_name="taxon_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        **_ENTITY_KWARGS,
    )
    code: str = Field(description="The code of the taxon set", max_length=255)
    name: str = Field(description="The name of the taxon set", max_length=255)


class TaxonSetMember(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxon_set_members",
        table_name="taxon_set_member",
        persistable=True,
        keys=create_keys({1: "taxon_set_id", 2: "taxon_id"}),
        links=create_links(
            {
                1: ("taxon_set_id", TaxonSet, "taxon_set"),
                2: ("taxon_id", Taxon, "taxon"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    taxon_set_id: UUID = Field(description="The ID of the taxon set. FOREIGN KEY")
    taxon_set: TaxonSet
    taxon_id: UUID = Field(description="The ID of the taxon. FOREIGN KEY")
    taxon: Taxon


class Locus(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="loci",
        table_name="locus",
        persistable=True,
        keys=create_keys({1: "code"}),
        **_ENTITY_KWARGS,
    )
    code: str = Field(description="The code of the locus.", max_length=255)
    gene_code: str | None = Field(
        default=None,
        description="The code of the gene, if the locus corresponds to one and a code is available.",
        max_length=255,
    )
    product_name: str | None = Field(
        default=None,
        description="The name of the gene product, if available.",
        max_length=255,
    )


class LocusSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_sets",
        table_name="locus_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        **_ENTITY_KWARGS,
    )
    code: str = Field(description="The code of the locus set.", max_length=255)
    name: str = Field(description="The name of the locus set.", max_length=255)
    n_loci: int = Field(description="The number of loci in the locus set.")
    locus_ids: list[UUID] = Field(
        description="The ordered IDs of the loci in the locus set."
    )

    @field_validator("locus_ids", mode="before")
    @classmethod
    def _validate_locus_ids(cls, value: list[UUID] | str) -> list[UUID]:
        """
        Validate and convert locus_ids representation to a list[UUID]. When given as a
        string, it is assumed to be a JSON list of UUID string representations.
        """
        if isinstance(value, str):
            return [UUID(x) for x in json.loads(value)]
        return value

    @field_serializer("locus_ids")
    def serialize_locus_ids(self, value: list[UUID], _info):
        return [str(x) for x in value]


class LocusSetMember(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_set_members",
        table_name="locus_set_member",
        persistable=True,
        keys=create_keys({1: ("locus_set_id", "locus_id")}),
        links=create_links(
            {
                1: ("locus_set_id", LocusSet, "locus_set"),
                2: ("locus_id", Locus, "locus"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    locus_set_id: UUID = Field(
        description="The unique identifier for the locus set. FOREIGN KEY"
    )
    locus_set: LocusSet | None = Field(default=None, description="The locus set.")
    locus_id: UUID = Field(
        description="The unique identifier for the locus. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")
    index: int = Field(
        description="The index (ordinal number) of the locus in the locus set."
    )


class TaxonLocusLink(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxon_locus_links",
        table_name="taxon_locus_link",
        persistable=True,
        keys=create_keys({1: ("taxon_id", "locus_id")}),
        links=create_links(
            {1: ("taxon_id", Taxon, "taxon"), 2: ("locus_id", Locus, "locus")}
        ),
        **_ENTITY_KWARGS,
    )
    taxon_id: UUID = Field(
        description="The unique identifier for the taxon. FOREIGN KEY"
    )
    taxon: Taxon | None = Field(default=None, description="The taxon.")
    locus_id: UUID = Field(
        description="The unique identifier for the locus. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")


class RefSeq(Model, SeqMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_seqs",
        table_name="ref_seq",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        links=create_links({1: ("taxon_id", Taxon, "taxon")}),
        **_ENTITY_KWARGS,
    )
    code: str = Field(description="The code of the reference sequence", max_length=255)
    name: str = Field(description="The name of the reference sequence", max_length=255)
    description: str | None = Field(
        default=None, description="The description of the reference sequence"
    )
    taxon_id: UUID = Field(description="The ID of the taxon. FOREIGN KEY")
    taxon: Taxon | None = Field(default=None, description="The taxon")
    genbank_accession_code: str | None = Field(
        default=None,
        description="The GenBank accession code of the reference sequence",
        max_length=255,
    )


class RefAllele(Model, SeqMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_alleles",
        table_name="ref_allele",
        persistable=True,
        keys=create_keys({1: ("locus_id", "index")}),
        links=create_links({1: ("locus_id", Locus, "locus")}),
        **_ENTITY_KWARGS,
    )
    locus_id: UUID = Field(
        description="The unique identifier for the locus. FOREIGN KEY"
    )
    locus: Locus | None = Field(default=None, description="The locus.")
    index: int = Field(
        description="The index (ordinal number) of the reference allele for the locus."
    )


class RefSnp(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_snps",
        table_name="ref_snp",
        persistable=True,
        keys=create_keys({1: "code", 2: ("ref_seq_id", "position", "nucleotide")}),
        links=create_links({1: ("ref_seq_id", RefSeq, "ref_seq")}),
        **_ENTITY_KWARGS,
    )
    code: str = Field(description="The code of the reference SNP.", max_length=255)
    ref_seq_id: UUID = Field(
        description="The unique identifier for the reference sequence. FOREIGN KEY"
    )
    ref_seq: RefSeq | None = Field(default=None, description="The reference sequence.")
    position: int = Field(description="The position of the reference SNP.")
    nucleotide: str = Field(
        description="The nucleotide of the reference SNP.", min_length=1, max_length=1
    )


class RefSnpSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_snp_sets",
        table_name="ref_snp_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        **_ENTITY_KWARGS,
    )
    code: str = Field(description="The code of the reference SNP set.", max_length=255)
    name: str = Field(description="The name of the reference SNP set.", max_length=255)


class RefSnpSetMember(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ref_snp_set_members",
        table_name="ref_snp_set_member",
        persistable=True,
        keys=create_keys(
            {
                1: ("ref_snp_set_id", "ref_snp_id"),
                2: ("ref_snp_set_id", "index"),
            }
        ),
        links=create_links(
            {
                1: ("ref_snp_set_id", RefSnpSet, "ref_snp_set"),
                2: ("ref_snp_id", RefSnp, "ref_snp"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    ref_snp_set_id: UUID = Field(
        description="The unique identifier for the reference SNP set. FOREIGN KEY"
    )
    ref_snp_set: RefSnpSet | None = Field(
        default=None, description="The reference SNP set."
    )
    ref_snp_id: UUID = Field(
        description="The unique identifier for the reference SNP. FOREIGN KEY"
    )
    ref_snp: RefSnp | None = Field(default=None, description="The reference SNP.")
    index: int = Field(
        description="The index (ordinal number) of the reference SNP in the reference SNP set."
    )

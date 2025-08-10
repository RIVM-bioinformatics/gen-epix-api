from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.common.domain.model import Model
from gen_epix.fastapp import Entity
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.metadata import RefSnp
from gen_epix.seqdb.domain.model.seq.persistable import (
    AstMeasurement,
    AstPrediction,
    PcrMeasurement,
    ReadSet,
    SeqClassification,
    SeqDistanceProtocol,
    SeqTaxonomy,
)

_SERVICE_TYPE = enum.ServiceType.SEQ
_ENTITY_KWARGS = {
    "service_type": _SERVICE_TYPE,
    "schema_name": _SERVICE_TYPE.value.lower(),
}


class CompleteContig(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_contigs",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    seq_id: UUID
    seq: str
    qc: enum.QualityControlResult
    index: int


class CompleteAlleleProfile(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_allele_profiles",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    seq_id: UUID
    locus_set_id: UUID
    locus_ids: list[UUID]
    allele_ids: list[UUID | None]
    multiple_allele_ids: dict[UUID, list[UUID]]
    allele_count_by_qc: dict[enum.QualityControlResult, int]


class CompleteSnpProfile(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_snp_profiles",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    seq_id: UUID
    ref_snps: list[RefSnp]
    snps: str
    snp_profile: str
    snp_profile_format: enum.SnpProfileFormat


class CompleteSeq(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_seqs",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    sample_id: UUID | None
    primary_taxon_id: UUID | None
    read_sets: list[ReadSet] | None
    contigs: list[CompleteContig] | None
    allele_profiles: list[CompleteAlleleProfile] | None
    snp_profiles: list[CompleteSnpProfile] | None
    taxa: list[SeqTaxonomy] | None
    ast_predictions: list[AstPrediction] | None
    classifications: list[SeqClassification] | None
    qc: enum.QualityControlResult | None


class CompleteSample(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_samples",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    primary_seq_id: UUID | None
    primary_taxon_id: UUID | None
    seqs: list[CompleteSeq] | None
    pcr_measurements: list[PcrMeasurement] | None
    ast_measurements: list[AstMeasurement] | None


class PhylogeneticTree(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="phylogenetic_trees",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    tree_algorithm: enum.TreeAlgorithm = Field(
        default=None, description="The tree algorithm"
    )
    seq_distance_protocol_id: UUID = Field(
        description="The ID of the sequence distance protocol. FOREIGN KEY"
    )
    seq_distance_protocol: SeqDistanceProtocol = Field(
        default=None, description="The sequence distance protocol"
    )
    leaf_names: list[str] | None = Field(
        default=None,
        description="The list of names of the leaves of the phylogenetic tree to be put in the tree representation instead of seq_ids. Must have the same length as seq_ids.",
    )
    seq_ids: list[UUID] | None = Field(
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
        if self.seq_ids:
            if len(set(self.seq_ids)) < len(self.seq_ids):
                raise ValueError("Duplicate seq_ids")
            if self.leaf_names and len(self.seq_ids) != len(self.leaf_names):
                raise ValueError(
                    "seq_ids and leaf_codes must have the same length if leaf_codes is provided."
                )
        return self


class MultipleAlignment(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="multiple_alignments",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    alignment_protocol_id: UUID
    seq_ids: list[UUID]
    n_seqs: int
    n_contigs: list[int]
    contig_seqs: list[list[str]]
    n_alignments: int
    n_columns: list[int]
    start_columns: list[list[int]]
    contig_ordinals: list[list[int]]
    contig_start_positions: list[list[int]]
    contig_directions: list[list[bool]]
    lengths: list[list[int]]

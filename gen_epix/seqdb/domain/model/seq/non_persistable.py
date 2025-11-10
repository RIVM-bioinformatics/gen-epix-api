from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model import Model
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


class CompleteContig(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_contigs",
        persistable=False,
    )
    seq_id: UUID = Field(description="The ID of the sequence.")
    seq: str = Field(description="The contig sequence.")
    qc: enum.QualityControlResult = Field(
        description="The quality control result of the contig sequence."
    )
    index: int = Field(description="The index of the contig in the sequence.")


class CompleteAlleleProfile(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_allele_profiles",
        persistable=False,
    )
    seq_id: UUID = Field(description="The ID of the sequence.")
    locus_set_id: UUID = Field(description="The ID of the locus set.")
    locus_ids: list[UUID] = Field(description="The IDs of the loci.")
    allele_ids: list[UUID | None] = Field(
        description="The IDs of the alleles for each locus."
    )
    multiple_allele_ids: dict[UUID, list[UUID]] = Field(
        description="Mapping of locus ID to multiple allele IDs."
    )
    allele_count_by_qc: dict[enum.QualityControlResult, int] = Field(
        description="Mapping of quality control result to allele count."
    )


class CompleteSnpProfile(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_snp_profiles",
        persistable=False,
    )
    seq_id: UUID = Field(description="The ID of the sequence.")
    ref_snps: list[RefSnp] = Field(description="The list of reference SNPs.")
    snps: str = Field(description="The SNPs in the profile.")
    snp_profile: str = Field(description="The SNP profile string.")
    snp_profile_format: enum.SnpProfileFormat = Field(
        description="The format of the SNP profile."
    )


class CompleteSeq(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_seqs",
        persistable=False,
    )
    sample_id: UUID | None = Field(default=None, description="The ID of the sample.")
    primary_taxon_id: UUID | None = Field(
        default=None, description="The ID of the primary taxon."
    )
    read_sets: list[ReadSet] | None = Field(
        default=None, description="The list of read sets associated with the sequence."
    )
    contigs: list[CompleteContig] | None = Field(
        default=None, description="The list of contigs associated with the sequence."
    )
    allele_profiles: list[CompleteAlleleProfile] | None = Field(
        default=None,
        description="The list of allele profiles associated with the sequence.",
    )
    snp_profiles: list[CompleteSnpProfile] | None = Field(
        default=None,
        description="The list of SNP profiles associated with the sequence.",
    )
    taxa: list[SeqTaxonomy] | None = Field(
        default=None, description="The list of taxonomies associated with the sequence."
    )
    ast_predictions: list[AstPrediction] | None = Field(
        default=None,
        description="The list of AST predictions associated with the sequence.",
    )
    classifications: list[SeqClassification] | None = Field(
        default=None,
        description="The list of classifications associated with the sequence.",
    )
    qc: enum.QualityControlResult | None = Field(
        default=None, description="The quality control result of the sequence."
    )


class CompleteSample(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_samples",
        persistable=False,
    )
    primary_seq_id: UUID | None = Field(
        default=None, description="The ID of the primary sequence."
    )
    primary_taxon_id: UUID | None = Field(
        default=None, description="The ID of the primary taxon."
    )
    seqs: list[CompleteSeq] | None = Field(
        default=None, description="The list of sequences associated with the sample."
    )
    pcr_measurements: list[PcrMeasurement] | None = Field(
        default=None,
        description="The list of PCR measurements associated with the sample.",
    )
    ast_measurements: list[AstMeasurement] | None = Field(
        default=None,
        description="The list of AST measurements associated with the sample.",
    )


class PhylogeneticTree(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="phylogenetic_trees",
        persistable=False,
    )
    tree_algorithm: enum.TreeAlgorithm = Field(description="The tree algorithm")
    seq_distance_protocol_id: UUID = Field(
        description="The ID of the sequence distance protocol. FOREIGN KEY"
    )
    seq_distance_protocol: SeqDistanceProtocol | None = Field(
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
    )
    alignment_protocol_id: UUID = Field(
        description="The ID of the alignment protocol. FOREIGN KEY"
    )
    seq_ids: list[UUID] = Field(
        description="The list of sequence IDs included in the multiple alignment."
    )
    n_seqs: int = Field(description="The number of sequences in the alignment.")
    n_contigs: list[int] = Field(
        description="The number of contigs for each sequence in the alignment."
    )
    contig_seqs: list[list[str]] = Field(
        description="The list of contig sequences for each sequence in the alignment."
    )
    n_alignments: int = Field(description="The number of alignments.")
    n_columns: list[int] = Field(
        description="The number of columns for each alignment."
    )
    start_columns: list[list[int]] = Field(
        description="The start column positions for each alignment."
    )
    contig_ordinals: list[list[int]] = Field(
        description="The ordinals of the contigs for each sequence in the alignment."
    )
    contig_start_positions: list[list[int]] = Field(
        description="The start positions of the contigs for each sequence in the alignment."
    )
    contig_directions: list[list[bool]] = Field(
        description="The directions of the contigs for each sequence in the alignment."
    )
    lengths: list[list[int]] = Field(
        description="The lengths of the contigs for each sequence in the alignment."
    )

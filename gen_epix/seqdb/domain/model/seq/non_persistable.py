from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model import Model
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.classification import (
    AstPrediction,
    SeqClassification,
    SeqTaxonomy,
)
from gen_epix.seqdb.domain.model.seq.pheno import AstMeasurement, PcrMeasurement
from gen_epix.seqdb.domain.model.seq.profile import (
    CompleteAlleleProfile,
    CompleteSnpProfile,
)
from gen_epix.seqdb.domain.model.seq.reads import ReadSet
from gen_epix.seqdb.domain.model.seq.seq import CompleteContig


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

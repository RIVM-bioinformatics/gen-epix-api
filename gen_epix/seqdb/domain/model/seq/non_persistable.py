from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.util import copy_model_field
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.classification import (
    AstPrediction,
    SeqClassification,
    SeqTaxonomy,
)
from gen_epix.seqdb.domain.model.seq.distance import SeqDistance
from gen_epix.seqdb.domain.model.seq.pheno import AstMeasurement, PcrMeasurement
from gen_epix.seqdb.domain.model.seq.profile import (
    AlleleProfile,
    CompleteAlleleProfile,
    CompleteSnpProfile,
    KmerProfile,
    LocusProfile,
    MlvaProfile,
    SnpProfile,
)
from gen_epix.seqdb.domain.model.seq.reads import ReadSet
from gen_epix.seqdb.domain.model.seq.sample import Sample, SampleIdentifier
from gen_epix.seqdb.domain.model.seq.seq import CompleteContig, Seq


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


class ExternalSampleIdentifier(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="external_sample_identifiers",
        persistable=False,
    )
    identifier: str = copy_model_field(SampleIdentifier, "identifier")
    identifier_issuer_id: UUID = copy_model_field(
        SampleIdentifier, "identifier_issuer_id"
    )


class CompleteSample(Sample):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_samples",
        persistable=False,
    )
    NAME = "CompleteSample"
    sample_identifiers: list[ExternalSampleIdentifier] | None = Field(
        default=None,
        description="The list of external identifiers associated with the sample. Empty list if none exist, None if not set.",
    )
    data_collection_ids: list[UUID] | None = Field(
        default=None,
        description="The list of data collection IDs associated with the sample, limited to those that the user has or should have the appropriate access rights to. Empty list if none exist, None if not set.",
    )
    read_sets: list[ReadSet] | None = Field(
        default=None,
        description="The list of read sets associated with the sample. Empty list if none exist, None if not set.",
    )
    seqs: list[Seq] | None = Field(
        default=None,
        description="The list of sequences associated with the sample. Empty list if none exist, None if not set.",
    )
    seq_taxonomies: list[SeqTaxonomy] | None = Field(
        default=None,
        description="The list of taxonomies associated with the sample. Empty list if none exist, None if not set.",
    )
    seq_classifications: list[SeqClassification] | None = Field(
        default=None,
        description="The list of classifications associated with the sample. Empty list if none exist, None if not set.",
    )
    locus_profiles: list[LocusProfile] | None = Field(
        default=None,
        description="The list of locus profiles associated with the sample. Empty list if none exist, None if not set.",
    )
    allele_profiles: list[AlleleProfile] | None = Field(
        default=None,
        description="The list of allele profiles associated with the sample. Empty list if none exist, None if not set.",
    )
    snp_profiles: list[SnpProfile] | None = Field(
        default=None,
        description="The list of SNP profiles associated with the sample. Empty list if none exist, None if not set.",
    )
    mlva_profiles: list[MlvaProfile] | None = Field(
        default=None,
        description="The list of MLVA profiles associated with the sample. Empty list if none exist, None if not set.",
    )
    kmer_profiles: list[KmerProfile] | None = Field(
        default=None,
        description="The list of k-mer profiles associated with the sample. Empty list if none exist, None if not set.",
    )
    distances: list[SeqDistance] | None = Field(
        default=None,
        description="The list of genetic distances associated with the sample. Empty list if none exist, None if not set.",
    )
    pcr_measurements: list[PcrMeasurement] | None = Field(
        default=None,
        description="The list of PCR measurements associated with the sample. Empty list if none exist, None if not set.",
    )
    ast_measurements: list[AstMeasurement] | None = Field(
        default=None,
        description="The list of AST measurements associated with the sample. Empty list if none exist, None if not set.",
    )

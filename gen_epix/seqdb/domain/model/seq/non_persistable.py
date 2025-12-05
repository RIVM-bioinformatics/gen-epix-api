from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.util import copy_model_field
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity
from gen_epix.seqdb.domain.model.seq.classification import (
    SeqClassification,
    SeqTaxonomy,
)
from gen_epix.seqdb.domain.model.seq.distance import SeqDistance
from gen_epix.seqdb.domain.model.seq.pheno import AstMeasurement, PcrMeasurement
from gen_epix.seqdb.domain.model.seq.profile import (
    AlleleProfile,
    KmerProfile,
    LocusProfile,
    MlvaProfile,
    SnpProfile,
)
from gen_epix.seqdb.domain.model.seq.reads import ReadSet
from gen_epix.seqdb.domain.model.seq.sample import Sample, SampleIdentifier
from gen_epix.seqdb.domain.model.seq.seq import Seq


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
    NULL_SAMPLE_ID: ClassVar[UUID] = UUID("00000000-0000-0000-0000-000000000000")
    RESULT_FIELD_NAMES: ClassVar[list[str]] = [
        "read_sets",
        "seqs",
        "seq_taxonomies",
        "seq_classifications",
        "locus_profiles",
        "allele_profiles",
        "snp_profiles",
        "mlva_profiles",
        "kmer_profiles",
        "distances",
        "pcr_measurements",
        "ast_measurements",
    ]

    is_existing_sample: bool = Field(
        description="Indicates whether the sample already exists in the database.",
    )
    sample_identifiers: list[ExternalSampleIdentifier] | None = Field(
        default=None,
        description="The list of external identifiers associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    data_collection_ids: list[UUID] | None = Field(
        default=None,
        description="The list of data collection IDs associated with the sample, limited to those that the user has or should have the appropriate access rights to. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    read_sets: list[ReadSet] | None = Field(
        default=None,
        description="The list of read sets associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id. If not is_existing_sample, the sample_id is to be filled with the null ",
    )
    seqs: list[Seq] | None = Field(
        default=None,
        description="The list of sequences associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    seq_taxonomies: list[SeqTaxonomy] | None = Field(
        default=None,
        description="The list of taxonomies associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    seq_classifications: list[SeqClassification] | None = Field(
        default=None,
        description="The list of classifications associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    locus_profiles: list[LocusProfile] | None = Field(
        default=None,
        description="The list of locus profiles associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    allele_profiles: list[AlleleProfile] | None = Field(
        default=None,
        description="The list of allele profiles associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    snp_profiles: list[SnpProfile] | None = Field(
        default=None,
        description="The list of SNP profiles associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    mlva_profiles: list[MlvaProfile] | None = Field(
        default=None,
        description="The list of MLVA profiles associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    kmer_profiles: list[KmerProfile] | None = Field(
        default=None,
        description="The list of k-mer profiles associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    distances: list[SeqDistance] | None = Field(
        default=None,
        description="The list of genetic distances associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    pcr_measurements: list[PcrMeasurement] | None = Field(
        default=None,
        description="The list of PCR measurements associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )
    ast_measurements: list[AstMeasurement] | None = Field(
        default=None,
        description="The list of AST measurements associated with the sample. If not is_existing_sample: can be None, indicating none provided; if not None then the sample_id property of each element may be the null sample_id.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        if self.is_existing_sample:
            if self.id == CompleteSample.NULL_SAMPLE_ID:
                raise ValueError(
                    "For existing samples, id cannot be the null sample ID."
                )
        else:
            if self.id is not None and self.id != CompleteSample.NULL_SAMPLE_ID:
                raise ValueError(
                    "For not existing samples, id must be the null sample ID or None."
                )
        if not self.is_existing_sample:
            for field_name in self.RESULT_FIELD_NAMES:
                items = getattr(self, field_name)
                for item in items or []:
                    if item.sample_id not in (None, CompleteSample.NULL_SAMPLE_ID):
                        raise ValueError(
                            f"For not existing samples, sample_id of {field_name} items must be None or the null sample ID."
                        )
        return self

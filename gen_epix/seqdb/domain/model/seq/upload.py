from collections.abc import Hashable
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, computed_field, field_validator, model_validator

from gen_epix.commondb.domain.literal import MAX_CODE_FIELD_LENGTH, NULL_ID
from gen_epix.commondb.domain.model.base import BaseBatchForUpload, UploadResult
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
from gen_epix.fastapp.domain import Entity
from gen_epix.seqdb.domain.model.seq.classification import (
    SeqClassification,
    SeqTaxonomy,
)
from gen_epix.seqdb.domain.model.seq.distance import SeqDistance
from gen_epix.seqdb.domain.model.seq.locus import Allele
from gen_epix.seqdb.domain.model.seq.pheno import AstMeasurement, PcrMeasurement
from gen_epix.seqdb.domain.model.seq.profile import (
    AlleleProfile,
    KmerProfile,
    LocusProfile,
    MlvaProfile,
    SnpProfile,
)
from gen_epix.seqdb.domain.model.seq.reads import ReadSet
from gen_epix.seqdb.domain.model.seq.sample import Sample
from gen_epix.seqdb.domain.model.seq.seq import Seq


class ReadSetForUpload(ReadSet):
    """
    A read set intended for upload.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "ReadSetForUpload"

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the read set is associated with. If not available, the null ID is put.",
    )


class SeqForUpload(Seq):
    """
    A sequence intended for upload.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "SeqForUpload"

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the sequence is associated with. If not available, the null ID is put.",
    )


class AlleleForUpload(Allele):
    """
    An allele intended for upload. Equal to an Allele, with
    additional variables.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "AlleleForUpload"

    locus_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the locus, if available. Must be present if locus_code is not present. "
        "If not available, the null ID is put. The use of locus_id is preferred over locus_code "
        "since the latter may change and implies an additional mapping step.",
    )
    locus_code: str | None = Field(
        default=None,
        description="The external code of the locus, to be mapped to locus_id through a LocusCodeMap "
        "supplied elsewhere. Must be present if locus_id is not present. The use of locus_code "
        "is meant for situations where the locus_id is not known, but the code is.",
        max_length=MAX_CODE_FIELD_LENGTH,
    )

    @model_validator(mode="after")
    def _validate_locus_reference(self) -> Self:
        """Ensure that either locus_code or locus_id is set."""
        if self.locus_code is None and self.locus_id == NULL_ID:
            raise ValueError("Either 'locus_code' or 'locus_id' must be provided.")
        return self


class AlleleProfileForUpload(AlleleProfile):
    """
    An allele profile record intended for upload. Equal to an AlleleProfile, with
    additional variables.
    """

    ENTITY: ClassVar[Entity] = Entity(persistable=False)
    NAME: ClassVar = "AlleleProfileForUpload"

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the allele profile is associated with. If not available, the null ID is put.",
    )
    seq_id: UUID | None = Field(
        default=None,
        description="The UUID of the sequence that the allele profile was derived from, if available.",
    )
    locus_detection_protocol_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the locus detection protocol, if available. If not available, the null ID is put. Must be present if locus_detection_protocol_code is not present. The use of locus_detection_protocol_id is preferred over locus_detection_protocol_code since the latter may change.",
    )
    locus_detection_protocol_code: str | None = Field(
        default=None,
        description="The code of the locus detection protocol. Must be present if locus_detection_protocol_id is not present. The use of locus_detection_protocol_code is meant for situations where the locus_detection_protocol_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )
    locus_set_id: UUID = Field(
        default=NULL_ID,
        description="UUID of the locus set, if available. If not available, the null ID is put. Must be present if locus_set_code is not present. The use of locus_set_id is preferred over locus_set_code since the latter may change.",
    )
    locus_set_code: str | None = Field(
        default=None,
        description="The code of the locus set. Must be present if locus_set_id is not present. The use of locus_set_code is meant for situations where the locus_set_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )
    locus_code_map_id: UUID = Field(
        default=NULL_ID,
        description="The id of the locus code map that has to be used to map locus codes to locus IDs, if available. Must be provided if locus_code_map_code is not provided and any alleles have locus_code filled in. The use of locus_code_map_id is preferred over locus_code_map_code since the latter may change.",
    )
    locus_code_map_code: str | None = Field(
        default=None,
        description="The code of the locus code map that has to be used to map locus codes to locus IDs, if available. Must be provided if locus_code_map_id is not provided and any alleles have locus_code filled in. The use of locus_code_map_code is meant for situations where the locus_code_map_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )
    allele_profile: str = Field(
        default="",
        description="The allele profile as a string representation, e.g. a comma-separated list of allele codes or ids, in the order defined by the locus set. Must be present if alleles and locus_allele_id_map are not provided: these 3 properties are different representations of the same data that can be chosen between.",
    )
    alleles: list[AlleleForUpload] | None = Field(
        default=None,
        description="List of all alleles detected for this sample and for the loci within the locus set, in any order. Must be present if allele_profile and locus_allele_id_map are not provided: these 3 properties are different representations of the same data that can be chosen between.",
    )
    locus_allele_id_map: dict[str, UUID] | None = Field(
        default=None,
        description="A mapping from locus codes to allele ids, which are the hashes of the allele sequence, for all detected loci, in any order and if available. Must be present if allele_profile and alleles are not provided: these 3 properties are different representations of the same data that can be chosen between.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Override parent validation for upload format to handle alleles and locus_allele_id_map.
        """
        # Check if we're using upload-specific formats
        using_alleles = self.alleles is not None
        using_locus_allele_id_map = self.locus_allele_id_map is not None
        using_allele_profile_string = self.allele_profile != ""

        if (
            using_allele_profile_string
            and not using_alleles
            and not using_locus_allele_id_map
        ):
            # Use parent validation for allele_profile string format
            super()._validate_model()
        else:
            # For upload formats with alleles/locus_allele_id_map, set defaults
            if self.allele_profile_hash == NULL_ID:
                # Set a placeholder hash since we can't calculate it from alleles/map
                from uuid import uuid4

                self.allele_profile_hash = uuid4()

        # Upload-specific validation
        if (
            not self.locus_detection_protocol_code
            and self.locus_detection_protocol_id == NULL_ID
        ):
            raise ValueError(
                "Either locus_detection_protocol_code or locus_detection_protocol_id must be provided."
            )
        if self.locus_set_code is None and self.locus_set_id == NULL_ID:
            raise ValueError("Either locus_set_code or locus_set_id must be provided.")
        if self.locus_code_map_id == NULL_ID and self.locus_code_map_code is None:
            for allele in self.alleles or []:
                if allele.locus_code is not None:
                    raise ValueError(
                        "Either locus_code_map_id or locus_code_map_code must be provided when alleles contain locus_code."
                    )
            if self.locus_allele_id_map is not None:
                raise ValueError(
                    "Either locus_code_map_id or locus_code_map_code must be provided when locus_allele_id_map is provided."
                )
        n_profiles = sum(
            [
                self.allele_profile != "",
                self.alleles is not None,
                self.locus_allele_id_map is not None,
            ]
        )
        if n_profiles != 1:
            raise ValueError(
                "Exactly one of allele_profile, alleles, or locus_allele_id_map must be provided."
            )
        return self


class SampleForUpload(Sample):
    """
    A sample intended for upload, together with any relevant associated data.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME = "SampleForUpload"
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

    # Sample level data
    external_ids: list[ExternalIdentifierForUpload] | None = Field(
        default=None,
        description="The external identifiers associated with the sample, if available.",
    )

    # Associated data
    read_sets: list[ReadSetForUpload] | None = Field(
        default=None,
        description="The read sets associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    seqs: list[SeqForUpload] | None = Field(
        default=None,
        description="The sequences associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    seq_taxonomies: list[SeqTaxonomy] | None = Field(
        default=None,
        description="The taxonomies associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    seq_classifications: list[SeqClassification] | None = Field(
        default=None,
        description="The classifications associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    locus_profiles: list[LocusProfile] | None = Field(
        default=None,
        description="The locus profiles associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    allele_profiles: list[AlleleProfileForUpload] | None = Field(
        default=None,
        description="The allele profiles associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    snp_profiles: list[SnpProfile] | None = Field(
        default=None,
        description="The SNP profiles associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    mlva_profiles: list[MlvaProfile] | None = Field(
        default=None,
        description="The MLVA profiles associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    kmer_profiles: list[KmerProfile] | None = Field(
        default=None,
        description="The k-mer profiles associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    distances: list[SeqDistance] | None = Field(
        default=None,
        description="The genetic distances associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    pcr_measurements: list[PcrMeasurement] | None = Field(
        default=None,
        description="The PCR measurements associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    ast_measurements: list[AstMeasurement] | None = Field(
        default=None,
        description="The AST measurements associated with the sample. If None, this element is not taken into consideration during the upload.",
    )

    @field_validator("external_ids", mode="after")
    def _validate_associated_ids(
        cls, value: list[Hashable] | None
    ) -> list[Hashable] | None:
        if value is None:
            return None
        if len(set(value)) != len(value):
            raise ValueError("Associated IDs must be unique.")
        return value

    @model_validator(mode="after")
    def _validate_sample_for_upload(self) -> Self:
        # Verify that external_ids contains no duplicates
        if self.external_ids is not None and len(self.external_ids) != len(
            set(self.external_ids)
        ):
            raise ValueError("external_ids must not contain duplicates.")
        # TODO: verify that each list of results is unique, e.g. no identical read sets
        # Verify that result sample_ids are consistent with sample id
        # If sample has an ID, then associated items must have NULL_ID or the same sample_id
        # If sample has NULL_ID, then associated items can have any sample_id
        if self.id is not None and self.id != NULL_ID:
            sample_id = self.id
            for field_name in self.RESULT_FIELD_NAMES:
                items = getattr(self, field_name)
                for item in items or []:
                    if item.sample_id != NULL_ID and item.sample_id != sample_id:
                        raise ValueError(
                            f"sample_id of {field_name} must be NULL_ID or match the sample's ID when sample has an ID."
                        )
        return self


class SampleUploadResult(UploadResult):
    """
    The result of uploading a single sample.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "SampleUploadResult"

    RESULT_FIELD_NAMES: ClassVar[list[str]] = [
        "sample_result",
    ]
    RESULT_LIST_FIELD_NAMES: ClassVar[list[str]] = [
        "external_id_results",
        "data_collection_id_results",
        "read_set_results",
        "seq_results",
        "seq_taxonomy_results",
        "seq_classification_results",
        "locus_profile_results",
        "allele_profile_results",
        "snp_profile_results",
        "mlva_profile_results",
        "kmer_profile_results",
        "distance_results",
        "pcr_measurement_results",
        "ast_measurement_results",
    ]

    sample_result: UploadResult | None = Field(
        default=None,
        description="The result of uploading the sample itself.",
    )
    external_id_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the external identifiers associated with the sample, if any were provided, in the same order as provided.",
    )
    read_set_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the read sets associated with the sample, if any were provided, in the same order as provided.",
    )
    seq_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the sequences associated with the sample, if any were provided, in the same order as provided.",
    )
    seq_taxonomy_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the seq taxonomies associated with the sample, if any were provided, in the same order as provided.",
    )
    seq_classification_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the seq classifications associated with the sample, if any were provided, in the same order as provided.",
    )
    locus_profile_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the locus profiles associated with the sample, if any were provided, in the same order as provided.",
    )
    allele_profile_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the allele profiles associated with the sample, if any were provided, in the same order as provided.",
    )
    snp_profile_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the SNP profiles associated with the sample, if any were provided, in the same order as provided.",
    )
    mlva_profile_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the MLVA profiles associated with the sample, if any were provided, in the same order as provided.",
    )
    kmer_profile_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the k-mer profiles associated with the sample, if any were provided, in the same order as provided.",
    )
    distance_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the genetic distances associated with the sample, if any were provided, in the same order as provided.",
    )
    pcr_measurement_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the PCR measurements associated with the sample, if any were provided, in the same order as provided.",
    )
    ast_measurement_results: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the AST measurements associated with the sample, if any were provided, in the same order as provided.",
    )


class SampleBatchForUpload(BaseBatchForUpload):
    """
    A set of samples intended for upload, together with any new reference data required
    for the storage of these data.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "SampleBatchForUpload"

    samples: list[SampleForUpload] = Field(
        description="The samples to be uploaded.",
    )

    # New reference data required to enable storage of the sample data
    alleles: list[AlleleForUpload] | None = Field(
        default=None,
        description="All unique allele_ids present in src_allele_profiles.allele_ids and that are not yet stored. This provides the means to store these new unique alleles together with any allele profiles, while at the same time compacting the src_allele_profiles by having each unique allele sequence stored only once in the model. Any additional alleles already stored, or not known to be stored, may be included as well.",
    )

    # Computed fields
    @computed_field
    @property
    def has_read_sets(self) -> bool:
        """Indicates whether there are any read sets in the sample set."""
        return any(len(x.read_sets or []) > 0 for x in self.samples)

    @computed_field
    @property
    def has_seqs(self) -> bool:
        """Indicates whether there are any sequences in the sample set."""
        return any(len(x.seqs or []) > 0 for x in self.samples)

    @computed_field
    @property
    def has_seq_taxonomies(self) -> bool:
        """Indicates whether there are any seq taxonomies in the sample set."""
        return any(len(x.seq_taxonomies or []) > 0 for x in self.samples)

    @computed_field
    @property
    def has_seq_classifications(self) -> bool:
        """Indicates whether there are any seq classifications in the sample set."""
        return any(len(x.seq_classifications or []) > 0 for x in self.samples)

    @computed_field
    @property
    def has_locus_profiles(self) -> bool:
        """Indicates whether there are any locus profiles in the sample set."""
        return any(len(x.locus_profiles or []) > 0 for x in self.samples)

    @computed_field
    @property
    def has_allele_profiles(self) -> bool:
        """Indicates whether there are any allele profiles in the sample set."""
        return any(len(x.allele_profiles or []) > 0 for x in self.samples)

    @computed_field
    @property
    def has_snp_profiles(self) -> bool:
        """Indicates whether there are any SNP profiles in the sample set."""
        return any(len(x.snp_profiles or []) > 0 for x in self.samples)

    @computed_field
    @property
    def has_mlva_profiles(self) -> bool:
        """Indicates whether there are any MLVA profiles in the sample set."""
        return any(len(x.mlva_profiles or []) > 0 for x in self.samples)

    @computed_field
    @property
    def has_kmer_profiles(self) -> bool:
        """Indicates whether there are any k-mer profiles in the sample set."""
        return any(len(x.kmer_profiles or []) > 0 for x in self.samples)

    @computed_field
    @property
    def has_distances(self) -> bool:
        """Indicates whether there are any distances in the sample set."""
        return any(len(x.distances or []) > 0 for x in self.samples)

    @computed_field
    @property
    def has_pcr_measurements(self) -> bool:
        """Indicates whether there are any PCR measurements in the sample set."""
        return any(len(x.pcr_measurements or []) > 0 for x in self.samples)

    @computed_field
    @property
    def has_ast_measurements(self) -> bool:
        """Indicates whether there are any AST measurements in the sample set."""
        return any(len(x.ast_measurements or []) > 0 for x in self.samples)

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        # Verify that samples contain no duplicate sample_ids
        sample_ids = [x.id for x in self.samples if x.id is not None]
        if len(sample_ids) != len(set(sample_ids)):
            raise ValueError("Samples must not contain duplicate sample IDs.")
        # Verify that samples contains no duplicate external_ids
        all_external_ids = []
        for sample in self.samples:
            if sample.external_ids is not None:
                all_external_ids.extend(sample.external_ids)
        if len(all_external_ids) != len(set(all_external_ids)):
            raise ValueError("Samples must not contain duplicate external_ids.")
        return self


class SampleBatchUploadResult(UploadResult):
    """
    The result of uploading a batch of cases.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "SampleBatchUploadResult"

    SUB_RESULT_LIST_FIELD_NAMES: ClassVar = [
        "sample_results",
    ]

    sample_results: list[SampleUploadResult] = Field(
        description="The results of uploading the individual samples, in the same order as provided."
    )

"""Define SeqDB domain models for domain.model.seq.upload."""

import json
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, computed_field, model_validator

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.base import EtlLogItem
from gen_epix.commondb.domain.model.upload import (
    BaseBatchForUpload,
    BaseBatchUploadResult,
    DataIssue,
    IdentifiersMixin,
    ParentForUpload,
    ParentUploadResult,
    UploadResult,
)
from gen_epix.fastapp.domain import Entity
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.classification import (
    SeqClassification,
    SeqTaxonomy,
)
from gen_epix.seqdb.domain.model.seq.locus import Allele
from gen_epix.seqdb.domain.model.seq.pheno import AstMeasurement, PcrMeasurement
from gen_epix.seqdb.domain.model.seq.profile import SeqProfile, SeqProfileIdentifier
from gen_epix.seqdb.domain.model.seq.reads import ReadSet, ReadSetIdentifier
from gen_epix.seqdb.domain.model.seq.sample import Sample, SampleIdentifier
from gen_epix.seqdb.domain.model.seq.seq import Seq, SeqIdentifier
from gen_epix.util import copy_model_field


class ValidateRefDataIdCodeMixin:
    """Require upload reference data to be identified by an ID or a code.

    Model validation: Each configured ID-and-code field pair must contain a
    non-null ID or a code so reference data can be resolved during upload.
    """

    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar[list[tuple[str, str]]] = []

    @model_validator(mode="after")
    def _validate_refdata(self) -> Self:
        """Require a code or non-null ID for every configured reference-data pair."""
        for refdata_id_field, refdata_code_field in self.REFDATA_FIELD_ID_CODE_PAIRS:
            refdata_code = getattr(self, refdata_code_field)
            refdata_id = getattr(self, refdata_id_field)
            if not refdata_code and refdata_id == NULL_ID:
                raise ValueError(
                    f"Either {refdata_code_field} or {refdata_id_field} must be provided."
                )
        return self


class ReadSetForUpload(ReadSet, IdentifiersMixin, ValidateRefDataIdCodeMixin):
    """Represent a read set intended for upload."""

    ENTITY: ClassVar = ReadSet.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "ReadSetForUpload"

    IDENTIFIER_CLASS: ClassVar = ReadSetIdentifier
    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar = [
        ("protocol_id", "protocol_code"),
    ]

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the read set is associated with. If not available, the null ID is put.",
    )
    protocol_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the protocol, if available. If not available, the null ID is put. Must be present if protocol_code is not present. The use of protocol_id is preferred over protocol_code since the latter may change.",
    )
    protocol_code: str | None = Field(
        default=None,
        description="The code of the protocol. Must be present if protocol_id is not present. The use of protocol_code is meant for situations where the protocol_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )


class SeqForUpload(Seq, IdentifiersMixin, ValidateRefDataIdCodeMixin):
    """Represent a sequence intended for upload."""

    ENTITY: ClassVar = Seq.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "SeqForUpload"
    IDENTIFIER_CLASS: ClassVar = SeqIdentifier
    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar = [
        ("protocol_id", "protocol_code"),
    ]

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the sequence is associated with. If not available, the null ID is put.",
    )
    protocol_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the protocol, if available. If not available, the null ID is put. Must be present if protocol_code is not present. The use of protocol_id is preferred over protocol_code since the latter may change.",
    )
    protocol_code: str | None = Field(
        default=None,
        description="The code of the protocol. Must be present if protocol_id is not present. The use of protocol_code is meant for situations where the protocol_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )


class SeqProfileForUpload(SeqProfile, IdentifiersMixin, ValidateRefDataIdCodeMixin):
    """Represent a sequence profile with upload-specific reference-data inputs.

    Model validation: Exactly one representation is accepted for allele, MLVA,
    and k-mer profiles. Ordered representations derive content and its hash;
    code-map representations require a locus code map.
    """

    ENTITY: ClassVar = SeqProfile.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "SeqProfileForUpload"

    IDENTIFIER_CLASS: ClassVar = SeqProfileIdentifier
    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar = [
        ("protocol_id", "protocol_code"),
    ]

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the sequence profile is associated with. If not available, the null ID is put.",
    )
    seq_id: UUID | None = Field(
        default=None,
        description="The UUID of the sequence that the sequence profile was derived from, if available.",
    )
    protocol_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the protocol, if available. If not available, the null ID is put. Must be present if protocol_code is not present. The use of protocol_id is preferred over protocol_code since the latter may change.",
    )
    protocol_code: str | None = Field(
        default=None,
        description="The code of the protocol. Must be present if protocol_id is not present. The use of protocol_code is meant for situations where the protocol_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )
    content: str = Field(
        default="",
        description="String representation of the sequence profile, with the format depending on the sequence profile format. Must be present if another for-upload representation is not provided.",
    )
    aligned_nucleotide_seq: str | None = Field(
        default=None,
        description="The full nucleotide sequence aligned to the reference sequence as a for-upload representation for SNP sequence profiles. Must be present if content is not provided.",
    )
    locus_code_map_id: UUID | None = Field(
        default=None,
        description="The id of the locus code map that has to be used to map locus codes to locus IDs, if available. Must be provided if locus_code_map_code is not provided and any alleles have locus_code filled in. The use of locus_code_map_id is preferred over locus_code_map_code since the latter may change.",
    )
    locus_code_map_code: str | None = Field(
        default=None,
        description="The code of the locus code map that has to be used to map locus codes to locus IDs, if available. Must be provided if locus_code_map_id is not provided and any alleles have locus_code filled in. The use of locus_code_map_code is meant for situations where the locus_code_map_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )
    allele_ids: list[UUID | None] | None = Field(
        default=None,
        description="List of all allele IDs detected for this sample and for the loci within the locus set, in the order of the locus set. Loci that are not present must have None as allele ID. Must be present if allele_profile and locus_allele_id_map are not provided: these 3 properties are different representations of the same data that can be chosen between.",
    )
    locus_allele_id_map: dict[str, UUID] | None = Field(
        default=None,
        description="A mapping from locus codes to allele ids, which are the hashes of the allele sequence, for all detected loci, in any order and if available. Must be present if allele_profile and alleles are not provided: these 3 properties are different representations of the same data that can be chosen between.",
    )
    repeat_numbers: list[int | None] | None = Field(
        default=None,
        description="List of all repeat numbers detected for this sample and for the loci within the locus set, in the order of the locus set. Loci that are not present must have None as repeat number. Must be present if mlva_profile and locus_repeat_number_map are not provided: these 3 properties are different representations of the same data that can be chosen between.",
    )
    locus_repeat_number_map: dict[str, int | None] | None = Field(
        default=None,
        description="A mapping from locus codes to repeat numbers for all detected loci, in any order and if available. Undetected loci must have None as repeat number or may be omitted. Must be present if mlva_profile and repeat_numbers are not provided: these 3 properties are different representations of the same data that can be chosen between.",
    )
    kmer_frequency_map: dict[str, float] | None = Field(
        default=None,
        description="A mapping from locus codes to repeat numbers for all detected loci, in any order and if available. Undetected loci must have None as repeat number or may be omitted. Must be present if kmer_profile is not provided: these 2 properties are different representations of the same data that can be chosen between.",
    )

    @staticmethod
    def _get_representation_list(field_names: tuple[str, ...]) -> str:
        """Format representation names for a validation error message."""
        if len(field_names) == 1:
            return field_names[0]
        if len(field_names) == 2:
            return f"{field_names[0]} or {field_names[1]}"
        return f"{', '.join(field_names[:-1])}, or {field_names[-1]}"

    def _validate_exactly_one_representation(
        self,
        representations: tuple[tuple[str, bool], ...],
    ) -> None:
        """Require exactly one named profile representation.

        Args:
            representations: Representation names paired with their presence flags.

        Raises:
            ValueError: If none or more than one representation is provided.
        """
        if sum(is_provided for _, is_provided in representations) != 1:
            raise ValueError(
                "Exactly one of "
                f"{self._get_representation_list(tuple(name for name, _ in representations))} "
                "must be provided."
            )

    def _require_locus_code_map(self, representation_name: str) -> None:
        """Require a locus code map for a map-based profile representation.

        Args:
            representation_name: The representation that requires the code map.

        Raises:
            ValueError: If neither a locus code-map ID nor code is provided.
        """
        if (
            self.locus_code_map_id is None or self.locus_code_map_id == NULL_ID
        ) and self.locus_code_map_code is None:
            raise ValueError(
                "locus_code_map_id or locus_code_map_code must be provided when "
                f"{representation_name} is used."
            )

    def _validate_locus_profile_upload(self) -> Self:
        """Require non-empty content for a locus profile upload.

        Returns:
            The validated upload model.

        Raises:
            ValueError: If profile content is empty.
        """
        if self.content == "":
            raise ValueError("content must be provided.")
        return self

    def _validate_snp_profile_upload(self) -> Self:
        """Require content or an aligned sequence for an SNP profile upload.

        Returns:
            The validated upload model.

        Raises:
            ValueError: If neither SNP representation is provided.
        """
        if self.content == "" and self.aligned_nucleotide_seq is None:
            raise ValueError(
                "content or aligned_nucleotide_seq must be provided for SNP profiles."
            )
        # TODO: When content is provided, the parent SeqProfile._validate_content validator
        # has already parsed the JSON, validated required NextClade fields, and
        # computed/verified the hash. Nothing more to do here.
        # When aligned_nucleotide_seq is provided (content == ""), the parent skips
        # validation and the conversion to content + hash computation will be
        # implemented here.

        return self

    def _validate_allele_profile_upload(self) -> Self:
        """Validate and normalize an allele-profile upload representation.

        Returns:
            The validated upload model.

        Raises:
            ValueError: If representations conflict, map data lacks a code map, or a
                supplied hash differs from the derived allele-profile hash.
        """
        # Already normalized (content was derived from allele_ids on a prior validation pass)
        if self.content != "" and self.allele_ids is not None:
            return self
        self._validate_exactly_one_representation(
            (
                ("content", self.content != ""),
                ("allele_ids", self.allele_ids is not None),
                ("locus_allele_id_map", self.locus_allele_id_map is not None),
            )
        )

        if self.allele_ids is not None:
            self.content = SeqProfile.get_ordered_allele_ids_representation(
                self.allele_ids
            )
            computed_profile_hash = SeqProfile.get_allele_profile_hash(self.allele_ids)
            if self.content_hash == NULL_ID:
                self.content_hash = computed_profile_hash
            elif self.content_hash != computed_profile_hash:
                raise ValueError(
                    "Provided allele profile hash does not match computed hash"
                )
        elif self.locus_allele_id_map is not None:
            self._require_locus_code_map("locus_allele_id_map")
        return self

    def _validate_mlva_profile_upload(self) -> Self:
        """Validate and normalize an MLVA-profile upload representation.

        Returns:
            The validated upload model.

        Raises:
            ValueError: If representations conflict, map data lacks a code map, or a
                supplied hash differs from the derived MLVA-profile hash.
        """
        # Already normalized (content was derived from repeat_numbers on a prior validation pass)
        if self.content != "" and self.repeat_numbers is not None:
            return self
        self._validate_exactly_one_representation(
            (
                ("content", self.content != ""),
                ("repeat_numbers", self.repeat_numbers is not None),
                (
                    "locus_repeat_number_map",
                    self.locus_repeat_number_map is not None,
                ),
            )
        )

        if self.repeat_numbers is not None:
            self.content = SeqProfile.get_ordered_repeat_numbers_representation(
                self.repeat_numbers
            )
            computed_profile_hash = SeqProfile.get_mlva_profile_hash(
                self.repeat_numbers
            )
            if self.content_hash == NULL_ID:
                self.content_hash = computed_profile_hash
            elif self.content_hash != computed_profile_hash:
                raise ValueError(
                    "Provided MLVA profile hash does not match computed hash"
                )
        elif self.locus_repeat_number_map is not None:
            self._require_locus_code_map("locus_repeat_number_map")
        return self

    def _validate_kmer_profile_upload(self) -> Self:
        """Validate and normalize a k-mer-profile upload representation.

        Returns:
            The validated upload model.

        Raises:
            ValueError: If representations conflict or a supplied hash differs from
                the derived k-mer-profile hash.
        """
        # Already normalized (content was derived from kmer_frequency_map on a prior validation pass)
        if self.content != "" and self.kmer_frequency_map is not None:
            return self
        self._validate_exactly_one_representation(
            (
                ("content", self.content != ""),
                ("kmer_frequency_map", self.kmer_frequency_map is not None),
            )
        )

        if self.kmer_frequency_map is not None:
            self.content = json.dumps(self.kmer_frequency_map)
            computed_profile_hash = SeqProfile.get_kmer_profile_hash(
                self.kmer_frequency_map
            )
            if self.content_hash == NULL_ID:
                self.content_hash = computed_profile_hash
            elif self.content_hash != computed_profile_hash:
                raise ValueError(
                    "Provided k-mer profile hash does not match computed hash"
                )
        return self

    # Validate upload representations per profile type and normalize the ordered ones.
    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """Apply validation for the selected sequence-profile type."""
        validators = {
            enum.SeqProfileType.LOCUS: self._validate_locus_profile_upload,
            enum.SeqProfileType.ALLELE: self._validate_allele_profile_upload,
            enum.SeqProfileType.SNP: self._validate_snp_profile_upload,
            enum.SeqProfileType.MLVA: self._validate_mlva_profile_upload,
            enum.SeqProfileType.KMER: self._validate_kmer_profile_upload,
        }
        return validators[self.seq_profile_type]()


class AlleleForUpload(Allele):
    """Represent an allele with upload-specific reference-data inputs."""

    ENTITY: ClassVar = Allele.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "AlleleForUpload"

    locus_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the locus, if available. If not available, the null ID is put.",
    )


class SeqClassificationForUpload(SeqClassification, ValidateRefDataIdCodeMixin):
    """Represent a sequence classification with upload-specific reference-data inputs.

    Model validation: Content validation is not implemented yet, so classification
    content is accepted unchanged after inherited validation.
    """

    ENTITY: ClassVar = SeqClassification.model_entity().clone(
        update={"persistable": False}
    )
    NAME: ClassVar = "SeqClassificationForUpload"
    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar = [
        ("protocol_id", "protocol_code"),
        ("primary_category_id", "primary_category_code"),
    ]

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the sequence classification is associated with. If not available, the null ID is put.",
    )
    seq_id: UUID | None = Field(
        default=None,
        description="The UUID of the sequence that the sequence classification was derived from, if available.",
    )
    protocol_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the protocol, if available. If not available, the null ID is put. Must be present if protocol_code is not present. The use of protocol_id is preferred over protocol_code since the latter may change.",
    )
    protocol_code: str | None = Field(
        default=None,
        description="The code of the protocol. Must be present if protocol_id is not present. The use of protocol_code is meant for situations where the protocol_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )
    primary_category_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the primary category, if available. If not available, the null ID is put. Must be present if primary_category_code is not present. The use of primary_category_id is preferred over primary_category_code since the latter may change.",
    )
    primary_category_code: str | None = Field(
        default=None,
        description="The code of the primary category. Must be present if primary_category_id is not present. The use of primary_category_code is meant for situations where the primary_category_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )

    @model_validator(mode="after")
    def _validate_content(self) -> Self:
        """Reserve post-validation for future classification-content verification."""
        # TODO: add validation
        return self


# TODO: add PcrMeasurementForUpload and update SampleForUpload accordingly
# TODO: add AstMeasurementForUpload and update SampleForUpload accordingly
# TODO: add SeqTaxonomyForUpload and update SampleForUpload accordingly
# TODO: add SeqClassificationForUpload and update SampleForUpload accordingly


class SampleForUpload(ParentForUpload):
    """Represent a sample and its associated data for upload."""

    ENTITY: ClassVar = ParentForUpload.model_entity().clone()
    NAME = "SampleForUpload"

    IDENTIFIER_CLASS: ClassVar = SampleIdentifier
    PARENT_CLASS: ClassVar = Sample
    PARENT_FIELD_NAME: ClassVar = "sample"
    CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar = {
        ReadSet: ReadSetForUpload,
        Seq: SeqForUpload,
        SeqTaxonomy: SeqTaxonomy,
        SeqClassification: SeqClassificationForUpload,
        SeqProfile: SeqProfileForUpload,
        PcrMeasurement: PcrMeasurement,
        AstMeasurement: AstMeasurement,
    }
    CHILDREN_FIELD_NAME_MAP: ClassVar = {
        ReadSet: "read_sets",
        Seq: "seqs",
        SeqTaxonomy: "seq_taxonomies",
        SeqClassification: "seq_classifications",
        SeqProfile: "seq_profiles",
        PcrMeasurement: "pcr_measurements",
        AstMeasurement: "ast_measurements",
    }
    CHILD_PARENT_ID_FIELD_NAME_MAP: ClassVar = {
        x: "sample_id" for x in CHILD_FOR_UPLOAD_CLASS_MAP.keys()
    }
    CHILD_INTRA_PARENT_LINKS_MAP: ClassVar = {
        Seq: [("read_set_id", ReadSet), ("read_set2_id", ReadSet)],
        SeqClassification: [("seq_id", Seq)],
        SeqProfile: [("seq_id", Seq)],
        SeqTaxonomy: [("seq_id", Seq)],
    }

    # Parent
    sample: Sample | None = Field(
        default=None,
        description="The sample model itself, if to be created or updated as a whole.",
    )

    # Children
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
    seq_classifications: list[SeqClassificationForUpload] | None = Field(
        default=None,
        description="The classifications associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    seq_profiles: list[SeqProfileForUpload] | None = Field(
        default=None,
        description="The sequence profiles associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    pcr_measurements: list[PcrMeasurement] | None = Field(
        default=None,
        description="The PCR measurements associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    ast_measurements: list[AstMeasurement] | None = Field(
        default=None,
        description="The AST measurements associated with the sample. If None, this element is not taken into consideration during the upload.",
    )


class SampleDataIssue(DataIssue):
    """Describe an issue found while uploading a sample or its associated data."""


class SampleUploadResult(ParentUploadResult):
    """Represent the outcome of uploading one sample and its associated data.

    Result field names match ``SampleForUpload`` fields to support caller processing.
    """

    ENTITY: ClassVar = ParentUploadResult.model_entity().clone()
    NAME: ClassVar = "SampleUploadResult"

    PARENT_FOR_UPLOAD_CLASS: ClassVar = SampleForUpload  # type: ignore[assignment]

    data_issues: list[SampleDataIssue] = copy_model_field(
        ParentUploadResult, "data_issues"
    )

    read_sets: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the read sets associated with the sample, if any were provided, in the same order as provided.",
    )
    seqs: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the sequences associated with the sample, if any were provided, in the same order as provided.",
    )
    seq_taxonomies: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the seq taxonomies associated with the sample, if any were provided, in the same order as provided.",
    )
    seq_classifications: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the seq classifications associated with the sample, if any were provided, in the same order as provided.",
    )
    seq_profiles: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the sequence profiles associated with the sample, if any were provided, in the same order as provided.",
    )
    pcr_measurements: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the PCR measurements associated with the sample, if any were provided, in the same order as provided.",
    )
    ast_measurements: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the AST measurements associated with the sample, if any were provided, in the same order as provided.",
    )

    def get_errors(self) -> list[EtlLogItem]:
        """Get all data issues that are errors."""
        log_items = super().get_errors()
        if self.identifiers:
            for identifier_result in self.identifiers:
                log_items.extend(identifier_result.get_errors())
        if self.read_sets:
            for read_set_result in self.read_sets:
                log_items.extend(read_set_result.get_errors())
        if self.seqs:
            for seq_result in self.seqs:
                log_items.extend(seq_result.get_errors())
        if self.seq_taxonomies:
            for seq_taxonomy_result in self.seq_taxonomies:
                log_items.extend(seq_taxonomy_result.get_errors())
        if self.seq_classifications:
            for seq_classification_result in self.seq_classifications:
                log_items.extend(seq_classification_result.get_errors())
        if self.seq_profiles:
            for seq_profile_result in self.seq_profiles:
                log_items.extend(seq_profile_result.get_errors())
        if self.pcr_measurements:
            for pcr_measurement_result in self.pcr_measurements:
                log_items.extend(pcr_measurement_result.get_errors())
        if self.ast_measurements:
            for ast_measurement_result in self.ast_measurements:
                log_items.extend(ast_measurement_result.get_errors())
        return log_items


class SampleBatchForUpload(BaseBatchForUpload):
    """Represent samples and reference data submitted in one upload batch.

    The batch can include new alleles required to store its sample data.
    """

    ENTITY: ClassVar = SampleForUpload.model_entity().clone()
    NAME: ClassVar = "SampleBatchForUpload"

    PARENT_FOR_UPLOAD_CLASS: ClassVar = SampleForUpload
    PARENTS_FOR_UPLOAD_FIELD_NAME: ClassVar = "samples"

    samples: list[SampleForUpload] = Field(
        description="The samples to be uploaded.",
    )

    # New reference data required to enable storage of the sample data
    alleles: list[AlleleForUpload] | None = Field(
        default=None,
        description="All unique allele_ids present in any of the sample allele profiles and that are not yet stored. Their locus_id must be set either to the correct locus ID or to the NULL_ID. In the latter case the locus_id will be derived from the allele profiles, where this information is implicitly or explicitly stored. Providing the new alleles separately allows to provide them only once instead of repeatedly for each allele profile that contains them. In addition, it avoids having to have two separate calls, first to store the new alleles and then the new profiles. Any additional alleles that were already stored, or are not known to be stored, may be included as well.",
    )

    # Computed fields
    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_read_sets(self) -> bool:
        """Indicates whether there are any read sets in the sample set."""
        return any(len(x.read_sets or []) > 0 for x in self.samples)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_seqs(self) -> bool:
        """Indicates whether there are any sequences in the sample set."""
        return any(len(x.seqs or []) > 0 for x in self.samples)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_seq_taxonomies(self) -> bool:
        """Indicates whether there are any seq taxonomies in the sample set."""
        return any(len(x.seq_taxonomies or []) > 0 for x in self.samples)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_seq_classifications(self) -> bool:
        """Indicates whether there are any seq classifications in the sample set."""
        return any(len(x.seq_classifications or []) > 0 for x in self.samples)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_seq_profiles(self) -> bool:
        """Indicates whether there are any sequence profiles in the sample set."""
        return any(len(x.seq_profiles or []) > 0 for x in self.samples)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_pcr_measurements(self) -> bool:
        """Indicates whether there are any PCR measurements in the sample set."""
        return any(len(x.pcr_measurements or []) > 0 for x in self.samples)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_ast_measurements(self) -> bool:
        """Indicates whether there are any AST measurements in the sample set."""
        return any(len(x.ast_measurements or []) > 0 for x in self.samples)


class CalculateSeqDistancesResult(UploadResult):
    """Represent distances calculated between existing and uploaded profiles.

    ``seq_distance_profile_id`` identifies the profile containing these distances.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "CalculateSeqDistancesResult"

    # TODO: 3034 since profiles of different types and subtypes (locus set, ref seq) can be provided, there can be many different distance profiles that are relevant. TBD how to handle this in the result.
    seq_distance_profile_id: UUID = Field(
        description="The UUID of the sequence distance profile that contains the calculated distances.",
    )


class SampleBatchUploadResult(BaseBatchUploadResult):
    """Represent the result of uploading a batch of samples."""

    ENTITY: ClassVar = SampleBatchForUpload.model_entity().clone()
    NAME: ClassVar = "SampleBatchUploadResult"

    BATCH_FOR_UPLOAD_CLASS: ClassVar = SampleBatchForUpload  # type: ignore[assignment]
    PARENT_RESULT_CLASS: ClassVar = SampleUploadResult  # type: ignore[assignment]

    samples: list[SampleUploadResult] = Field(
        description="The results of uploading the individual samples, in the same order as provided."
    )
    seq_distances: list[CalculateSeqDistancesResult] | None = Field(
        default=None,
        description="The results of calculating distances between sequences, if this was performed as part of the upload.",
    )

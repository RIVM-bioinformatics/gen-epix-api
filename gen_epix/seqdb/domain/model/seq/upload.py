from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, computed_field, model_validator

from gen_epix.commondb.domain.literal import NULL_ID
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
from gen_epix.seqdb.domain.model.seq.classification import (
    SeqClassification,
    SeqTaxonomy,
)
from gen_epix.seqdb.domain.model.seq.locus import Allele
from gen_epix.seqdb.domain.model.seq.pheno import AstMeasurement, PcrMeasurement
from gen_epix.seqdb.domain.model.seq.profile import (
    AlleleProfile,
    AlleleProfileIdentifier,
    KmerProfile,
    KmerProfileIdentifier,
    LocusProfile,
    MlvaProfile,
    MlvaProfileIdentifier,
    SnpProfile,
    SnpProfileIdentifier,
)
from gen_epix.seqdb.domain.model.seq.reads import ReadSet, ReadSetIdentifier
from gen_epix.seqdb.domain.model.seq.sample import Sample, SampleIdentifier
from gen_epix.seqdb.domain.model.seq.seq import Seq, SeqIdentifier
from gen_epix.util import copy_model_field


class ValidateRefDataIdCodeMixin:
    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar[list[tuple[str, str]]] = []

    @model_validator(mode="after")
    def _validate_refdata(self) -> Self:
        """Validate that either refdata code or refdata id is provided."""
        for refdata_id_field, refdata_code_field in self.REFDATA_FIELD_ID_CODE_PAIRS:
            refdata_code = getattr(self, refdata_code_field)
            refdata_id = getattr(self, refdata_id_field)
            if not refdata_code and refdata_id == NULL_ID:
                raise ValueError(
                    f"Either {refdata_code_field} or {refdata_id_field} must be provided."
                )
        return self


class ReadSetForUpload(ReadSet, IdentifiersMixin, ValidateRefDataIdCodeMixin):
    """
    A read set intended for upload.
    """

    ENTITY: ClassVar = ReadSet.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "ReadSetForUpload"

    IDENTIFIER_CLASS: ClassVar = ReadSetIdentifier
    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar = [
        ("sequencing_protocol_id", "sequencing_protocol_code"),
    ]

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the read set is associated with. If not available, the null ID is put.",
    )
    sequencing_protocol_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sequencing protocol, if available. If not available, the null ID is put. Must be present if sequencing_protocol_code is not present. The use of sequencing_protocol_id is preferred over sequencing_protocol_code since the latter may change.",
    )
    sequencing_protocol_code: str | None = Field(
        default=None,
        description="The code of the sequencing protocol. Must be present if sequencing_protocol_id is not present. The use of sequencing_protocol_code is meant for situations where the sequencing_protocol_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )


class SeqForUpload(Seq, IdentifiersMixin, ValidateRefDataIdCodeMixin):
    """
    A sequence intended for upload.
    """

    ENTITY: ClassVar = Seq.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "SeqForUpload"
    IDENTIFIER_CLASS: ClassVar = SeqIdentifier
    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar = [
        ("assembly_protocol_id", "assembly_protocol_code"),
    ]

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the sequence is associated with. If not available, the null ID is put.",
    )
    assembly_protocol_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the assembly protocol, if available. If not available, the null ID is put. Must be present if assembly_protocol_code is not present. The use of assembly_protocol_id is preferred over assembly_protocol_code since the latter may change.",
    )
    assembly_protocol_code: str | None = Field(
        default=None,
        description="The code of the assembly protocol. Must be present if assembly_protocol_id is not present. The use of assembly_protocol_code is meant for situations where the assembly_protocol_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )


class SnpProfileForUpload(SnpProfile, IdentifiersMixin, ValidateRefDataIdCodeMixin):
    """
    A SNP profile record intended for upload. Equal to a SnpProfile, with
    additional variables.
    """

    ENTITY: ClassVar = SnpProfile.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "SnpProfileForUpload"

    IDENTIFIER_CLASS: ClassVar = SnpProfileIdentifier
    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar = [
        ("snp_detection_protocol_id", "snp_detection_protocol_code"),
        ("ref_seq_id", "ref_seq_code"),
    ]

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the SNP profile is associated with. If not available, the null ID is put.",
    )
    seq_id: UUID | None = Field(
        default=None,
        description="The UUID of the sequence that the SNP profile was derived from, if available.",
    )
    ref_seq_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the reference sequence, if available. If not available, the null ID is put. Must be present if ref_seq_code is not present. The use of ref_seq_id is preferred over ref_seq_code since the latter may change.",
    )
    ref_seq_code: str | None = Field(
        default=None,
        description="The code of the reference sequence. Must be present if ref_seq_id is not present. The use of ref_seq_code is meant for situations where the ref_seq_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )
    snp_detection_protocol_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the SNP detection protocol, if available. If not available, the null ID is put. Must be present if snp_detection_protocol_code is not present. The use of snp_detection_protocol_id is preferred over snp_detection_protocol_code since the latter may change.",
    )
    snp_detection_protocol_code: str | None = Field(
        default=None,
        description="The code of the SNP detection protocol. Must be present if snp_detection_protocol_id is not present. The use of snp_detection_protocol_code is meant for situations where the snp_detection_protocol_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )
    snp_profile: str = Field(
        default="",
        description="String representation of the SNPs detected in the sequence, with the format depending on snp_profile_format. Must be present if aligned_nucleotide_seq is not provided: these 2 properties are different representations of the same data that can be chosen between.",
    )
    aligned_nucleotide_seq: str | None = Field(
        default=None,
        description="The full nucleotide sequence aligned to the reference sequence. Must be present if snp_profile is not provided: these 2 properties are different representations of the same data that can be chosen between.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Override parent validation for upload format to handle aligned_nucleotide_seq.
        """
        n_representations = sum(
            [
                self.snp_profile != "",
                self.aligned_nucleotide_seq is not None,
            ]
        )
        if n_representations != 1:
            raise ValueError(
                "Exactly one of snp_profile or aligned_nucleotide_seq must be provided."
            )

        if self.snp_profile != "":
            # Use parent validation for snp_profile string format
            super()._validate_model()
        elif self.aligned_nucleotide_seq is not None:
            pass
        return self


class AlleleForUpload(Allele):
    """
    An allele intended for upload. Equal to an Allele, with
    additional variables.
    """

    ENTITY: ClassVar = Allele.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "AlleleForUpload"

    locus_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the locus, if available. If not available, the null ID is put.",
    )


class AlleleProfileForUpload(
    AlleleProfile, IdentifiersMixin, ValidateRefDataIdCodeMixin
):
    """
    An allele profile record intended for upload. Equal to an AlleleProfile, with
    additional variables.
    """

    ENTITY: ClassVar = AlleleProfile.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "AlleleProfileForUpload"

    IDENTIFIER_CLASS: ClassVar = AlleleProfileIdentifier
    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar = [
        ("locus_detection_protocol_id", "locus_detection_protocol_code"),
        ("locus_set_id", "locus_set_code"),
        ("locus_code_map_id", "locus_code_map_code"),
    ]

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
    locus_code_map_id: UUID | None = Field(
        default=None,
        description="The id of the locus code map that has to be used to map locus codes to locus IDs, if available. Must be provided if locus_code_map_code is not provided and any alleles have locus_code filled in. The use of locus_code_map_id is preferred over locus_code_map_code since the latter may change.",
    )
    locus_code_map_code: str | None = Field(
        default=None,
        description="The code of the locus code map that has to be used to map locus codes to locus IDs, if available. Must be provided if locus_code_map_id is not provided and any alleles have locus_code filled in. The use of locus_code_map_code is meant for situations where the locus_code_map_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )
    allele_profile: str = Field(
        default="",
        description="String representation of the alleles detected in the sequence for the loci in the locus set, with the format depending on allele_profile_format. Must be present if alleles and locus_allele_id_map are not provided: these 3 properties are different representations of the same data that can be chosen between.",
    )
    allele_ids: list[UUID | None] | None = Field(
        default=None,
        description="List of all allele IDs detected for this sample and for the loci within the locus set, in the order of the locus set. Loci that are not present must have None as allele ID. Must be present if allele_profile and locus_allele_id_map are not provided: these 3 properties are different representations of the same data that can be chosen between.",
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
        n_representations = sum(
            [
                self.allele_profile != "",
                self.allele_ids is not None,
                self.locus_allele_id_map is not None,
            ]
        )
        if n_representations != 1:
            raise ValueError(
                "Exactly one of allele_profile, allele_ids, or locus_allele_id_map must be provided."
            )

        if self.allele_profile != "":
            # Use parent validation for allele_profile string format
            super()._validate_model()
        elif self.allele_ids is not None:
            # Set or verify n_loci
            computed_n_loci = sum(x is not None for x in self.allele_ids)
            if self.n_loci == 0:
                if computed_n_loci == 0:
                    raise ValueError("Unable to calculate number of loci")
                self.n_loci = computed_n_loci
            elif self.n_loci != computed_n_loci:
                raise ValueError(
                    f"Provided n_loci does not match computed n_loci: {self.n_loci} != {computed_n_loci}"
                )
            # Set or verify allele_profile_hash
            computed_profile_hash = AlleleProfile.get_allele_profile_hash(
                self.allele_ids
            )  # Will raise ValueError if invalid
            if self.allele_profile_hash == NULL_ID:
                self.allele_profile_hash = computed_profile_hash
            elif self.allele_profile_hash != computed_profile_hash:
                raise ValueError(
                    "Provided allele profile hash does not match computed hash"
                )
        elif self.locus_allele_id_map is not None:
            # Set or verify n_loci
            computed_n_loci = len(self.locus_allele_id_map)
            if self.n_loci == 0:
                if computed_n_loci == 0:
                    raise ValueError("Unable to calculate number of loci")
                self.n_loci = computed_n_loci
            elif self.n_loci != computed_n_loci:
                raise ValueError(
                    f"Provided n_loci does not match computed n_loci: {self.n_loci} != {computed_n_loci}"
                )
            # Verify locus code map provided
            if (
                self.locus_code_map_id is None or self.locus_code_map_id == NULL_ID
            ) and self.locus_code_map_code is None:
                raise ValueError(
                    "locus_code_map_id or locus_code_map_code must be provided when locus_allele_id_map is used."
                )
            # Set or verify allele_profile_hash: not possible with this representation since loci are unordered

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
        if (
            self.locus_allele_id_map is not None
            and self.locus_code_map_id == NULL_ID
            and self.locus_code_map_code is None
        ):
            raise ValueError(
                "Either locus_code_map_id or locus_code_map_code must be provided when locus_allele_id_map is used."
            )
        return self


class MlvaProfileForUpload(MlvaProfile, IdentifiersMixin, ValidateRefDataIdCodeMixin):
    """
    An MLVA profile record intended for upload. Equal to an MlvaProfile, with
    additional variables.
    """

    ENTITY: ClassVar = MlvaProfile.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "MlvaProfileForUpload"

    IDENTIFIER_CLASS: ClassVar = MlvaProfileIdentifier
    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar = [
        ("mlva_detection_protocol_id", "mlva_detection_protocol_code"),
        ("locus_set_id", "locus_set_code"),
        ("locus_code_map_id", "locus_code_map_code"),
    ]

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the allele profile is associated with. If not available, the null ID is put.",
    )
    seq_id: UUID | None = Field(
        default=None,
        description="The UUID of the sequence that the allele profile was derived from, if available.",
    )
    mlva_detection_protocol_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the MLVA detection protocol, if available. If not available, the null ID is put. Must be present if mlva_detection_protocol_code is not present. The use of mlva_detection_protocol_id is preferred over mlva_detection_protocol_code since the latter may change.",
    )
    mlva_detection_protocol_code: str | None = Field(
        default=None,
        description="The code of the MLVA detection protocol. Must be present if mlva_detection_protocol_id is not present. The use of mlva_detection_protocol_code is meant for situations where the mlva_detection_protocol_id is not known, but the code is and/or improves human interpretation.",
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
    locus_code_map_id: UUID | None = Field(
        default=None,
        description="The id of the locus code map that has to be used to map locus codes to locus IDs, if available. Must be provided if locus_code_map_code is not provided and any alleles have locus_code filled in. The use of locus_code_map_id is preferred over locus_code_map_code since the latter may change.",
    )
    locus_code_map_code: str | None = Field(
        default=None,
        description="The code of the locus code map that has to be used to map locus codes to locus IDs, if available. Must be provided if locus_code_map_id is not provided and any alleles have locus_code filled in. The use of locus_code_map_code is meant for situations where the locus_code_map_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )
    mlva_profile: str = Field(
        default="",
        description="String representation of the repeat number per locus in the locus set, with the format depending on mlva_profile_format. Must be present if repeat_numbers and locus_repeat_number_map are not provided: these 3 properties are different representations of the same data that can be chosen between.",
    )
    repeat_numbers: list[int | None] | None = Field(
        default=None,
        description="List of all repeat numbers detected for this sample and for the loci within the locus set, in the order of the locus set. Loci that are not present must have None as repeat number. Must be present if mlva_profile and locus_repeat_number_map are not provided: these 3 properties are different representations of the same data that can be chosen between.",
    )
    locus_repeat_number_map: dict[str, int | None] | None = Field(
        default=None,
        description="A mapping from locus codes to repeat numbers for all detected loci, in any order and if available. Undetected loci must have None as repeat number or may be omitted. Must be present if mlva_profile and repeat_numbers are not provided: these 3 properties are different representations of the same data that can be chosen between.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Override parent validation for upload format to handle alleles and locus_allele_id_map.
        """
        n_representations = sum(
            [
                self.mlva_profile != "",
                self.repeat_numbers is not None,
                self.locus_repeat_number_map is not None,
            ]
        )
        if n_representations != 1:
            raise ValueError(
                "Exactly one of mlva_profile, repeat_numbers, or locus_repeat_number_map must be provided."
            )

        if self.mlva_profile != "":
            # Use parent validation for mlva_profile string format
            super()._validate_model()
        elif self.repeat_numbers is not None:
            # Set or verify mlva_profile_hash
            computed_profile_hash = MlvaProfile.get_mlva_profile_hash(
                self.repeat_numbers
            )  # Will raise ValueError if invalid
            if self.mlva_profile_hash == NULL_ID:
                self.mlva_profile_hash = computed_profile_hash
            elif self.mlva_profile_hash != computed_profile_hash:
                raise ValueError(
                    "Provided MLVA profile hash does not match computed hash"
                )
        elif self.locus_repeat_number_map is not None:
            # Verify locus code map provided
            if (
                self.locus_code_map_id is None or self.locus_code_map_id == NULL_ID
            ) and self.locus_code_map_code is None:
                raise ValueError(
                    "locus_code_map_id or locus_code_map_code must be provided when locus_repeat_number_map is used."
                )
            # Set or verify mlva_profile_hash: not possible with this representation since loci are unordered

        # Upload-specific validation
        if (
            not self.mlva_detection_protocol_code
            and self.mlva_detection_protocol_id == NULL_ID
        ):
            raise ValueError(
                "Either mlva_detection_protocol_code or mlva_detection_protocol_id must be provided."
            )
        if self.locus_set_code is None and self.locus_set_id == NULL_ID:
            raise ValueError("Either locus_set_code or locus_set_id must be provided.")
        if (
            self.locus_repeat_number_map is not None
            and self.locus_code_map_id == NULL_ID
            and self.locus_code_map_code is None
        ):
            raise ValueError(
                "Either locus_code_map_id or locus_code_map_code must be provided when locus_repeat_number_map is used."
            )
        return self


class KmerProfileForUpload(KmerProfile, IdentifiersMixin, ValidateRefDataIdCodeMixin):
    """
    A k-mer profile record intended for upload. Equal to a KmerProfile, with
    additional variables.
    """

    ENTITY: ClassVar = KmerProfile.model_entity().clone(update={"persistable": False})
    NAME: ClassVar = "KmerProfileForUpload"

    IDENTIFIER_CLASS: ClassVar = KmerProfileIdentifier
    REFDATA_FIELD_ID_CODE_PAIRS: ClassVar = [
        ("kmer_detection_protocol_id", "kmer_detection_protocol_code"),
    ]

    sample_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the sample that the k-mer profile is associated with. If not available, the null ID is put.",
    )
    seq_id: UUID | None = Field(
        default=None,
        description="The UUID of the sequence that the k-mer profile was derived from, if available.",
    )
    kmer_detection_protocol_id: UUID = Field(
        default=NULL_ID,
        description="The UUID of the k-mer detection protocol, if available. If not available, the null ID is put. Must be present if kmer_detection_protocol_code is not present. The use of kmer_detection_protocol_id is preferred over kmer_detection_protocol_code since the latter may change.",
    )
    kmer_detection_protocol_code: str | None = Field(
        default=None,
        description="The code of the k-mer detection protocol. Must be present if kmer_detection_protocol_id is not present. The use of kmer_detection_protocol_code is meant for situations where the kmer_detection_protocol_id is not known, but the code is and/or improves human interpretation.",
        max_length=255,
    )
    kmer_profile: str = Field(
        default="",
        description="String representation of the k-mer profile, with the format depending on kmer_profile_format. Must be present if kmer_frequency_map is not provided: these 2 properties are different representations of the same data that can be chosen between.",
    )
    kmer_frequency_map: dict[str, float] | None = Field(
        default=None,
        description="A mapping from locus codes to repeat numbers for all detected loci, in any order and if available. Undetected loci must have None as repeat number or may be omitted. Must be present if kmer_profile is not provided: these 2 properties are different representations of the same data that can be chosen between.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Override parent validation for upload format to handle kmer_frequency_map.
        """
        n_representations = sum(
            [
                self.kmer_profile != "",
                self.kmer_frequency_map is not None,
            ]
        )
        if n_representations != 1:
            raise ValueError(
                "Exactly one of kmer_profile or kmer_frequency_map must be provided."
            )

        if self.kmer_profile != "":
            # Use parent validation for kmer_profile string format
            super()._validate_model()
        elif self.kmer_frequency_map is not None:
            # Set or verify kmer_profile_hash
            computed_profile_hash = KmerProfile.get_kmer_profile_hash(
                self.kmer_frequency_map
            )  # Will raise ValueError if invalid
            if self.kmer_profile_hash == NULL_ID:
                self.kmer_profile_hash = computed_profile_hash
            elif self.kmer_profile_hash != computed_profile_hash:
                raise ValueError(
                    "Provided k-mer profile hash does not match computed hash"
                )

        # Upload-specific validation
        if (
            not self.kmer_detection_protocol_code
            and self.kmer_detection_protocol_id == NULL_ID
        ):
            raise ValueError(
                "Either kmer_detection_protocol_code or kmer_detection_protocol_id must be provided."
            )
        return self


# TODO: add PcrMeasurementForUpload and update SampleForUpload accordingly
# TODO: add AstMeasurementForUpload and update SampleForUpload accordingly
# TODO: add SeqTaxonomyForUpload and update SampleForUpload accordingly
# TODO: add SeqClassificationForUpload and update SampleForUpload accordingly
# TODO: add LocusProfileForUpload and update SampleForUpload accordingly


class SampleForUpload(ParentForUpload):
    """
    A sample intended for upload, together with any relevant associated data.
    """

    ENTITY: ClassVar = ParentForUpload.model_entity().clone()
    NAME = "SampleForUpload"

    IDENTIFIER_CLASS: ClassVar = SampleIdentifier
    PARENT_CLASS: ClassVar = Sample
    PARENT_FIELD_NAME: ClassVar = "sample"
    CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar = {
        ReadSet: ReadSetForUpload,
        Seq: SeqForUpload,
        SeqTaxonomy: SeqTaxonomy,
        SeqClassification: SeqClassification,
        LocusProfile: LocusProfile,
        AlleleProfile: AlleleProfileForUpload,
        SnpProfile: SnpProfileForUpload,
        MlvaProfile: MlvaProfileForUpload,
        KmerProfile: KmerProfileForUpload,
        PcrMeasurement: PcrMeasurement,
        AstMeasurement: AstMeasurement,
    }
    CHILDREN_FIELD_NAME_MAP: ClassVar = {
        ReadSet: "read_sets",
        Seq: "seqs",
        SeqTaxonomy: "seq_taxonomies",
        SeqClassification: "seq_classifications",
        LocusProfile: "locus_profiles",
        AlleleProfile: "allele_profiles",
        SnpProfile: "snp_profiles",
        MlvaProfile: "mlva_profiles",
        KmerProfile: "kmer_profiles",
        PcrMeasurement: "pcr_measurements",
        AstMeasurement: "ast_measurements",
    }
    CHILD_PARENT_ID_FIELD_NAME_MAP: ClassVar = {
        x: "sample_id" for x in CHILD_FOR_UPLOAD_CLASS_MAP.keys()
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
    snp_profiles: list[SnpProfileForUpload] | None = Field(
        default=None,
        description="The SNP profiles associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    mlva_profiles: list[MlvaProfileForUpload] | None = Field(
        default=None,
        description="The MLVA profiles associated with the sample. If None, this element is not taken into consideration during the upload.",
    )
    kmer_profiles: list[KmerProfileForUpload] | None = Field(
        default=None,
        description="The k-mer profiles associated with the sample. If None, this element is not taken into consideration during the upload.",
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
    pass


class SampleUploadResult(ParentUploadResult):
    """
    The result of uploading a single sample. The field names for the results for
    the associated data match those in SampleForUpload to facilitate processing.
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
    locus_profiles: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the locus profiles associated with the sample, if any were provided, in the same order as provided.",
    )
    allele_profiles: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the allele profiles associated with the sample, if any were provided, in the same order as provided.",
    )
    snp_profiles: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the SNP profiles associated with the sample, if any were provided, in the same order as provided.",
    )
    mlva_profiles: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the MLVA profiles associated with the sample, if any were provided, in the same order as provided.",
    )
    kmer_profiles: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the k-mer profiles associated with the sample, if any were provided, in the same order as provided.",
    )
    pcr_measurements: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the PCR measurements associated with the sample, if any were provided, in the same order as provided.",
    )
    ast_measurements: list[UploadResult] | None = Field(
        default=None,
        description="The results of uploading the AST measurements associated with the sample, if any were provided, in the same order as provided.",
    )


class SampleBatchForUpload(BaseBatchForUpload):
    """
    A set of samples intended for upload, together with any new reference data required
    for the storage of these data.
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
    def has_locus_profiles(self) -> bool:
        """Indicates whether there are any locus profiles in the sample set."""
        return any(len(x.locus_profiles or []) > 0 for x in self.samples)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_allele_profiles(self) -> bool:
        """Indicates whether there are any allele profiles in the sample set."""
        return any(len(x.allele_profiles or []) > 0 for x in self.samples)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_snp_profiles(self) -> bool:
        """Indicates whether there are any SNP profiles in the sample set."""
        return any(len(x.snp_profiles or []) > 0 for x in self.samples)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_mlva_profiles(self) -> bool:
        """Indicates whether there are any MLVA profiles in the sample set."""
        return any(len(x.mlva_profiles or []) > 0 for x in self.samples)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_kmer_profiles(self) -> bool:
        """Indicates whether there are any k-mer profiles in the sample set."""
        return any(len(x.kmer_profiles or []) > 0 for x in self.samples)

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
    """
    Represents the result of calculating distances between existing profiles and new profiles or
    between new profiles themselves, as part of the upload process.
    The seq_distance_profile_id refers to the sequence distance profile (i.e., AlleleProfile or MlvaProfile).
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "CalculateSeqDistancesResult"

    seq_distance_profile_id: UUID = Field(
        description="The UUID of the sequence distance profile that contains the calculated distances.",
    )


class SampleBatchUploadResult(BaseBatchUploadResult):
    """
    The result of uploading a batch of cases.
    """

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

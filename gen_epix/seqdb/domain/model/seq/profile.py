import hashlib
from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_serializer, field_validator

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import ProtocolMixin, QualityMixin
from gen_epix.seqdb.domain.model.seq.locus import LocusSet
from gen_epix.seqdb.domain.model.seq.seq import RefSeq, RefSnp, Seq


class LocusDetectionProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_detection_protocols",
        table_name="locus_detection_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class LocusProfile(Model, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_profiles",
        table_name="locus_profile",
        persistable=True,
        keys=create_keys(
            {1: ("seq_id", "locus_set_id", "locus_detection_protocol_id")}
        ),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: (
                    "locus_detection_protocol_id",
                    LocusDetectionProtocol,
                    "locus_detection_protocol",
                ),
            }
        ),
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    locus_detection_protocol_id: UUID = Field(
        description="The unique identifier for the locus detection protocol. FOREIGN KEY"
    )
    locus_detection_protocol: LocusDetectionProtocol | None = Field(
        default=None, description="The locus detection protocol."
    )
    n_loci: int = Field(description="The number of loci detected.")
    locus_profile: str = Field(
        description="The loci detected in the sequence, including their start and stop positions."
    )
    locus_profile_format: enum.LocusProfileFormat = Field(
        default=enum.LocusProfileFormat.LOCUS_PROFILE_FORMAT1,
        description="The representation format of the loci.",
    )
    locus_profile_hash_sha256: bytes = Field(
        description="The SHA256 hash of the sorted list of allele ids as bytes.",
        min_length=32,
        max_length=32,
    )


class AlleleProfile(Model, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="allele_profiles",
        table_name="allele_profile",
        persistable=True,
        keys=create_keys(
            {1: ("seq_id", "locus_set_id", "locus_detection_protocol_id")}
        ),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: ("locus_set_id", LocusSet, "locus_set"),
                3: (
                    "locus_detection_protocol_id",
                    LocusDetectionProtocol,
                    "locus_detection_protocol",
                ),
            }
        ),
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    locus_set_id: UUID = Field(
        description="The unique identifier for the locus set. FOREIGN KEY"
    )
    locus_set: LocusSet | None = Field(default=None, description="The locus set.")
    locus_detection_protocol_id: UUID = Field(
        description="The unique identifier for the locus detection protocol. FOREIGN KEY"
    )
    locus_detection_protocol: LocusDetectionProtocol | None = Field(
        default=None, description="The locus detection protocol."
    )
    n_loci: int = Field(description="The number of loci detected.")
    allele_profile: str = Field(
        description="The alleles detected in the sequence for the loci in the locus set."
    )
    allele_profile_format: enum.AlleleProfileFormat = Field(
        default=enum.AlleleProfileFormat.SORTED_ALLELE_IDS,
        description="The representation format of the alleles.",
    )
    allele_profile_hash_sha256: bytes = Field(
        description="The SHA256 hash of the sorted list of allele ids as bytes.",
        min_length=32,
        max_length=32,
    )

    @field_validator("allele_profile_hash_sha256", mode="before")
    def _validate_allele_profile_hash_sha256(cls, value: str | bytes) -> bytes:
        if isinstance(value, str):
            value = bytes.fromhex(value)
        return value

    @staticmethod
    def get_allele_profile_hash_sha256(allele_ids: list[UUID | None]) -> bytes:
        sha256 = hashlib.sha256()
        sha256.update(b"".join(sorted([x.bytes for x in allele_ids if x is not None])))
        return sha256.digest()

    @field_serializer("allele_profile_format", mode="plain")
    def _serialize_snp_profile_format(
        self, value: str | enum.AlleleProfileFormat
    ) -> str:
        if isinstance(value, enum.AlleleProfileFormat):
            return value.value
        return value


class SnpDetectionProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="snp_detection_protocols",
        table_name="snp_detection_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class SnpProfile(Model, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="snp_profiles",
        table_name="snp_profile",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "seq_id",
                    "ref_seq_id",
                    "snp_detection_protocol_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: ("ref_seq_id", RefSeq, "ref_seq"),
                3: (
                    "snp_detection_protocol_id",
                    SnpDetectionProtocol,
                    "snp_detection_protocol",
                ),
            }
        ),
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    ref_seq_id: UUID = Field(
        description="The unique identifier for the reference sequence. FOREIGN KEY"
    )
    ref_seq: RefSeq | None = Field(default=None, description="The reference sequence.")
    snp_detection_protocol_id: UUID = Field(
        description="The unique identifier for the SNP detection protocol. FOREIGN KEY"
    )
    snp_detection_protocol: SnpDetectionProtocol | None = Field(
        default=None, description="The SNP detection protocol."
    )
    snp_profile: str = Field(description="The SNPs detected in the sequence.")
    snp_profile_format: enum.SnpProfileFormat = Field(
        default=enum.SnpProfileFormat.REF_ALN_SEQ,
        description="The representation format of the SNPs.",
    )
    snp_profile_hash_sha256: bytes = Field(
        description="The SHA256 hash of the ASCII lower case reference sequence with all SNPs applied.",
        min_length=32,
        max_length=32,
    )

    @field_validator("snp_profile_hash_sha256", mode="before")
    def _validate_snp_profile_hash_sha256(cls, value: str | bytes) -> bytes:
        if isinstance(value, str):
            value = bytes.fromhex(value)
        return value

    @field_serializer("snp_profile_format", mode="plain")
    def _serialize_snp_profile_format(self, value: str | enum.SnpProfileFormat) -> str:
        if isinstance(value, enum.SnpProfileFormat):
            return value.value
        return value


class MlvaDetectionProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="mlva_detection_protocols",
        table_name="mlva_detection_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class MlvaProfile(Model, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="mlva_profiles",
        table_name="mlva_profile",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "seq_id",
                    "mlva_detection_protocol_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: (
                    "mlva_detection_protocol_id",
                    MlvaDetectionProtocol,
                    "mlva_detection_protocol",
                ),
            }
        ),
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    kmer_detection_protocol_id: UUID = Field(
        description="The unique identifier for the MLVA detection protocol. FOREIGN KEY"
    )
    mlva_detection_protocol: MlvaDetectionProtocol | None = Field(
        default=None, description="The MLVA detection protocol."
    )
    mlva_profile: str = Field(
        description="The MLVA detected in the sequence and their frequency."
    )
    mlva_profile_format: enum.MlvaProfileFormat = Field(
        default=enum.MlvaProfileFormat.MLVA_PROFILE_FORMAT1,
        description="The representation format of the MLVA.",
    )
    mlva_profile_hash_sha256: bytes = Field(
        description="The SHA256 hash of the ASCII sorted MLVA followed by their sorted frequencies as double precision floats.",
        min_length=32,
        max_length=32,
    )


class KmerDetectionProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="kmer_detection_protocols",
        table_name="kmer_detection_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class KmerProfile(Model, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="kmer_profiles",
        table_name="kmer_profile",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "seq_id",
                    "kmer_detection_protocol_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: (
                    "kmer_detection_protocol_id",
                    KmerDetectionProtocol,
                    "kmer_detection_protocol",
                ),
            }
        ),
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    kmer_detection_protocol_id: UUID = Field(
        description="The unique identifier for the k-mer detection protocol. FOREIGN KEY"
    )
    kmer_detection_protocol: KmerDetectionProtocol | None = Field(
        default=None, description="The k-mer detection protocol."
    )
    kmer_profile: str = Field(
        description="The k-mers detected in the sequence and their frequency."
    )
    kmer_profile_format: enum.KmerProfileFormat = Field(
        default=enum.KmerProfileFormat.KMER_PROFILE_FORMAT1,
        description="The representation format of the k-mers.",
    )
    kmer_profile_hash_sha256: bytes = Field(
        description="The SHA256 hash of the ASCII sorted k-mers followed by their sorted frequencies as double precision floats.",
        min_length=32,
        max_length=32,
    )


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

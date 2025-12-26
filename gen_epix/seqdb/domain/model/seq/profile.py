import base64
import hashlib
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, field_serializer, model_validator

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import ProtocolMixin, QualityMixin
from gen_epix.seqdb.domain.model.seq.locus import LocusSet
from gen_epix.seqdb.domain.model.seq.sample import HasSampleMixin, Sample
from gen_epix.seqdb.domain.model.seq.seq import RefSeq, RefSnp, Seq


class LocusDetectionProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_detection_protocols",
        table_name="locus_detection_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class LocusProfile(Model, HasSampleMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_profiles",
        table_name="locus_profile",
        persistable=True,
        keys=create_keys(
            {1: ("seq_id", "locus_set_id", "locus_detection_protocol_id")}
        ),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: ("locus_set_id", LocusSet, "locus_set"),
                4: (
                    "locus_detection_protocol_id",
                    LocusDetectionProtocol,
                    "locus_detection_protocol",
                ),
            }
        ),
    )
    seq_id: UUID | None = Field(
        description="The unique identifier for the sequence that the result was derived from, if available. FOREIGN KEY"
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
    locus_profile: str = Field(
        description="The loci detected in the sequence, including their start and stop positions."
    )
    locus_profile_format: enum.LocusProfileFormat = Field(
        default=enum.LocusProfileFormat.LOCUS_PROFILE_FORMAT1,
        description="The representation format of the loci.",
    )
    locus_profile_hash: UUID = Field(
        description="The first 128 bits of the SHA256 hash of the sorted list of allele ids as bytes.",
    )

    @field_serializer("locus_profile_hash")
    def _serialize_locus_profile_hash(self, value: UUID) -> str:
        return str(value)


class AlleleProfile(Model, HasSampleMixin, QualityMixin):
    """
    An allele profile derived from a sequence for a given locus set and locus
    detection protocol. The class includes validation logic to ensure consistency
    between the profile, its format, number of detected loci, and derived profile hash.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="allele_profiles",
        table_name="allele_profile",
        persistable=True,
        keys=create_keys(
            {1: ("sample_id", "seq_id", "locus_set_id", "locus_detection_protocol_id")}
        ),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: ("locus_set_id", LocusSet, "locus_set"),
                4: (
                    "locus_detection_protocol_id",
                    LocusDetectionProtocol,
                    "locus_detection_protocol",
                ),
            }
        ),
    )
    seq_id: UUID | None = Field(
        description="The unique identifier for the sequence that the result was derived from, if available. FOREIGN KEY"
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
    n_loci: int = Field(
        default=0,
        description="The number of detected loci. Derived from the profile if possible and if the value is set to zero. If set to zero and it is not possible to derive the value, an error is raised.",
        ge=0,
    )
    allele_profile: str = Field(
        description="The alleles detected in the sequence for the loci in the locus set."
    )
    allele_profile_format: enum.AlleleProfileFormat = Field(
        default=enum.AlleleProfileFormat.SORTED_ALLELE_IDS,
        description="The representation format of the alleles.",
    )
    allele_profile_hash: UUID = Field(
        default=NULL_ID,
        description="The first 128 bits of the SHA256 hash of the sorted list of allele ids, including null alleles (null ID) as bytes. Derived from the allele profile if possible and if the value is the null ID. If set to the null ID and it is not possible to derive the value, an error is raised.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Derive the allele profile hash, if not provided, or otherwise verify that it is
        correctly derived if possible. Also derive n_loci if set to zero.
        """
        profile_hash = self.allele_profile_hash

        # Parse allele profile and derive values depending on allele_profile_format
        if self.allele_profile_format == enum.AlleleProfileFormat.SORTED_ALLELE_IDS:
            # Parse the allele profile from base64 encoded concatenated 128-bit allele IDs
            allele_bytes = base64.b64decode(self.allele_profile)
            if len(allele_bytes) % 16 != 0:
                raise ValueError("Allele profile bytes length is not a multiple of 16")
            sha256 = hashlib.sha256()
            sha256.update(allele_bytes)
            computed_profile_hash = UUID(sha256.digest()[:16].hex())
            computed_n_loci = sum(
                allele_bytes[i : i + 16] != NULL_ID.bytes
                for i in range(0, len(allele_bytes), 16)
            )
        else:
            if profile_hash is None:
                raise ValueError(
                    "Unable to calculate allele profile hash for this format"
                )
            # Unable to compute n_loci or profile hash but provided -> assume correct
            computed_n_loci = self.n_loci
            computed_profile_hash = profile_hash

        # Set or verify n_loci
        if self.n_loci == 0:
            if computed_n_loci == 0:
                raise ValueError("Unable to calculate number of loci")
            self.n_loci = computed_n_loci
        elif self.n_loci != computed_n_loci:
            raise ValueError(
                f"Provided n_loci does not match computed n_loci: {self.n_loci} != {computed_n_loci}"
            )

        # Set or verify allele_profile_hash
        if profile_hash is None:
            self.allele_profile_hash = computed_profile_hash
        elif profile_hash != computed_profile_hash:
            raise ValueError(
                "Provided allele profile hash does not match computed hash"
            )

        return self

    @field_serializer("allele_profile_hash")
    def _serialize_allele_profile_hash(self, value: UUID) -> str:
        return str(value)

    @field_serializer("allele_profile_format", mode="plain")
    def _serialize_snp_profile_format(
        self, value: str | enum.AlleleProfileFormat
    ) -> str:
        if isinstance(value, enum.AlleleProfileFormat):
            return value.value
        return value

    @staticmethod
    def get_allele_profile_hash(allele_ids: list[UUID | None]) -> UUID:
        sha256 = hashlib.sha256()
        sha256.update(b"".join(sorted([x.bytes for x in allele_ids if x is not None])))
        return UUID(sha256.digest()[:16].hex())


class SnpDetectionProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="snp_detection_protocols",
        table_name="snp_detection_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class SnpProfile(Model, HasSampleMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="snp_profiles",
        table_name="snp_profile",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "sample_id",
                    "seq_id",
                    "ref_seq_id",
                    "snp_detection_protocol_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: ("ref_seq_id", RefSeq, "ref_seq"),
                4: (
                    "snp_detection_protocol_id",
                    SnpDetectionProtocol,
                    "snp_detection_protocol",
                ),
            }
        ),
    )
    seq_id: UUID | None = Field(
        description="The unique identifier for the sequence that the result was derived from, if available. FOREIGN KEY"
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
    snp_profile_hash: UUID = Field(
        description="The first 128 bits of the SHA256 hash of the ASCII lower case reference sequence with all SNPs applied.",
    )

    @field_serializer("snp_profile_hash")
    def _serialize_snp_profile_hash(self, value: UUID) -> str:
        return str(value)

    @field_serializer("snp_profile_format", mode="plain")
    def _serialize_snp_profile_format(self, value: enum.SnpProfileFormat) -> str:
        return value.value


class MlvaDetectionProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="mlva_detection_protocols",
        table_name="mlva_detection_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class MlvaProfile(Model, HasSampleMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="mlva_profiles",
        table_name="mlva_profile",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "sample_id",
                    "seq_id",
                    "mlva_detection_protocol_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: (
                    "mlva_detection_protocol_id",
                    MlvaDetectionProtocol,
                    "mlva_detection_protocol",
                ),
            }
        ),
    )
    seq_id: UUID | None = Field(
        description="The unique identifier for the sequence that the result was derived from, if available. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    mlva_detection_protocol_id: UUID = Field(
        description="The unique identifier for the MLVA detection protocol. FOREIGN KEY"
    )
    mlva_detection_protocol: MlvaDetectionProtocol | None = Field(
        default=None, description="The MLVA detection protocol."
    )
    mlva_profile: str = Field(description="The number of tandem repeats per locus.")
    mlva_profile_format: enum.MlvaProfileFormat = Field(
        default=enum.MlvaProfileFormat.MLVA_PROFILE_FORMAT1,
        description="The representation format of the profile.",
    )
    mlva_profile_hash: UUID = Field(
        description="The first 128 bits of the SHA256 hash of the ASCII sorted loci followed by their corresponding sorted counts as 32 bit signed integers.",
    )

    @field_serializer("mlva_profile_hash")
    def _serialize_mlva_profile_hash(self, value: UUID) -> str:
        return str(value)


class KmerDetectionProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="kmer_detection_protocols",
        table_name="kmer_detection_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class KmerProfile(Model, HasSampleMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="kmer_profiles",
        table_name="kmer_profile",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "sample_id",
                    "seq_id",
                    "kmer_detection_protocol_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: (
                    "kmer_detection_protocol_id",
                    KmerDetectionProtocol,
                    "kmer_detection_protocol",
                ),
            }
        ),
    )
    seq_id: UUID | None = Field(
        description="The unique identifier for the sequence that the result was derived from, if available. FOREIGN KEY"
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
    kmer_profile_hash: UUID = Field(
        description="The first 128 bits of the SHA256 hash of the ASCII sorted k-mers followed by their correspondingsorted frequencies as double precision floats.",
    )

    @field_serializer("kmer_profile_hash")
    def _serialize_kmer_profile_hash(self, value: UUID) -> str:
        return str(value)


class CompleteAlleleProfile(Model, HasSampleMixin):
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


class CompleteSnpProfile(Model, HasSampleMixin):
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

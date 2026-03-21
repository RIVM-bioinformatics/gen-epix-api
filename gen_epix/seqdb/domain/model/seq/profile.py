import base64
import hashlib
import json
import struct
from typing import Any, ClassVar, Self
from uuid import UUID

from pydantic import Field, field_serializer, model_validator

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import BaseIdentifier
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.literal import MLVA_NO_LOCUS_REPEAT_NUMBER
from gen_epix.seqdb.domain.model.seq.base import ContentMixin, QualityMixin
from gen_epix.seqdb.domain.model.seq.locus import LocusSet
from gen_epix.seqdb.domain.model.seq.protocol import HasProtocolMixin, Protocol
from gen_epix.seqdb.domain.model.seq.ref_seq import RefSeq
from gen_epix.seqdb.domain.model.seq.sample import HasSampleMixin, Sample
from gen_epix.seqdb.domain.model.seq.seq import HasSeqMixin, Seq


class SeqProfile(
    Model,
    HasSampleMixin,
    HasSeqMixin,
    HasProtocolMixin,
    ContentMixin[enum.SeqProfileFormat],
    QualityMixin,
):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_profiles",
        table_name="seq_profile",
        persistable=True,
        keys=create_keys({1: ("seq_id", "protocol_id")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: (
                    "protocol_id",
                    Protocol,
                    "protocol",
                ),
            }
        ),
    )
    FORMATS_BY_SEQ_PROFILE_TYPE: ClassVar[
        dict[enum.SeqProfileType, frozenset[enum.SeqProfileFormat]]
    ] = {
        enum.SeqProfileType.LOCUS: frozenset(
            {
                enum.SeqProfileFormat.LOCUS_PROFILE_FORMAT1,
            }
        ),
        enum.SeqProfileType.ALLELE: frozenset(
            {
                enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            }
        ),
        enum.SeqProfileType.SNP: frozenset(
            {
                enum.SeqProfileFormat.REF_ALN_SEQ,
            }
        ),
        enum.SeqProfileType.MLVA: frozenset(
            {
                enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
            }
        ),
        enum.SeqProfileType.KMER: frozenset(
            {
                enum.SeqProfileFormat.KMER_FREQUENCY_MAP,
            }
        ),
    }

    seq_profile_type: enum.SeqProfileType = Field(
        description="The type of the sequence profile."
    )

    @model_validator(mode="after")
    def _validate_seq_profile_type(self) -> Self:
        """
        Validate that the content format is compatible with the sequence profile type.
        """
        if self.format not in self.FORMATS_BY_SEQ_PROFILE_TYPE[self.seq_profile_type]:
            raise ValueError(
                f"Invalid format {self.format} for sequence profile type {self.seq_profile_type}"
            )
        return self

    @field_serializer("seq_profile_type")
    def _serialize_seq_profile_type(self, value: enum.SeqProfileType) -> int:
        return value.value


class LocusProfile(Model, HasSampleMixin, HasSeqMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="locus_profiles",
        table_name="locus_profile",
        persistable=True,
        keys=create_keys({1: ("seq_id", "locus_set_id", "protocol_id")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: ("locus_set_id", LocusSet, "locus_set"),
                4: (
                    "protocol_id",
                    Protocol,
                    "protocol",
                ),
            }
        ),
    )
    locus_set_id: UUID = Field(
        description="The unique identifier for the locus set. FOREIGN KEY"
    )
    locus_set: LocusSet | None = Field(default=None, description="The locus set.")
    protocol_id: UUID = Field(
        description="The unique identifier for the locus detection protocol. FOREIGN KEY"
    )
    protocol: Protocol | None = Field(
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


class LocusProfileIdentifier(BaseIdentifier):
    ENTITY: ClassVar = BaseIdentifier.create_entity(
        LocusProfile,
        relationship_field_name="locus_profile",
        snake_case_plural_name="locus_profile_identifiers",
        table_name="locus_profile_identifier",
    )
    NAME: ClassVar = "LocusProfileIdentifier"
    MODEL_CLASS: ClassVar = LocusProfile

    locus_profile: LocusProfile | None = Field(
        default=None, description="The locus profile associated with this identifier."
    )


class AlleleProfile(Model, HasSampleMixin, HasSeqMixin, QualityMixin):
    """
    An allele profile derived from a sequence for a given locus set and protocol.
    The class includes validation logic to ensure consistency
    between the profile, its format, number of detected loci, and derived profile hash.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="allele_profiles",
        table_name="allele_profile",
        persistable=True,
        keys=create_keys({1: ("sample_id", "seq_id", "locus_set_id", "protocol_id")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: ("locus_set_id", LocusSet, "locus_set"),
                4: (
                    "protocol_id",
                    Protocol,
                    "protocol",
                ),
            }
        ),
    )
    locus_set_id: UUID = Field(
        description="The unique identifier for the locus set. FOREIGN KEY"
    )
    locus_set: LocusSet | None = Field(default=None, description="The locus set.")
    protocol_id: UUID = Field(
        description="The unique identifier for the protocol. FOREIGN KEY"
    )
    protocol: Protocol | None = Field(default=None, description="The protocol.")
    n_loci: int = Field(
        default=0,
        description="The number of detected loci. Derived from the profile if possible and if the value is set to zero. If set to zero and it is not possible to derive the value, an error is raised.",
        ge=0,
    )
    allele_profile: str = Field(
        description="String representation of the alleles detected in the sequence for the loci in the locus set, with the format depending on allele_profile_format."
    )
    allele_profile_format: enum.AlleleProfileFormat = Field(
        default=enum.AlleleProfileFormat.ORDERED_ALLELE_IDS,
        description="The representation format of the alleles.",
    )
    allele_profile_hash: UUID = Field(
        default=NULL_ID,
        description="The first 128 bits of the SHA256 hash of the list allele ids ordered by locus set loci, and including null alleles (null ID) as bytes. Derived from the allele profile if possible and if the value is the null ID. If set to the null ID and it is not possible to derive the value, an error is raised.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Derive the allele profile hash, if not provided, or otherwise verify that it is
        correctly derived if possible. Also derive n_loci if set to zero.
        """
        profile_hash = self.allele_profile_hash

        # Parse allele profile and derive values depending on allele_profile_format
        if self.allele_profile_format == enum.AlleleProfileFormat.ORDERED_ALLELE_IDS:
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
            if profile_hash == NULL_ID:
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
        if profile_hash == NULL_ID:
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
    def _serialize_allele_profile_format(self, value: enum.AlleleProfileFormat) -> int:
        return int(value)

    def get_allele_ids(self, **kwargs: Any) -> list[UUID | None]:
        """
        Parse and return the allele IDs from the allele profile based on its format.
        """
        n_loci = self.n_loci
        allele_ids: list[UUID | None] = [None] * n_loci
        if self.allele_profile_format == enum.AlleleProfileFormat.ORDERED_ALLELE_IDS:
            allele_bytes = base64.b64decode(self.allele_profile)
            null_id_bytes = NULL_ID.bytes
            for i, j in zip(range(0, len(allele_bytes), 16), range(n_loci)):
                allele_id_bytes = allele_bytes[i : i + 16]
                if allele_id_bytes != null_id_bytes:
                    allele_ids[j] = UUID(bytes=allele_id_bytes)
        else:
            raise NotImplementedError(
                "Unable to parse allele IDs for this allele profile format"
            )
        return allele_ids

    @staticmethod
    def get_sorted_allele_ids_profile(allele_ids: list[UUID | None]) -> str:
        """
        Generate and return the allele profile in SORTED_ALLELE_IDS format based on
        the sorted allele IDs.
        """
        return base64.b64encode(
            b"".join(NULL_ID.bytes if x is None else x.bytes for x in allele_ids)
        ).decode("ascii")

    @staticmethod
    def get_allele_profile_hash(allele_ids: list[UUID | None]) -> UUID:
        sha256 = hashlib.sha256()
        for allele_id in allele_ids:
            if allele_id is not None:
                sha256.update(allele_id.bytes)
            else:
                sha256.update(NULL_ID.bytes)
        return UUID(sha256.digest()[:16].hex())


class AlleleProfileIdentifier(BaseIdentifier):
    ENTITY: ClassVar = BaseIdentifier.create_entity(
        AlleleProfile,
        relationship_field_name="allele_profile",
        snake_case_plural_name="allele_profile_identifiers",
        table_name="allele_profile_identifier",
    )
    NAME: ClassVar = "AlleleProfileIdentifier"
    MODEL_CLASS: ClassVar = AlleleProfile

    allele_profile: AlleleProfile | None = Field(
        default=None, description="The allele profile associated with this identifier."
    )


class SnpProfile(Model, HasSampleMixin, HasSeqMixin, QualityMixin):
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
                    "protocol_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: ("ref_seq_id", RefSeq, "ref_seq"),
                4: (
                    "protocol_id",
                    Protocol,
                    "protocol",
                ),
            }
        ),
    )
    ref_seq_id: UUID = Field(
        description="The unique identifier for the reference sequence. FOREIGN KEY"
    )
    ref_seq: RefSeq | None = Field(default=None, description="The reference sequence.")
    protocol_id: UUID = Field(
        description="The unique identifier for the protocol. FOREIGN KEY"
    )
    protocol: Protocol | None = Field(default=None, description="The protocol.")
    snp_profile: str = Field(description="The SNPs detected in the sequence.")
    snp_profile_format: enum.SnpProfileFormat = Field(
        default=enum.SnpProfileFormat.REF_ALN_SEQ,
        description="The representation format of the SNPs.",
    )
    snp_profile_hash: UUID = Field(
        description="The first 128 bits of the SHA256 hash of the ASCII lower case reference sequence with all SNPs applied.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Derive the SNP profile hash, if not provided, or otherwise verify that it is
        correctly derived if possible.
        """
        profile_hash = self.snp_profile_hash

        # Parse SNP profile and derive values depending on snp_profile_format
        if self.snp_profile_format == enum.SnpProfileFormat.REF_ALN_SEQ:
            # TODO: implement any validation and calculate hash
            computed_profile_hash = profile_hash
        else:
            if profile_hash == NULL_ID:
                raise ValueError("Unable to calculate SNP profile hash for this format")
            # Unable to compute profile hash but provided -> assume correct
            computed_profile_hash = profile_hash

        # Set or verify snp_profile_hash
        if profile_hash == NULL_ID:
            self.snp_profile_hash = computed_profile_hash
        elif profile_hash != computed_profile_hash:
            raise ValueError("Provided SNP profile hash does not match computed hash")

        return self

    @field_serializer("snp_profile_hash")
    def _serialize_snp_profile_hash(self, value: UUID) -> str:
        return str(value)

    @field_serializer("snp_profile_format", mode="plain")
    def _serialize_snp_profile_format(self, value: enum.SnpProfileFormat) -> int:
        return int(value)

    def get_aligned_nucleotide_seq(self, **kwargs: Any) -> str:
        """
        Parse and return the aligned nucleotide sequence from the SNP profile based on
        its format.
        """
        if self.snp_profile_format == enum.SnpProfileFormat.REF_ALN_SEQ:
            return self.snp_profile
        else:
            raise NotImplementedError(
                "Unable to parse aligned nucleotide sequence for this SNP profile format"
            )


class SnpProfileIdentifier(BaseIdentifier):
    ENTITY: ClassVar = BaseIdentifier.create_entity(
        SnpProfile,
        relationship_field_name="snp_profile",
        snake_case_plural_name="snp_profile_identifiers",
        table_name="snp_profile_identifier",
    )
    NAME: ClassVar = "SnpProfileIdentifier"
    MODEL_CLASS: ClassVar = SnpProfile

    snp_profile: SnpProfile | None = Field(
        default=None, description="The SNP profile associated with this identifier."
    )


class MlvaProfile(Model, HasSampleMixin, HasSeqMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="mlva_profiles",
        table_name="mlva_profile",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "sample_id",
                    "seq_id",
                    "protocol_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: ("locus_set_id", LocusSet, "locus_set"),
                4: (
                    "protocol_id",
                    Protocol,
                    "protocol",
                ),
            }
        ),
    )
    protocol_id: UUID = Field(
        description="The unique identifier for the protocol. FOREIGN KEY"
    )
    protocol: Protocol | None = Field(default=None, description="The protocol.")
    locus_set_id: UUID = Field(
        description="The unique identifier for the locus set. FOREIGN KEY"
    )
    locus_set: LocusSet | None = Field(default=None, description="The locus set.")
    mlva_profile: str = Field(
        description="String representation of the repeat number per locus in the locus set, with the format depending on mlva_profile_format."
    )
    mlva_profile_format: enum.MlvaProfileFormat = Field(
        default=enum.MlvaProfileFormat.ORDERED_REPEAT_NUMBERS,
        description="The representation format of the profile.",
    )
    mlva_profile_hash: UUID = Field(
        default=NULL_ID,
        description="The first 128 bits of the SHA256 hash of the repeat numbers ordered by locus set loci, as 4-byte big-endian signed integers.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Derive the MLVA profile hash, if not provided, or otherwise verify that it is
        correctly derived if possible.
        """
        profile_hash = self.mlva_profile_hash

        # Parse MLVA profile and derive values depending on mlva_profile_format
        if self.mlva_profile_format == enum.MlvaProfileFormat.ORDERED_REPEAT_NUMBERS:
            # Parse the MLVA profile from json array
            repeat_numbers: list[int] = json.loads(self.mlva_profile)
            # Compute hash
            computed_profile_hash = MlvaProfile.get_mlva_profile_hash(repeat_numbers)
        else:
            if profile_hash == NULL_ID:
                raise ValueError(
                    "Unable to calculate allele profile hash for this format"
                )
            # Unable to compute n_loci or profile hash but provided -> assume correct
            computed_profile_hash = profile_hash

        # Set or verify mlva_profile_hash
        if profile_hash == NULL_ID:
            self.mlva_profile_hash = computed_profile_hash
        elif profile_hash != computed_profile_hash:
            raise ValueError("Provided MLVA profile hash does not match computed hash")

        return self

    @field_serializer("mlva_profile_hash")
    def _serialize_mlva_profile_hash(self, value: UUID) -> str:
        return str(value)

    @field_serializer("mlva_profile_format", mode="plain")
    def _serialize_mlva_profile_format(self, value: enum.MlvaProfileFormat) -> int:
        return int(value)

    def get_repeat_numbers(self, **kwargs: Any) -> list[int]:
        """
        Parse and return the repeat numbers from the MLVA profile based on its format.
        """
        if self.mlva_profile_format == enum.MlvaProfileFormat.ORDERED_REPEAT_NUMBERS:
            return json.loads(self.mlva_profile)
        else:
            raise NotImplementedError(
                "Unable to parse repeat numbers for this MLVA profile format"
            )

    @staticmethod
    def get_sorted_repeat_numbers_profile(repeat_numbers: list[int | None]) -> str:
        """
        Generate and return the MLVA profile in SORTED_REPEAT_NUMBERS format based on
        the sorted repeat numbers.
        """
        return json.dumps(
            [
                int(x) if x is not None else MLVA_NO_LOCUS_REPEAT_NUMBER
                for x in repeat_numbers
            ]
        )

    @staticmethod
    def get_mlva_profile_hash(repeat_numbers: list[int | None]) -> UUID:
        sha256 = hashlib.sha256()
        for repeat_number in repeat_numbers:
            if repeat_number is not None:
                sha256.update(repeat_number.to_bytes(4, byteorder="big", signed=True))
            else:
                sha256.update(
                    MLVA_NO_LOCUS_REPEAT_NUMBER.to_bytes(
                        4, byteorder="big", signed=True
                    )
                )
        return UUID(sha256.digest()[:16].hex())


class MlvaProfileIdentifier(BaseIdentifier):
    ENTITY: ClassVar = BaseIdentifier.create_entity(
        MlvaProfile,
        relationship_field_name="mlva_profile",
        snake_case_plural_name="mlva_profile_identifiers",
        table_name="mlva_profile_identifier",
    )
    NAME: ClassVar = "MlvaProfileIdentifier"
    MODEL_CLASS: ClassVar = MlvaProfile

    mlva_profile: MlvaProfile | None = Field(
        default=None, description="The MLVA profile associated with this identifier."
    )


class KmerProfile(Model, HasSampleMixin, HasSeqMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="kmer_profiles",
        table_name="kmer_profile",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "sample_id",
                    "seq_id",
                    "protocol_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: (
                    "protocol_id",
                    Protocol,
                    "protocol",
                ),
            }
        ),
    )
    protocol_id: UUID = Field(
        description="The unique identifier for the protocol. FOREIGN KEY"
    )
    protocol: Protocol | None = Field(default=None, description="The protocol.")
    kmer_profile: str = Field(
        description="The k-mers detected in the sequence and their frequency."
    )
    kmer_profile_format: enum.KmerProfileFormat = Field(
        default=enum.KmerProfileFormat.KMER_FREQUENCY_MAP,
        description="The representation format of the k-mers.",
    )
    kmer_profile_hash: UUID = Field(
        description="The first 128 bits of the SHA256 hash of the ASCII sorted k-mers followed by their corresponding sorted frequencies as double precision floats.",
    )

    @field_serializer("kmer_profile_hash")
    def _serialize_kmer_profile_hash(self, value: UUID) -> str:
        return str(value)

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Validate the k-mer profile and derive the k-mer profile hash if not provided.
        """
        profile_hash = self.kmer_profile_hash

        # Parse k-mer profile and derive hash depending on kmer_profile_format
        if self.kmer_profile_format == enum.KmerProfileFormat.KMER_FREQUENCY_MAP:
            # Parse the k-mer profile from json object
            kmer_frequency_map: dict[str, float] = json.loads(self.kmer_profile)
            # Compute hash
            computed_profile_hash = KmerProfile.get_kmer_profile_hash(
                kmer_frequency_map
            )
        else:
            if profile_hash == NULL_ID:
                raise ValueError(
                    "Unable to calculate k-mer profile hash for this format"
                )
            # Unable to compute profile hash but provided -> assume correct
            computed_profile_hash = profile_hash
        self.kmer_profile_hash = computed_profile_hash
        return self

    def get_kmer_frequency_map(self, **kwargs: Any) -> dict[str, float]:
        """
        Parse and return the k-mer frequency map from the k-mer profile based on its format.
        """
        if self.kmer_profile_format == enum.KmerProfileFormat.KMER_FREQUENCY_MAP:
            retval: dict[str, float] = json.loads(self.kmer_profile)
            return retval
        else:
            raise NotImplementedError(
                "Unable to parse k-mer frequency map for this k-mer profile format"
            )

    @staticmethod
    def get_kmer_profile_hash(kmer_frequency_map: dict[str, float]) -> UUID:
        sha256 = hashlib.sha256()
        for kmer in sorted(kmer_frequency_map.keys()):
            freq = kmer_frequency_map[kmer]
            sha256.update(kmer.encode("ascii"))
            sha256.update(bytearray(struct.pack(">d", freq)))
        return UUID(sha256.digest()[:16].hex())


class KmerProfileIdentifier(BaseIdentifier):
    ENTITY: ClassVar = BaseIdentifier.create_entity(
        KmerProfile,
        relationship_field_name="kmer_profile",
        snake_case_plural_name="kmer_profile_identifiers",
        table_name="kmer_profile_identifier",
    )
    NAME: ClassVar = "KmerProfileIdentifier"
    MODEL_CLASS: ClassVar = KmerProfile

    kmer_profile: KmerProfile | None = Field(
        default=None, description="The k-mer profile associated with this identifier."
    )

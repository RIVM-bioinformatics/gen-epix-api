import base64
import hashlib
import json
import struct
from typing import Any, ClassVar, Self
from uuid import UUID

from pydantic import Field, field_serializer, field_validator, model_validator

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import Model, validate_int_enum_value
from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import BaseIdentifier
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.literal import MLVA_NO_LOCUS_REPEAT_NUMBER
from gen_epix.seqdb.domain.model.seq.base import ContentMixin, QualityMixin
from gen_epix.seqdb.domain.model.seq.protocol import HasProtocolMixin, Protocol
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

    @field_validator("seq_profile_type", mode="before")
    @classmethod
    def _validate_seq_profile_type(
        cls, value: str | int | float | enum.SeqProfileType
    ) -> enum.SeqProfileType:
        return validate_int_enum_value(enum.SeqProfileType, value)  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_format_for_seq_profile_type(self) -> Self:
        """
        Validate that the content format is compatible with the sequence profile type.
        """
        if self.format not in self.FORMATS_BY_SEQ_PROFILE_TYPE[self.seq_profile_type]:
            raise ValueError(
                f"Invalid format {self.format} for sequence profile type {self.seq_profile_type}"
            )
        return self

    @model_validator(mode="after")
    def _validate_content(self) -> Self:
        """
        Verify the representation of the content depending on the format. Verify or set
        the content hash.
        """
        if self.content == "" and any(
            getattr(self, field_name, None) is not None
            for field_name in (
                "aligned_nucleotide_seq",
                "allele_ids",
                "locus_allele_id_map",
                "repeat_numbers",
                "locus_repeat_number_map",
                "kmer_frequency_map",
            )
        ):
            return self

        profile_hash = self.content_hash
        computed_profile_hash = profile_hash
        if self.seq_profile_type == enum.SeqProfileType.LOCUS:
            if self.format == enum.SeqProfileFormat.LOCUS_PROFILE_FORMAT1:
                # TODO: implement calculation of hash based on the content of the locus profile
                computed_profile_hash = profile_hash
            else:
                if profile_hash == NULL_ID:
                    raise ValueError(
                        "Unable to calculate locus profile hash for this format"
                    )
        elif self.seq_profile_type == enum.SeqProfileType.ALLELE:
            # Parse allele profile and derive values depending on allele_profile_format
            if self.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
                # Parse the profile from base64 encoded concatenated 128-bit allele IDs
                allele_bytes = base64.b64decode(self.content)
                if len(allele_bytes) % 16 != 0:
                    raise ValueError(
                        "Allele profile bytes length is not a multiple of 16"
                    )
                sha256 = hashlib.sha256()
                sha256.update(allele_bytes)
                computed_profile_hash = UUID(sha256.digest()[:16].hex())
            else:
                SeqProfile._raise_no_computable_hash()
        elif self.seq_profile_type == enum.SeqProfileType.MLVA:
            # Parse MLVA SeqProfile and derive values depending on format
            if self.format == enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS:
                # Parse the profile from json array
                repeat_numbers: list[int] = json.loads(self.content)
                # Compute hash
                computed_profile_hash = SeqProfile.get_mlva_profile_hash(repeat_numbers)
            else:
                SeqProfile._raise_no_computable_hash()
        elif self.seq_profile_type == enum.SeqProfileType.KMER:
            # Parse KMER SeqProfile and derive hash depending on format
            if self.format == enum.SeqProfileFormat.KMER_FREQUENCY_MAP:
                # Parse the profile from json object
                kmer_frequency_map: dict[str, float] = json.loads(self.content)
                # Compute hash
                computed_profile_hash = SeqProfile.get_kmer_profile_hash(
                    kmer_frequency_map
                )
            else:
                SeqProfile._raise_no_computable_hash()
        elif self.seq_profile_type == enum.SeqProfileType.SNP:
            # Parse SNP profile and derive values depending on snp_profile_format
            if self.format == enum.SeqProfileFormat.REF_ALN_SEQ:
                # TODO: implement any validation and calculate hash
                computed_profile_hash = profile_hash
            else:
                SeqProfile._raise_no_computable_hash()
        else:
            raise NotImplementedError(
                f"Unable to calculate profile hash for this sequence profile type: {self.seq_profile_type}"
            )
        if profile_hash == NULL_ID:
            self.content_hash = computed_profile_hash
        elif profile_hash != computed_profile_hash:
            raise ValueError("Provided content hash does not match computed hash")
        return self

    @field_serializer("seq_profile_type", mode="plain")
    def _serialize_seq_profile_type(self, value: enum.SeqProfileType) -> int:
        return value.value

    def get_aligned_nucleotide_seq(
        self, ref_seq_str: str | None = None, **kwargs: Any
    ) -> str:
        """
        Parse and return the aligned nucleotide sequence from the SNP profile based on its
        format. The sequence is guaranteed to be lower case.
        """
        if self.seq_profile_type != enum.SeqProfileType.SNP:
            raise ValueError(
                "Aligned nucleotide sequence can only be retrieved for SNP profiles"
            )
        if self.format == enum.SeqProfileFormat.REF_ALN_SEQ:
            seq = self.content
            if not seq:
                raise ValueError("Empty aligned nucleotide sequence")
            invalid = set(seq) - enum.SeqAlphabet.DNA_INCL_AMBIGUOUS_AND_GAP.value
            if invalid:
                raise ValueError(
                    "Invalid characters in aligned"
                    " nucleotide sequence:"
                    f" {sorted(invalid)}"
                )
            return seq
        raise NotImplementedError(
            "Unable to parse aligned nucleotide" " sequence for this SNP profile format"
        )

    def get_allele_id_bytes(self, **kwargs: Any) -> list[bytes | None]:
        """Return allele IDs as raw 16-byte chunks."""
        if self.seq_profile_type != enum.SeqProfileType.ALLELE:
            raise ValueError("Allele IDs can only be retrieved for allele profiles")
        if self.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
            allele_bytes = base64.b64decode(self.content)
            n_loci = len(allele_bytes) // 16
            result: list[bytes | None] = [None] * n_loci
            null_id_bytes = NULL_ID.bytes
            for i in range(n_loci):
                offset = i * 16
                chunk = allele_bytes[offset : offset + 16]
                if chunk != null_id_bytes:
                    result[i] = chunk
            return result
        raise NotImplementedError(
            "Unable to parse allele IDs for this allele profile format"
        )

    def get_allele_ids(self, **kwargs: Any) -> list[UUID | None]:
        """
        Parse and return the allele IDs from the allele profile based on its format.
        """
        if self.seq_profile_type != enum.SeqProfileType.ALLELE:
            raise ValueError("Allele IDs can only be retrieved for allele profiles")

        if self.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
            allele_bytes = base64.b64decode(self.content)
            n_loci = len(allele_bytes) // 16
            allele_ids: list[UUID | None] = [None] * n_loci
            null_id_bytes = NULL_ID.bytes
            for i, j in zip(range(0, len(allele_bytes), 16), range(n_loci)):
                allele_id_bytes = allele_bytes[i : i + 16]
                if allele_id_bytes != null_id_bytes:
                    allele_ids[j] = UUID(bytes=allele_id_bytes)
            return allele_ids
        raise NotImplementedError(
            "Unable to parse allele IDs for this allele profile format"
        )

    def get_n_loci(self, **kwargs: Any) -> int:
        """
        Parse and return the number of loci from the allele profile based on its format.
        """
        if self.seq_profile_type != enum.SeqProfileType.ALLELE:
            raise ValueError("Number of loci can only be retrieved for allele profiles")
        if self.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
            allele_bytes = base64.b64decode(self.content)
            computed_n_loci = sum(
                allele_bytes[i : i + 16] != NULL_ID.bytes
                for i in range(0, len(allele_bytes), 16)
            )
            return computed_n_loci
        raise NotImplementedError(
            "Unable to parse number of loci for this allele profile format"
        )

    def get_repeat_numbers(self, **kwargs: Any) -> list[int]:
        """
        Parse and return the repeat numbers from the MLVA profile based on its format.
        """
        if self.format == enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS:
            return json.loads(self.content)
        raise NotImplementedError(
            "Unable to parse repeat numbers for this MLVA profile format"
        )

    def get_kmer_frequency_map(self, **kwargs: Any) -> dict[str, float]:
        """
        Parse and return the k-mer frequency map from the k-mer profile based on its format.
        """
        if self.format == enum.SeqProfileFormat.KMER_FREQUENCY_MAP:
            retval: dict[str, float] = json.loads(self.content)
            return retval
        raise NotImplementedError(
            "Unable to parse k-mer frequency map for this k-mer profile format"
        )

    @staticmethod
    def get_ordered_allele_ids_representation(allele_ids: list[UUID | None]) -> str:
        """
        Generate and return the allele profile in ORDERED_ALLELE_IDS format based on
        the ordered allele IDs.
        """
        return base64.b64encode(
            b"".join(NULL_ID.bytes if x is None else x.bytes for x in allele_ids)
        ).decode("ascii")

    @staticmethod
    def get_ordered_repeat_numbers_representation(
        repeat_numbers: list[int | None],
    ) -> str:
        """
        Generate and return the MLVA profile in ORDERED_REPEAT_NUMBERS format based on
        the ordered repeat numbers.
        """
        return json.dumps(
            [
                int(x) if x is not None else MLVA_NO_LOCUS_REPEAT_NUMBER
                for x in repeat_numbers
            ]
        )

    @staticmethod
    def get_allele_profile_hash(allele_ids: list[UUID | None]) -> UUID:
        sha256 = hashlib.sha256()
        for allele_id in allele_ids:
            if allele_id is not None:
                sha256.update(allele_id.bytes)
            else:
                sha256.update(NULL_ID.bytes)
        return UUID(sha256.digest()[:16].hex())

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

    @staticmethod
    def get_kmer_profile_hash(kmer_frequency_map: dict[str, float]) -> UUID:
        sha256 = hashlib.sha256()
        for kmer in sorted(kmer_frequency_map.keys()):
            freq = kmer_frequency_map[kmer]
            sha256.update(kmer.encode("ascii"))
            sha256.update(bytearray(struct.pack(">d", freq)))
        return UUID(sha256.digest()[:16].hex())

    @staticmethod
    def _raise_no_computable_hash() -> None:
        raise NotImplementedError("Unable to compute content hash for this format")


class SeqProfileIdentifier(BaseIdentifier):
    ENTITY: ClassVar = BaseIdentifier.create_entity(
        SeqProfile,
        relationship_field_name="seq_profile",
        snake_case_plural_name="seq_profile_identifiers",
        table_name="seq_profile_identifier",
    )
    NAME: ClassVar = "SeqProfileIdentifier"
    MODEL_CLASS: ClassVar = SeqProfile

    seq_profile: SeqProfile | None = Field(
        default=None,
        description="The sequence profile associated with this identifier.",
    )

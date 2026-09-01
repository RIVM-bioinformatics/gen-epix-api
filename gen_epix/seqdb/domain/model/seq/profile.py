"""Define seqdb domain models for domain.model.seq.profile."""

import base64
import hashlib
import json
import struct
from typing import Any, ClassVar, Self
from uuid import UUID

import numpy as np
from pydantic import Field, field_serializer, field_validator, model_validator

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import Model, validate_int_enum_value
from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import BaseIdentifier
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.fastapp.domain.util import create_multi_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.literal import (
    MLVA_NO_LOCUS_REPEAT_NUMBER,
    REQUIRED_NEXTCLADE_SEQ_KEYS,
)
from gen_epix.seqdb.domain.model.seq.base import ContentMixin, QualityMixin
from gen_epix.seqdb.domain.model.seq.locus import Allele, Locus
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
    """Store a typed sequence profile derived from a sequence and protocol.

    Model validation: The content format must match the profile type. Content is
    parsed according to that type, and its hash is derived or verified.

    Model serialization: The profile type is emitted as its integer enum value.
    """

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
        multi_links=create_multi_links([("content", Locus), ("content", Allele)]),
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
                enum.SeqProfileFormat.NEXTCLADE,
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
        """Normalize the profile type from its accepted enum representation."""
        return validate_int_enum_value(enum.SeqProfileType, value)  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_format_for_seq_profile_type(self) -> Self:
        """Validate that the content format matches the sequence profile type."""
        if self.format not in self.FORMATS_BY_SEQ_PROFILE_TYPE[self.seq_profile_type]:
            raise ValueError(
                f"Invalid format {self.format} for sequence profile type {self.seq_profile_type}"
            )
        return self

    @model_validator(mode="after")
    def _validate_content(self) -> Self:
        """Verify profile content and derive or validate its content hash.

        Upload-only alternate representations skip this validation until normalized.
        """
        # TODO: 3268: not sure why this is here since these fields do not exist. Perhaps because of SeqProfileForUpload having these fields?
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

        # Validate
        # TODO: 3268 changed meaning of functions from "compute hash" to in general "validate profile", and returning the hash as a by-product for further use (OK for private method)
        computed_content_hash = NULL_ID
        if self.seq_profile_type == enum.SeqProfileType.LOCUS:
            computed_content_hash = self._validate_locus_profile()
        elif self.seq_profile_type == enum.SeqProfileType.ALLELE:
            computed_content_hash = self._validate_allele_profile()
        elif self.seq_profile_type == enum.SeqProfileType.MLVA:
            computed_content_hash = self._validate_mlva_profile()
        elif self.seq_profile_type == enum.SeqProfileType.KMER:
            computed_content_hash = self._validate_kmer_profile()
        elif self.seq_profile_type == enum.SeqProfileType.SNP:
            computed_content_hash = self._validate_snp_profile()
        else:
            raise NotImplementedError(
                f"Unable to validate profile hash for this sequence profile type: {self.seq_profile_type}"
            )
        if self.content_hash == NULL_ID:
            self.content_hash = computed_content_hash
        elif self.content_hash != computed_content_hash:
            raise ValueError("Provided content hash does not match computed hash")
        return self

    def _validate_snp_profile(self) -> UUID:
        """Validate SNP content and derive its hash.

        Returns:
            The derived SNP profile hash.

        Raises:
            ValueError: If required NextClade fields are absent.
            NotImplementedError: If the content format cannot produce a hash.
        """
        computed_content_hash = NULL_ID
        if self.format == enum.SeqProfileFormat.NEXTCLADE:
            # content is a flat JSON dict of NextClade fields for this single sample
            nextclade_dict: dict[str, Any] = json.loads(self.content)
            # Validate required fields at the top level of the flat dict
            if any(key not in REQUIRED_NEXTCLADE_SEQ_KEYS for key in nextclade_dict):
                raise ValueError(
                    f"Missing required NextClade fields for SNP profile content with format {self.format}: {REQUIRED_NEXTCLADE_SEQ_KEYS}"
                )
            snps = self.get_snps()
            computed_content_hash = SeqProfile.get_snp_profile_hash(snps)
        else:
            SeqProfile._raise_no_computable_hash()
        return computed_content_hash

    def _validate_kmer_profile(self) -> UUID:
        """Validate the k-mer profile content."""
        computed_content_hash = NULL_ID
        if self.format == enum.SeqProfileFormat.KMER_FREQUENCY_MAP:
            # Parse the profile from json object
            kmer_frequency_map: dict[str, float] = json.loads(self.content)
            # Compute hash
            computed_content_hash = SeqProfile.get_kmer_profile_hash(kmer_frequency_map)
        else:
            SeqProfile._raise_no_computable_hash()

        return computed_content_hash

    def _validate_mlva_profile(self) -> UUID:
        """Validate the MLVA profile content."""
        computed_content_hash = NULL_ID
        if self.format == enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS:
            # Parse the profile from json array
            repeat_numbers: list[int | None] = json.loads(self.content)
            # Compute hash
            computed_content_hash = SeqProfile.get_mlva_profile_hash(repeat_numbers)
        else:
            SeqProfile._raise_no_computable_hash()
        return computed_content_hash

    def _validate_allele_profile(self) -> UUID:
        """Validate allele content and derive its hash.

        Returns:
            The derived allele profile hash.

        Raises:
            ValueError: If decoded allele content is not a multiple of 16 bytes.
            NotImplementedError: If the content format cannot produce a hash.
        """
        computed_content_hash = NULL_ID
        if self.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
            # Parse the profile from base64 encoded concatenated 128-bit allele IDs
            allele_bytes = base64.b64decode(self.content)
            if len(allele_bytes) % 16 != 0:
                raise ValueError("Allele profile bytes length is not a multiple of 16")
            sha256 = hashlib.sha256()
            sha256.update(allele_bytes)
            computed_content_hash = UUID(sha256.digest()[:16].hex())
        else:
            SeqProfile._raise_no_computable_hash()

        return computed_content_hash

    def _validate_locus_profile(self) -> UUID:
        """Report that locus-profile hash validation is not implemented.

        Returns:
            A profile hash, although this implementation never returns.

        Raises:
            NotImplementedError: Always, because locus-profile hashing is unsupported.
        """
        # TODO: 3268 just put a NotImplemented error here
        raise NotImplementedError(
            "Unable to validate locus profile content hash for this format"
        )

    @field_serializer("seq_profile_type", mode="plain")
    def _serialize_seq_profile_type(self, value: enum.SeqProfileType) -> int:
        """Serialize the profile type as its integer enum value."""
        return value.value

    def get_aligned_nucleotide_seq(
        self, ref_seq_str: str | None = None, **kwargs: Any
    ) -> str:
        """Return the lower-case aligned nucleotide sequence for an SNP profile.

        Args:
            ref_seq_str: Reserved reference sequence input.
            **kwargs: Reserved compatibility arguments.

        Returns:
            The stored aligned nucleotide sequence.

        Raises:
            ValueError: If this is not an SNP profile.
        """
        if self.seq_profile_type != enum.SeqProfileType.SNP:
            raise ValueError(
                "Aligned nucleotide sequence can only be retrieved for SNP profiles"
            )
        # TODO: LSP-3268-Implement-SNP-profile-support-seqdb:
        # - derive aligned nucleotide seq for SNP profiles format other than NextClade
        return self.content

    def get_allele_id_bytes(self, **kwargs: Any) -> list[bytes | None]:
        """Return ordered allele IDs as raw 16-byte chunks.

        Args:
            **kwargs: Reserved compatibility arguments.

        Returns:
            One UUID byte sequence or ``None`` for each locus.

        Raises:
            ValueError: If this is not an allele profile.
            NotImplementedError: If its allele representation is unsupported.
        """
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

    def get_allele_array(self) -> np.ndarray:
        r"""Return allele IDs as an (n_loci,) S16 numpy array.

        Each element is a 16-byte UUID; missing loci (null UUID) appear as
        b"\\x00" * 16 matching the _NULL_ALLELE sentinel in distance kernels.
        Zero-copy frombuffer view of the decoded base64 blob.

        Returns:
            A one-dimensional array of 16-byte allele identifiers.

        Raises:
            ValueError: If this is not an allele profile.
            NotImplementedError: If its allele representation is unsupported.
        """
        if self.seq_profile_type != enum.SeqProfileType.ALLELE:
            raise ValueError("Allele array can only be computed for allele profiles")
        if self.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
            return np.frombuffer(base64.b64decode(self.content), dtype="S16")
        raise NotImplementedError(
            "Unable to compute allele array for this allele profile format"
        )

    def get_allele_ids(self, **kwargs: Any) -> list[UUID | None]:
        """Return ordered allele identifiers from this profile.

        Args:
            **kwargs: Reserved compatibility arguments.

        Returns:
            One identifier or ``None`` for each locus.

        Raises:
            ValueError: If this is not an allele profile.
            NotImplementedError: If its allele representation is unsupported.
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
        """Return the number of non-null loci in this allele profile.

        Args:
            **kwargs: Reserved compatibility arguments.

        Returns:
            The number of loci with an allele identifier.

        Raises:
            ValueError: If this is not an allele profile.
            NotImplementedError: If its allele representation is unsupported.
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
        """Return MLVA repeat numbers from this profile.

        Args:
            **kwargs: Reserved compatibility arguments.

        Returns:
            The ordered repeat-number representation.

        Raises:
            NotImplementedError: If the MLVA representation is unsupported.
        """
        if self.format == enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS:
            return json.loads(self.content)
        raise NotImplementedError(
            "Unable to parse repeat numbers for this MLVA profile format"
        )

    def get_kmer_frequency_map(self, **kwargs: Any) -> dict[str, float]:
        """Return the k-mer frequency map from this profile.

        Args:
            **kwargs: Reserved compatibility arguments.

        Returns:
            Frequencies keyed by k-mer string.

        Raises:
            NotImplementedError: If the k-mer representation is unsupported.
        """
        if self.format == enum.SeqProfileFormat.KMER_FREQUENCY_MAP:
            retval: dict[str, float] = json.loads(self.content)
            return retval
        raise NotImplementedError(
            "Unable to parse k-mer frequency map for this k-mer profile format"
        )

    def get_snps(self, **kwargs: Any) -> list[tuple[int, str]]:
        """Return ordered, lower-case SNP substitutions from NextClade content.

        Args:
            **kwargs: Reserved compatibility arguments.

        Returns:
            One-based position and nucleotide pairs in position order.

        Raises:
            NotImplementedError: If the SNP representation is unsupported.
        """
        if self.format == enum.SeqProfileFormat.NEXTCLADE:
            nextclade_dict: dict[str, Any] = json.loads(self.content)
            snps: list[tuple[int, str]] = []
            substitutions = nextclade_dict.get("substitutions")
            if isinstance(substitutions, str):
                for substitution in substitutions.split(","):
                    if not substitution:
                        continue
                    reference_nucleotide = substitution[0]
                    position = int(substitution[1:-1])
                    mutated_nucleotide = substitution[-1]
                    snps.append((position, mutated_nucleotide.lower()))
            # TODO: 3268 check if this is correct for the non_actgn representation
            non_actgns = nextclade_dict.get("nonACGTNs")
            if isinstance(non_actgns, str):
                for non_actgn in non_actgns.split(","):
                    if not non_actgn:
                        continue
                    non_actgn_nucleotide = non_actgn[0]
                    non_actgn_range = non_actgn[2:].split("-")
                    non_actgn_start = int(non_actgn_range[0])
                    if len(non_actgn_range) == 2:
                        non_actgn_end = int(non_actgn_range[1])
                    else:
                        non_actgn_end = non_actgn_start
                    for position in range(non_actgn_start, non_actgn_end + 1):
                        snps.append((position, non_actgn_nucleotide.lower()))
            return sorted(snps, key=lambda x: x[0])
        raise NotImplementedError(
            f"Unable to parse SNPs for SNP profile format {self.format}"
        )

    def get_missing_seq_ranges(self, ref_seq_length: int) -> list[tuple[int, int]]:
        """Return ordered inclusive missing sequence ranges from NextClade content.

        Args:
            ref_seq_length: Length of the reference sequence.

        Returns:
            One-based inclusive start and end position pairs.

        Raises:
            NotImplementedError: If the SNP representation is unsupported.
        """
        if self.format == enum.SeqProfileFormat.NEXTCLADE:
            nextclade_dict: dict[str, Any] = json.loads(self.content)
            missing_ranges: list[tuple[int, int]] = []
            # Add any missing range at the start
            alignment_start = int(nextclade_dict["alignment_start"])
            if alignment_start > 1:
                missing_ranges.append((1, alignment_start - 1))
            # Add any missing range at the end
            alignment_end = int(nextclade_dict["alignment_end"])
            if alignment_end < ref_seq_length:
                missing_ranges.append((alignment_end + 1, ref_seq_length))
            # Add any missing ranges between the start and end
            missing = nextclade_dict["missing"]
            if missing:
                for missing_range in missing.split(","):
                    missing_range_split = missing_range.split("-")
                    missing_start = int(missing_range_split[0])
                    if len(missing_range_split) == 2:
                        missing_end = int(missing_range_split[1])
                    else:
                        missing_end = missing_start
                    missing_ranges.append((missing_start, missing_end))
            return sorted(missing_ranges, key=lambda x: x[0])
        raise NotImplementedError(
            f"Unable to parse missing sequence ranges for format {self.format}"
        )

    @staticmethod
    def get_ordered_allele_ids_representation(allele_ids: list[UUID | None]) -> str:
        """Return ordered allele identifiers in their encoded profile representation."""
        return base64.b64encode(
            b"".join(NULL_ID.bytes if x is None else x.bytes for x in allele_ids)
        ).decode("ascii")

    @staticmethod
    def get_ordered_repeat_numbers_representation(
        repeat_numbers: list[int | None],
    ) -> str:
        """Return ordered MLVA repeat numbers in their JSON profile representation."""
        return json.dumps(
            [
                int(x) if x is not None else MLVA_NO_LOCUS_REPEAT_NUMBER
                for x in repeat_numbers
            ]
        )

    @staticmethod
    def get_allele_profile_hash(allele_ids: list[UUID | None]) -> UUID:
        """Return the deterministic content hash for ordered allele identifiers."""
        sha256 = hashlib.sha256()
        for allele_id in allele_ids:
            if allele_id is not None:
                sha256.update(allele_id.bytes)
            else:
                sha256.update(NULL_ID.bytes)
        return UUID(sha256.digest()[:16].hex())

    @staticmethod
    def get_mlva_profile_hash(repeat_numbers: list[int | None]) -> UUID:
        """Return the deterministic content hash for ordered MLVA repeat numbers."""
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
        """Return the deterministic content hash for a k-mer frequency map."""
        sha256 = hashlib.sha256()
        for kmer in sorted(kmer_frequency_map.keys()):
            freq = kmer_frequency_map[kmer]
            sha256.update(kmer.encode("ascii"))
            sha256.update(bytearray(struct.pack(">d", freq)))
        return UUID(sha256.digest()[:16].hex())

    @staticmethod
    # TODO: 3268 This should instead calculate the hash from a canonical representation of SNPs. I kept the old function commented out for reference - to be removed
    def get_snp_profile_hash(snps: list[tuple[int, str]]) -> UUID:
        """Return a deterministic hash for SNPs in position-sorted order."""
        sha256 = hashlib.sha256()
        for position, nucleotide in sorted(snps, key=lambda x: x[0]):
            sha256.update(str(position).encode("ascii"))
            sha256.update(nucleotide.encode("ascii"))
        return UUID(sha256.digest()[:16].hex())

    # def get_snp_profile_hash(nextclade_fields: dict[str, Any]) -> UUID:
    #     """Compute a deterministic hash from the flat NextClade fields of a single
    #     sample. Field names and values are iterated in sorted order."""
    #     sha256 = hashlib.sha256()
    #     for field_name in sorted(nextclade_fields.keys()):
    #         value = nextclade_fields[field_name]
    #         sha256.update(field_name.encode("ascii"))
    #         if isinstance(value, str):
    #             sha256.update(value.encode("ascii"))
    #         elif isinstance(value, list):
    #             for item in value:
    #                 sha256.update(str(item).encode("ascii"))
    #         elif value is not None:
    #             sha256.update(str(value).encode("ascii"))
    #     return UUID(sha256.digest()[:16].hex())

    @staticmethod
    def _raise_no_computable_hash() -> None:
        """Report that the active profile format has no supported hash calculation.

        Raises:
            NotImplementedError: Always, because the profile format is unsupported.
        """
        raise NotImplementedError("Unable to compute content hash for this format")


class SeqProfileIdentifier(BaseIdentifier):
    """Associate an external identifier with a sequence profile."""

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

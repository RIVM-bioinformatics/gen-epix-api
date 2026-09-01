"""Define seqdb domain models for domain.model.seq.base."""

import hashlib
import json
import typing
import uuid
from enum import IntEnum
from typing import Annotated, Any, ClassVar, Self
from uuid import UUID

from pydantic import Field, Json, field_serializer, field_validator, model_validator

from gen_epix.commondb.domain.model import Model, validate_int_enum_value
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.literal import REQUIRED_NEXTCLADE_SEQ_KEYS


def str_uuid4() -> str:
    """Return a newly generated UUID4 as text."""
    return str(uuid.uuid4())


class ContentMixin[FormatType: IntEnum]:
    """Add formatted content and a content hash to a model.

    Model validation: Subclasses must validate the relationship between their
    content, format, and content hash.
    """

    _FORMAT_TYPE_CLASS: ClassVar[type[FormatType]] = None  # type: ignore[assignment]

    # Annotation-only: an assigned Field lingers as class attr -> pydantic shadow warning
    format: Annotated[
        FormatType,
        Field(
            description="The representation format of the content.",
        ),
    ]
    content_hash: Annotated[
        UUID,
        Field(
            description="A 128-bit hash code of the content represented as UUID.",
        ),
    ]
    content: Annotated[
        str,
        Field(
            description="The content in a specified format. Depending on the format, the content2 field may be used as well e.g. to optimize performance."
        ),
    ]
    content2: Annotated[
        str | None,
        Field(
            default=None,
            description="The second part of the content, if applicabe, depending on the specified format.",
        ),
    ]

    @field_validator("format", mode="before")
    @classmethod
    def _validate_format(cls, value: str | int | float | FormatType) -> FormatType:
        """Convert the supplied value to the content format enum used by the subclass."""
        if cls._FORMAT_TYPE_CLASS is None:
            for base in getattr(cls, "__orig_bases__", []):  # type: ignore[unreachable]
                if typing.get_origin(base) is not ContentMixin:
                    continue
                cls._FORMAT_TYPE_CLASS = format_class = typing.get_args(base)[0]  # type: ignore[assigment]
        return validate_int_enum_value(cls._FORMAT_TYPE_CLASS, value)  # type: ignore[return-value]

    # TODO: discuss and implement content hash validation per format
    @model_validator(mode="after")
    def _validate_content(self) -> Self:
        """Validate that the content hash matches the content."""
        raise NotImplementedError(
            "Content validation must be implemented in the model using the mixin, as it depends on the format and content fields."
        )

    @field_serializer("format")
    def _serialize_format(self, value: FormatType) -> int:
        """Serialize the format enum to its integer value."""
        return value.value


class QualityMixin:
    """Add qualitative and numeric quality-control data to a model."""

    qc_result: Annotated[
        enum.QualityControlResult,
        Field(
            default=enum.QualityControlResult.PENDING,
            description="The quality of the result as a qualitative value that is used by the application, where applicable, for filtering results.",
        ),
    ]
    qc_score: Annotated[
        float | None,
        Field(
            default=None,
            description="The quality of the result, as a numerical value. A higher score indicates better quality. The range and interpretation of this value is not in scope of the application and must be defined by the user.",
        ),
    ]
    qc_report: Annotated[
        Json | None,
        Field(
            default=None,
            description="A detailed report of the quality control results, which can include any relevant information such as metrics, logs, or other data that provides insights into the quality of the result. The structure and content of this report is not defined by the application and must be determined by the user. The only condition is that the data are JSON serializable.",
        ),
    ]

    @field_validator("qc_result", mode="before")
    @classmethod
    def _validate_qc_result(
        cls, value: str | int | float | enum.QualityControlResult | None
    ) -> enum.QualityControlResult:
        """Convert a supplied quality result, defaulting missing values to pending."""
        if value is None:
            return enum.QualityControlResult.PENDING
        return validate_int_enum_value(enum.QualityControlResult, value)  # type: ignore[return-value]

    @field_serializer("qc_result", mode="plain")
    def _serialize_qc_result(self, value: enum.QualityControlResult) -> int:
        """Serialize the quality result as its stable integer representation."""
        return value.value

    @staticmethod
    def get_sort_key(instance: "QualityMixin") -> tuple[int, float]:
        """Return the quality-control sort key for an instance.

        The quality result is primary, followed by the optional numeric quality
        result and subsequently score. The qc_result is considered leading as it is
        mandatory, and the qc_score is considered secondary as it is optional and may be
        less reliable.
        """
        return instance.qc_result.get_sort_key(), (
            instance.qc_score if instance.qc_score is not None else float("-inf")
        )


class BaseSeq(Model):
    """Represent a sequence with a validated representation, length, and hash.

    The class includes validation logic to ensure
    consistency between the sequence, its format, length, and derived sequence hash.
    The sequence hash is stored in the id field of the model and is equal to the first
    128 bits of the SHA256 hash of the lower case sequence.

    Model validation: Normalizes DNA sequence casing, derives verifiable sequence
    hashes and lengths, and rejects inconsistent or unsupported representations.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seqs",
        persistable=False,
    )

    seq: str = Field(
        description="The sequence in the representation defined by seq_format"
    )
    seq_format: enum.SeqFormat = Field(
        default=enum.SeqFormat.STR_DNA,
        description="The format of the sequence",
    )
    length: int = Field(
        default=0,
        description="The length of the sequence. Derived from the sequence if possible and if the value is set to zero. If set to zero and it is not possible to derive the length, an error is raised.",
        ge=0,
    )

    @field_validator("seq_format", mode="before")
    @classmethod
    def _validate_seq_format(
        cls, value: str | int | float | enum.SeqFormat
    ) -> enum.SeqFormat:
        """Convert a supplied value to a supported sequence representation format."""
        return validate_int_enum_value(enum.SeqFormat, value)  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """Normalize and validate the sequence representation, length, and hash.

        Derives the sequence hash as the first 128 bits of the SHA256 hash of the lower
        case sequence, if not provided, or otherwise verify that it is correctly derived
        if possible. The sequence hash is stored in the id field that must be present in
        the class making use of the mixin.
        """
        seq_hash = self.id
        # Verify sequence hash, seq and length depending on seq_format
        if self.seq_format == enum.SeqFormat.STR_DNA:
            # Verify length
            computed_length = len(self.seq)
            # Make seq lower case and validate characters
            seq = self.seq.lower()
            invalid_chars = set(seq) - enum.SeqAlphabet.DNA_INCL_AMBIGUOUS.value
            if invalid_chars:
                raise ValueError(
                    f"Sequence contains invalid characters for {self.seq_format.value} format: {"".join(sorted(invalid_chars))}"
                )
            self.seq = seq
            # Compute sequence hash
            computed_seq_hash = UUID(
                hashlib.sha256(seq.encode("ascii")).digest()[:16].hex()
            )
        elif self.seq_format == enum.SeqFormat.NEXTCLADE:
            # Parse compact NextClade notation for a single sequence
            nextclade_seq: dict[str, Any] = json.loads(self.seq)
            # Validate required fields
            missing_keys = [
                x for x in REQUIRED_NEXTCLADE_SEQ_KEYS if x not in nextclade_seq
            ]
            if missing_keys:
                raise ValueError(
                    f"Missing required NextClade sequence fields: {missing_keys}"
                )
            # Derive alignment length from the reported alignment bounds
            computed_length = (
                nextclade_seq["alignment_end"] - nextclade_seq["alignment_start"] + 1
            )
            if computed_length <= 0:
                raise ValueError(
                    "alignment_end must be greater than or equal to alignment_start"
                )
            # TODO: 3268: remove commented out code
            # seq_hash cannot be computed at this stage, since it requires the reference sequence, it can only be verified that a value is provided
            if seq_hash is None:
                raise ValueError(
                    f"Unable to calculate sequence hash for seq_format {self.seq_format.value}"
                )
            computed_seq_hash = seq_hash
            # # Compute hash deterministically from sorted field names/values,
            # # mirroring the approach used in SeqProfile.get_snp_profile_hash
            # sha256 = hashlib.sha256()
            # for field_name in sorted(nextclade_seq.keys()):
            #     value = nextclade_seq[field_name]
            #     sha256.update(field_name.encode("ascii"))
            #     if isinstance(value, str):
            #         sha256.update(value.encode("ascii"))
            #     elif value is not None:
            #         sha256.update(str(value).encode("ascii"))
            # computed_seq_hash = UUID(sha256.digest()[:16].hex())
        else:
            if seq_hash is None:
                raise ValueError(
                    f"Unable to calculate sequence hash for seq_format {self.seq_format.value}"
                )
            # Unable to compute length or sequence hash but provided -> assume correct
            computed_length = self.length
            computed_seq_hash = seq_hash
        # Set or verify length
        if self.length == 0:
            if computed_length == 0:
                raise ValueError("Unable to calculate sequence length")
            self.length = computed_length
        elif self.length != computed_length:
            raise ValueError(
                f"Provided length does not match computed length: {self.length} != {computed_length}"
            )
        # Set or verify seq_hash
        if seq_hash is None:
            self.id = computed_seq_hash
        elif seq_hash != computed_seq_hash:
            raise ValueError(
                f"Provided sequence hash, i.e. the id, does not match computed sequence hash for seq_format {self.seq_format.value}: {seq_hash} != {computed_seq_hash}"
            )
        return self

    @field_serializer("seq_format")
    def _serialize_seq_format(self, value: enum.SeqFormat) -> int:
        """Serialize the seq_format enum to its integer value."""
        return value.value

    # TODO: adding the serializer gives issues writing as binary to the database, but not adding it may give other issues
    # @field_serializer("seq_hash", mode="plain")
    # def _serialize_seq_hash(self, value: str | bytes) -> str:
    #     if isinstance(value, bytes):
    #         return value.hex()
    #     return value

    def get_nucleotide_seq(self, ref_seq_str: str | None = None) -> str:
        """Return the nucleotide sequence represented by this model.

        Args:
            ref_seq_str: Reference sequence required to resolve NextClade content.

        Returns:
            The sequence as a nucleotide string when the format is directly supported.

        Raises:
            ValueError: If a required reference sequence or valid mutation position is
                missing.
            NotImplementedError: If the sequence format or required NextClade features
                cannot yet be converted.
        """
        if self.seq_format == enum.SeqFormat.STR_DNA:
            return self.seq
        elif self.seq_format == enum.SeqFormat.NEXTCLADE:
            if ref_seq_str is None:
                raise ValueError(
                    "Reference sequence string must be provided to get the nucleotide sequence for NEXTCLADE format"
                )
            # Parse compact NextClade notation for a single sequence
            nextclade_seq: dict[str, Any] = json.loads(self.seq)
            # Derive nucleotide sequence from the reference sequence and the list of mutations
            seq_list = list(ref_seq_str)
            for mutation in nextclade_seq["substitutions"]:
                pos = mutation["pos"] - 1  # Convert to 0-based index
                if pos < 0 or pos >= len(seq_list):
                    raise ValueError(
                        f"Mutation position {mutation['pos']} is out of bounds for reference sequence of length {len(seq_list)}"
                    )
                seq_list[pos] = mutation["alt"]
            # TODO 3268: handle insertions, deletions, alignment start/end and non-ACTGN
            # for deletion in nextclade_seq["deletions"]:
            #     start_pos = deletion["start"] - 1  # Convert to 0-based index
            #     end_pos = deletion["end"] - 1  # Convert to 0-based index
            #     if start_pos < 0 or end_pos >= len(seq_list) or start_pos > end_pos:
            #         raise ValueError(
            #             f"Deletion positions {deletion['start']}-{deletion['end']} are out of bounds or invalid for reference sequence of length {len(seq_list)}"
            #         )
            #     for pos in range(start_pos, end_pos + 1):
            #         seq_list[pos] = "-"
            raise NotImplementedError(
                "Handling of insertions, deletions, alignment start/end and non-ACTGN characters is not implemented yet for getting the nucleotide sequence from NEXTCLADE format"
            )
            return "".join(seq_list)
        else:
            raise NotImplementedError(
                f"Getting the nucleotide sequence is not implemented for format {self.seq_format}"
            )

import hashlib
import typing
import uuid
from enum import IntEnum
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, Json, field_serializer, field_validator, model_validator

from gen_epix.commondb.domain.model import Model, validate_int_enum_value
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.seqdb.domain import enum


def str_uuid4() -> str:
    return str(uuid.uuid4())


class CodeMixin:
    """
    Mixin class to add a code field to a model.
    """

    code: str = Field(
        default_factory=str_uuid4,
        description="A unique code for the instance, e.g. for external reference. Defaults to a UUID4.",
        max_length=255,
    )


class ContentMixin[FormatType: IntEnum]:
    """
    Mixin class to add content-related fields to a model.
    """

    _FORMAT_TYPE_CLASS: ClassVar[type[FormatType]] = None  # type: ignore[assignment]

    format: FormatType = Field(
        description="The representation format of the content.",
    )
    content_hash: UUID = Field(
        description="A 128-bit hash code of the content represented as UUID.",
    )
    content: str = Field(
        description="The content in a specified format. Depending on the format, the content2 field may be used as well e.g. to optimize performance."
    )
    content2: str | None = Field(
        default=None,
        description="The second part of the content, if applicabe, depending on the specified format.",
    )

    @field_validator("format", mode="before")
    @classmethod
    def _validate_format(cls, value: str | int | float | FormatType) -> FormatType:
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
    """
    Mixin class to add quality related fields to a model.
    """

    qc_result: enum.QualityControlResult = Field(
        default=enum.QualityControlResult.PENDING,
        description="The quality of the result as a qualitative value that is used by the application, where applicable, for filtering results.",
    )
    qc_score: float | None = Field(
        default=None,
        description="The quality of the result, as a numerical value. A higher score indicates better quality. The range and interpretation of this value is not in scope of the application and must be defined by the user.",
    )
    qc_report: Json | None = Field(
        default=None,
        description="A detailed report of the quality control results, which can include any relevant information such as metrics, logs, or other data that provides insights into the quality of the result. The structure and content of this report is not defined by the application and must be determined by the user. The only condition is that the data are JSON serializable.",
    )

    @field_validator("qc_result", mode="before")
    @classmethod
    def _validate_qc_result(
        cls, value: str | int | float | enum.QualityControlResult | None
    ) -> enum.QualityControlResult:
        if value is None:
            return enum.QualityControlResult.PENDING
        return validate_int_enum_value(enum.QualityControlResult, value)  # type: ignore[return-value]

    @field_serializer("qc_result", mode="plain")
    def _serialize_qc_result(self, value: enum.QualityControlResult) -> int:
        return value.value

    @staticmethod
    def get_sort_key(instance: "QualityMixin") -> tuple[int, float]:
        """
        Return a sort key for sorting instances of QualityMixin by quality control
        result and subsequently score. The qc_result is considered leading as it is
        mandatory, and the qc_score is considered secondary as it is optional and may be
        less reliable.
        """
        return instance.qc_result.get_sort_key(), (
            instance.qc_score if instance.qc_score is not None else float("-inf")
        )


class BaseSeq(Model):
    """
    Base class for a sequence. The class includes validation logic to ensure
    consistency between the sequence, its format, length, and derived sequence hash.
    The sequence hash is stored in the id field of the model.
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
        return validate_int_enum_value(enum.SeqFormat, value)  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """
        Derive the sequence hash, if not provided, or otherwise verify that it is
        correctly derived if possible. The sequence hash is stored in the id field
        that must be present in the class making use of the mixin.
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
        else:
            if seq_hash is None:
                raise ValueError("Unable to calculate sequence hash")
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
                "Provided sequence hash, i.e. the id, does not match computed sequence hash"
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
        """Return the nucleotide sequence as a string, if possible, otherwise raise an error."""
        if self.seq_format == enum.SeqFormat.STR_DNA:
            return self.seq
        else:
            raise NotImplementedError(
                f"Getting the nucleotide sequence is not implemented for format {self.seq_format}"
            )

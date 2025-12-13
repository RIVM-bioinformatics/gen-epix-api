import hashlib
import json
import uuid
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, field_serializer, field_validator, model_validator

from gen_epix.commondb.domain.model.base import Model
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


class QualityMixin:
    """
    Mixin class to add quality related fields to a model.
    """

    # TODO [LSP-2690] Add qc and qc_format fields
    qc_score: float | None = Field(
        default=None,
        description="The quality of the result, as a numerical value. A higher score indicates better quality. The range and interpretation of this value is not in scope of the application and must be defined by the user.",
    )
    qc_result: enum.QualityControlResult | None = Field(
        default=None,
        description="The quality of the result as a qualitative value that is used by the application, where applicable, for filtering results.",
    )

    @field_serializer("qc_result", mode="plain")
    def _serialize_quality(self, value: str | enum.QualityControlResult) -> str:
        if isinstance(value, enum.QualityControlResult):
            return value.value
        return value


class BaseSeq(Model):
    """
    Base class The class includes validation logic to ensure consistency between
    the sequence, its format, length, and derived sequence hash. The sequence hash
    is stored in the id field of the model.
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
        description="The length of the sequence. Derived from the sequence if possible and if the value is set to zero. If set to zero and it is not possible to derive the length, an error is raised.",
        ge=0,
    )

    @field_serializer("seq_format")
    def _serialize_seq_format(self, value: enum.SeqFormat) -> str:
        """Serialize the seq_format enum to its string value."""
        return value.value

    @model_validator(mode="after")
    def _validate_mixin(self) -> Self:
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

    # TODO: adding the serializer gives issues writing as binary to the database, but not adding it may give other issues
    # @field_serializer("seq_hash", mode="plain")
    # def _serialize_seq_hash(self, value: str | bytes) -> str:
    #     if isinstance(value, bytes):
    #         return value.hex()
    #     return value


class AlignmentMixin:
    """
    Mixin class to add alignment related fields to a model.
    """

    aln: str = Field(
        description="The alignment in the representation defined by alignment_format"
    )
    aln_format: enum.AlignmentFormat = Field(
        default=enum.AlignmentFormat.CIGAR,
        description="The format of the alignment",
    )
    aln_hash: UUID = Field(
        description="The first 128 bits of the SHA256 hash of the ASCII lower case aligned reference sequence followed by the aligned contig seq.",
    )


class ProtocolMixin:
    """
    Mixin class to add protocol related fields to a model.
    """

    code: str = Field(description="The code of the protocol", max_length=255)
    name: str = Field(description="The name of the protocol", max_length=255)
    version: str | None = Field(
        default=None, description="The version of the protocol", max_length=255
    )
    description: str | None = Field(
        default=None, description="The description of the protocol"
    )
    props: dict[str, str] = Field(
        default_factory=dict, description="The properties of the protocol"
    )

    @field_validator("props", mode="before")
    def _validate_props(cls, value: str | dict) -> dict:
        if isinstance(value, str):
            value = json.loads(value)
        return value

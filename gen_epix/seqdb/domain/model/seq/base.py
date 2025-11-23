import hashlib
import json
import uuid
from typing import Any
from uuid import UUID

from pydantic import Field, field_serializer, field_validator

from gen_epix.seqdb.domain import enum


def str_uuid4() -> str:
    return str(uuid.uuid4())


class CodeMixin:
    code: str = Field(
        default_factory=str_uuid4,
        description="A unique code for the instance, e.g. for external reference. Defaults to a UUID4.",
        max_length=255,
    )


class QualityMixin:
    quality_score: float | None = Field(
        default=None, description="The quality of the sequence, as a numerical value."
    )
    quality: enum.QualityControlResult | None = Field(
        default=None, description="The quality control result of the sequence."
    )

    @field_serializer("quality", mode="plain")
    def _serialize_quality(self, value: str | enum.QualityControlResult) -> str:
        if isinstance(value, enum.QualityControlResult):
            return value.value
        return value


class SeqMixin:

    seq: str = Field(
        description="The sequence in the representation defined by seq_format"
    )
    seq_format: enum.SeqFormat = Field(
        default=enum.SeqFormat.STR_DNA,
        description="The format of the sequence",
    )
    seq_hash: UUID = Field(
        description="The first 128 bits of the SHA256 hash of the lower case ASCII encoded sequence without gaps.",
    )
    length: int = Field(
        description="The length of the sequence.",
        ge=1,
    )

    @field_serializer("seq_format")
    def _serialize_seq_format(self, value: enum.SeqFormat) -> str:
        return value.value

    @field_serializer("seq_hash")
    def _serialize_seq_hash(self, value: UUID) -> str:
        return str(value)

    @staticmethod
    def _validate_model(values: dict[str, Any]) -> dict[str, Any]:
        """
        Derive the sequence hash if not provided, or otherwise verify that it is
        correctly derived if possible.

        Make sure the sequence content matches the specified format, where verifiable.
        """
        # Verify seq_hash
        seq_hash = values.get("seq_hash")
        if isinstance(seq_hash, str):
            seq_hash = UUID(seq_hash)
            values["seq_hash"] = seq_hash
        elif isinstance(seq_hash, bytes):
            seq_hash = UUID(seq_hash.hex())
            values["seq_hash"] = seq_hash
        # Verify seq_format
        seq_format = values.get("seq_format")
        if seq_format is None:
            seq_format = enum.SeqFormat.STR_DNA
            values["seq_format"] = seq_format
        elif isinstance(seq_format, str):
            seq_format = enum.SeqFormat(seq_format)
            values["seq_format"] = seq_format
        # Verify seq_hash, seq and length depending on seq_format
        seq: str | None = values.get("seq")
        length: int | None = values.get("length")
        if seq is None:
            raise ValueError("seq must be provided")
        if isinstance(length, (str, float)):
            length = int(length)
            values["length"] = length
        if seq_format == enum.SeqFormat.STR_DNA:
            # Verify length
            computed_length = len(seq)
            # Make seq lower case and validate characters
            seq = seq.lower()
            invalid_chars = set(seq) - enum.SeqAlphabet.IUPAC_DNA.value
            if invalid_chars:
                raise ValueError(
                    f"Sequence contains invalid characters for {seq_format.value} format: {"".join(sorted(invalid_chars))}"
                )
            values["seq"] = seq
            # Compute seq_hash
            computed_seq_hash = UUID(
                hashlib.sha256(seq.encode("ascii")).digest()[:16].hex()
            )
        else:
            if length is None:
                raise ValueError("length must be provided")
            if seq_hash is None:
                raise ValueError("Unable to calculate seq_hash")
            # Unable to compute length or seq_hash but provided -> assume correct
            computed_length = length
            computed_seq_hash = seq_hash
        # Set or verify length
        if length is None:
            values["length"] = computed_length
        elif length != computed_length:
            raise ValueError("Provided length does not match computed length")
        # Set or verify seq_hash
        if seq_hash is None:
            values["seq_hash"] = computed_seq_hash
        elif seq_hash != computed_seq_hash:
            raise ValueError("Provided seq_hash does not match computed seq_hash")
        return values

    @staticmethod
    def _validate_model_and_id(values: dict[str, Any]) -> dict[str, Any]:
        """
        Derive the sequence hash if not provided, or otherwise verify that it is
        correctly derived if possible.

        Set the ID equal to the sequence hash if not given or otherwise verify that it
        is identical.
        """
        values = SeqMixin._validate_model(values)
        id_ = values.get("id")
        if isinstance(id_, str):
            id_ = UUID(id_)
            values["id"] = id_
        if id_ is not None:
            if id_ != values.get("seq_hash"):
                raise ValueError("ID must be equal to the sequence hash.")
        else:
            values["id"] = values.get("seq_hash")
        return values

    # TODO: adding the serializer gives issues writing as binary to the database, but not adding it may give other issues
    # @field_serializer("seq_hash", mode="plain")
    # def _serialize_seq_hash(self, value: str | bytes) -> str:
    #     if isinstance(value, bytes):
    #         return value.hex()
    #     return value


class AlignmentMixin:
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

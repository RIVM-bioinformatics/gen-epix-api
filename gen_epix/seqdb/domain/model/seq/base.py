import json
import uuid

from pydantic import Field, field_serializer, field_validator

from gen_epix.seqdb.domain import enum


def str_uuid4() -> str:
    return str(uuid.uuid4())


class SeqMixin:
    seq: str = Field(
        description="The sequence in the representation defined by seq_format"
    )
    seq_format: enum.SeqFormat = Field(
        default=enum.SeqFormat.STR_DNA5,
        description="The format of the sequence",
    )
    seq_hash_sha256: bytes = Field(
        description="The SHA256 hash of the lower case ASCII encoded sequence without gaps. In the case of multiple contigs, this is the hash of the lexicographically sorted and concatenated contig sequences with a single gap ('-') as separator.",
        min_length=32,
        max_length=32,
    )
    length: int = Field(
        description="The length of the sequence. In case of multiple contigs, this is the sum of the lengths of all contigs.",
        ge=1,
    )

    @field_validator("seq_hash_sha256", mode="before")
    def _validate_seq_hash_sha256(cls, value: str | bytes) -> bytes:
        if isinstance(value, str):
            value = bytes.fromhex(value)
        return value

    @field_serializer("seq_format")
    def _serialize_seq_format(self, value: str | enum.SeqFormat) -> str:
        if isinstance(value, enum.SeqFormat):
            return value.value
        return value

    # TODO: adding the serializer gives issues writing as binary to the database, but not adding it may give other issues
    # @field_serializer("seq_hash_sha256")
    # def _serialize_seq_hash_sha256(self, value: str | bytes) -> str:
    #     if isinstance(value, bytes):
    #         return value.hex()
    #     return value


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

    @field_serializer("quality")
    def _serialize_quality(self, value: str | enum.QualityControlResult) -> str:
        if isinstance(value, enum.QualityControlResult):
            return value.value
        return value


class AlignmentMixin:
    aln: str = Field(
        description="The alignment in the representation defined by alignment_format"
    )
    aln_format: enum.AlignmentFormat = Field(
        default=enum.AlignmentFormat.CIGAR,
        description="The format of the alignment",
    )
    aln_hash_sha256: bytes = Field(
        description="The SHA256 hash of the ASCII lower case aligned reference sequence followed by the aligned contig seq.",
        min_length=32,
        max_length=32,
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

"""Define seqdb domain models for domain.model.seq.reads."""

from typing import ClassVar, Self
from uuid import UUID

from pydantic import (
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model, validate_int_enum_value_or_none
from gen_epix.commondb.domain.model.organization import BaseIdentifier
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.file import File
from gen_epix.seqdb.domain.model.seq.base import QualityMixin
from gen_epix.seqdb.domain.model.seq.protocol import HasProtocolMixin, Protocol
from gen_epix.seqdb.domain.model.seq.sample import HasSampleMixin, Sample


class ReadSet(Model, HasSampleMixin, HasProtocolMixin, QualityMixin):
    """Represent single-end or paired-end reads produced from a sample.

    Read data can be linked later through URIs or file references. ``is_available``
    reports whether either link representation is present.

    Model validation: Forward and reverse URIs, file identifiers, and content hashes
    must differ when both are provided. URI and file links cannot be mixed. File links
    require a format and default missing compression to ``NONE``.

    Model serialization: Read-file format and compression are emitted as integer enum
    values when present.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="read_sets",
        table_name="read_set",
        persistable=True,
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: (
                    "protocol_id",
                    Protocol,
                    "protocol",
                ),
                3: ("fwd_file_id", File, "fwd_file"),
                4: ("rev_file_id", File, "rev_file"),
            }
        ),
    )
    fwd_uri: str | None = Field(
        default=None,
        description="The URI of the forward read set. In case of single-end reads, this is the only read set.",
    )
    rev_uri: str | None = Field(
        default=None, description="The URI of the reverse read set, if any."
    )
    fwd_file_id: UUID | None = Field(
        default=None,
        description="The unique file identifier for the forward read set. In case of single-end reads, this is the only read set. FOREIGN KEY",
    )
    fwd_file: File | None = Field(
        default=None, description="The file representing the forward read set."
    )
    rev_file_id: UUID | None = Field(
        default=None,
        description="The unique file identifier for the reverse read set, if any.",
    )
    rev_file: File | None = Field(
        default=None, description="The file representing the reverse read set."
    )
    file_format: enum.ReadsFileFormat | None = Field(
        default=None, description="The format of the reads files."
    )
    file_compression: enum.FileCompression | None = Field(
        default=None, description="The compression of the reads files."
    )
    fwd_reads_hash: UUID | None = Field(
        default=None,
        description="The first 128 bits of the SHA256 hash of the uncompressed FASTQ file representation of the forward read set.",
    )
    rev_reads_hash: UUID | None = Field(
        default=None,
        description="The first 128 bits of the SHA256 hash of the uncompressed FASTQ file representation of the reverse read set.",
    )
    sequencing_run_code: str | None = Field(
        description="The code of the sequencing run.", max_length=255, default=None
    )
    code: str | None = Field(
        default=None,
        max_length=255,
        description="A code for the read set for further reference",
    )

    @computed_field(  # type: ignore[prop-decorator]
        description="Whether the read set has any linked reads data available, either via URIs or file links."
    )
    @property
    def is_available(self) -> bool:
        """Return whether forward or reverse reads have a URI or file link."""
        return (
            self.fwd_uri is not None
            or self.fwd_file_id is not None
            or self.rev_uri is not None
            or self.rev_file_id is not None
        )

    @field_validator("file_format", mode="before")
    @classmethod
    def _validate_file_format(
        cls, value: enum.ReadsFileFormat | str | int | None
    ) -> enum.ReadsFileFormat | None:
        """Normalize the read-file format from its accepted enum representation."""
        return validate_int_enum_value_or_none(enum.ReadsFileFormat, value)  # type: ignore[return-value]

    @field_validator("file_compression", mode="before")
    @classmethod
    def _validate_file_compression(
        cls, value: enum.FileCompression | str | int | None
    ) -> enum.FileCompression | None:
        """Normalize read-file compression from its accepted enum representation."""
        return validate_int_enum_value_or_none(enum.FileCompression, value)  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """Validate mutually exclusive read links and paired-read values."""
        if self.fwd_uri and self.rev_uri and self.fwd_uri == self.rev_uri:
            raise ValueError("fwd_uri must be different from rev_uri")
        if (
            self.fwd_file_id
            and self.rev_file_id
            and self.fwd_file_id == self.rev_file_id
        ):
            raise ValueError("fwd_file_id must be different from rev_file_id")
        if (
            self.fwd_reads_hash
            and self.rev_reads_hash
            and self.fwd_reads_hash == self.rev_reads_hash
        ):
            raise ValueError("fwd_reads_hash must be different from rev_reads_hash")
        if self.fwd_file_id is not None or self.rev_file_id is not None:
            if self.file_format is None:
                raise ValueError("file_format must be provided when linking read files")
            if self.file_compression is None:
                self.file_compression = enum.FileCompression.NONE
        if (self.fwd_uri is not None or self.rev_uri is not None) and (
            self.fwd_file_id is not None or self.rev_file_id is not None
        ):
            raise ValueError("Cannot have both uri and file_id")
        return self

    @field_serializer("file_format", "file_compression")
    def _serialize_file_format(
        self, value: enum.ReadsFileFormat | enum.FileCompression | None
    ) -> int | None:
        """Serialize read-file enum values as integers."""
        if value is not None:
            return value.value
        return value


class ReadSetIdentifier(BaseIdentifier):
    """Associate an external identifier with a read set."""

    ENTITY: ClassVar = BaseIdentifier.create_entity(
        ReadSet,
        relationship_field_name="read_set",
        snake_case_plural_name="read_set_identifiers",
        table_name="read_set_identifier",
    )
    NAME: ClassVar = "ReadSetIdentifier"
    MODEL_CLASS: ClassVar = ReadSet

    read_set: ReadSet | None = Field(
        default=None, description="The read set associated with this identifier."
    )

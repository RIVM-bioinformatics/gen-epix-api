from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain.model.seq.base import CodeMixin, ProtocolMixin, QualityMixin


class LibraryPrepProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="library_prep_protocols",
        table_name="library_prep_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class ReadSet(Model, CodeMixin, QualityMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="read_sets",
        table_name="read_set",
        persistable=True,
        keys=create_keys({1: "code"}),
        links=create_links(
            {
                #!FIXME links with None foreign keys are not supported yet
                # 1: (
                #     "fwd_file_id",
                #     File,
                #     None,
                # ),
                # 2: (
                #     "rev_file_id",
                #     File,
                #     None,
                # ),
                1: (
                    "library_prep_protocol_id",
                    LibraryPrepProtocol,
                    "library_prep_protocol",
                ),
            }
        ),
    )
    library_prep_protocol_id: UUID = Field(
        description="The unique identifier for the library preparation protocol. FOREIGN KEY"
    )
    library_prep_protocol: LibraryPrepProtocol | None = Field(
        default=None, description="The sequencing protocol."
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
    rev_file_id: UUID | None = Field(
        default=None,
        description="The unique file identifier for the reverse read set, if any.",
    )
    fwd_reads_hash_sha256: bytes | None = Field(
        default=None,
        description="The SHA256 hash of the uncompressed FASTQ file representation of the forward read set.",
        min_length=32,
        max_length=32,
    )
    rev_reads_hash_sha256: bytes | None = Field(
        default=None,
        description="The SHA256 hash of the uncompressed FASTQ file representation of the reverse read set.",
        min_length=32,
        max_length=32,
    )
    sequencing_run_code: str | None = Field(
        description="The code of the sequencing run.", max_length=255, default=None
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        if self.fwd_uri and self.rev_uri and self.fwd_uri == self.rev_uri:
            raise ValueError("fwd_uri must be different from rev_uri")
        if (
            self.fwd_file_id
            and self.rev_file_id
            and self.fwd_file_id == self.rev_file_id
        ):
            raise ValueError("fwd_file_id must be different from rev_file_id")
        if (
            self.fwd_reads_hash_sha256
            and self.rev_reads_hash_sha256
            and self.fwd_reads_hash_sha256 == self.rev_reads_hash_sha256
        ):
            raise ValueError(
                "fwd_reads_hash_sha256 must be different from rev_reads_hash_sha256"
            )
        return self

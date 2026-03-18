from typing import ClassVar, Self
from urllib.parse import urlparse
from uuid import UUID

from pydantic import Field, field_serializer, model_validator

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain.enum import ProtocolType, ProtocolTypeSet
from gen_epix.seqdb.domain.model.seq.locus import LocusSet
from gen_epix.seqdb.domain.model.seq.seq import RefSeq


def is_hexadecimal(s: str) -> bool:
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


class Protocol(Model):
    """
    Represents the global protocol definition for genomic detection.

    This model serves as a generic schema for various detection methods (e.g.,
    MLVA, SNP, or Locus detection). It links specific analytical logic
    stored in a Git repository to the reference sequences and parameters
    required to execute the protocol reproducibly.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="protocols",
        table_name="protocol",
        persistable=True,
        keys=create_keys({1: "code"})
    )

    code: str = Field(
        description="A unique code for the protocol, used for external reference."
    )

    name: str | None = Field(default=None, description="The name of the protocol.")

    description: str | None = Field(
        default=None, description="A detailed description of the protocol"
    )
    protocol_type: ProtocolType = Field(description="The type of the protocol.")

    git_repository_uri: str | None = Field(
        default=None,
        description="URI of the Git repository containing the analytical logic for this protocol.",
    )
    git_commit_hash: str | None = Field(
        default=None,
        description="The specific Git commit hash to ensure reproducibility of the protocol execution.",
    )
    git_commit_tag: str | None = Field(
        default=None,
        description="An optional Git tag for easier reference to a specific version of the protocol.",
    )
    ref_seq_id: UUID | None = Field(
        default=None,
        description="The UUID of the reference sequence associated with this protocol.",
    )
    locus_set_id: UUID | None = Field(
        default=None,
        description="The UUID of the locus set associated with this protocol.",
    )
    props: dict[str, str | int | float | bool | list] = Field(
        # list is added to allow PcrProtocol.target_names and AstProtocol.antimicrobial_names
        default_factory=dict,
        description="A dictionary of additional properties specific to the protocol.",
    )

    @model_validator(mode="after")
    def _validate_protocol_type(self) -> Self:
        # TODO: check if this logic is biologically correct
        if self.protocol_type == ProtocolType.MLVA_DETECTION:
            if self.ref_seq_id is not None:
                raise ValueError("ref_seq_id must be empty for MLVA protocols.")
            if self.locus_set_id is None:
                raise ValueError("locus_set_id must be filled for MLVA protocols.")
        elif self.protocol_type in ProtocolTypeSet.DETECTION_PROTOCOLS.value:
            if self.ref_seq_id is None:
                raise ValueError(
                    "ref_seq_id must be filled for SNP and LOCUS protocols."
                )
            if self.locus_set_id is not None:
                raise ValueError(
                    "locus_set_id must be empty for SNP and LOCUS protocols."
                )
        return self

    @model_validator(mode="after")
    def _validate_git_info(self) -> Self:
        if self.git_commit_hash is not None:
            # TODO: maybe to strict and heavy to check if hash is valid hexadecimal
            if not is_hexadecimal(self.git_commit_hash):
                raise ValueError("git_commit_hash must be a valid hexadecimal string.")
            if len(self.git_commit_hash) != 40:
                raise ValueError("git_commit_hash must be 40 characters long.")

        if self.git_repository_uri is not None:
            parsed_uri = urlparse(self.git_repository_uri)
            if not all([parsed_uri.scheme, parsed_uri.netloc]):
                raise ValueError("git_repository_uri must be a valid URI.")

        return self

    @field_serializer("ref_seq_id", mode="plain")
    def _serialize_ref_seq_id(self, value: UUID | None) -> str | None:
        if value is not None:
            return str(value)
        return value

    @field_serializer("locus_set_id", mode="plain")
    def _serialize_locus_set_id(self, value: UUID | None) -> str | None:
        if value is not None:
            return str(value)
        return value

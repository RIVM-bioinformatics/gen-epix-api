import json
import string
from datetime import datetime, timezone
from enum import IntEnum
from typing import Any, ClassVar, Self
from urllib.parse import urlparse
from uuid import UUID

from pydantic import Field, field_serializer, field_validator, model_validator

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model, validate_int_enum_value
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_keys
from gen_epix.fastapp.domain.util import create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.enum import (
    ProtocolType,
    ProtocolTypeSet,
    SeqDistanceType,
    SeqProfileType,
)
from gen_epix.seqdb.domain.model.seq.category import SeqCategorySet
from gen_epix.seqdb.domain.model.seq.locus import LocusSet
from gen_epix.seqdb.domain.model.seq.ref_seq import RefSeq


def _create_field_description(
    required_protocol_types: frozenset[ProtocolType],
    optional_protocol_types: frozenset[ProtocolType],
) -> str:
    """Helper function to create field descriptions based on protocol type dependencies."""
    description = ""
    if required_protocol_types:
        description += (
            "Required for protocols of type "
            + ", ".join(sorted(x.name for x in required_protocol_types))
            + "."
        )
        if optional_protocol_types:
            description += " "
    if optional_protocol_types:
        description += (
            "Optional for protocols of type "
            + ", ".join(sorted(x.name for x in optional_protocol_types))
            + "."
        )
    return description


class Protocol(Model):
    """
    Represents an analytical method used to derive a result from source data. The class
    is conceptually polymorphic, with the protocol_type field determining which
    additional fields are required and which results it may be linked to. This design
    allows for a flexible and extensible representation of various analytical protocols
    while maintaining a single model for this type of reference data.

    The Protocol model includes optional fields for linking to Git repositories and
    commits, so that the exact analytical logic can be traced.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="protocols",
        table_name="protocol",
        persistable=True,
        keys=create_keys({1: "code"}),
        links=create_links(
            {
                1: ("ref_seq_id", RefSeq, None),
                2: ("seq_category_set_id", SeqCategorySet, None),
                3: ("locus_set_id", LocusSet, None),
            }
        ),
    )
    # Mapping of fields to the protocol types that either require or optionally have
    # them. Used for validation.
    PROTOCOL_TYPE_FIELD_DEPENDENCIES: ClassVar[
        dict[str, tuple[frozenset[ProtocolType], frozenset[ProtocolType]]]
    ] = {
        "ref_seq_id": (
            ProtocolTypeSet.HAS_REF_SEQ.value,
            ProtocolTypeSet.HAS_OPTIONAL_REF_SEQ.value,
        ),
        "seq_category_set_id": (
            ProtocolTypeSet.HAS_SEQ_CATEGORY_SET.value,
            ProtocolTypeSet.HAS_OPTIONAL_SEQ_CATEGORY_SET.value,
        ),
        "locus_set_id": (
            ProtocolTypeSet.HAS_LOCUS_SET.value,
            ProtocolTypeSet.HAS_OPTIONAL_LOCUS_SET.value,
        ),
        "seq_profile_type": (ProtocolTypeSet.SEQ_PROFILE.value, frozenset()),
        "seq_distance_type": (ProtocolTypeSet.IS_SEQ_DISTANCE.value, frozenset()),
        "is_integer_distance": (ProtocolTypeSet.IS_SEQ_DISTANCE.value, frozenset()),
        "max_stored_distance": (ProtocolTypeSet.IS_SEQ_DISTANCE.value, frozenset()),
    }
    SEQ_PROFILE_DISTANCE_TYPE_MAP: ClassVar[
        dict[enum.SeqProfileType, enum.SeqDistanceTypeSet]
    ] = {
        enum.SeqProfileType.ALLELE: enum.SeqDistanceTypeSet.ALLELE_PROFILE_BASED,
        enum.SeqProfileType.SNP: enum.SeqDistanceTypeSet.SNP_PROFILE_BASED,
        enum.SeqProfileType.KMER: enum.SeqDistanceTypeSet.KMER_PROFILE_BASED,
        enum.SeqProfileType.MLVA: enum.SeqDistanceTypeSet.MLVA_PROFILE_BASED,
    }
    PROPS_MAX_JSON_LENGTH: ClassVar[int] = 2000

    code: str = Field(
        description="A unique code for the protocol, used for external reference.",
        max_length=255,
    )
    name: str | None = Field(
        default=None, description="The name of the protocol.", max_length=255
    )

    description: str | None = Field(
        default=None,
        description="A detailed description of the protocol",
        max_length=1000,
    )
    protocol_type: ProtocolType = Field(
        description="The type of the protocol. Determines additional required fields."
    )
    git_repository_uri: str | None = Field(
        default=None,
        description="URI of the Git repository containing the analytical logic for the protocol.",
        max_length=2000,
    )
    git_commit_hash: str | None = Field(
        default=None,
        description="The specific Git commit hash to ensure reproducibility of the protocol execution. Must be a 40-character hexadecimal string.",
        max_length=40,
    )
    git_commit_tag: str | None = Field(
        default=None,
        description="An optional Git tag for easier reference to a specific version of the protocol.",
        max_length=255,
    )
    valid_start_datetime: datetime | None = Field(
        default=None,
        description="The UTC date and time from which the protocol is considered valid.",
    )
    valid_end_datetime: datetime | None = Field(
        default=None,
        description="The UT C date and time until which the protocol is considered valid.",
    )
    ref_seq_id: UUID | None = Field(
        default=None,
        description="The reference sequence used. FOREIGN KEY. "
        + _create_field_description(*PROTOCOL_TYPE_FIELD_DEPENDENCIES["ref_seq_id"]),
    )
    seq_category_set_id: UUID | None = Field(
        default=None,
        description="The sequence category set used. FOREIGN KEY. "
        + _create_field_description(
            *PROTOCOL_TYPE_FIELD_DEPENDENCIES["seq_category_set_id"]
        ),
    )
    locus_set_id: UUID | None = Field(
        default=None,
        description="The locus set used. FOREIGN KEY. "
        + _create_field_description(*PROTOCOL_TYPE_FIELD_DEPENDENCIES["locus_set_id"]),
    )
    seq_profile_type: SeqProfileType | None = Field(
        default=None,
        description="The type of sequence profile. "
        + _create_field_description(
            *PROTOCOL_TYPE_FIELD_DEPENDENCIES["seq_profile_type"]
        ),
    )
    seq_distance_type: SeqDistanceType | None = Field(
        default=None,
        description="The type of sequence distance calculation used. "
        + _create_field_description(
            *PROTOCOL_TYPE_FIELD_DEPENDENCIES["seq_distance_type"]
        ),
    )
    is_integer_distance: bool | None = Field(
        default=None,
        description="Whether the sequence distances are integers. "
        + _create_field_description(
            *PROTOCOL_TYPE_FIELD_DEPENDENCIES["is_integer_distance"]
        ),
    )
    max_stored_distance: float | None = Field(
        default=None,
        description="The maximum sequencedistance that is guaranteed to be stored. "
        + _create_field_description(
            *PROTOCOL_TYPE_FIELD_DEPENDENCIES["max_stored_distance"]
        ),
    )
    props: dict[str, Any] = Field(
        default_factory=dict,
        description="A dictionary of additional properties specific to the protocol. Must be JSON-serializable. Can also be passed as a JSON string.",
    )

    @field_validator("valid_start_datetime", "valid_end_datetime", mode="before")
    @classmethod
    def _validate_datetime_to_utc(cls, value: str | datetime | None) -> datetime | None:
        """Parses datetime strings and converts timezone-aware values to UTC."""
        if value is None:
            return None
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc)
        return value

    @field_validator("protocol_type", mode="before")
    @classmethod
    def _validate_protocol_type(
        cls, value: str | int | float | ProtocolType
    ) -> ProtocolType:
        return validate_int_enum_value(ProtocolType, value)  # type: ignore[return-value]

    @field_validator("git_commit_hash", mode="after")
    @classmethod
    def _validate_git_commit_hash(cls, value: str | None) -> str | None:
        """Validates the git_commit_hash."""
        if value is None:
            return value
        if not all(x in string.hexdigits for x in value):
            raise ValueError("git_commit_hash must be a valid hexadecimal string.")
        if len(value) != 40:
            raise ValueError("git_commit_hash must be 40 characters long.")
        return value

    @field_validator("git_repository_uri", mode="after")
    @classmethod
    def _validate_git_repository_uri(cls, value: str | None) -> str | None:
        """Validates the git_repository_uri."""
        if value is None:
            return None
        parsed_uri = urlparse(value)
        if not all([parsed_uri.scheme, parsed_uri.netloc]):
            raise ValueError("git_repository_uri must be a valid URI.")
        return value

    @field_validator("seq_profile_type", mode="before")
    @classmethod
    def _validate_seq_profile_type(
        cls, value: str | int | float | SeqProfileType | None
    ) -> SeqProfileType | None:
        if value is None:
            return None
        return validate_int_enum_value(SeqProfileType, value)  # type: ignore[return-value]

    @field_validator("seq_distance_type", mode="before")
    @classmethod
    def _validate_seq_distance_type(
        cls, value: str | int | float | SeqDistanceType | None
    ) -> SeqDistanceType | None:
        if value is None:
            return None
        return validate_int_enum_value(SeqDistanceType, value)  # type: ignore[return-value]

    @field_validator("props", mode="before")
    @classmethod
    def _validate_props(cls, value: dict[str, Any] | str) -> dict[str, Any]:
        """Allows props to be passed as a JSON string or a dictionary. Validates
        that the JSON representation does not exceed PROPS_MAX_JSON_LENGTH characters.
        """
        if isinstance(value, str):
            if len(value) > cls.PROPS_MAX_JSON_LENGTH:
                raise ValueError(
                    f"props JSON string must not exceed {cls.PROPS_MAX_JSON_LENGTH} characters."
                )
            return json.loads(value)
        if not isinstance(value, dict):
            raise ValueError("props must be a dictionary.")
        json_repr = json.dumps(value)
        if len(json_repr) > cls.PROPS_MAX_JSON_LENGTH:
            raise ValueError(
                f"props JSON representation must not exceed {cls.PROPS_MAX_JSON_LENGTH} characters."
            )
        return value

    @model_validator(mode="after")
    def _validate_protocol_type_dependencies(self) -> Self:
        """
        Validates that the fields required for the specified protocol type are correctly
        filled.For each field that has protocol type dependencies, checks if the current
        protocol type requires it. If required, ensures the field is not None. If not
        required, ensures the field is None.
        """
        for (
            field_name,
            (required_protocol_types, optional_protocol_types),
        ) in self.PROTOCOL_TYPE_FIELD_DEPENDENCIES.items():
            field_value = getattr(self, field_name)
            if self.protocol_type in required_protocol_types:
                if field_value is None:
                    raise ValueError(
                        f"{field_name} must be filled for {self.protocol_type.name} protocols."
                    )
                continue
            if self.protocol_type in optional_protocol_types:
                # The field is optional for this protocol type, so it can be filled or
                # not. No validation needed.
                continue
            if field_value is not None:
                raise ValueError(
                    f"{field_name} must be empty for non-{self.protocol_type.name} protocols."
                )
        return self

    @field_serializer(
        "protocol_type", "seq_profile_type", "seq_distance_type", mode="plain"
    )
    def _serialize_int_enums(self, value: IntEnum | None) -> int | None:
        """Serializes the IntEnums to their int value."""
        if value is None:
            return None
        return value.value

    @field_serializer("ref_seq_id", "locus_set_id", mode="plain")
    def _serialize_ref_seq_id(self, value: UUID | None) -> str | None:
        """Serializes UUID fields as strings. If the value is None, it returns None."""
        if value is not None:
            return str(value)
        return value


class HasProtocolMixin:
    """Mixin for models that have an associated Protocol. Provides a protocol_id field
    and a method to retrieve the associated Protocol.
    """

    protocol_id: UUID = Field(
        description="The ID of the associated protocol. FOREIGN KEY."
    )
    protocol: Protocol | None = Field(
        default=None, description="The associated protocol."
    )

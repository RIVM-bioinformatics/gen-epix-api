"""Provide commondb base models and helpers for ETL result reporting.

The models add audit metadata and identifiers to FastApp models. ETL result
types accumulate structured log entries, while enum helpers normalize values
submitted to integer-enum fields.
"""

from datetime import UTC, datetime
from enum import IntEnum
from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix import fastapp
from gen_epix.etl.enum import EtlStatus as EtlStatus


class ModelNoId(fastapp.Model):
    """Represents creation and modification metadata to a FastApp domain model.

    This model serves as a base class for other models in the different
    applications.

    Services call the mutation helpers before persisting a model so audit
    timestamps and the responsible user ID remain synchronized.
    """

    METADATA_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {"created_at", "modified_at", "modified_by"}
    )
    TIMESTAMP_METADATA_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {"created_at", "modified_at"}
    )
    MODIFIED_BY_FIELD_NAME: ClassVar[str] = "modified_by"

    created_at: datetime | None = Field(
        default=None,
        description="The UTC datetime when the object was created.",
    )
    modified_at: datetime | None = Field(
        default=None,
        description="The UTC datetime when the object was last modified.",
    )
    modified_by: UUID | None = Field(
        default=None,
        description="The ID of the user who last modified the object.",
    )

    def set_modified(self, user_id: UUID) -> None:
        """Record the current UTC time and user as the latest modification."""
        now = datetime.now(UTC)
        self.modified_at = now
        self.modified_by = user_id

    def set_created(self, user_id: UUID) -> None:
        """Record the current UTC time and user as both creation and modification."""
        now = datetime.now(UTC)
        self.modified_at = now
        self.modified_by = user_id
        self.created_at = now


class Model(ModelNoId):
    """Represents an optional persistent identifier to commondb audit-aware models."""

    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the object.",
    )


def validate_int_enum_value(
    enum_class: type[IntEnum], value: int | str | float | IntEnum
) -> IntEnum:
    """Normalize a value to a member of an integer enumeration.

    This function is intended to be used in model validators to ensure that values
    assigned to integer-enum fields are correctly normalized.

    Args:
        enum_class: The enumeration that accepts the value.
        value: A member name, integer value, integral float, or member.

    Returns:
        The corresponding member of ``enum_class``.

    Raises:
        ValueError: If ``value`` has an unsupported type or is not a member.
        KeyError: If a string value does not name a member.
    """
    if isinstance(value, enum_class):
        return value
    if isinstance(value, str):
        return enum_class[value]
    if isinstance(value, int):
        return enum_class(value)
    if isinstance(value, float):
        return enum_class(int(value))
    raise ValueError(f"Unsupported type for {enum_class.__name__} field: {type(value)}")


def validate_int_enum_value_or_none(
    enum_class: type[IntEnum], value: int | str | float | IntEnum | None
) -> IntEnum | None:
    """Normalize an optional value to a member of an integer enumeration.

    This function is intended to be used in model validators to ensure that optional
    values assigned to integer-enum fields are correctly normalized.

    Args:
        enum_class: The enumeration that accepts non-null values.
        value: A member name, integer value, integral float, member, or None.

    Returns:
        The corresponding member of ``enum_class``, or None when ``value`` is None.

    Raises:
        ValueError: If a non-null value has an unsupported type or is not a member.
        KeyError: If a string value does not name a member.
    """
    if value is None:
        return None
    return validate_int_enum_value(enum_class, value)

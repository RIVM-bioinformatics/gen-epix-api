"""Provide commondb base models and helpers for ETL result reporting.

The models add audit metadata and identifiers to FastApp models. ETL result
types accumulate structured log entries, while enum helpers normalize values
submitted to integer-enum fields.
"""

from datetime import UTC, datetime
from enum import IntEnum
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer, field_validator

from gen_epix import fastapp
from gen_epix.commondb.domain.enum import EtlStatus as EtlStatus
from gen_epix.fastapp.enum import LogLevel


class ModelNoId(fastapp.Model):
    """Add creation and modification metadata to a FastApp domain model.

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
    """Add an optional persistent identifier to commondb audit-aware models."""

    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the object.",
    )


class EtlLogItem(BaseModel):
    """Represent one immutable, structured event in an ETL result accumulator."""

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="The UTC timestamp when the log item was created.",
    )
    code: str = Field(
        description="A code categorizing the log item.",
    )
    message: str = Field(
        description="The log message describing the event or information.",
    )
    severity: LogLevel = Field(
        description="Log severity, accepting a LogLevel or member name and serializing to its string value.",
    )
    source: str | None = Field(
        default=None,
        description="Optional field to capture source trace information, e.g. relevant source record ids.",
    )
    target: str | None = Field(
        default=None,
        description="Optional field to capture target trace information, e.g. relevant target record ids created or updated as a result of the logged event.",
    )

    @field_validator("severity", mode="before")
    @classmethod
    def _validate_severity(cls, severity: LogLevel | str) -> LogLevel:
        """Normalize a severity member name to a LogLevel."""
        if isinstance(severity, str):
            return LogLevel[severity]
        return severity

    @field_serializer("severity")
    def _serialize_severity(self, value: LogLevel) -> str:
        """Serialize a log level as its configured value."""
        return value.value


class BaseEtlResult(BaseModel):
    """Accumulate structured ETL messages and expose severity-specific queries.

    Pydantic subclasses declare their status field and override
    :meth:`set_error_status` to mark an error after :meth:`add_error` appends
    an ERROR-severity event.

    """

    logs: list[EtlLogItem] = Field(
        default_factory=list,
        description="Log items capturing messages and events that occurred during the operation.",
    )

    def add_error(
        self,
        code: str,
        message: str,
        source: str | None = None,
        target: str | None = None,
    ) -> None:
        """Append an ERROR-severity log item and update the status."""
        self.logs.append(
            EtlLogItem(
                code=code,
                message=message,
                severity=LogLevel.ERROR,
                source=source,
                target=target,
            )
        )
        self.set_error_status()

    def set_error_status(self) -> None:
        """Set the concrete result's status to its error value.

        Subclasses override this hook when their status is represented by an
        application-specific enum.
        """

    def add_warning(
        self,
        code: str,
        message: str,
        source: str | None = None,
        target: str | None = None,
    ) -> None:
        """Append a WARN-severity log item."""
        self.logs.append(
            EtlLogItem(
                code=code,
                message=message,
                severity=LogLevel.WARN,
                source=source,
                target=target,
            )
        )

    def add_info(
        self,
        code: str,
        message: str,
        source: str | None = None,
        target: str | None = None,
    ) -> None:
        """Append an INFO-severity log item."""
        self.logs.append(
            EtlLogItem(
                code=code,
                message=message,
                severity=LogLevel.INFO,
                source=source,
                target=target,
            )
        )

    def has_errors(self) -> bool:
        """Return True if any log item has ERROR severity."""
        return any(x.severity == LogLevel.ERROR for x in self.logs)

    def has_warnings(self) -> bool:
        """Return True if any log item has WARN severity."""
        return any(x.severity == LogLevel.WARN for x in self.logs)

    def has_infos(self) -> bool:
        """Return True if any log item has INFO severity."""
        return any(x.severity == LogLevel.INFO for x in self.logs)

    def has_log_code(self, code: str) -> bool:
        """Return True if any log item carries the given code."""
        return any(x.code == code for x in self.logs)

    def get_errors(self) -> list[EtlLogItem]:
        """Return a list of log items with ERROR severity."""
        return [x for x in self.logs if x.severity == LogLevel.ERROR]

    def get_warnings(self) -> list[EtlLogItem]:
        """Return a list of log items with WARN severity."""
        return [x for x in self.logs if x.severity == LogLevel.WARN]

    def get_infos(self) -> list[EtlLogItem]:
        """Return a list of log items with INFO severity."""
        return [x for x in self.logs if x.severity == LogLevel.INFO]


def validate_int_enum_value(
    enum_class: type[IntEnum], value: int | str | float | IntEnum
) -> IntEnum:
    """Normalize a value to a member of an integer enumeration.

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

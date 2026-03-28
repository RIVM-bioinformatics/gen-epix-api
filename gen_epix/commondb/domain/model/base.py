import datetime
from enum import IntEnum
from uuid import UUID

from pydantic import BaseModel, Field

from gen_epix import fastapp
from gen_epix.commondb.domain.enum import EtlStatus as EtlStatus
from gen_epix.fastapp.enum import LogLevel


class ModelNoId(fastapp.Model):

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
        now = datetime.now(UTC)
        self.modified_at = now
        self.modified_by = user_id

    def set_created(self, user_id: UUID) -> None:
        now = datetime.now(UTC)
        self.modified_at = now
        self.modified_by = user_id
        self.created_at = now


class Model(ModelNoId):
    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the object.",
    )


class EtlLogItem(BaseModel):
    """
    Represents a log item for an ETL result accumulator, containing a timestamp,
    code, message and severity. Immutable Pydantic value object.
    """

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
        description="The severity level of the log item.",
    )


class BaseEtlResult(BaseModel):
    """
    Pydantic BaseModel that declares ``logs`` and provides log accumulation
    and query helpers.

    ``add_error`` appends an ERROR log item and then calls
    ``_set_error_status()``.  Override ``_set_error_status`` in each
    concrete class to apply the appropriate status enum value, e.g.::

        def _set_error_status(self) -> None:
            self.status = MyStatus.ERROR
    """

    logs: list[EtlLogItem] = Field(
        default_factory=list,
        description="Log items capturing messages and events that occurred during the operation.",
    )

    def add_error(self, code: str, message: str) -> None:
        """Append an ERROR-severity log item and update the status."""
        self.logs.append(
            EtlLogItem(code=code, message=message, severity=LogLevel.ERROR)
        )
        self.set_error_status()

    def set_error_status(self) -> None:
        """Override to set the concrete class's error status value."""

    def add_warning(self, code: str, message: str) -> None:
        """Append a WARN-severity log item."""
        self.logs.append(EtlLogItem(code=code, message=message, severity=LogLevel.WARN))

    def add_info(self, code: str, message: str) -> None:
        """Append an INFO-severity log item."""
        self.logs.append(EtlLogItem(code=code, message=message, severity=LogLevel.INFO))

    def has_errors(self) -> bool:
        """Return True if any log item has ERROR severity."""
        return any(log.severity == LogLevel.ERROR for log in self.logs)

    def has_warnings(self) -> bool:
        """Return True if any log item has WARN severity."""
        return any(log.severity == LogLevel.WARN for log in self.logs)

    def has_infos(self) -> bool:
        """Return True if any log item has INFO severity."""
        return any(log.severity == LogLevel.INFO for log in self.logs)

    def has_log_code(self, code: str) -> bool:
        """Return True if any log item carries the given code."""
        return any(log.code == code for log in self.logs)


def validate_int_enum_value(
    enum_class: type[IntEnum], value: int | str | float | IntEnum
) -> IntEnum:
    """Validate that the given value is a valid member of the given IntEnum class."""
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
    """Validate that the given value is a valid member of the given IntEnum class or None."""
    if value is None:
        return None
    return validate_int_enum_value(enum_class, value)

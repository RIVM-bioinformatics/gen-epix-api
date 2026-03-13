"""
Shared result infrastructure for ETL and upload result accumulators.

Provides:
- ``ResultLogItem``: immutable Pydantic log-entry value object.
- ``BaseResult``: Pydantic BaseModel base class that declares the ``logs`` field
  and adds log-query helpers and ``add_error`` / ``add_warning`` / ``add_info``
  conveniences.  ``add_error`` appends an ERROR log item and delegates
  status-setting to ``_set_error_status()``, which subclasses override to apply
  their own status enum value.
"""

import datetime

from pydantic import BaseModel, Field

from gen_epix.fastapp.enum import LogLevel


class ResultLogItem(BaseModel):
    """
    Represents a log item for a result accumulator, containing a timestamp,
    code, message and severity. Immutable Pydantic value object.
    """

    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
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


class BaseResult(BaseModel):
    """
    Pydantic BaseModel that declares ``logs`` and provides log accumulation
    and query helpers.

    ``add_error`` appends an ERROR log item and then calls
    ``_set_error_status()``.  Override ``_set_error_status`` in each
    concrete class to apply the appropriate status enum value, e.g.::

        def _set_error_status(self) -> None:
            self.status = MyStatus.ERROR
    """

    logs: list[ResultLogItem] = Field(
        default_factory=list,
        description="Log items capturing messages and events that occurred during the operation.",
    )

    def add_error(self, code: str, message: str) -> None:
        """Append an ERROR-severity log item and update the status."""
        self.logs.append(ResultLogItem(code=code, message=message, severity=LogLevel.ERROR))
        self._set_error_status()

    def _set_error_status(self) -> None:
        """Override to set the concrete class's error status value."""

    def add_warning(self, code: str, message: str) -> None:
        """Append a WARN-severity log item."""
        self.logs.append(ResultLogItem(code=code, message=message, severity=LogLevel.WARN))

    def add_info(self, code: str, message: str) -> None:
        """Append an INFO-severity log item."""
        self.logs.append(ResultLogItem(code=code, message=message, severity=LogLevel.INFO))

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
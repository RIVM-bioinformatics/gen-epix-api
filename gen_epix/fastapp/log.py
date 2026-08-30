"""Structured log message types and JSON serialization."""

import abc
import datetime
import json
from typing import Any


class BaseLogItem(abc.ABC):
    """
    BaseLogItem class for creating log messages. Defined as a regular class instead of a
    dataclass for efficiency reasons. The `dumps` method is used to convert the object
    to a JSON string that can be inserted in a log.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize a BaseLogItem instance."""
        self.content = kwargs

    @abc.abstractmethod
    def dumps(
        self, indent: int | str | None = None, separators: tuple[str, str] = (",", ":")
    ) -> str:
        """Convert the log item to a JSON string."""
        raise NotImplementedError()

    @staticmethod
    def _custom_json_encoder(obj: Any) -> str:
        """Serialize exceptions, datetimes, and other unsupported objects as strings."""
        if isinstance(obj, Exception):
            # TODO: Provide more structured encoding of exception
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return str(obj)


class LogItem(BaseLogItem):
    """Serialize an application log code, message, and optional contextual fields."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize a LogItem instance."""
        self.code: str | None = kwargs.pop("code", None)  # type: ignore
        self.msg: str | None = kwargs.pop("msg", None)  # type: ignore
        self.content = kwargs if kwargs else None

    def dumps(self, indent=None, separators=(",", ":")) -> str:
        """Serialize this log item as JSON."""
        msg = {
            "code": self.code,
            "msg": self.msg,
        }
        msg = msg if not self.content else msg | self.content
        return json.dumps(
            msg,
            indent=indent,
            separators=separators,
            default=BaseLogItem._custom_json_encoder,
        )

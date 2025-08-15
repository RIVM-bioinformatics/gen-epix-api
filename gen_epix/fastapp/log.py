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
        self.content = kwargs

    @abc.abstractmethod
    def dumps(
        self, indent: int | str | None = None, separators: tuple[str, str] = (",", ":")
    ) -> str:
        raise NotImplementedError

    @staticmethod
    def _custom_json_encoder(obj: Any) -> str:
        if isinstance(obj, Exception):
            # TODO: Provide more structured encoding of exception
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return str(obj)


class LogItem(BaseLogItem):
    def __init__(self, **kwargs: Any) -> None:
        self.code: str | None = kwargs.pop("code", None)  # type: ignore
        self.msg: str | None = kwargs.pop("msg", None)  # type: ignore
        self.content = kwargs if kwargs else None

    def dumps(self, indent=None, separators=(",", ":")) -> str:
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

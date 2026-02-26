import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any

"""
Central JSON logging formatter for all GenEpix container applications.
Ensures every log entry is valid single-line JSON using json.dumps().
Prevents inconsistent Azure Monitor parsing caused by raw string formatting.
Enables reliable structured logging for observability and security dashboards.
"""

_ISO8601_Z_RE = re.compile(r"\+00:00$")


def _utc_iso(ts: float) -> str:
    s = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="milliseconds")
    return _ISO8601_Z_RE.sub("Z", s)


def _safe_json_loads(s: str) -> Any:
    s = s.strip()
    if not s:
        return None
    if not (s.startswith("{") or s.startswith("[")):
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


class JsonFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        service: str | None = None,
        environment: str | None = None,
        merge_message_json: bool = True,
        extras_key: str = "props",
    ):
        super().__init__()
        self.service = (
            service or os.getenv("SERVICE_NAME") or os.getenv("APP_NAME") or None
        )
        self.environment = (
            environment
            or os.getenv("ENVIRONMENT")
            or os.getenv("ASPNETCORE_ENVIRONMENT")
            or None
        )
        self.merge_message_json = merge_message_json
        self.extras_key = extras_key

        self._reserved = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
        }

    def format(self, record: logging.LogRecord) -> str:
        base: dict[str, Any] = {
            "ts": _utc_iso(record.created),
            "level": record.levelname,
            "logger": record.name,
        }
        if self.service:
            base["service"] = self.service
        if self.environment:
            base["environment"] = self.environment

        message = record.getMessage()

        if self.merge_message_json:
            msg_obj = _safe_json_loads(message)
            if isinstance(msg_obj, dict):
                base.update(msg_obj)
            else:
                base["message"] = message
        else:
            base["message"] = message

        if record.exc_info:
            base["exception"] = {
                "type": getattr(record.exc_info[0], "__name__", "Exception"),
                "message": str(record.exc_info[1]),
                "stacktrace": self.formatException(record.exc_info),
            }

        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in self._reserved and not k.startswith("_")
        }
        if extras:
            base[self.extras_key] = extras

        return json.dumps(base, ensure_ascii=False, separators=(",", ":"))

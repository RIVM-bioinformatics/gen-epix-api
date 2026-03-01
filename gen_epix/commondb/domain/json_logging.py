"""
Central JSON logging formatter for all GenEpix container applications.
Ensures every log entry is valid single-line JSON using json.dumps().
Prevents inconsistent Monitoring Platform parsing caused by raw string formatting.
Enables reliable structured logging for observability and security dashboards.

Fix index:
  1. json.dumps uses default=str so non-serialisable extras never crash the
     formatter and always produce valid JSON.
  2. Envelope fields (ts/level/logger) are re-enforced after merging a JSON
     message dict, preventing the merged payload from silently overriding them.
  3. Sensitive key=value pairs (client_secret, password, …) are redacted to
     [REDACTED] in both the message string and string-valued extras.
  4. Stacktraces longer than max_stacktrace_length are truncated before
     serialisation, staying well under the Monitoring Platform 16384-byte limit.
  5. A `content` field in a merged JSON message is normalised to `message`
     when `message` is absent, eliminating the content/message split in monitoring query engines.
  6. UvicornAccessLogFilter extracts HTTP fields (method/path/status/client/
     version) from uvicorn.access records into a structured `http` dict that
     JsonFormatter hoists to the top level, enabling monitoring query engines to filter/project
     them directly without regex extraction.
"""

import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any

_ISO8601_Z_RE = re.compile(r"\+00:00$")

# Fix 3 – patterns whose values must be redacted wherever they appear as
# key=value pairs (query-string or space-separated form).
_SENSITIVE_RE = re.compile(
    r"(?i)(client_secret|password|client_pwd|secret|api_key)=(\S+)"
)
_REDACTED = r"\1=[REDACTED]"

# Fix 6 – regex fallback for when uvicorn access-log args have already been
# evaluated into a single formatted string.
_UVICORN_ACCESS_RE = re.compile(
    r'^(?P<client>\S+) - "(?P<method>\w+) (?P<path>\S+) HTTP/(?P<version>[\d.]+)"'
    r" (?P<status>\d+)"
)

_DEFAULT_MAX_STACKTRACE_LENGTH = 8000  # empirical value keeping typical stacktraces well under the 384-byte limit after JSON overhead


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


def _redact(value: str) -> str:
    """Replace sensitive key=value occurrences with key=[REDACTED]."""
    return _SENSITIVE_RE.sub(_REDACTED, value)


class UvicornAccessLogFilter(logging.Filter):
    """
    Logging filter for the ``uvicorn.access`` logger.

    Parses the structured args tuple that uvicorn emits
    (``(client, method, path, http_version, status_code)``) and injects them
    into ``record._json_fields`` as a nested ``http`` dict.  JsonFormatter
    subsequently hoists ``_json_fields`` to the top level of the JSON output,
    so monitoring query engines can project ``http.method``, ``http.path``, ``http.status``, etc.
    directly without any regex extraction.

    When the record args have already been interpolated (e.g. in tests or
    certain uvicorn configurations) a regex fallback is used instead.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # Priority 1: raw args tuple from uvicorn internals – most reliable.
        if isinstance(record.args, tuple) and len(record.args) == 5:
            client, method, path, version, status = record.args
            record._json_fields = {  # type: ignore[attr-defined]
                "http": {
                    "client": str(client),
                    "method": str(method),
                    "path": str(path),
                    "version": str(version),
                    "status": int(status),
                }
            }
            # Clear args so getMessage() returns the plain event key.
            record.args = ()
            record.msg = "http.access"
        else:
            # Priority 2: regex fallback for already-formatted strings.
            m = _UVICORN_ACCESS_RE.match(record.getMessage())
            if m:
                record._json_fields = {  # type: ignore[attr-defined]
                    "http": {
                        "client": m.group("client"),
                        "method": m.group("method"),
                        "path": m.group("path"),
                        "version": m.group("version"),
                        "status": int(m.group("status")),
                    }
                }
                record.args = ()
                record.msg = "http.access"
        return True


class JsonFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        service: str | None = None,
        environment: str | None = None,
        merge_message_json: bool = True,
        extras_key: str = "props",
        # Fix 4 – default keeps output well under the Monitoring Platform 16384-byte
        # hard limit; set to None to disable truncation entirely.
        max_stacktrace_length: int | None = _DEFAULT_MAX_STACKTRACE_LENGTH,
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
        self.max_stacktrace_length = max_stacktrace_length

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

        # Fix 6 – hoist any structured fields injected by a filter (e.g.
        # UvicornAccessLogFilter) to the top level of the JSON payload.
        json_fields = getattr(record, "_json_fields", None)
        if isinstance(json_fields, dict):
            base.update(json_fields)

        # Fix 3 – redact sensitive values before any further processing.
        message = _redact(record.getMessage())

        if self.merge_message_json:
            msg_obj = _safe_json_loads(message)
            if isinstance(msg_obj, dict):
                base.update(msg_obj)
                # Fix 2 – re-enforce envelope fields so a merged payload can
                # never silently override ts / level / logger.
                base["ts"] = _utc_iso(record.created)
                base["level"] = record.levelname
                base["logger"] = record.name
                # Fix 5 – normalise `content` → `message` when `message` is
                # absent (eliminates the content/message split seen in monitoring query engines).
                if "content" in base and "message" not in base:
                    base["message"] = base.pop("content")
                elif "content" in base:
                    # message already present; drop the redundant content key
                    del base["content"]
            else:
                base["message"] = message
        else:
            base["message"] = message

        if record.exc_info:
            stacktrace = self.formatException(record.exc_info)
            # Fix 4 – truncate long stacktraces before serialisation so the
            # final JSON stays within the Monitoring Platform 16384-byte limit.
            if (
                self.max_stacktrace_length is not None
                and len(stacktrace) > self.max_stacktrace_length
            ):
                stacktrace = (
                    stacktrace[: self.max_stacktrace_length] + "\u2026[truncated]"
                )
            base["exception"] = {
                "type": getattr(record.exc_info[0], "__name__", "Exception"),
                "message": str(record.exc_info[1]),
                "stacktrace": stacktrace,
            }

        extras: dict[str, Any] = {
            k: v
            for k, v in record.__dict__.items()
            if k not in self._reserved and not k.startswith("_")
        }
        # Fix 3 – redact string values inside extras (e.g. request body dict).
        extras = {k: _redact(v) if isinstance(v, str) else v for k, v in extras.items()}
        if extras:
            base[self.extras_key] = extras

        # Fix 1 – default=str ensures non-serialisable values (e.g. arbitrary
        # Python objects) are coerced to strings rather than crashing the
        # formatter and silently producing a non-JSON line.
        return json.dumps(base, ensure_ascii=False, separators=(",", ":"), default=str)

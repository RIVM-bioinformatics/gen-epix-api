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
     serialisation, e.g. to stay below a log monitoring platform limit.
  5. A `content` field in a merged JSON message is normalised to `message`
     when `message` is absent, eliminating the content/message split in monitoring query engines.
  6. UvicornAccessLogFilter extracts HTTP fields (method/path/status/client/
     version) from uvicorn.access records into a structured `http` dict that
     JsonFormatter hoists to the top level, enabling monitoring query engines to filter/project
     them directly without regex extraction.
  7. UvicornAccessLogFilter hardens uvicorn.access handlers at runtime to use
     JsonFormatter when a non-JSON formatter is detected, preventing regressions
     where LogMessage contains plain `INFO ...` text instead of JSON lines.
  8. App events are guaranteed to emit a top-level `message` by normalising from
     `msg` or falling back to `event.<code>` when `msg` is null.
  9. Operational aliases `app_id` and `command_id` are projected to top level
     from nested payload fields for reliable query ergonomics in ContainerLogV2.
 10. Structured service payloads are preserved under `service_meta` so the
     configured top-level `service` label remains dashboard-stable.
 11. Auth-sensitive payloads such as `jwt`, `token`, `authorization`, and
     `claims` are redacted in both merged JSON payloads and extras.
 12. Actor aliases `user_id` and `organization_id` are promoted from nested
     command payloads when present.
 13. Exception messages longer than max_exception_message_length are truncated
     from the middle (prefix …[N chars omitted]… suffix) before serialisation,
     preserving both the echoed SQL/context at the start and the driver's
     actual error text at the end, e.g. for FK/unique constraint violations.
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
_DEFAULT_SENSITIVE_KEYS = (
    "client_secret",
    "password",
    "client_pwd",
    "secret",
    "api_key",
    "jwt",
    "token",
    "access_token",
    "refresh_token",
    "id_token",
    "authorization",
    "claims",
)
_DEFAULT_REDACTED_VALUE = "[REDACTED]"

# Fix 6 – regex fallback for when uvicorn access-log args have already been
# evaluated into a single formatted string.
_UVICORN_ACCESS_RE = re.compile(
    r'^(?P<client>\S+) - "(?P<method>\w+) (?P<path>\S+) HTTP/(?P<version>[\d.]+)"'
    r" (?P<status>\d+)"
)

_DEFAULT_MAX_STACKTRACE_LENGTH = 8000  # empirical value keeping typical stacktraces not too long for e.g. a log monitoring platform
_DEFAULT_MAX_EXCEPTION_MSG_LENGTH = 2000  # prevents huge SQL payloads in exception messages from drowning out the error context


def _truncate_middle(text: str, max_length: int) -> str:
    """Truncate *text* to *max_length* chars, keeping a prefix and a suffix.
    DB driver errors (e.g. FK/unique constraint violations) often echo the
    full SQL statement first and put the actual error message at the end, so
    a head-only cut would hide it."""
    if len(text) <= max_length:
        return text
    half = max_length // 2
    omitted = len(text) - max_length
    return f"{text[:half]}…[{omitted} chars omitted]…{text[-half:]}"


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


def _normalise_sensitive_keys(
    sensitive_keys: list[str] | tuple[str, ...] | set[str] | None,
) -> tuple[str, ...]:
    if sensitive_keys is None:
        return _DEFAULT_SENSITIVE_KEYS
    deduped: list[str] = []
    for key in sensitive_keys:
        normalized = str(key).strip().lower()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return tuple(deduped) if deduped else _DEFAULT_SENSITIVE_KEYS


def _build_sensitive_re(sensitive_keys: tuple[str, ...]) -> re.Pattern[str]:
    escaped = "|".join(re.escape(x) for x in sensitive_keys)
    return re.compile(rf"(?i)({escaped})=((?:Bearer\s+)?[^\s&,;]+)")


class UvicornAccessLogFilter(logging.Filter):
    """
    Logging filter for the ``uvicorn.access`` logger.

    Parses the structured args tuple that uvicorn emits
    (``(client, method, path, http_version, status_code)``) and injects them
    into ``record._json_fields`` as a nested ``http`` dict.  JsonFormatter
    subsequently hoists ``_json_fields`` to the top level of the JSON output,
    so monitoring query engines can project ``http.method``, ``http.path``, ``http.status``, etc.
    directly without any regex extraction.

    The filter also normalises the emitted event text by rewriting
    ``record.msg`` to ``http.access <method> <path> <status>`` and clearing
    ``record.args`` after extraction.

    In some runtime combinations (e.g. when another component re-attaches a
    non-JSON formatter to ``uvicorn.access`` handlers), the structured fields
    are still injected but output is rendered as plain text like
    ``INFO http.access ...``. To keep downstream ContainerLog/Grafana parsing
    stable, this filter also hardens ``uvicorn.access`` handlers back to
    JsonFormatter on the fly.

    When the record args have already been interpolated (e.g. in tests or
    certain uvicorn configurations) a regex fallback is used instead.
    """

    @staticmethod
    def _build_access_message(method: Any, path: Any, status: Any) -> str:
        return f"http.access {method} {path} {status}"

    @staticmethod
    def _is_json_formatter(formatter: logging.Formatter | None) -> bool:
        return isinstance(formatter, JsonFormatter)

    @classmethod
    def _discover_json_formatter(cls) -> logging.Formatter | None:
        """Find an existing JsonFormatter instance from any configured logger."""
        root_logger = logging.getLogger()
        candidate_loggers: list[logging.Logger] = [root_logger]
        for logger_name in logging.root.manager.loggerDict.keys():
            logger = logging.getLogger(logger_name)
            candidate_loggers.append(logger)

        for logger in candidate_loggers:
            for handler in logger.handlers:
                if cls._is_json_formatter(handler.formatter):
                    return handler.formatter
        return None

    @classmethod
    def _ensure_uvicorn_access_json_formatter(cls, record: logging.LogRecord) -> None:
        """Guarantee uvicorn.access handlers use JsonFormatter at emit time."""
        logger = logging.getLogger(record.name)
        if not logger.handlers:
            return
        if all(
            cls._is_json_formatter(handler.formatter) for handler in logger.handlers
        ):
            return

        json_formatter = cls._discover_json_formatter()
        if json_formatter is None:
            json_formatter = JsonFormatter()

        for handler in logger.handlers:
            if cls._is_json_formatter(handler.formatter):
                continue
            handler.setFormatter(json_formatter)

    def filter(self, record: logging.LogRecord) -> bool:
        self._ensure_uvicorn_access_json_formatter(record)

        # Priority 1: raw args tuple from uvicorn internals – most reliable.
        if isinstance(record.args, tuple) and len(record.args) == 5:
            client, method, path, version, status_raw = record.args
            if not isinstance(status_raw, (int, str)):
                return True
            try:
                status_i = int(status_raw)
            except ValueError:
                return True
            record._json_fields = {
                "http": {
                    "client": str(client),
                    "method": str(method),
                    "path": str(path),
                    "version": str(version),
                    "status": status_i,
                }
            }
            # Clear args so getMessage() returns the plain event key.
            record.args = ()
            record.msg = self._build_access_message(method, path, status_i)
        else:
            # Priority 2: regex fallback for already-formatted strings.
            m = _UVICORN_ACCESS_RE.match(record.getMessage())
            if m:
                status_i = int(str(m.group("status")))
                record._json_fields = {
                    "http": {
                        "client": m.group("client"),
                        "method": m.group("method"),
                        "path": m.group("path"),
                        "version": m.group("version"),
                        "status": status_i,
                    }
                }
                record.args = ()
                record.msg = self._build_access_message(
                    m.group("method"),
                    m.group("path"),
                    status_i,
                )
        return True


class JsonFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        service: str | None = None,
        environment: str | None = None,
        merge_message_json: bool = True,
        extras_key: str = "props",
        sensitive_keys: list[str] | tuple[str, ...] | set[str] | None = None,
        redacted_value: str = _DEFAULT_REDACTED_VALUE,
        max_stacktrace_length: int | None = _DEFAULT_MAX_STACKTRACE_LENGTH,
        max_exception_message_length: int | None = _DEFAULT_MAX_EXCEPTION_MSG_LENGTH,
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
        self.sensitive_keys = _normalise_sensitive_keys(sensitive_keys)
        self._sensitive_key_set = set(self.sensitive_keys)
        self.redacted_value = redacted_value or _DEFAULT_REDACTED_VALUE
        self._sensitive_re = _build_sensitive_re(self.sensitive_keys)
        self._redacted_kv = rf"\1={self.redacted_value}"
        self.max_stacktrace_length = max_stacktrace_length
        self.max_exception_message_length = max_exception_message_length

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

    def _redact(self, value: str) -> str:
        """Replace sensitive key=value occurrences with key=[REDACTED]."""
        return self._sensitive_re.sub(self._redacted_kv, value)

    def _redact_nested(self, value: Any, *, key_name: str | None = None) -> Any:
        """Recursively redact sensitive values in nested dict/list payloads."""
        if key_name is not None and key_name.lower() in self._sensitive_key_set:
            return self.redacted_value

        if isinstance(value, str):
            return self._redact(value)

        if isinstance(value, dict):
            return {
                x: self._redact_nested(y, key_name=str(x)) for x, y in value.items()
            }

        if isinstance(value, list):
            return [self._redact_nested(x) for x in value]

        if isinstance(value, tuple):
            return tuple(self._redact_nested(x) for x in value)

        return value

    @staticmethod
    def _get_app_id(payload: dict[str, Any]) -> str | None:
        app = payload.get("app")
        if not isinstance(app, dict):
            return None
        app_id = app.get("id")
        if app_id is None:
            return None
        return str(app_id)

    @staticmethod
    def _get_command_id(payload: dict[str, Any]) -> str | None:
        command = payload.get("command")
        if not isinstance(command, dict):
            return None
        command_id = command.get("id")
        if command_id is None:
            command_object = command.get("object")
            if isinstance(command_object, dict):
                command_id = command_object.get("id")
        if command_id is None:
            return None
        return str(command_id)

    @staticmethod
    def _get_user_id(payload: dict[str, Any]) -> str | None:
        command = payload.get("command")
        if not isinstance(command, dict):
            return None

        # Prefer the explicit command-level actor field when present; some log
        # payloads only carry user context inside command.object.user, so keep
        # that as a backwards-compatible fallback for queryable top-level aliases.
        user_id = command.get("user_id")
        if user_id is not None:
            return str(user_id)

        command_object = command.get("object")
        if not isinstance(command_object, dict):
            return None

        user = command_object.get("user")
        if not isinstance(user, dict):
            return None

        user_id = user.get("id")
        if user_id is None:
            return None
        return str(user_id)

    @staticmethod
    def _get_organization_id(payload: dict[str, Any]) -> str | None:
        command = payload.get("command")
        if not isinstance(command, dict):
            return None

        command_object = command.get("object")
        if not isinstance(command_object, dict):
            return None

        user = command_object.get("user")
        if not isinstance(user, dict):
            return None

        organization_id = user.get("organization_id")
        if organization_id is None:
            return None
        return str(organization_id)

    @staticmethod
    def _is_non_empty_string(value: Any) -> bool:
        return isinstance(value, str) and value.strip() != ""

    def _normalise_containerlogv2_fields(self, payload: dict[str, Any]) -> None:
        # Ensure every app-style log event has a usable top-level message.
        if "message" not in payload:
            raw_msg = payload.get("msg")
            if self._is_non_empty_string(raw_msg):
                payload["message"] = raw_msg
            else:
                code = payload.get("code")
                if self._is_non_empty_string(code):
                    payload["message"] = f"event.{code}"

        # Add top-level aliases for common operational IDs to simplify queries.
        if "app_id" not in payload:
            app_id = self._get_app_id(payload)
            if app_id is not None:
                payload["app_id"] = app_id

        if "command_id" not in payload:
            command_id = self._get_command_id(payload)
            if command_id is not None:
                payload["command_id"] = command_id

        if "user_id" not in payload:
            user_id = self._get_user_id(payload)
            if user_id is not None:
                payload["user_id"] = user_id

        if "organization_id" not in payload:
            organization_id = self._get_organization_id(payload)
            if organization_id is not None:
                payload["organization_id"] = organization_id

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
        message = self._redact(record.getMessage())

        if self.merge_message_json:
            msg_obj = _safe_json_loads(message)
            if isinstance(msg_obj, dict):
                msg_obj = self._redact_nested(msg_obj)
                structured_service = None
                if isinstance(msg_obj.get("service"), dict):
                    structured_service = msg_obj.pop("service")
                base.update(msg_obj)
                # Fix 2 – re-enforce envelope fields so a merged payload can
                # never silently override ts / level / logger.
                base["ts"] = _utc_iso(record.created)
                base["level"] = record.levelname
                base["logger"] = record.name
                if self.service is not None:
                    base["service"] = self.service
                if self.environment is not None:
                    base["environment"] = self.environment
                if isinstance(structured_service, dict):
                    existing_service_meta = base.get("service_meta")
                    if isinstance(existing_service_meta, dict):
                        base["service_meta"] = {
                            **structured_service,
                            **existing_service_meta,
                        }
                    else:
                        base["service_meta"] = structured_service
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

        self._normalise_containerlogv2_fields(base)

        if record.exc_info:
            stacktrace = self.formatException(record.exc_info)
            if (
                self.max_stacktrace_length is not None
                and len(stacktrace) > self.max_stacktrace_length
            ):
                stacktrace = (
                    stacktrace[: self.max_stacktrace_length] + "\u2026[truncated]"
                )
            exc_msg = str(record.exc_info[1])
            if self.max_exception_message_length is not None:
                exc_msg = _truncate_middle(exc_msg, self.max_exception_message_length)
            base["exception"] = {
                "type": getattr(record.exc_info[0], "__name__", "Exception"),
                "message": exc_msg,
                "stacktrace": stacktrace,
            }

        extras: dict[str, Any] = {
            x: y
            for x, y in record.__dict__.items()
            if x not in self._reserved and not x.startswith("_")
        }
        # Fix 3 – redact string values inside extras (e.g. request body dict).
        extras = self._redact_nested(extras)
        if extras:
            base[self.extras_key] = extras

        # Fix 1 – default=str ensures non-serialisable values (e.g. arbitrary
        # Python objects) are coerced to strings rather than crashing the
        # formatter and silently producing a non-JSON line.
        return json.dumps(base, ensure_ascii=False, separators=(",", ":"), default=str)

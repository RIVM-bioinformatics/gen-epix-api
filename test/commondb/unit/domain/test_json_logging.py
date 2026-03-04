import json
import logging
import sys
from typing import Any

import pytest

from gen_epix.commondb.config.json_logging import JsonFormatter, UvicornAccessLogFilter


def _make_record(
    *,
    msg: str,
    level: int = logging.INFO,
    extra: dict[str, object] | None = None,
    exc_info: (
        tuple[type[BaseException], BaseException, Any] | tuple[None, None, None] | None
    ) = None,
) -> logging.LogRecord:
    logger = logging.getLogger("test.logger")
    return logger.makeRecord(
        name=logger.name,
        level=level,
        fn=__file__,
        lno=42,
        msg=msg,
        args=(),
        exc_info=exc_info,
        extra=extra,
    )


def test_green_formats_plain_message_and_expected_extras() -> None:
    formatter = JsonFormatter(service="commondb", environment="test")
    record = _make_record(msg="hello world", extra={"request_id": "req-1"})

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "test.logger"
    assert payload["service"] == "commondb"
    assert payload["environment"] == "test"
    assert payload["message"] == "hello world"
    # Red learning: LogRecord can include runtime-specific extra keys (e.g. taskName).
    # Assert only the contract we care about.
    assert payload["props"]["request_id"] == "req-1"
    assert payload["ts"].endswith("Z")


def test_merges_json_message_dict_by_default() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg='{"event":"login","ok":true}')

    payload = json.loads(formatter.format(record))

    assert payload["event"] == "login"
    assert payload["ok"] is True
    assert "message" not in payload


def test_keeps_message_when_json_merge_is_disabled() -> None:
    formatter = JsonFormatter(merge_message_json=False)
    record = _make_record(msg='{"event":"login","ok":true}')

    payload = json.loads(formatter.format(record))

    assert payload["message"] == '{"event":"login","ok":true}'
    assert "event" not in payload


def test_adds_exception_payload() -> None:
    formatter = JsonFormatter()

    try:
        raise ValueError("boom")
    except ValueError:
        record = _make_record(
            msg="failed", level=logging.ERROR, exc_info=sys.exc_info()
        )

    payload = json.loads(formatter.format(record))

    assert payload["message"] == "failed"
    assert payload["exception"]["type"] == "ValueError"
    assert payload["exception"]["message"] == "boom"
    assert "ValueError: boom" in payload["exception"]["stacktrace"]


def test_uses_env_when_constructor_values_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SERVICE_NAME", "service-from-env")
    monkeypatch.setenv("ENVIRONMENT", "env-from-env")

    formatter = JsonFormatter()
    record = _make_record(msg="from env")

    payload = json.loads(formatter.format(record))

    assert payload["service"] == "service-from-env"
    assert payload["environment"] == "env-from-env"


# ---------------------------------------------------------------------------
# Fix 1 – non-serializable extras must still produce valid JSON
# ---------------------------------------------------------------------------


def test_non_serializable_extra_still_produces_valid_json() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg="hello", extra={"obj": object()})

    result = formatter.format(record)

    # Must not raise – i.e. output is always valid JSON even with exotic extras
    payload = json.loads(result)
    assert payload["message"] == "hello"
    # The non-serializable value should have been coerced to a string
    assert isinstance(payload["props"]["obj"], str)


# ---------------------------------------------------------------------------
# Fix 2 – merged JSON dict must not override envelope fields
# ---------------------------------------------------------------------------


def test_merged_json_cannot_override_envelope_ts_level_logger() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg='{"ts":"2000-01-01T00:00:00.000Z","level":"DEBUG","logger":"evil","event":"ok"}'
    )

    payload = json.loads(formatter.format(record))

    # Envelope fields must come from the LogRecord, not from the merged dict
    assert not payload["ts"].startswith("2000-01-01")
    assert payload["level"] == "INFO"
    assert payload["logger"] == "test.logger"
    # Other fields from the merged dict are still present
    assert payload["event"] == "ok"


def test_merged_json_cannot_override_service_and_environment() -> None:
    formatter = JsonFormatter(service="svc-a", environment="prod")
    record = _make_record(
        msg='{"service":{"id":"not-allowed"},"environment":{"name":"shadow"},"event":"ok"}'
    )

    payload = json.loads(formatter.format(record))

    assert payload["service"] == "svc-a"
    assert payload["environment"] == "prod"
    assert payload["event"] == "ok"


# ---------------------------------------------------------------------------
# Fix 3 – sensitive key=value pairs are redacted
# ---------------------------------------------------------------------------


def test_sensitive_client_secret_is_redacted_in_plain_message() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg="POST /oauth/token client_secret=super-secret&grant_type=client_credentials"
    )

    payload = json.loads(formatter.format(record))

    assert "super-secret" not in payload["message"]
    assert "client_secret=[REDACTED]" in payload["message"]


def test_sensitive_password_is_redacted_in_plain_message() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg="login attempt password=hunter2 user=alice")

    payload = json.loads(formatter.format(record))

    assert "hunter2" not in payload["message"]
    assert "password=[REDACTED]" in payload["message"]


def test_sensitive_value_is_redacted_in_string_extras() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg="auth request",
        extra={"body": "client_secret=my-secret&grant_type=password"},
    )

    payload = json.loads(formatter.format(record))

    serialized = json.dumps(payload)
    assert "my-secret" not in serialized
    assert "client_secret=[REDACTED]" in serialized


def test_sensitive_keys_are_redacted_in_merged_json_payload() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg='{"client_secret":"abc","nested":{"password":"hunter2"},"records":[{"api_key":"k-1"}]}'
    )

    payload = json.loads(formatter.format(record))

    assert payload["client_secret"] == "[REDACTED]"
    assert payload["nested"]["password"] == "[REDACTED]"
    assert payload["records"][0]["api_key"] == "[REDACTED]"


def test_sensitive_keys_are_redacted_in_nested_extras() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg="auth request",
        extra={
            "payload": {
                "client_pwd": "abc",
                "items": [{"secret": "s1"}, {"password": "s2"}],
            }
        },
    )

    payload = json.loads(formatter.format(record))

    assert payload["props"]["payload"]["client_pwd"] == "[REDACTED]"
    assert payload["props"]["payload"]["items"][0]["secret"] == "[REDACTED]"
    assert payload["props"]["payload"]["items"][1]["password"] == "[REDACTED]"


def test_redaction_can_be_configured_with_custom_sensitive_keys() -> None:
    formatter = JsonFormatter(
        sensitive_keys=["token_subject"],
        redacted_value="[MASKED]",
    )
    record = _make_record(
        msg='{"token_subject":"abc","password":"hunter2"}',
    )

    payload = json.loads(formatter.format(record))

    assert payload["token_subject"] == "[MASKED]"
    assert payload["password"] == "hunter2"


def test_redaction_can_be_configured_with_custom_redacted_value() -> None:
    formatter = JsonFormatter(redacted_value="[MASKED]")
    record = _make_record(msg="auth api_key=secret-123")

    payload = json.loads(formatter.format(record))

    assert "secret-123" not in payload["message"]
    assert "api_key=[MASKED]" in payload["message"]


def test_non_sensitive_message_is_unchanged() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg="GET /api/cases HTTP/1.1 200 OK")

    payload = json.loads(formatter.format(record))

    assert payload["message"] == "GET /api/cases HTTP/1.1 200 OK"


# ---------------------------------------------------------------------------
# Fix 4 – long stacktraces are truncated to stay within the max length
# ---------------------------------------------------------------------------


def test_stacktrace_truncated_when_max_stacktrace_length_set() -> None:
    formatter = JsonFormatter(max_stacktrace_length=80)

    try:
        raise ValueError("deep boom")
    except ValueError:
        record = _make_record(
            msg="failed", level=logging.ERROR, exc_info=sys.exc_info()
        )

    payload = json.loads(formatter.format(record))

    assert "exception" in payload
    stacktrace = payload["exception"]["stacktrace"]
    assert len(stacktrace) <= 80 + len("…[truncated]")
    assert stacktrace.endswith("…[truncated]")


def test_stacktrace_not_truncated_below_threshold() -> None:
    # With a generous limit the full traceback should be preserved
    formatter = JsonFormatter(max_stacktrace_length=100_000)

    try:
        raise ValueError("small boom")
    except ValueError:
        record = _make_record(
            msg="failed", level=logging.ERROR, exc_info=sys.exc_info()
        )

    payload = json.loads(formatter.format(record))

    assert "…[truncated]" not in payload["exception"]["stacktrace"]


# ---------------------------------------------------------------------------
# Fix 5 – `content` field in merged JSON is normalised to `message`
# ---------------------------------------------------------------------------


def test_content_field_normalised_to_message_when_message_absent() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg='{"content":"HTTP Request: GET /cases","event":"http"}')

    payload = json.loads(formatter.format(record))

    assert payload.get("message") == "HTTP Request: GET /cases"
    assert "content" not in payload
    assert payload["event"] == "http"


def test_content_field_not_overriding_explicit_message() -> None:
    # When the merged dict already has 'message', 'content' should not clobber it
    formatter = JsonFormatter()
    record = _make_record(msg='{"content":"secondary","message":"primary","event":"x"}')

    payload = json.loads(formatter.format(record))

    assert payload["message"] == "primary"
    # content should be dropped since message was already set
    assert "content" not in payload


# ---------------------------------------------------------------------------
# Fix 6 – UvicornAccessLogFilter: structured HTTP fields from access logs
# ---------------------------------------------------------------------------


def _make_uvicorn_access_record(
    client: str = "127.0.0.1:12345",
    method: str = "GET",
    path: str = "/v1/cases",
    version: str = "1.1",
    status: int = 200,
    *,
    pre_format: bool = False,
) -> logging.LogRecord:
    """Build a LogRecord that mimics what uvicorn.access emits."""
    logger = logging.getLogger("uvicorn.access")
    if pre_format:
        # Simulate a record where getMessage() has already been evaluated
        msg = f'{client} - "{method} {path} HTTP/{version}" {status}'
        record = logger.makeRecord(
            name=logger.name,
            level=logging.INFO,
            fn="<uvicorn>",
            lno=0,
            msg=msg,
            args=(),
            exc_info=None,
        )
    else:
        record = logger.makeRecord(
            name=logger.name,
            level=logging.INFO,
            fn="<uvicorn>",
            lno=0,
            msg='%s - "%s %s HTTP/%s" %d',
            args=(client, method, path, version, status),
            exc_info=None,
        )
    return record


def test_uvicorn_access_filter_parses_args_tuple() -> None:
    filt = UvicornAccessLogFilter()
    formatter = JsonFormatter()
    record = _make_uvicorn_access_record(method="POST", path="/v1/upload", status=201)

    filt.filter(record)
    payload = json.loads(formatter.format(record))

    assert payload["message"] == "http.access POST /v1/upload 201"
    http = payload["http"]
    assert http["method"] == "POST"
    assert http["path"] == "/v1/upload"
    assert http["status"] == 201
    assert http["client"] == "127.0.0.1:12345"
    assert http["version"] == "1.1"


def test_uvicorn_access_filter_falls_back_to_regex_on_formatted_string() -> None:
    filt = UvicornAccessLogFilter()
    formatter = JsonFormatter()
    record = _make_uvicorn_access_record(
        method="DELETE", path="/v1/cases/abc", status=204, pre_format=True
    )

    filt.filter(record)
    payload = json.loads(formatter.format(record))

    assert payload["message"] == "http.access DELETE /v1/cases/abc 204"
    http = payload["http"]
    assert http["method"] == "DELETE"
    assert http["path"] == "/v1/cases/abc"
    assert http["status"] == 204


def test_uvicorn_access_filter_passes_through_non_access_records() -> None:
    filt = UvicornAccessLogFilter()
    formatter = JsonFormatter()
    record = _make_record(msg="startup complete")

    filt.filter(record)
    payload = json.loads(formatter.format(record))

    assert payload["message"] == "startup complete"
    assert "http" not in payload


def test_json_fields_merged_to_top_level_not_into_props() -> None:
    # _json_fields injected by a filter must appear at the top level of the
    # JSON output, not nested under 'props'.
    formatter = JsonFormatter()
    record = _make_record(msg="synthesised")
    record._json_fields = {"http": {"method": "GET", "status": 200}}  # type: ignore[attr-defined]

    payload = json.loads(formatter.format(record))

    assert payload["http"] == {"method": "GET", "status": 200}
    # Must NOT also appear inside props
    assert "http" not in payload.get("props", {})

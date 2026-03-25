import json
import logging
import sys
from io import StringIO
from typing import Any

import pytest

from gen_epix.commondb.config.json_logging import JsonFormatter, UvicornAccessLogFilter


_TRUNCATED_SUFFIX = "\u2026[truncated]"


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


def _format_payload(
    formatter: JsonFormatter, record: logging.LogRecord
) -> dict[str, Any]:
    return json.loads(formatter.format(record))


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_merges_json_message_dict_by_default() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg='{"event":"login","ok":true}')

    payload = json.loads(formatter.format(record))

    assert payload["event"] == "login"
    assert payload["ok"] is True
    assert "message" not in payload


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_keeps_message_when_json_merge_is_disabled() -> None:
    formatter = JsonFormatter(merge_message_json=False)
    record = _make_record(msg='{"event":"login","ok":true}')

    payload = json.loads(formatter.format(record))

    assert payload["message"] == '{"event":"login","ok":true}'
    assert "event" not in payload


@pytest.mark.scenario_ids("TC-LOG-01-01")
@pytest.mark.parametrize("msg", ['["event","login"]', '{"event":'])
def test_non_mergeable_json_like_messages_are_kept_as_plain_text(msg: str) -> None:
    payload = _format_payload(JsonFormatter(), _make_record(msg=msg))

    assert payload["message"] == msg
    assert "event" not in payload


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_uses_secondary_env_fallbacks_when_primary_env_vars_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SERVICE_NAME", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.setenv("APP_NAME", "service-from-app-name")
    monkeypatch.setenv("ASPNETCORE_ENVIRONMENT", "env-from-aspnet")

    payload = _format_payload(JsonFormatter(), _make_record(msg="from secondary env"))

    assert payload["service"] == "service-from-app-name"
    assert payload["environment"] == "env-from-aspnet"


# ---------------------------------------------------------------------------
# Fix 1 – non-serializable extras must still produce valid JSON
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_non_serializable_extra_still_produces_valid_json() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg="hello", extra={"obj": object()})

    result = formatter.format(record)

    # Must not raise – i.e. output is always valid JSON even with exotic extras
    payload = json.loads(result)
    assert payload["message"] == "hello"
    # The non-serializable value should have been coerced to a string
    assert isinstance(payload["props"]["obj"], str)


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_custom_extras_key_is_used_for_extra_fields() -> None:
    payload = _format_payload(
        JsonFormatter(extras_key="context"),
        _make_record(msg="hello", extra={"request_id": "req-1"}),
    )

    assert payload["context"]["request_id"] == "req-1"
    assert "props" not in payload


# ---------------------------------------------------------------------------
# Fix 2 – merged JSON dict must not override envelope fields
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_merged_json_cannot_override_service_and_environment() -> None:
    formatter = JsonFormatter(service="svc-a", environment="prod")
    record = _make_record(
        msg='{"service":{"id":"not-allowed"},"environment":{"name":"shadow"},"event":"ok"}'
    )

    payload = json.loads(formatter.format(record))

    assert payload["service"] == "svc-a"
    assert payload["environment"] == "prod"
    assert payload["event"] == "ok"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_structured_service_payload_is_preserved_under_service_meta() -> None:
    formatter = JsonFormatter(service="svc-a", environment="prod")
    record = _make_record(
        msg='{"service":{"id":"svc-123","name":"UploadService"},"event":"ok"}'
    )

    payload = json.loads(formatter.format(record))

    assert payload["service"] == "svc-a"
    assert payload["environment"] == "prod"
    assert payload["service_meta"] == {"id": "svc-123", "name": "UploadService"}
    assert payload["event"] == "ok"


# ---------------------------------------------------------------------------
# Fix 3 – sensitive key=value pairs are redacted
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_sensitive_client_secret_is_redacted_in_plain_message() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg="POST /oauth/token client_secret=super-secret&grant_type=client_credentials"
    )

    payload = json.loads(formatter.format(record))

    assert "super-secret" not in payload["message"]
    assert "client_secret=[REDACTED]" in payload["message"]


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_sensitive_password_is_redacted_in_plain_message() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg="login attempt password=hunter2 user=alice")

    payload = json.loads(formatter.format(record))

    assert "hunter2" not in payload["message"]
    assert "password=[REDACTED]" in payload["message"]


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_sensitive_auth_fields_are_redacted_in_plain_message() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg="auth token=tok-123 access_token=acc-123 refresh_token=ref-123 id_token=id-123 authorization=Bearer-123 jwt=jwt-123"
    )

    payload = json.loads(formatter.format(record))

    serialized = json.dumps(payload)
    for secret in ("tok-123", "acc-123", "ref-123", "id-123", "Bearer-123", "jwt-123"):
        assert secret not in serialized
    assert "token=[REDACTED]" in payload["message"]
    assert "access_token=[REDACTED]" in payload["message"]
    assert "refresh_token=[REDACTED]" in payload["message"]
    assert "id_token=[REDACTED]" in payload["message"]
    assert "authorization=[REDACTED]" in payload["message"]
    assert "jwt=[REDACTED]" in payload["message"]


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_sensitive_bearer_authorization_is_fully_redacted_in_plain_message() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg="auth header authorization=Bearer abc.def.ghi token=tok-123"
    )

    payload = json.loads(formatter.format(record))

    serialized = json.dumps(payload)
    assert "abc.def.ghi" not in serialized
    assert "tok-123" not in serialized
    assert payload["message"] == (
        "auth header authorization=[REDACTED] token=[REDACTED]"
    )


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_sensitive_keys_are_redacted_in_merged_json_payload() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg='{"client_secret":"abc","nested":{"password":"hunter2"},"records":[{"api_key":"k-1"}]}'
    )

    payload = json.loads(formatter.format(record))

    assert payload["client_secret"] == "[REDACTED]"
    assert payload["nested"]["password"] == "[REDACTED]"
    assert payload["records"][0]["api_key"] == "[REDACTED]"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_sensitive_auth_keys_are_redacted_in_merged_json_and_extras() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg='{"jwt":"jwt-123","claims":{"sub":"user-1"},"authorization":"Bearer-123"}',
        extra={
            "payload": {
                "token": "tok-123",
                "access_token": "acc-123",
                "refresh_token": "ref-123",
                "id_token": "id-123",
            }
        },
    )

    payload = json.loads(formatter.format(record))

    serialized = json.dumps(payload)
    for secret in ("jwt-123", "Bearer-123", "tok-123", "acc-123", "ref-123", "id-123"):
        assert secret not in serialized
    assert payload["jwt"] == "[REDACTED]"
    assert payload["claims"] == "[REDACTED]"
    assert payload["authorization"] == "[REDACTED]"
    assert payload["props"]["payload"]["token"] == "[REDACTED]"
    assert payload["props"]["payload"]["access_token"] == "[REDACTED]"
    assert payload["props"]["payload"]["refresh_token"] == "[REDACTED]"
    assert payload["props"]["payload"]["id_token"] == "[REDACTED]"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_nested_claims_are_redacted_in_merged_json_payload() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg='{"auth":{"claims":{"sub":"user-1","roles":["admin"]}},"event":"ok"}'
    )

    payload = json.loads(formatter.format(record))

    serialized = json.dumps(payload)
    assert "user-1" not in serialized
    assert "admin" not in serialized
    assert payload["auth"]["claims"] == "[REDACTED]"
    assert payload["event"] == "ok"


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_redaction_can_be_configured_with_custom_redacted_value() -> None:
    formatter = JsonFormatter(redacted_value="[MASKED]")
    record = _make_record(msg="auth api_key=secret-123")

    payload = json.loads(formatter.format(record))

    assert "secret-123" not in payload["message"]
    assert "api_key=[MASKED]" in payload["message"]


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_non_sensitive_message_is_unchanged() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg="GET /api/cases HTTP/1.1 200 OK")

    payload = json.loads(formatter.format(record))

    assert payload["message"] == "GET /api/cases HTTP/1.1 200 OK"


# ---------------------------------------------------------------------------
# Fix 4 – long stacktraces are truncated to stay within the max length
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-LOG-01-01")
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
    assert len(stacktrace) <= 80 + len(_TRUNCATED_SUFFIX)
    assert stacktrace.endswith(_TRUNCATED_SUFFIX)


@pytest.mark.scenario_ids("TC-LOG-01-01")
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

    assert _TRUNCATED_SUFFIX not in payload["exception"]["stacktrace"]


# ---------------------------------------------------------------------------
# Fix 5 – `content` field in merged JSON is normalised to `message`
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_content_field_normalised_to_message_when_message_absent() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg='{"content":"HTTP Request: GET /cases","event":"http"}')

    payload = json.loads(formatter.format(record))

    assert payload.get("message") == "HTTP Request: GET /cases"
    assert "content" not in payload
    assert payload["event"] == "http"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_content_field_not_overriding_explicit_message() -> None:
    # When the merged dict already has 'message', 'content' should not clobber it
    formatter = JsonFormatter()
    record = _make_record(msg='{"content":"secondary","message":"primary","event":"x"}')

    payload = json.loads(formatter.format(record))

    assert payload["message"] == "primary"
    # content should be dropped since message was already set
    assert "content" not in payload


# ---------------------------------------------------------------------------
# Fix 8/9 – ContainerLogV2-friendly message + operational ID aliases
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_starting_app_msg_is_promoted_and_app_id_alias_is_added() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg='{"code":"e8aafcec","msg":"STARTING_APP","app":{"id":"app-123","name":"CASEDB"}}'
    )

    payload = json.loads(formatter.format(record))

    assert payload["message"] == "STARTING_APP"
    assert payload["app"]["id"] == "app-123"
    assert payload["app_id"] == "app-123"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_started_command_info_has_command_id_alias() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg='{"code":"e94cad9b","msg":"STARTED_COMMAND","command":{"class":"DemoCommand","id":"cmd-123","user_id":"u-1"}}'
    )

    payload = json.loads(formatter.format(record))

    assert payload["message"] == "STARTED_COMMAND"
    assert payload["command"]["id"] == "cmd-123"
    assert payload["command_id"] == "cmd-123"
    assert payload["user_id"] == "u-1"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_started_command_debug_derives_command_id_from_command_object() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg='{"code":"e94cad9b","msg":"STARTED_COMMAND","command":{"class":"DemoCommand","object":{"id":"cmd-obj-123"},"parent_command_id":null}}',
        level=logging.DEBUG,
    )

    payload = json.loads(formatter.format(record))

    assert payload["message"] == "STARTED_COMMAND"
    assert payload["command"]["object"]["id"] == "cmd-obj-123"
    assert payload["command_id"] == "cmd-obj-123"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_nested_command_object_promotes_user_and_organization_aliases() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        msg='{"code":"e94cad9b","msg":"STARTED_COMMAND","command":{"class":"DemoCommand","object":{"id":"cmd-obj-123","user":{"id":"u-123","organization_id":"org-456"}},"parent_command_id":null}}',
        level=logging.DEBUG,
    )

    payload = json.loads(formatter.format(record))

    assert payload["command_id"] == "cmd-obj-123"
    assert payload["user_id"] == "u-123"
    assert payload["organization_id"] == "org-456"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_null_msg_with_code_gets_non_empty_fallback_message() -> None:
    formatter = JsonFormatter()
    record = _make_record(msg='{"code":"da1d8a32","msg":null}')

    payload = json.loads(formatter.format(record))

    assert payload["msg"] is None
    assert payload["message"] == "event.da1d8a32"


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


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_uvicorn_access_message_is_request_specific_not_constant() -> None:
    filt = UvicornAccessLogFilter()
    formatter = JsonFormatter()
    first = _make_uvicorn_access_record(method="GET", path="/v1/health", status=200)
    second = _make_uvicorn_access_record(method="PUT", path="/v1/cases/42", status=409)

    filt.filter(first)
    filt.filter(second)
    first_payload = json.loads(formatter.format(first))
    second_payload = json.loads(formatter.format(second))

    assert first_payload["message"] == "http.access GET /v1/health 200"
    assert second_payload["message"] == "http.access PUT /v1/cases/42 409"
    assert first_payload["message"] != second_payload["message"]
    assert first_payload["message"] != "http.access"
    assert second_payload["message"] != "http.access"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_uvicorn_access_filter_passes_through_non_access_records() -> None:
    filt = UvicornAccessLogFilter()
    formatter = JsonFormatter()
    record = _make_record(msg="startup complete")

    filt.filter(record)
    payload = json.loads(formatter.format(record))

    assert payload["message"] == "startup complete"
    assert "http" not in payload


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_uvicorn_access_filter_leaves_unparseable_status_records_untouched() -> None:
    filt = UvicornAccessLogFilter()
    formatter = JsonFormatter()
    logger = logging.getLogger("uvicorn.access")
    record = logger.makeRecord(
        name=logger.name,
        level=logging.INFO,
        fn="<uvicorn>",
        lno=0,
        msg='%s - "%s %s HTTP/%s" %s',
        args=("127.0.0.1:12345", "GET", "/v1/cases", "1.1", "abc"),
        exc_info=None,
    )

    filt.filter(record)
    payload = _format_payload(formatter, record)

    assert payload["message"] == '127.0.0.1:12345 - "GET /v1/cases HTTP/1.1" abc'
    assert "http" not in payload


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_uvicorn_access_filter_hardens_plain_formatter_to_json_output() -> None:
    logger = logging.getLogger("uvicorn.access")
    original_handlers = list(logger.handlers)
    original_filters = list(logger.filters)
    original_level = logger.level
    original_propagate = logger.propagate

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    uvicorn_filter = UvicornAccessLogFilter()

    try:
        logger.handlers = [handler]
        logger.filters = [uvicorn_filter]
        logger.level = logging.INFO
        logger.propagate = False

        logger.info(
            '%s - "%s %s HTTP/%s" %d',
            "127.0.0.1:54321",
            "GET",
            "/v1/runtime-hardening",
            "1.1",
            200,
        )
    finally:
        logger.handlers = original_handlers
        logger.filters = original_filters
        logger.level = original_level
        logger.propagate = original_propagate

    emitted_line = stream.getvalue().strip()
    payload = json.loads(emitted_line)

    assert payload["logger"] == "uvicorn.access"
    assert payload["level"] == "INFO"
    assert payload["message"] == "http.access GET /v1/runtime-hardening 200"
    assert payload["http"]["path"] == "/v1/runtime-hardening"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_uvicorn_access_filter_reuses_existing_json_formatter_configuration() -> None:
    # Contract: when uvicorn.access is repaired back to JSON, it must reuse the
    # already-configured shared JsonFormatter behavior rather than install a
    # fresh default formatter. The app centrally pins logger behavior in
    # commondb.config.cfg, so formatter settings such as service/environment
    # must stay aligned across managed loggers.
    access_logger = logging.getLogger("uvicorn.access")
    root_logger = logging.getLogger()

    original_access_handlers = list(access_logger.handlers)
    original_access_filters = list(access_logger.filters)
    original_access_level = access_logger.level
    original_access_propagate = access_logger.propagate
    original_root_handlers = list(root_logger.handlers)

    root_handler = logging.StreamHandler(StringIO())
    root_handler.setFormatter(
        JsonFormatter(service="shared-service", environment="prod")
    )

    stream = StringIO()
    access_handler = logging.StreamHandler(stream)
    access_handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))

    try:
        root_logger.handlers = [root_handler]
        access_logger.handlers = [access_handler]
        access_logger.filters = [UvicornAccessLogFilter()]
        access_logger.level = logging.INFO
        access_logger.propagate = False

        access_logger.info(
            '%s - "%s %s HTTP/%s" %d',
            "127.0.0.1:54321",
            "GET",
            "/v1/discovered-formatter",
            "1.1",
            200,
        )
    finally:
        access_logger.handlers = original_access_handlers
        access_logger.filters = original_access_filters
        access_logger.level = original_access_level
        access_logger.propagate = original_access_propagate
        root_logger.handlers = original_root_handlers

    payload = json.loads(stream.getvalue().strip())

    assert payload["service"] == "shared-service"
    assert payload["environment"] == "prod"
    assert payload["message"] == "http.access GET /v1/discovered-formatter 200"

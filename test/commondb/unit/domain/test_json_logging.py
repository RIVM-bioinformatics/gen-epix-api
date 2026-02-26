import json
import logging
import sys
from typing import Any

import pytest

from gen_epix.commondb.domain.json_logging import JsonFormatter


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

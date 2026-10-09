"""Tests for structured log item serialization."""

import datetime
import json

import pytest

from gen_epix.fastapp.log import LogItem


def test_dumps_includes_code_message_and_context() -> None:
    item = LogItem(code="LSP-3893", msg="created", request_id="request-1")

    assert json.loads(item.dumps()) == {
        "code": "LSP-3893",
        "msg": "created",
        "request_id": "request-1",
    }


def test_dumps_passes_formatting_options_to_json_encoder() -> None:
    item = LogItem(code="event", msg="created")

    assert item.dumps(indent=2, separators=(",", ": ")) == json.dumps(
        {"code": "event", "msg": "created"},
        indent=2,
        separators=(",", ": "),
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (datetime.datetime(2026, 10, 9, 12, 30), "2026-10-09T12:30:00"),
        (ValueError("invalid value"), "invalid value"),
        (object(), None),
    ],
    ids=["datetime-isoformat", "exception-message", "other-object-string"],
)
def test_dumps_stringifies_unsupported_context_values(
    value: object, expected: str | None
) -> None:
    item = LogItem(code="event", msg="created", value=value)

    result = json.loads(item.dumps())

    assert result["value"] == (str(value) if expected is None else expected)

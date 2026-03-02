"""
TDD tests for _summarise_command_object(), the helper that prevents large list
fields inside a serialized Command from blowing through downstream log-sink
size limits.

Fix index:
  7. Commands with large list fields (e.g. hundreds of case_ids in a
     RetrieveCasesByIdCommand) are summarised before being merged into the log
     payload. Lists longer than _MAX_LIST_ITEMS_IN_LOG are replaced with
     {"_count": N, "_sample": [first_n_items]} at every level of nesting.
"""

import json
import uuid
from typing import ClassVar, List
from uuid import UUID

from gen_epix.fastapp.app import _summarise_command_object
from gen_epix.fastapp.log import LogItem
from gen_epix.fastapp.model import Command, User


# ---------------------------------------------------------------------------
# Minimal Command subclass that mirrors the real RetrieveCasesByIdCommand shape
# ---------------------------------------------------------------------------


class _LargeListCommand(Command):
    NAME: ClassVar[str | None] = "test_large_list"
    case_ids: List[UUID]


def _make_user() -> User:
    return User(
        id=uuid.uuid4(),
    )


# ---------------------------------------------------------------------------
# Tests for _summarise_command_object()
# ---------------------------------------------------------------------------


def test_short_list_is_logged_verbatim() -> None:
    """Lists with <= _MAX_LIST_ITEMS_IN_LOG items pass through unchanged."""
    data = {"ids": ["a", "b", "c"]}
    result = _summarise_command_object(data)
    assert result == data


def test_long_list_is_summarised() -> None:
    """Lists with > _MAX_LIST_ITEMS_IN_LOG items are replaced with a count+sample dict."""
    long_list = [str(uuid.uuid4()) for _ in range(500)]
    data = {"case_ids": long_list}

    result = _summarise_command_object(data)

    summary = result["case_ids"]
    assert isinstance(summary, dict), "Long list must be replaced by a dict summary"
    assert summary["_count"] == 500
    assert summary["_sample"] == long_list[:3]


def test_nested_long_list_is_summarised() -> None:
    """Long lists nested inside a dict field are also summarised."""
    long_list = [str(uuid.uuid4()) for _ in range(200)]
    data = {"command": {"class": "SomeCommand", "object": {"ids": long_list}}}

    result = _summarise_command_object(data)

    summary = result["command"]["object"]["ids"]
    assert isinstance(summary, dict)
    assert summary["_count"] == 200
    assert len(summary["_sample"]) == 3


def test_long_list_respects_configured_sample_items() -> None:
    """Configured sample_items controls the number of sampled list elements."""
    long_list = [str(uuid.uuid4()) for _ in range(50)]
    result = _summarise_command_object(
        {"ids": long_list}, max_items=5, sample_items=1
    )
    summary = result["ids"]
    assert summary["_count"] == 50
    assert summary["_sample"] == long_list[:1]


def test_create_log_message_with_summarization_disabled_keeps_full_list() -> None:
    """When disabled in config, command.object preserves full lists."""
    from gen_epix.fastapp.app import App

    app = App(
        logger=None,
        log_item_class=LogItem,
        cfg={"log": {"command_object_summarization": {"enabled": False}}},
    )
    cmd = _LargeListCommand(
        case_ids=[uuid.uuid4() for _ in range(500)],
        user=_make_user(),
    )

    parsed = json.loads(app.create_log_message("test1234", "STARTED_COMMAND", cmd=cmd))
    case_ids = parsed["command"]["object"]["case_ids"]
    assert isinstance(case_ids, list)
    assert len(case_ids) == 500


def test_create_log_message_uses_configured_threshold_and_sample_size() -> None:
    """Config can tune max_list_items and sample_items."""
    from gen_epix.fastapp.app import App

    app = App(
        logger=None,
        log_item_class=LogItem,
        cfg={
            "log": {
                "command_object_summarization": {
                    "enabled": True,
                    "max_list_items": 2,
                    "sample_items": 1,
                }
            }
        },
    )
    cmd = _LargeListCommand(
        case_ids=[uuid.uuid4() for _ in range(3)],
        user=_make_user(),
    )

    parsed = json.loads(app.create_log_message("test1234", "STARTED_COMMAND", cmd=cmd))
    summary = parsed["command"]["object"]["case_ids"]
    assert summary["_count"] == 3
    assert len(summary["_sample"]) == 1


def test_create_log_message_invalid_config_falls_back_to_defaults() -> None:
    """Invalid config values fall back to default summarization settings."""
    from gen_epix.fastapp.app import App

    app = App(
        logger=None,
        log_item_class=LogItem,
        cfg={
            "log": {
                "command_object_summarization": {
                    "enabled": "not-a-bool",
                    "max_list_items": "not-an-int",
                    "sample_items": -7,
                }
            }
        },
    )
    cmd = _LargeListCommand(
        case_ids=[uuid.uuid4() for _ in range(11)],
        user=_make_user(),
    )

    parsed = json.loads(app.create_log_message("test1234", "STARTED_COMMAND", cmd=cmd))
    summary = parsed["command"]["object"]["case_ids"]
    assert summary["_count"] == 11
    assert len(summary["_sample"]) == 3


def test_create_log_message_with_large_command_stays_under_16384_bytes() -> None:
    """
    End-to-end: a command carrying 500 UUIDs in case_ids produces a log message
    that is strictly under 16 384 bytes.
    """
    from gen_epix.fastapp.app import App

    app = App(logger=None, log_item_class=LogItem)

    cmd = _LargeListCommand(
        case_ids=[uuid.uuid4() for _ in range(500)],
        user=_make_user(),
    )

    log_message = app.create_log_message("test1234", "STARTED_COMMAND", cmd=cmd)
    assert (
        len(log_message) < 16_384
    ), f"Log message exceeds 16 384 bytes: {len(log_message)}"

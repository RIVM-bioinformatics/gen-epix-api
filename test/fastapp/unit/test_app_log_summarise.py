"""
TDD tests for _summarise_command_object() — the helper that prevents large list
fields inside a serialised Command from blowing through Monitoring Platform's 384-byte
hard limit on log-line length.

Fix index:
  7. Commands with large list fields (e.g. hundreds of case_ids in a
     RetrieveCasesByIdCommand) are summarised before being merged into the log
     payload. Lists longer than _MAX_LIST_ITEMS_IN_LOG are replaced with
     {"_count": N, "_sample": [first_3_items]} at every level of nesting.
"""

import uuid
from typing import ClassVar, List
from uuid import UUID


from gen_epix.fastapp.app import _summarise_command_object
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


def test_create_log_message_with_large_command_stays_under_16384_bytes() -> None:
    """
    End-to-end: a command carrying 500 UUIDs in case_ids produces a log message
    that is strictly under 16 384 bytes (Azure Monitor hard limit).
    """
    from gen_epix.fastapp.app import App
    from gen_epix.fastapp.log import LogItem

    app = App(logger=None, log_item_class=LogItem)

    cmd = _LargeListCommand(
        case_ids=[uuid.uuid4() for _ in range(500)],
        user=_make_user(),
    )

    log_message = app.create_log_message("test1234", "STARTED_COMMAND", cmd=cmd)
    assert (
        len(log_message) < 16_384
    ), f"Log message exceeds 16 384 bytes: {len(log_message)}"

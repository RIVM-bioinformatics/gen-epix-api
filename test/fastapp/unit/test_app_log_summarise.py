"""
TDD tests for _summarise_command_object(), the helper that prevents large list
fields inside a serialized Command from blowing through downstream log-sink
size limits.

Fix index:
  7. Commands with large list fields (e.g. hundreds of case_ids in a
     RetrieveCasesByIdCommand) are summarised before being merged into the log
     payload. Lists longer than App.DEFAULT_LOG_MAX_LIST_ITEMS are replaced with
     {"_count": N, "_sample": [first_n_items]} at every level of nesting.
"""

import json
import uuid
from typing import ClassVar, List
from uuid import UUID

import pytest

from gen_epix.fastapp.app import App
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_short_list_is_logged_verbatim() -> None:
    """Lists with <= App.DEFAULT_LOG_MAX_LIST_ITEMS items pass through unchanged."""
    app = App(logger=None, log_item_class=LogItem)
    data = {"ids": ["a", "b", "c"]}
    result = app._summarise_command_object_for_log(data)
    assert result == data


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_long_list_is_summarised() -> None:
    """Lists with > App.DEFAULT_LOG_MAX_LIST_ITEMS items are replaced with a count+sample dict."""
    app = App(logger=None, log_item_class=LogItem)
    long_list = [str(uuid.uuid4()) for _ in range(500)]
    data = {"case_ids": long_list}

    result = app._summarise_command_object_for_log(data)

    summary = result["case_ids"]
    assert isinstance(summary, dict), "Long list must be replaced by a dict summary"
    assert summary["_count"] == 500
    assert summary["_sample"] == long_list[: App.DEFAULT_LOG_MAX_LIST_ITEMS]


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_nested_long_list_is_summarised() -> None:
    """Long lists nested inside a dict field are also summarised."""
    app = App(logger=None, log_item_class=LogItem)
    long_list = [str(uuid.uuid4()) for _ in range(200)]
    data = {"command": {"class": "SomeCommand", "object": {"ids": long_list}}}

    result = app._summarise_command_object_for_log(data)

    summary = result["command"]["object"]["ids"]
    assert isinstance(summary, dict)
    assert summary["_count"] == 200
    assert len(summary["_sample"]) == App.DEFAULT_LOG_MAX_LIST_ITEMS


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_long_list_respects_configured_max_list_items() -> None:
    """Configured max_list_items controls the summarization threshold and sample size."""
    app = App(
        logger=None,
        log_item_class=LogItem,
        cfg={
            "log": {
                "command_object_summarization": {"enabled": True, "max_list_items": 5}
            }
        },
    )
    long_list = [str(uuid.uuid4()) for _ in range(50)]
    result = app._summarise_command_object_for_log({"ids": long_list})
    summary = result["ids"]
    assert summary["_count"] == 50
    assert summary["_sample"] == long_list[:5]


@pytest.mark.scenario_ids("TC-LOG-01-01")
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


@pytest.mark.scenario_ids("TC-LOG-01-01")
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
    assert len(summary["_sample"]) == 2


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_large_dict_is_summarised() -> None:
    """Dicts with more than DEFAULT_LOG_MAX_DICT_ITEMS entries (e.g. locus_allele_id_map)
    are replaced with a _count/_sample summary, even when individual values are short.
    """
    app = App(logger=None, log_item_class=LogItem)
    large_map = {f"LOCUS_{i:04d}": str(uuid.uuid4()) for i in range(500)}
    result = app._summarise_command_object_for_log({"locus_allele_id_map": large_map})
    summary = result["locus_allele_id_map"]
    assert isinstance(summary, dict)
    assert summary["_count"] == 500
    assert len(summary["_sample"]) == App.DEFAULT_LOG_MAX_LIST_ITEMS
    assert "_count" not in summary["_sample"]


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_small_dict_passes_through() -> None:
    """Dicts at or below DEFAULT_LOG_MAX_DICT_ITEMS entries are not modified."""
    app = App(logger=None, log_item_class=LogItem)
    small_map = {
        f"k{i}": str(uuid.uuid4()) for i in range(App.DEFAULT_LOG_MAX_DICT_ITEMS)
    }
    result = app._summarise_command_object_for_log({"mapping": small_map})
    assert result["mapping"] == small_map


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_long_string_is_truncated() -> None:
    """Strings longer than DEFAULT_LOG_MAX_STRING_LENGTH are shortened to a
    prefix with a suffix showing the total character count; they are NOT
    replaced by the _count/_sample dict pattern used for lists."""
    app = App(logger=None, log_item_class=LogItem)
    long_str = "x" * 1000
    result = app._summarise_command_object_for_log({"content": long_str})
    truncated = result["content"]
    assert isinstance(
        truncated, str
    ), "Truncated string must remain a string, not a dict"
    assert len(truncated) < len(long_str)
    assert truncated.startswith("x" * App.DEFAULT_LOG_MAX_STRING_LENGTH)
    assert "[1000 chars]" in truncated


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_short_string_passes_through() -> None:
    """Strings at or below DEFAULT_LOG_MAX_STRING_LENGTH are not modified."""
    app = App(logger=None, log_item_class=LogItem)
    short_str = "x" * App.DEFAULT_LOG_MAX_STRING_LENGTH
    result = app._summarise_command_object_for_log({"content": short_str})
    assert result["content"] == short_str


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_long_string_respects_configured_max_string_length() -> None:
    """Config key max_string_length controls both the truncation threshold and
    the length of the preserved prefix."""
    app = App(
        logger=None,
        log_item_class=LogItem,
        cfg={
            "log": {
                "command_object_summarization": {
                    "enabled": True,
                    "max_string_length": 20,
                }
            }
        },
    )
    long_str = "a" * 200
    result = app._summarise_command_object_for_log({"seq": long_str})
    truncated = result["seq"]
    assert truncated.startswith("a" * 20)
    assert "[200 chars]" in truncated
    assert len(truncated) < len(long_str)


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_long_exception_message_is_truncated_from_the_middle() -> None:
    """Exceptions get their own, longer budget than plain strings, and are
    truncated from the middle: DB driver errors (e.g. FK constraint
    violations) often echo the full SQL statement first and put the actual
    error message at the end, so a head-only cut would hide it."""
    app = App(
        logger=None,
        log_item_class=LogItem,
        cfg={
            "log": {
                "command_object_summarization": {
                    "max_exception_message_length": 50,
                }
            }
        },
    )
    long_msg = "a" * 500 + "b" * 500
    result = app._summarise_command_object_for_log({"exception": RuntimeError(long_msg)})
    truncated = result["exception"]
    assert truncated.startswith("a" * 25)
    assert truncated.endswith("b" * 25)
    assert "[950 chars omitted]" in truncated


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_short_exception_message_passes_through() -> None:
    app = App(logger=None, log_item_class=LogItem)
    result = app._summarise_command_object_for_log({"exception": RuntimeError("boom")})
    assert result["exception"] == "boom"


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_create_log_message_invalid_bool_config_raises() -> None:
    """Invalid boolean config value raises InitializationServiceError."""
    from gen_epix.fastapp.exc import InitializationServiceError

    with pytest.raises(InitializationServiceError):
        App(
            logger=None,
            log_item_class=LogItem,
            cfg={
                "log": {
                    "command_object_summarization": {
                        "enabled": "not-a-bool",
                    }
                }
            },
        )


@pytest.mark.scenario_ids("TC-LOG-01-01")
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

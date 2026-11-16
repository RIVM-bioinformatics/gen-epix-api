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
import logging
import uuid
from datetime import datetime
from test.util.mock_compat import Mock
from typing import ClassVar, List
from uuid import UUID

import pytest

from gen_epix.commondb.domain.enum import FeatureFlag
from gen_epix.fastapp import exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.enum import EventTiming
from gen_epix.fastapp.log import LogItem
from gen_epix.fastapp.model import Command, User

# ---------------------------------------------------------------------------
# Minimal Command subclass that mirrors the real RetrieveCasesByIdCommand shape
# ---------------------------------------------------------------------------


class _LargeListCommand(Command):
    NAME: ClassVar[str | None] = "test_large_list"
    case_ids: List[UUID]


class _CacheCommand(Command):
    NAME: ClassVar[str] = "test_cache_command"


class _OtherCacheCommand(Command):
    NAME: ClassVar[str] = "other_cache_command"


class _ParentCommand(Command):
    NAME: ClassVar[str] = "parent_command"


class _ChildCommand(_ParentCommand):
    NAME: ClassVar[str] = "child_command"


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
    result = app._summarise_command_object_for_log(
        {"exception": RuntimeError(long_msg)}
    )
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


def test_app_starts_with_empty_cache_registries() -> None:
    app = App(logger=None)

    assert app._cache_invalidator_map == {}
    assert app._auto_invalidate_cache_set == set()


def test_register_cache_invalidator_allows_multiple_and_rejects_duplicates() -> None:
    app = App(logger=None)
    first = Mock()
    second = Mock()

    app.register_cache_invalidator(_CacheCommand, first)
    app.register_cache_invalidator(_CacheCommand, second)

    assert app._cache_invalidator_map[_CacheCommand] == [first, second]
    with pytest.raises(exc.InitializationServiceError):
        app.register_cache_invalidator(_CacheCommand, first)


def test_register_cache_invalidator_logs_at_debug_level() -> None:
    logger = Mock()
    logger.level = logging.DEBUG
    app = App(logger=logger)

    app.register_cache_invalidator(_CacheCommand, Mock())

    assert "REGISTERING_CACHE_INVALIDATOR" in logger.debug.call_args.args[0]


def test_invalidate_cache_uses_exact_command_type_and_propagates_errors() -> None:
    app = App(logger=None)
    invalidator = Mock()
    app.register_cache_invalidator(_CacheCommand, invalidator)

    app.invalidate_cache(_CacheCommand())
    app.invalidate_cache(_OtherCacheCommand())

    invalidator.assert_called_once()
    failing_invalidator = Mock(side_effect=RuntimeError("cache failure"))
    app.register_cache_invalidator(_OtherCacheCommand, failing_invalidator)
    with pytest.raises(RuntimeError, match="cache failure"):
        app.invalidate_cache(_OtherCacheCommand())


def test_set_auto_invalidate_cache_toggles_without_removing_registrations() -> None:
    app = App(logger=None)
    invalidator = Mock()
    app.register_cache_invalidator(_CacheCommand, invalidator)

    app.set_auto_invalidate_cache(_CacheCommand, True)
    assert _CacheCommand in app._auto_invalidate_cache_set
    app.set_auto_invalidate_cache(_CacheCommand, False)
    app.set_auto_invalidate_cache(_OtherCacheCommand, False)

    assert _CacheCommand not in app._auto_invalidate_cache_set
    assert app._cache_invalidator_map[_CacheCommand] == [invalidator]


def test_auto_invalidation_runs_after_success_only() -> None:
    app = App(logger=None)
    invalidator = Mock()
    app.register_handler(_CacheCommand, lambda cmd: "done")
    app.register_cache_invalidator(_CacheCommand, invalidator)
    app.set_auto_invalidate_cache(_CacheCommand, True)

    assert app.handle(_CacheCommand()) == "done"
    invalidator.assert_called_once()

    invalidator.reset_mock()
    app.register_handler(
        _OtherCacheCommand, lambda cmd: (_ for _ in ()).throw(RuntimeError())
    )
    app.register_cache_invalidator(_OtherCacheCommand, invalidator)
    app.set_auto_invalidate_cache(_OtherCacheCommand, True)
    with pytest.raises(RuntimeError):
        app.handle(_OtherCacheCommand())
    invalidator.assert_not_called()


def test_auto_invalidation_runs_for_nested_commands() -> None:
    app = App(logger=None)
    invalidator = Mock()
    app.register_handler(_OtherCacheCommand, lambda cmd: "inner")

    def handle_outer(_cmd: Command) -> str:
        return app.handle(_OtherCacheCommand())

    app.register_handler(_CacheCommand, handle_outer)
    app.register_cache_invalidator(_OtherCacheCommand, invalidator)
    app.set_auto_invalidate_cache(_OtherCacheCommand, True)

    assert app.handle(_CacheCommand()) == "inner"
    invalidator.assert_called_once()


@pytest.mark.parametrize(
    "query_key",
    [
        pytest.param("ALLOW_DELETE_ALL_OPERATIONAL_DATA", id="uppercase"),
        pytest.param("allow_delete_all_operational_data", id="lowercase"),
        pytest.param("Allow_Delete_All_Operational_Data", id="mixed-case"),
    ],
)
def test_get_feature_flag_matches_string_keys_without_regard_to_case(
    query_key: str,
) -> None:
    """Match string feature-flag keys without regard to case."""
    app = App(logger=None)
    app.set_feature_flag("allow_delete_all_operational_data", True)

    assert app.get_feature_flag(query_key) is True


def test_get_feature_flag_uses_exact_enum_keys() -> None:
    """Look up enum-keyed feature flags by their enum member."""
    app = App(
        logger=None,
        feature_flags={FeatureFlag.ALLOW_DELETE_ALL_OPERATIONAL_DATA: True},
    )

    assert app.get_feature_flag(FeatureFlag.ALLOW_DELETE_ALL_OPERATIONAL_DATA) is True
    assert app.get_feature_flag("ALLOW_DELETE_ALL_OPERATIONAL_DATA") is False


def test_get_feature_flag_uses_default_when_string_key_is_missing() -> None:
    """Return the caller's default when no normalized string key is present."""
    app = App(logger=None)

    assert app.get_feature_flag("missing") is False
    assert app.get_feature_flag("missing", default=True) is True


def test_destructor_handles_partial_initialization() -> None:
    app = object.__new__(App)

    app.__del__()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        ("  YES ", True),
        ("On", True),
        ("true", True),
        ("1", True),
        ("NO", False),
        ("off", False),
        ("false", False),
        ("0", False),
    ],
)
def test_get_bool_from_cfg_value_accepts_supported_forms(
    value: object, expected: bool
) -> None:
    assert App._get_bool_from_cfg_value(value) is expected


@pytest.mark.parametrize("value", [None, 1, "maybe", ""])
def test_get_bool_from_cfg_value_rejects_unsupported_forms(value: object) -> None:
    with pytest.raises(exc.InitializationServiceError, match="Invalid boolean config"):
        App._get_bool_from_cfg_value(value)


@pytest.mark.parametrize(("value", "expected"), [(4, 4), ("12", 12), (False, 0)])
def test_get_int_from_cfg_value_converts_supported_values(
    value: object, expected: int
) -> None:
    assert App._get_int_from_cfg_value(value) == expected


@pytest.mark.parametrize("value", [None, "not-an-int"])
def test_get_int_from_cfg_value_rejects_unconvertible_values(value: object) -> None:
    with pytest.raises(exc.InitializationServiceError, match="Invalid integer config"):
        App._get_int_from_cfg_value(value)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("Feature_Name", True),
        (FeatureFlag.ALLOW_DELETE_ALL_OPERATIONAL_DATA, False),
    ],
)
def test_set_feature_flag_normalizes_string_keys_and_preserves_enum_keys(
    key: object, value: bool
) -> None:
    app = App(logger=None)

    app.set_feature_flag(key, value)

    expected_key = key.upper() if isinstance(key, str) else key
    assert app.get_feature_flag(expected_key) is value


def test_feature_flags_property_returns_a_copy() -> None:
    app = App(logger=None, feature_flags={"enabled": True})

    flags = app.feature_flags
    flags["enabled"] = False

    assert app.feature_flags == {"enabled": True}


def test_set_feature_flag_rejects_non_boolean_values() -> None:
    with pytest.raises(ValueError, match="must be a boolean"):
        App(logger=None).set_feature_flag("enabled", 1)


def test_optional_dependency_properties_raise_when_unconfigured() -> None:
    app = App(logger=None)

    with pytest.raises(exc.InitializationServiceError, match="Policy decision"):
        app.pdp = None
        app.pdp
    with pytest.raises(exc.InitializationServiceError, match="User manager"):
        app.user_manager
    with pytest.raises(exc.InitializationServiceError, match="Configuration data"):
        app.cfg
    with pytest.raises(exc.InitializationServiceError, match="Implementation details"):
        app.impl

    user_manager = object()
    config = {"test": True}
    implementation = object()
    logger = Mock()
    app.user_manager = user_manager
    app.logger = logger
    app._cfg = config
    app._impl = implementation

    assert app.user_manager is user_manager
    assert app.logger is logger
    assert app.cfg is config
    assert app.impl is implementation
    assert app.log_item_class is LogItem
    assert app.id


def test_generate_id_and_timestamp_use_injected_factories() -> None:
    generated_id = uuid.uuid4()
    generated_timestamp = datetime(2024, 1, 1)
    app = App(
        logger=None,
        id_factory=lambda: generated_id,
        timestamp_factory=lambda: generated_timestamp,
    )

    assert app.generate_id() == generated_id
    assert app.generate_timestamp() == generated_timestamp


def test_register_command_and_policy_forward_to_domain_and_pdp() -> None:
    app = App(logger=None)
    policy = Mock()

    app.register_command(_CacheCommand)
    app.register_policy(_CacheCommand, policy, EventTiming.AFTER)
    app.unregister_policy(_CacheCommand, policy, EventTiming.AFTER)

    assert _CacheCommand in app.domain.commands
    assert app.pdp.get_policies(_CacheCommand, EventTiming.AFTER) == []


def test_listener_registration_unregistration_and_errors() -> None:
    app = App(logger=None)
    first = Mock()
    second = Mock()

    app.register_listener(_CacheCommand, first, EventTiming.BEFORE)
    app.register_listener(_CacheCommand, second, EventTiming.BEFORE)
    app.unregister_listener(_CacheCommand, first, EventTiming.BEFORE)

    assert app._command_listeners[EventTiming.BEFORE][_CacheCommand] == [second]
    with pytest.raises(exc.InitializationServiceError, match="already registered"):
        app.register_listener(_CacheCommand, second, EventTiming.BEFORE)
    with pytest.raises(exc.InitializationServiceError, match="not registered"):
        app.unregister_listener(_CacheCommand, first, EventTiming.BEFORE)


def test_handler_registration_replacement_and_parent_lookup() -> None:
    app = App(logger=None)
    parent_handler = Mock(return_value="parent")
    child_handler = Mock(return_value="child")

    app.register_handler(_ParentCommand, parent_handler)
    assert app.get_handler(_ChildCommand) is parent_handler
    app.register_handler(_ChildCommand, child_handler)
    app.register_handler(_ChildCommand, parent_handler)

    assert app.get_handler(_ChildCommand) is parent_handler
    with pytest.raises(exc.InitializationServiceError, match="already added"):
        app.register_handler(_ChildCommand, child_handler, replace=False)
    with pytest.raises(exc.InitializationServiceError, match="No handler set"):
        app.get_handler(_OtherCacheCommand)


def test_handle_runs_policy_phases_and_lifecycle_listeners() -> None:
    pdp = Mock()
    app = App(logger=None, pdp=pdp)
    phases = []
    events = []

    def apply_policy(_cmd, timing, retval=None):
        phases.append(timing)
        return "filtered" if timing is EventTiming.AFTER else retval

    pdp.apply.side_effect = apply_policy
    app.register_handler(_CacheCommand, lambda _cmd: "handled")
    app.register_listener(
        _CacheCommand,
        lambda _cmd, retval: events.append((EventTiming.BEFORE, retval)),
        EventTiming.BEFORE,
    )
    app.register_listener(
        _CacheCommand,
        lambda _cmd, retval: events.append((EventTiming.AFTER, retval)),
        EventTiming.AFTER,
    )

    assert app.handle(_CacheCommand()) == "filtered"
    assert phases == [EventTiming.BEFORE, EventTiming.DURING, EventTiming.AFTER]
    assert events == [(EventTiming.BEFORE, None), (EventTiming.AFTER, "filtered")]
    assert app._command_stack == []


def test_handle_unwinds_stack_after_policy_handler_and_resolution_errors() -> None:
    pdp = Mock()
    app = App(logger=None, pdp=pdp)
    pdp.apply.side_effect = RuntimeError("policy failed")
    with pytest.raises(RuntimeError, match="policy failed"):
        app.handle(_CacheCommand())
    assert app._command_stack == []

    pdp.apply.side_effect = None
    pdp.apply.return_value = None
    app.register_handler(
        _CacheCommand,
        lambda _cmd: (_ for _ in ()).throw(RuntimeError("handler failed")),
    )
    with pytest.raises(RuntimeError, match="handler failed"):
        app.handle(_CacheCommand())
    assert app._command_stack == []

    with pytest.raises(exc.InitializationServiceError, match="No handler set"):
        app.handle(_OtherCacheCommand())
    assert app._command_stack == []


def test_create_minimal_and_static_log_messages_include_command_identity() -> None:
    app = App(logger=None, log_item_class=LogItem)
    cmd = _CacheCommand(user=_make_user())

    minimal = json.loads(
        app.create_log_message("code", "message", add_debug_info=False, cmd=cmd)
    )
    static = json.loads(App.create_static_log_message("code", "message", cmd=cmd))

    for payload in (minimal, static):
        assert payload["command"]["class"] == "_CacheCommand"
        assert payload["command"]["id"] == str(cmd.id)
        assert payload["command"]["user_id"] == str(cmd.user.id)


@pytest.mark.parametrize(
    ("text", "max_length", "expected"),
    [
        ("short", 5, "short"),
        ("abcdef", 4, "ab…[2 chars omitted]…ef"),
        ("abc", 0, "…[3 chars omitted]…"),
        ("abc", -1, "…[3 chars omitted]…"),
        ("abcdefg", 5, "ab…[2 chars omitted]…efg"),
    ],
)
def test_truncate_middle_handles_length_boundaries(
    text: str, max_length: int, expected: str
) -> None:
    assert App._truncate_middle(text, max_length) == expected


def test_stack_trace_exemption_matches_exception_causes_and_avoids_cycles() -> None:
    app = App(logger=None)
    app.register_stack_trace_exemption(ValueError)
    root = RuntimeError("outer")
    cause = ValueError("inner")
    root.__cause__ = cause

    assert app._is_exempted_from_stack_trace(root)
    assert not app._is_exempted_from_stack_trace(RuntimeError("unrelated"))

    first = RuntimeError("first")
    second = RuntimeError("second")
    first.__cause__ = second
    second.__cause__ = first
    assert not app._is_exempted_from_stack_trace(first)


def test_registration_methods_log_at_debug_level() -> None:
    logger = Mock()
    logger.level = logging.DEBUG
    app = App(logger=logger)
    policy = Mock()
    invalidator = Mock()
    handler = Mock()

    def listener(_cmd: Command, _retval: object) -> None:
        return None

    app.register_command(_CacheCommand)
    app.register_policy(_CacheCommand, policy, EventTiming.BEFORE)
    app.unregister_policy(_CacheCommand, policy, EventTiming.BEFORE)
    app.register_listener(_CacheCommand, listener, EventTiming.BEFORE)
    app.unregister_listener(_CacheCommand, listener, EventTiming.BEFORE)
    app.register_handler(_CacheCommand, handler)
    app.register_cache_invalidator(_CacheCommand, invalidator)

    assert logger.debug.call_count == 7


@pytest.mark.parametrize(
    ("level", "debug_calls", "info_calls"),
    [
        (logging.DEBUG, 4, 0),
        (logging.INFO, 0, 2),
    ],
)
def test_handle_logs_outer_and_nested_command_at_configured_level(
    level: int, debug_calls: int, info_calls: int
) -> None:
    logger = Mock()
    logger.level = level
    pdp = Mock()
    pdp.apply.side_effect = lambda _cmd, _timing, retval=None: retval
    app = App(logger=logger, pdp=pdp)

    def handle_child(_cmd: Command) -> str:
        return "child result"

    def handle_parent(_cmd: Command) -> str:
        return app.handle(_ChildCommand())

    app.register_handler(_ParentCommand, handle_parent)
    app.register_handler(_ChildCommand, handle_child)
    logger.reset_mock()

    assert app.handle(_ParentCommand()) == "child result"
    assert logger.debug.call_count == debug_calls
    assert logger.info.call_count == info_calls
    assert app._command_stack == []


def test_register_handler_rejects_non_command_model() -> None:
    with pytest.raises(exc.InitializationServiceError, match="Handler can only"):
        App(logger=None).register_handler(User, Mock())


@pytest.mark.parametrize(
    ("failure", "log_method", "has_stack_trace"),
    [
        (exc.ServiceException("service", "failed"), "error", True),
        (exc.DomainException("domain", "failed"), "warning", None),
        (RuntimeError("unexpected"), "error", True),
    ],
)
def test_handle_logs_and_unwinds_categorized_failures(
    failure: Exception, log_method: str, has_stack_trace: bool | None
) -> None:
    logger = Mock()
    logger.level = logging.INFO
    app = App(logger=logger)
    app.register_handler(_CacheCommand, lambda _cmd: (_ for _ in ()).throw(failure))
    logger.reset_mock()

    with pytest.raises(type(failure)):
        app.handle(_CacheCommand())

    log_method_mock = getattr(logger, log_method)
    log_method_mock.assert_called_once()
    if has_stack_trace is not None:
        assert log_method_mock.call_args.kwargs["exc_info"] is has_stack_trace
    assert app._command_stack == []


def test_handle_logs_exempt_service_exception_without_stack_trace() -> None:
    logger = Mock()
    logger.level = logging.INFO
    app = App(logger=logger)
    app.register_stack_trace_exemption(ValueError)
    app.register_handler(
        _CacheCommand,
        lambda _cmd: (_ for _ in ()).throw(ValueError("remote failure")),
    )
    logger.reset_mock()

    with pytest.raises(ValueError, match="remote failure"):
        app.handle(_CacheCommand())

    assert logger.error.call_args.kwargs["exc_info"] is False
    assert logger.error.call_args.kwargs["stack_info"] is False


def test_handle_cleans_stack_when_before_policy_rejects_command() -> None:
    logger = Mock()
    logger.level = logging.INFO
    pdp = Mock()
    pdp.apply.side_effect = exc.UnauthorizedAuthError("denied")
    app = App(logger=logger, pdp=pdp)
    app.register_handler(_CacheCommand, lambda _cmd: None)
    logger.reset_mock()

    with pytest.raises(exc.UnauthorizedAuthError):
        app.handle(_CacheCommand())

    assert logger.info.call_count == 2
    assert "NOT_AUTHORIZED" in logger.info.call_args_list[-1].args[0]
    assert app._command_stack == []


def test_handle_logs_unexpected_before_policy_failure_and_cleans_stack() -> None:
    logger = Mock()
    logger.level = logging.INFO
    pdp = Mock()
    pdp.apply.side_effect = RuntimeError("policy failure")
    app = App(logger=logger, pdp=pdp)
    logger.reset_mock()

    with pytest.raises(RuntimeError, match="policy failure"):
        app.handle(_CacheCommand())

    logger.error.assert_called_once()
    assert logger.error.call_args.kwargs["exc_info"] is True
    assert app._command_stack == []


def test_handle_logs_missing_handler_and_cleans_stack() -> None:
    logger = Mock()
    logger.level = logging.INFO
    app = App(logger=logger)
    logger.reset_mock()

    with pytest.raises(exc.InitializationServiceError, match="No handler set"):
        app.handle(_OtherCacheCommand())

    logger.error.assert_called_once()
    assert app._command_stack == []


def test_destructor_logs_when_logger_is_configured() -> None:
    logger = Mock()
    app = App(logger=logger)
    logger.reset_mock()

    app.__del__()

    logger.info.assert_called_once()

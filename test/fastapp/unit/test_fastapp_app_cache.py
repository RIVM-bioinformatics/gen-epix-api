import logging
from typing import ClassVar
from unittest.mock import Mock

import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.model import Command


class _Command(Command):
    NAME: ClassVar[str] = "test_command"


class _OtherCommand(Command):
    NAME: ClassVar[str] = "other_command"


def test_app_starts_with_empty_cache_registries() -> None:
    app = App(logger=None)

    assert app._cache_invalidator_map == {}
    assert app._auto_invalidate_cache_set == set()


def test_register_cache_invalidator_allows_multiple_and_rejects_duplicates() -> None:
    app = App(logger=None)
    first = Mock()
    second = Mock()

    app.register_cache_invalidator(_Command, first)
    app.register_cache_invalidator(_Command, second)

    assert app._cache_invalidator_map[_Command] == [first, second]
    with pytest.raises(exc.InitializationServiceError):
        app.register_cache_invalidator(_Command, first)


def test_register_cache_invalidator_logs_at_debug_level() -> None:
    logger = Mock()
    logger.level = logging.DEBUG
    app = App(logger=logger)

    app.register_cache_invalidator(_Command, Mock())

    assert "REGISTERING_CACHE_INVALIDATOR" in logger.debug.call_args.args[0]


def test_invalidate_cache_uses_exact_command_type_and_propagates_errors() -> None:
    app = App(logger=None)
    invalidator = Mock()
    app.register_cache_invalidator(_Command, invalidator)

    app.invalidate_cache(_Command())
    app.invalidate_cache(_OtherCommand())

    invalidator.assert_called_once()
    failing_invalidator = Mock(side_effect=RuntimeError("cache failure"))
    app.register_cache_invalidator(_OtherCommand, failing_invalidator)
    with pytest.raises(RuntimeError, match="cache failure"):
        app.invalidate_cache(_OtherCommand())


def test_set_auto_invalidate_cache_toggles_without_removing_registrations() -> None:
    app = App(logger=None)
    invalidator = Mock()
    app.register_cache_invalidator(_Command, invalidator)

    app.set_auto_invalidate_cache(_Command, True)
    assert _Command in app._auto_invalidate_cache_set
    app.set_auto_invalidate_cache(_Command, False)
    app.set_auto_invalidate_cache(_OtherCommand, False)

    assert _Command not in app._auto_invalidate_cache_set
    assert app._cache_invalidator_map[_Command] == [invalidator]


def test_auto_invalidation_runs_after_success_only() -> None:
    app = App(logger=None)
    invalidator = Mock()
    app.register_handler(_Command, lambda cmd: "done")
    app.register_cache_invalidator(_Command, invalidator)
    app.set_auto_invalidate_cache(_Command, True)

    assert app.handle(_Command()) == "done"
    invalidator.assert_called_once()

    invalidator.reset_mock()
    app.register_handler(
        _OtherCommand, lambda cmd: (_ for _ in ()).throw(RuntimeError())
    )
    app.register_cache_invalidator(_OtherCommand, invalidator)
    app.set_auto_invalidate_cache(_OtherCommand, True)
    with pytest.raises(RuntimeError):
        app.handle(_OtherCommand())
    invalidator.assert_not_called()


def test_auto_invalidation_runs_for_nested_commands() -> None:
    app = App(logger=None)
    invalidator = Mock()
    app.register_handler(_OtherCommand, lambda cmd: "inner")

    def handle_outer(_cmd: Command) -> str:
        return app.handle(_OtherCommand())

    app.register_handler(_Command, handle_outer)
    app.register_cache_invalidator(_OtherCommand, invalidator)
    app.set_auto_invalidate_cache(_OtherCommand, True)

    assert app.handle(_Command()) == "inner"
    invalidator.assert_called_once()

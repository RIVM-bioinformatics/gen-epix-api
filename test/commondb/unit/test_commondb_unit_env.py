"""Unit tests for the shared no-app application composer."""

from test.util.mock_compat import Mock, patch

import pytest

from gen_epix.commondb import env
from gen_epix.fastapp import exc
from gen_epix.fastapp.model import Command


class DummyCommand(Command):
    """Minimal command used to verify no-app handler registration."""

    NAME = "DummyCommand"


def test_no_app_composer_registers_exception_handlers() -> None:
    """Register handlers that reject every command."""
    app = Mock()
    domain = Mock()
    domain.get_commands.return_value = [DummyCommand]
    composer = object.__new__(env.NoAppComposer)
    app_cfg = Mock()
    app_cfg.setup_logger = None
    app_cfg.app_logger = None
    app_cfg.app_name = "test"
    setattr(composer, "_app_cfg", app_cfg)
    setattr(composer, "_domain", domain)
    setattr(composer, "_log_setup", False)

    with patch.object(env, "App", return_value=app):
        result = composer.compose_application()

    domain.get_commands.assert_called_once_with(include_crud=True)
    app.register_handler.assert_called_once()
    handler = app.register_handler.call_args.args[1]
    with pytest.raises(exc.ServiceUnavailableError, match="No App available"):
        handler(DummyCommand())
    assert result["app"] is app
    assert not result["services"]
    assert not result["repositories"]
    assert result["registered_user_dependency"](None) is None
    assert result["new_user_dependency"](None) is None
    assert result["idp_user_dependency"](None) is None

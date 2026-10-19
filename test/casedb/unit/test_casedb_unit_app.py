"""Unit tests for the casedb application module."""

import importlib.util
from test.util.mock_compat import Mock, patch
from types import ModuleType
from typing import Any, Callable

import pytest

from gen_epix.casedb import config as config_module
from gen_epix.casedb import env as env_module
from gen_epix.casedb.domain import enum
from gen_epix.commondb import app_setup

APP_SPEC = importlib.util.find_spec("gen_epix.casedb.app")


@pytest.fixture(name="load_app_module")
def load_app_module_fixture() -> Callable[..., ModuleType]:
    """Provide a loader executing a fresh copy of the module under mocks."""

    def _load(
        debug: Any = False, services: dict[Any, Any] | None = None
    ) -> tuple[ModuleType, Mock, Mock, Mock, Mock]:
        app_cfg = Mock()
        app_cfg.cfg = {"app": {"debug": debug}}
        cfg_class = Mock(return_value=app_cfg)
        composer = Mock()
        composer.services = (
            {enum.ServiceType.AUTH: Mock()} if services is None else services
        )
        composer_class = Mock(return_value=composer)
        create_fast_api = Mock(return_value=Mock(name="fast_api"))
        assert APP_SPEC is not None and APP_SPEC.origin is not None
        spec = importlib.util.spec_from_file_location(
            "_casedb_app_under_test", APP_SPEC.origin
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        with (
            patch.object(config_module, "CasedbAppCfg", cfg_class),
            patch.object(env_module, "AppComposer", composer_class),
            patch.object(app_setup, "create_fast_api", create_fast_api),
        ):
            spec.loader.exec_module(module)
        return module, cfg_class, composer_class, create_fast_api, composer

    return _load


def test_schema_kwargs_metadata(load_app_module: Callable[..., Any]) -> None:
    """Expose the casedb OpenAPI metadata."""
    kwargs = load_app_module()[0].SCHEMA_KWARGS

    assert kwargs["title"] == "Gen-EpiX casedb"
    assert kwargs["version"]
    assert kwargs["license_info"]["identifier"] == "EUPL-1.2"
    assert set(kwargs["contact"]) == {"name", "url", "email"}


def test_import_composes_application(load_app_module: Callable[..., Any]) -> None:
    """Create config, composer, and FastAPI exactly once at import."""
    module, cfg_class, composer_class, create_fast_api, composer = load_app_module()

    cfg_class.assert_called_once_with()
    composer_class.assert_called_once_with(module.APP_CFG)
    create_fast_api.assert_called_once()
    assert module.APP_COMPOSER is composer
    assert module.FAST_API is create_fast_api.return_value
    assert module.app is module.FAST_API


def test_create_fast_api_arguments(load_app_module: Callable[..., Any]) -> None:
    """Forward composed application, routers, loggers, and OpenAPI options."""
    module, _, _, create_fast_api, composer = load_app_module()

    kwargs = create_fast_api.call_args.kwargs
    assert not create_fast_api.call_args.args
    assert kwargs["app"] is composer.app
    assert kwargs["create_routers_fn"] is module.create_routers
    assert kwargs["setup_logger"] is module.APP_CFG.setup_logger
    assert kwargs["api_logger"] is module.APP_CFG.api_logger
    assert kwargs["update_openapi_schema"] is True
    assert kwargs["update_openapi_kwargs"] == {
        "get_openapi_kwargs": module.SCHEMA_KWARGS,
        "fix_schema": True,
        "auth_service": composer.services[enum.ServiceType.AUTH],
    }


@pytest.mark.parametrize("debug", [True, False], ids=["debug", "no-debug"])
def test_debug_flag_forwarded(load_app_module: Callable[..., Any], debug: bool) -> None:
    """Forward the configured debug flag unchanged."""
    _, _, _, create_fast_api, _ = load_app_module(debug=debug)

    assert create_fast_api.call_args.kwargs["debug"] is debug


def test_missing_auth_service_raises(load_app_module: Callable[..., Any]) -> None:
    """Fail at import when the composer has no auth service."""
    with pytest.raises(KeyError):
        load_app_module(services={})

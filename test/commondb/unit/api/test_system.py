"""Test feature-gated system API endpoints."""

from test.util.mock_compat import Mock, patch
from types import SimpleNamespace
from typing import Any, NoReturn

import pytest
from fastapi import APIRouter
from fastapi.routing import APIRoute

from gen_epix.commondb.api.system import create_system_endpoints
from gen_epix.commondb.domain import command, enum, model
from gen_epix.fastapp.api import CrudEndpointGenerator


class ConcreteDeleteAllRefDataCommand(command.DeleteAllRefDataCommand):
    """Concrete command supplied by an application router."""


def _handle_exception(*_args: Any) -> NoReturn:
    """Provide the endpoint factory's required exception adapter."""
    raise AssertionError("unexpected endpoint exception")


def _create_app(feature_flags: dict[str, bool]) -> Mock:
    """Create an app double with the dependencies needed by the endpoint factory."""
    app = Mock()
    app.impl = SimpleNamespace(
        registered_user_dependency=lambda: None,
        idp_user_dependency=lambda: None,
    )
    app.get_feature_flag.side_effect = lambda key, default=False: feature_flags.get(
        key, default
    )
    return app


def _get_route(router: APIRouter, path: str) -> APIRoute | None:
    """Return a route matching the requested path, if one was registered."""
    return next(
        (
            route
            for route in router.routes
            if isinstance(route, APIRoute) and route.path == path
        ),
        None,
    )


def test_reset_routes_are_absent_when_feature_flags_are_disabled() -> None:
    """Do not register reset routes when both flags are disabled."""
    router = APIRouter()
    app = _create_app({})

    with (
        patch.object(
            CrudEndpointGenerator,
            "create_crud_endpoint_set_for_domain",
            return_value=[],
        ),
        patch.object(CrudEndpointGenerator, "generate_endpoints"),
    ):
        create_system_endpoints(
            router,
            app,
            handle_exception=_handle_exception,
            delete_all_operational_data_command_class=command.DeleteAllOperationalDataCommand,
            delete_all_operational_data_result_class=model.DeleteAllOperationalDataResult,
        )

    assert _get_route(router, "/operational_data") is None
    assert _get_route(router, "/ref_data") is None


def test_reset_routes_return_json_results_with_success_status() -> None:
    """Register reset routes with a body-compatible success status and models."""
    router = APIRouter()
    app = _create_app(
        {
            "allow_delete_all_operational_data": True,
            "allow_delete_ref_data": True,
        }
    )

    with (
        patch.object(
            CrudEndpointGenerator,
            "create_crud_endpoint_set_for_domain",
            return_value=[],
        ),
        patch.object(CrudEndpointGenerator, "generate_endpoints"),
    ):
        create_system_endpoints(
            router,
            app,
            handle_exception=_handle_exception,
            delete_all_operational_data_command_class=command.DeleteAllOperationalDataCommand,
            delete_all_operational_data_result_class=model.DeleteAllOperationalDataResult,
            delete_all_ref_data_command_class=ConcreteDeleteAllRefDataCommand,
        )

    operational_route = _get_route(router, "/operational_data")
    ref_route = _get_route(router, "/ref_data")
    assert operational_route is not None
    assert ref_route is not None
    assert operational_route.status_code == 200
    assert ref_route.status_code == 200
    assert operational_route.response_model is model.DeleteAllOperationalDataResult
    assert ref_route.response_model is model.DeleteAllRefDataResult


def test_ref_data_route_requires_concrete_application_command() -> None:
    """Fail startup instead of exposing the empty shared refdata command."""
    router = APIRouter()
    app = _create_app({"allow_delete_ref_data": True})

    with (
        patch.object(
            CrudEndpointGenerator,
            "create_crud_endpoint_set_for_domain",
            return_value=[],
        ),
        patch.object(CrudEndpointGenerator, "generate_endpoints"),
        pytest.raises(
            AssertionError,
            match="delete_all_ref_data_command_class must be provided",
        ),
    ):
        create_system_endpoints(router, app, handle_exception=_handle_exception)

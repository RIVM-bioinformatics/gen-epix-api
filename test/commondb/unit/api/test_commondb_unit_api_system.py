"""Test feature-gated system API endpoint registration and contracts."""

import ast
from collections.abc import Hashable
from pathlib import Path
from test.util.mock_compat import Mock, patch
from types import SimpleNamespace
from typing import Any, NoReturn

import pytest
from fastapi import APIRouter
from fastapi.routing import APIRoute

from gen_epix.commondb.api.system import create_system_endpoints
from gen_epix.commondb.domain import command, enum, model
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.fastapp.app import App

_REPO_ROOT = Path(__file__).parents[4]
_ROUTER_FILES = [
    _REPO_ROOT / "gen_epix" / "casedb" / "api" / "router.py",
    _REPO_ROOT / "gen_epix" / "seqdb" / "api" / "router.py",
    _REPO_ROOT / "gen_epix" / "omopdb" / "api" / "router.py",
]


async def _dummy_dependency() -> dict:
    return {}


@pytest.mark.parametrize("flag_enabled", [True, False])
def test_delete_all_operational_data_route_registration(flag_enabled: bool) -> None:
    """The delete-all-operational-data route registers only when the flag is set."""
    router = APIRouter()
    app = Mock()
    app.get_feature_flag.side_effect = lambda key, default=False: (
        key == enum.FeatureFlag.ALLOW_DELETE_ALL_OPERATIONAL_DATA and flag_enabled
    )
    # Real callables, not further Mocks: create_system_endpoints uses these as
    # bare parameter type annotations on the routes it registers, which
    # FastAPI inspects at decoration time to build response/request schemas —
    # a Mock() there fails schema generation before this test can even
    # observe the conditional registration under test.
    app.impl = SimpleNamespace(
        idp_user_dependency=_dummy_dependency,
        registered_user_dependency=_dummy_dependency,
    )
    # create_system_endpoints also generates CRUD endpoints for the SYSTEM
    # service, unrelated to the flag under test; an empty entity list keeps
    # that generation a no-op instead of iterating a Mock.
    app.domain.get_dag_sorted_entities.return_value = []

    create_system_endpoints(
        router,
        app,
        handle_exception=Mock(),
        delete_all_operational_data_command_class=command.DeleteAllOperationalDataCommand,
    )

    app.get_feature_flag.assert_any_call(
        enum.FeatureFlag.ALLOW_DELETE_ALL_OPERATIONAL_DATA
    )
    operation_ids = {
        route.operation_id for route in router.routes if isinstance(route, APIRoute)
    }
    assert ("operational_data__delete" in operation_ids) is flag_enabled


@pytest.mark.parametrize(
    "router_file", _ROUTER_FILES, ids=lambda p: p.parent.parent.name
)
def test_router_wiring_supplies_delete_command_classes(router_file: Path) -> None:
    """Each app router wires commands required by the reset endpoints."""
    tree = ast.parse(router_file.read_text(encoding="utf-8"))
    dicts_with_command_class = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Dict)
        and any(
            isinstance(key, ast.Constant)
            and key.value == "delete_all_operational_data_command_class"
            for key in node.keys
            if key is not None
        )
    ]
    assert dicts_with_command_class, (
        f"{router_file} no longer wires delete_all_operational_data_command_class; "
        "update this test if that endpoint was intentionally removed"
    )
    for node in dicts_with_command_class:
        key_names = {key.value for key in node.keys if isinstance(key, ast.Constant)}
        assert "delete_all_ref_data_command_class" in key_names, (
            f"{router_file} passes delete_all_operational_data_command_class "
            "without delete_all_ref_data_command_class"
        )


class ConcreteDeleteAllRefDataCommand(command.DeleteAllRefDataCommand):
    """Concrete command supplied by an application router."""


def _handle_exception(*_args: Any) -> NoReturn:
    """Provide the endpoint factory's required exception adapter."""
    raise AssertionError("unexpected endpoint exception")


def _create_app(feature_flags: dict[Hashable, bool]) -> App:
    """Create an app double with the dependencies needed by the endpoint factory."""
    return App(
        impl=SimpleNamespace(
            registered_user_dependency=lambda: None,
            idp_user_dependency=lambda: None,
        ),
        feature_flags=feature_flags,
    )


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
            delete_all_ref_data_command_class=ConcreteDeleteAllRefDataCommand,
        )

    assert _get_route(router, "/operational_data") is None
    assert _get_route(router, "/ref_data") is None


def test_reset_routes_return_json_results_with_success_status() -> None:
    """Register reset routes with a body-compatible success status and models."""
    router = APIRouter()
    app = _create_app(
        {
            enum.FeatureFlag.ALLOW_DELETE_ALL_OPERATIONAL_DATA: True,
            enum.FeatureFlag.ALLOW_DELETE_ALL_REF_DATA: True,
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
    app = _create_app({enum.FeatureFlag.ALLOW_DELETE_ALL_REF_DATA: True})

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

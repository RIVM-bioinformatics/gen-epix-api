"""Test feature-flag-gated route registration in create_system_endpoints."""

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import APIRouter
from fastapi.routing import APIRoute
from test.util.mock_compat import Mock

from gen_epix.commondb.api.system import create_system_endpoints
from gen_epix.commondb.domain import command, enum, model

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
    app.get_feature_flag.return_value = flag_enabled
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
        delete_all_operational_data_result_class=model.DeleteAllOperationalDataResult,
    )

    app.get_feature_flag.assert_any_call(enum.FeatureFlag.ALLOW_DELETE_ALL_OPERATIONAL_DATA)
    operation_ids = {
        route.operation_id for route in router.routes if isinstance(route, APIRoute)
    }
    assert ("operational_data__delete" in operation_ids) is flag_enabled


@pytest.mark.parametrize("router_file", _ROUTER_FILES, ids=lambda p: p.parent.parent.name)
def test_router_wiring_supplies_result_class_alongside_command_class(
    router_file: Path,
) -> None:
    """Every router.py that wires a delete-all-operational-data command also
    wires its result class.

    create_system_endpoints asserts both are present whenever the feature
    flag is enabled; supplying only the command class was reachable only
    after the ALLOW_DELETE_ALL_OPERATIONAL_DATA lookup bug (LSP-3596 Phase
    1) was fixed, and crashed app startup the first time it was actually
    reachable. This is a static contract check on router.py's own source,
    since exercising create_routers() end-to-end would require a fully
    functional App/Domain rather than a lightweight double.
    """
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
        key_names = {
            key.value
            for key in node.keys
            if isinstance(key, ast.Constant)
        }
        assert "delete_all_operational_data_result_class" in key_names, (
            f"{router_file} passes delete_all_operational_data_command_class "
            "without delete_all_operational_data_result_class; "
            "create_system_endpoints asserts both are present"
        )

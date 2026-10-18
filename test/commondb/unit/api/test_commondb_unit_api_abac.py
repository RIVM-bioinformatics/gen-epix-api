"""Test the commondb ABAC endpoint factory contract."""

from test.util.mock_compat import Mock, patch
from types import SimpleNamespace
from typing import Callable
from uuid import uuid4

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

from gen_epix.commondb.api.abac import create_abac_endpoints
from gen_epix.commondb.domain import command, enum, model
from gen_epix.fastapp.api import CrudEndpointGenerator


def _registered_user_dependency() -> None:
    return None


def _create_abac_routes(
    result: list[model.UserNameEmail],
    router_factory: Callable[[], APIRouter | FastAPI] = APIRouter,
    service_type_kwargs: dict[str, enum.ServiceType] | None = None,
) -> tuple[APIRouter | FastAPI, Mock, Mock, Mock, Mock]:
    router = router_factory()
    app = Mock()
    app.impl = SimpleNamespace(
        registered_user_dependency=_registered_user_dependency,
    )
    app.handle.return_value = result
    handle_exception = Mock()
    crud_endpoint_sets = [object()]

    with (
        patch.object(
            CrudEndpointGenerator,
            "create_crud_endpoint_set_for_domain",
            return_value=crud_endpoint_sets,
        ) as create_endpoint_sets,
        patch.object(CrudEndpointGenerator, "generate_endpoints") as generate_endpoints,
    ):
        create_abac_endpoints(
            router,
            app,
            handle_exception=handle_exception,
            **(service_type_kwargs or {}),
        )

    return (
        router,
        app,
        handle_exception,
        create_endpoint_sets,
        generate_endpoints,
    )


def _get_admin_names_route(router: APIRouter | FastAPI) -> APIRoute:
    return next(
        route
        for route in router.routes
        if isinstance(route, APIRoute)
        and route.operation_id == "retrieve_organization_admin_name_emails"
    )


@pytest.mark.parametrize(
    ("router_factory", "service_type_kwargs", "expected_service_type"),
    [
        pytest.param(APIRouter, {}, enum.ServiceType.ABAC, id="router-default-service"),
        pytest.param(
            FastAPI,
            {"service_type": enum.ServiceType.RBAC},
            enum.ServiceType.RBAC,
            id="fastapi-explicit-service",
        ),
    ],
)
def test_create_abac_endpoints_generates_crud_routes(
    router_factory: Callable[[], APIRouter | FastAPI],
    service_type_kwargs: dict[str, enum.ServiceType],
    expected_service_type: enum.ServiceType,
) -> None:
    router, app, handle_exception, create_endpoint_sets, generate_endpoints = (
        _create_abac_routes([], router_factory, service_type_kwargs)
    )

    create_endpoint_sets.assert_called_once_with(
        app,
        service_type=expected_service_type,
        user_dependency=_registered_user_dependency,
    )
    generate_endpoints.assert_called_once_with(
        router,
        create_endpoint_sets.return_value,
        handle_exception,
    )


@pytest.mark.asyncio
async def test_admin_names_route_dispatches_command_for_registered_user() -> None:
    result: list[model.UserNameEmail] = []
    router, app, _, _, _ = _create_abac_routes(result)
    route = _get_admin_names_route(router)
    user = model.User(
        id=uuid4(),
        key="user@example.com",
        email="user@example.com",
        roles={"COMMONDB_USER"},
        organization_id=uuid4(),
        is_active=True,
    )

    response = await route.endpoint(user)

    assert response is result
    assert route.path == "/retrieve_organization_admin_name_emails"
    assert route.dependant.dependencies[0].call is _registered_user_dependency
    dispatched_command = app.handle.call_args.args[0]
    assert isinstance(
        dispatched_command,
        command.RetrieveOrganizationAdminNameEmailsCommand,
    )
    assert dispatched_command.user is user


@pytest.mark.asyncio
async def test_admin_names_route_delegates_dispatch_errors() -> None:
    router, app, handle_exception, _, _ = _create_abac_routes([])
    app.handle.side_effect = ValueError("dispatch failed")
    translated_error = RuntimeError("translated")
    handle_exception.side_effect = translated_error

    with pytest.raises(RuntimeError, match="translated"):
        await _get_admin_names_route(router).endpoint(Mock())

    handle_exception.assert_called_once()
    assert handle_exception.call_args.args[0] == "fd6a9c3e"
    assert handle_exception.call_args.args[1] is None
    assert isinstance(handle_exception.call_args.args[2], ValueError)

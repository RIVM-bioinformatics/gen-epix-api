"""Test the commondb authentication endpoint factory contract."""

from test.util.mock_compat import Mock, patch

import pytest
from fastapi import APIRouter
from fastapi.routing import APIRoute

from gen_epix.commondb.api.auth import create_auth_endpoints
from gen_epix.commondb.domain import command, enum
from gen_epix.fastapp.api import CrudEndpointGenerator


def _registered_user_dependency() -> None:
    return None


def _create_auth_routes(
    result: list[object],
    service_type: enum.ServiceType = enum.ServiceType.AUTH,
) -> tuple[APIRouter, Mock, Mock, Mock, Mock]:
    router = APIRouter()
    app = Mock()
    app.impl.registered_user_dependency = _registered_user_dependency
    app.handle.return_value = result
    handle_exception = Mock()

    with (
        patch.object(
            CrudEndpointGenerator,
            "create_crud_endpoint_set_for_domain",
            return_value=[],
        ) as create_endpoint_set,
        patch.object(CrudEndpointGenerator, "generate_endpoints") as generate_endpoints,
    ):
        create_auth_endpoints(
            router,
            app,
            service_type=service_type,
            handle_exception=handle_exception,
        )

    return router, app, handle_exception, create_endpoint_set, generate_endpoints


def _get_identity_providers_route(router: APIRouter) -> APIRoute:
    return next(
        route
        for route in router.routes
        if isinstance(route, APIRoute)
        and route.operation_id == "identity_providers__get_all"
    )


@pytest.mark.asyncio
async def test_public_identity_provider_route_dispatches_public_command() -> None:
    providers: list[object] = []
    router, app, _, _, _ = _create_auth_routes(providers)

    result = await _get_identity_providers_route(router).endpoint()

    assert result is providers
    dispatched_command = app.handle.call_args.args[0]
    assert isinstance(dispatched_command, command.GetIdentityProvidersCommand)
    assert dispatched_command.user is None
    assert dispatched_command.public is True
    assert _get_identity_providers_route(router).path == "/identity_providers"


@pytest.mark.asyncio
async def test_identity_provider_route_delegates_dispatch_errors() -> None:
    router, app, handle_exception, _, _ = _create_auth_routes([])
    app.handle.side_effect = ValueError("dispatch failed")
    translated_error = RuntimeError("translated")
    handle_exception.side_effect = translated_error

    with pytest.raises(RuntimeError, match="translated"):
        await _get_identity_providers_route(router).endpoint()

    handle_exception.assert_called_once()
    assert handle_exception.call_args.args[0] == "3ddf8ebb"
    assert handle_exception.call_args.args[1] is None
    assert isinstance(handle_exception.call_args.args[2], ValueError)


@pytest.mark.parametrize(
    "service_type",
    [enum.ServiceType.AUTH, enum.ServiceType.RBAC],
    ids=["default-service", "explicit-service"],
)
def test_crud_endpoint_generation_receives_service_and_registered_dependency(
    service_type: enum.ServiceType,
) -> None:
    router, app, handle_exception, create_endpoint_set, generate_endpoints = (
        _create_auth_routes([], service_type)
    )

    create_endpoint_set.assert_called_once_with(
        app,
        service_type=service_type,
        user_dependency=_registered_user_dependency,
    )
    generate_endpoints.assert_called_once_with(router, [], handle_exception)

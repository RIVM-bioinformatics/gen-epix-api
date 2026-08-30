"""Compose commondb API routers for mounting below the application's v1 prefix."""

from collections.abc import Callable
from typing import Any, NoReturn

from fastapi import APIRouter

from gen_epix.commondb.api.abac import create_abac_endpoints
from gen_epix.commondb.api.auth import create_auth_endpoints
from gen_epix.commondb.api.organization import (
    ApiPermission,
    create_organization_endpoints,
)
from gen_epix.commondb.api.rbac import create_rbac_endpoints
from gen_epix.commondb.api.system import create_system_endpoints
from gen_epix.commondb.domain import enum
from gen_epix.fastapp import App
from gen_epix.fastapp.api.router import RouterData


def create_routers(
    app: App | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    router_kwargs: dict = {},
) -> list[APIRouter]:
    """Create routers for commondb authentication, RBAC, organization, ABAC, and system APIs.

    Args:
        app: Composed commondb application that dispatches endpoint commands.
        handle_exception: Exception adapter passed to endpoint factories.
        router_kwargs: Additional arguments applied to each router.

    Returns:
        Tagged routers for the commondb API surface.
    """
    assert app
    router_data: list[RouterData] = [
        # Common routers
        {
            "name": "auth",
            "create_endpoints_fn": create_auth_endpoints,
            "endpoints_function_kwargs": {"service_type": enum.ServiceType.AUTH},
        },
        {
            "name": "rbac",
            "create_endpoints_fn": create_rbac_endpoints,
            "endpoints_function_kwargs": {"service_type": enum.ServiceType.RBAC},
        },
        {
            "name": "organization",
            "create_endpoints_fn": create_organization_endpoints,
            "endpoints_function_kwargs": {
                "service_type": enum.ServiceType.ORGANIZATION,
                "api_permission_class": ApiPermission,
            },
        },
        {
            "name": "abac",
            "create_endpoints_fn": create_abac_endpoints,
            "endpoints_function_kwargs": {"service_type": enum.ServiceType.ABAC},
        },
        {
            "name": "system",
            "create_endpoints_fn": create_system_endpoints,
            "endpoints_function_kwargs": {"service_type": enum.ServiceType.SYSTEM},
        },
    ]
    routers: list[APIRouter] = []
    for curr_router_data in router_data:
        router = APIRouter(tags=[curr_router_data["name"]], **router_kwargs)
        curr_router_data["create_endpoints_fn"](
            router,
            app,
            handle_exception=handle_exception,
            **curr_router_data.get("endpoints_function_kwargs", {}),
        )
        routers.append(router)
    return routers

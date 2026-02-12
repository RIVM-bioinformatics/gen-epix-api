from collections.abc import Callable
from typing import Any, NoReturn

from fastapi import APIRouter

from gen_epix.commondb.api.auth import create_auth_endpoints
from gen_epix.commondb.api.organization import (
    ApiPermission,
    create_organization_endpoints,
)
from gen_epix.commondb.api.rbac import create_rbac_endpoints
from gen_epix.commondb.api.system import create_system_endpoints
from gen_epix.commondb import enum
from gen_epix.fastapp import App


def create_routers(
    app: App | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    router_kwargs: dict = {},
) -> list[APIRouter]:
    assert app
    router_data = [
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
            "name": "system",
            "create_endpoints_fn": create_system_endpoints,
            "endpoints_function_kwargs": {"service_type": enum.ServiceType.SYSTEM},
        },
    ]
    routers: list[APIRouter] = []
    for curr_router_data in router_data:
        name: str = curr_router_data["name"]  # type: ignore[assignment]
        create_endpoints_fn: Callable = curr_router_data["create_endpoints_fn"]  # type: ignore[assignment]
        router = APIRouter(tags=[name], **router_kwargs)
        endpoints_function_kwargs: dict = curr_router_data.get(  # type: ignore[assignment]
            "endpoints_function_kwargs", {}
        )
        create_endpoints_fn(
            router,
            app,
            handle_exception=handle_exception,
            **endpoints_function_kwargs,
        )
        routers.append(router)
    return routers

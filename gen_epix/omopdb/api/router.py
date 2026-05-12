from collections.abc import Callable
from typing import Any, NoReturn

from fastapi import APIRouter

from gen_epix.commondb.api.abac import create_abac_endpoints
from gen_epix.commondb.api.auth import create_auth_endpoints
from gen_epix.commondb.api.organization import create_organization_endpoints
from gen_epix.commondb.api.rbac import create_rbac_endpoints
from gen_epix.commondb.api.system import create_system_endpoints
from gen_epix.fastapp import App
from gen_epix.fastapp.api.router import RouterData
from gen_epix.omopdb.api.omop import create_omop_endpoints
from gen_epix.omopdb.api.organization import ApiPermission
from gen_epix.omopdb.domain import enum


def create_routers(
    app: App | None = None,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    router_kwargs: dict = {},
) -> list[APIRouter]:
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
        # Specific routers
        {
            "name": "omop",
            "create_endpoints_fn": create_omop_endpoints,
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

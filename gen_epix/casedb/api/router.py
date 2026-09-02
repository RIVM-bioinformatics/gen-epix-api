"""Compose casedb API routers from shared and domain endpoint factories."""

from collections.abc import Callable
from typing import Any, NoReturn

from fastapi import APIRouter

from gen_epix.casedb.api.abac import create_abac_endpoints
from gen_epix.casedb.api.case import create_case_endpoints
from gen_epix.casedb.api.geo import create_geo_endpoints
from gen_epix.casedb.api.ontology import create_ontology_endpoints
from gen_epix.casedb.api.organization import ApiPermission
from gen_epix.casedb.domain import enum
from gen_epix.commondb.api.auth import create_auth_endpoints
from gen_epix.commondb.api.organization import create_organization_endpoints
from gen_epix.commondb.api.rbac import create_rbac_endpoints
from gen_epix.commondb.api.system import create_system_endpoints
from gen_epix.fastapp import App
from gen_epix.fastapp.api.router import RouterData


def create_routers(
    app: App | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    router_kwargs: dict = {},
) -> list[APIRouter]:
    """Create the tagged routers that make up the casedb API."""
    assert app
    router_data: list[RouterData] = [
        # commondb routers
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
        # Specific routers
        {
            "name": "ontology",
            "create_endpoints_fn": create_ontology_endpoints,
        },
        {
            "name": "geo",
            "create_endpoints_fn": create_geo_endpoints,
        },
        {
            "name": "case",
            "create_endpoints_fn": create_case_endpoints,
        },
        {
            "name": "abac",
            "create_endpoints_fn": create_abac_endpoints,
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

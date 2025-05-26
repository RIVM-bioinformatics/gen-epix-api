from typing import Callable

from fastapi import APIRouter

from gen_epix.casedb.api.abac import create_abac_endpoints
from gen_epix.casedb.api.auth import create_auth_endpoints
from gen_epix.casedb.api.case import create_case_endpoints
from gen_epix.casedb.api.geo import create_geo_endpoints
from gen_epix.casedb.api.ontology import create_ontology_endpoints
from gen_epix.casedb.api.organization import create_organization_endpoints
from gen_epix.casedb.api.rbac import create_rbac_endpoints
from gen_epix.casedb.api.system import create_system_endpoints
from gen_epix.fastapp import App


def create_routers(
    app: App | None = None,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable | None = None,
    router_kwargs: dict = {},
) -> list[APIRouter]:
    assert app
    router_data = [
        {
            "name": "auth",
            "create_endpoints_function": create_auth_endpoints,
        },
        {
            "name": "rbac",
            "create_endpoints_function": create_rbac_endpoints,
        },
        {
            "name": "ontology",
            "create_endpoints_function": create_ontology_endpoints,
        },
        {
            "name": "geo",
            "create_endpoints_function": create_geo_endpoints,
        },
        {
            "name": "organization",
            "create_endpoints_function": create_organization_endpoints,
        },
        {
            "name": "case",
            "create_endpoints_function": create_case_endpoints,
        },
        {
            "name": "abac",
            "create_endpoints_function": create_abac_endpoints,
        },
        {
            "name": "system",
            "create_endpoints_function": create_system_endpoints,
        },
    ]
    routers: list[APIRouter] = []
    for curr_router_data in router_data:
        name: str = curr_router_data["name"]  # type: ignore[assignment]
        create_endpoints_function: Callable = curr_router_data[  # type: ignore[assignment]
            "create_endpoints_function"
        ]
        router = APIRouter(tags=[name], **router_kwargs)
        create_endpoints_function(
            router,
            app,
            registered_user_dependency=registered_user_dependency,
            new_user_dependency=new_user_dependency,
            idp_user_dependency=idp_user_dependency,
            handle_exception=handle_exception,
        )
        routers.append(router)
    return routers

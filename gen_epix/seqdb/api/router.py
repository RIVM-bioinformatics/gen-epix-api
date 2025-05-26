from typing import Callable

from fastapi import APIRouter

from gen_epix.fastapp import App
from gen_epix.seqdb.api.auth import create_auth_endpoints
from gen_epix.seqdb.api.organization import create_organization_endpoints
from gen_epix.seqdb.api.rbac import create_rbac_endpoints
from gen_epix.seqdb.api.seq import create_seq_endpoints
from gen_epix.seqdb.api.system import create_system_endpoints


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
            "name": "organization",
            "create_endpoints_function": create_organization_endpoints,
        },
        {
            "name": "seq",
            "create_endpoints_function": create_seq_endpoints,
        },
        {
            "name": "system",
            "create_endpoints_function": create_system_endpoints,
        },
    ]
    routers: list[APIRouter] = []
    for curr_router_data in router_data:
        name = curr_router_data["name"]  # type: ignore[assignment]
        create_endpoints_function = curr_router_data["create_endpoints_function"]  # type: ignore[assignment]
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

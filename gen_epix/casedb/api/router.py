from typing import Any, Callable, NoReturn

from fastapi import APIRouter

from gen_epix.casedb.api.abac import create_abac_endpoints
from gen_epix.casedb.api.case import create_case_endpoints
from gen_epix.casedb.api.geo import create_geo_endpoints
from gen_epix.casedb.api.ontology import create_ontology_endpoints
from gen_epix.casedb.api.organization import (
    ApiPermission,
    UpdateUserRequestBody,
    UserInvitationRequestBody,
)
from gen_epix.casedb.api.subject import create_subject_endpoints
from gen_epix.casedb.domain import enum, model
from gen_epix.common.api.auth import create_auth_endpoints
from gen_epix.common.api.organization import create_organization_endpoints
from gen_epix.common.api.rbac import create_rbac_endpoints
from gen_epix.common.api.system import create_system_endpoints
from gen_epix.fastapp import App


def create_routers(
    app: App | None = None,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    router_kwargs: dict = {},
) -> list[APIRouter]:
    assert app
    router_data = [
        {
            "name": "auth",
            "create_endpoints_function": create_auth_endpoints,
            "endpoints_function_kwargs": {"service_type": enum.ServiceType.AUTH},
        },
        {
            "name": "rbac",
            "create_endpoints_function": create_rbac_endpoints,
            "endpoints_function_kwargs": {"service_type": enum.ServiceType.RBAC},
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
            "endpoints_function_kwargs": {
                "service_type": enum.ServiceType.ORGANIZATION,
                "user_class": model.User,
                "user_invitation_class": model.UserInvitation,
                "user_invitation_request_body_class": UserInvitationRequestBody,
                "update_user_request_body_class": UpdateUserRequestBody,
                "api_permission_class": ApiPermission,
            },
        },
        {
            "name": "subject",
            "create_endpoints_function": create_subject_endpoints,
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
            "endpoints_function_kwargs": {"service_type": enum.ServiceType.SYSTEM},
        },
    ]
    routers: list[APIRouter] = []
    for curr_router_data in router_data:
        name: str = curr_router_data["name"]  # type: ignore[assignment]
        create_endpoints_function: Callable = curr_router_data["create_endpoints_function"]  # type: ignore[assignment]
        router = APIRouter(tags=[name], **router_kwargs)
        endpoints_function_kwargs: dict = curr_router_data.get(  # type: ignore[assignment]
            "endpoints_function_kwargs", {}
        )
        create_endpoints_function(
            router,
            app,
            registered_user_dependency=registered_user_dependency,
            new_user_dependency=new_user_dependency,
            idp_user_dependency=idp_user_dependency,
            handle_exception=handle_exception,
            **endpoints_function_kwargs,
        )
        routers.append(router)
    return routers

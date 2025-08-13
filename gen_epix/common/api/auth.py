from typing import Any, Callable, NoReturn

from fastapi import APIRouter, FastAPI

from gen_epix.common.domain import command, enum, model
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.fastapp.enum import LogLevel


def create_auth_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    service_type: enum.ServiceType = enum.ServiceType.AUTH,
    **kwargs: Any,
) -> None:
    assert handle_exception

    # Specific endpoints - Auth
    @router.get(
        "/identity_providers",
        operation_id="identity_providers__get_all",
        name="IdentityProvider",
    )
    async def identity_providers__get_all() -> list[model.IdentityProvider]:
        try:
            cmd = command.GetIdentityProvidersCommand(user=None)
            retval: list[model.IdentityProvider] = app.handle(cmd)
        except Exception as exception:
            handle_exception("3ddf8ebb", None, exception)
        return retval

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=service_type,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )

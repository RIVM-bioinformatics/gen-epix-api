"""Create transport-only API endpoints for commondb authentication commands."""

from collections.abc import Callable
from typing import Any, NoReturn

from fastapi import APIRouter, FastAPI
from fastapi.concurrency import run_in_threadpool

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, enum, model
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator


def create_auth_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    service_type: enum.ServiceType = enum.ServiceType.AUTH,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    """Register public identity-provider and generated authentication CRUD endpoints.

    Args:
        router: Router or application receiving the endpoints.
        app: Composed commondb application that dispatches commands.
        service_type: Domain service type used to generate CRUD endpoints.
        handle_exception: Exception adapter used by endpoint handlers.
        **kwargs: Unused router composition options.
    """
    assert handle_exception
    app_impl: AppImplDetails = app.impl
    registered_user_dependency = app_impl.registered_user_dependency

    # Specific endpoints - Auth
    @router.get(
        "/identity_providers",
        operation_id="identity_providers__get_all",
        name="IdentityProvider",
        description="Get all public identity providers",
    )
    async def identity_providers__get_all() -> list[model.IdentityProvider]:
        """Retrieve publicly available identity-provider configuration."""
        try:
            cmd = command.GetIdentityProvidersCommand(user=None, public=True)
            retval: list[model.IdentityProvider] = await run_in_threadpool(
                app.handle, cmd
            )
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

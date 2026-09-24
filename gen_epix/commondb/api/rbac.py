"""Create transport-only API endpoints for commondb RBAC commands."""

from collections.abc import Callable
from typing import Any, NoReturn

from fastapi import APIRouter, FastAPI

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import enum
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator


def create_rbac_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    service_type: enum.ServiceType = enum.ServiceType.RBAC,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    """Register generated CRUD endpoints for the commondb RBAC service.

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

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=service_type,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )

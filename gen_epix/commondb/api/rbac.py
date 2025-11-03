from typing import Any, Callable, NoReturn

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

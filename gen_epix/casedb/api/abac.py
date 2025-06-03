from typing import Callable

from fastapi import APIRouter, FastAPI

from gen_epix.casedb.api.base import EXCLUDED_PERMISSIONS
from gen_epix.casedb.domain import enum
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator


def create_abac_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable | None = None,
    **kwargs: dict,
) -> None:
    assert handle_exception
    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=enum.ServiceType.ABAC,
        user_dependency=registered_user_dependency,
        excluded_permissions=EXCLUDED_PERMISSIONS,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )

from collections.abc import Callable
from typing import Any, NoReturn

from fastapi import APIRouter, FastAPI
from fastapi.concurrency import run_in_threadpool

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator


def create_abac_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    assert handle_exception
    app_impl: AppImplDetails = app.impl
    registered_user_dependency = app_impl.registered_user_dependency

    @router.get(
        "/retrieve_organization_admin_name_emails",
        operation_id="retrieve_organization_admin_name_emails",
        name="RetrieveOrganizationAdminNameEmailsCommand",
        description=command.RetrieveOrganizationAdminNameEmailsCommand.__doc__,
    )
    async def retrieve_organization_admin_name_emails(user: registered_user_dependency) -> list[model.UserNameEmail]:  # type: ignore
        try:
            cmd = command.RetrieveOrganizationAdminNameEmailsCommand(
                user=user,
            )
            retval: list[model.UserNameEmail] = await run_in_threadpool(app.handle, cmd)
        except Exception as exception:
            handle_exception("fd6a9c3e", None, exception)
        return retval

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=enum.ServiceType.ABAC,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )

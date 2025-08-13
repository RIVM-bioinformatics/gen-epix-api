from typing import Any, Callable, NoReturn

from fastapi import APIRouter, FastAPI

from gen_epix.casedb.domain import command, enum, model
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.fastapp.enum import LogLevel


def create_abac_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    assert handle_exception

    @router.get(
        "/retrieve_organization_admin_name_emails",
        operation_id="retrieve_organization_admin_name_emails",
        name="RetrieveOrganizationAdminNameEmailsCommand",
    )
    async def retrieve_organization_admin_name_emails(user: registered_user_dependency) -> list[model.UserNameEmail]:  # type: ignore
        try:
            cmd = command.RetrieveOrganizationAdminNameEmailsCommand(
                user=user,
            )
            retval: list[model.UserNameEmail] = app.handle(cmd)
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

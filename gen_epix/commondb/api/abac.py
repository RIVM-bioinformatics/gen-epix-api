"""Create transport-only API endpoints for CommonDB ABAC commands."""

from collections.abc import Callable
from typing import Any, NoReturn

from fastapi import APIRouter, FastAPI

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, enum, model
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator


def create_abac_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    service_type: enum.ServiceType = enum.ServiceType.ABAC,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **_kwargs: Any,
) -> None:
    """Register ABAC retrieval and generated CRUD endpoints.

    Handlers construct commands and delegate policy and business behavior to
    ``app.handle``.

    Args:
        router: Router or application receiving the endpoints.
        app: Composed CommonDB application that dispatches commands.
        service_type: Domain service type used to generate CRUD endpoints.
        handle_exception: Exception adapter used by endpoint handlers.
        **_kwargs: Unused router composition options.
    """
    assert handle_exception
    app_impl: AppImplDetails = app.impl
    registered_user_dependency = app_impl.registered_user_dependency

    @router.get(
        "/retrieve_organization_admin_name_emails",
        operation_id="retrieve_organization_admin_name_emails",
        name="RetrieveOrganizationAdminNameEmailsCommand",
        description=command.RetrieveOrganizationAdminNameEmailsCommand.__doc__,
    )
    async def retrieve_organization_admin_name_emails(
        user: registered_user_dependency,  # type: ignore
    ) -> list[model.UserNameEmail]:
        """Retrieve names and email addresses of the user's organization admins."""
        try:
            cmd = command.RetrieveOrganizationAdminNameEmailsCommand(user=user)
            retval: list[model.UserNameEmail] = app.handle(cmd)
        except Exception as exception:
            handle_exception("fd6a9c3e", None, exception)
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

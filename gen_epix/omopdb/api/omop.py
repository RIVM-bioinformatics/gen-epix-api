from collections.abc import Callable
from typing import Any, NoReturn, cast

from fastapi import APIRouter, FastAPI

from gen_epix.commondb.api.exc import handle_command
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.fastapp import App
from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator
from gen_epix.omopdb.domain import command, enum, model


def create_omop_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:

    assert handle_exception
    app_impl: AppImplDetails = app.impl
    registered_user_dependency = app_impl.registered_user_dependency

    @router.post(
        "/upload/persons",
        operation_id="upload__persons",
        name="Upload persons",
        description=command.UploadPersonsCommand.__doc__,
    )
    async def upload__persons(
        user: registered_user_dependency,  # type: ignore
        cmd: command.UploadPersonsCommand,
    ) -> model.PersonBatchUploadResult:
        cmd.user = user
        return cast(
            model.PersonBatchUploadResult,
            handle_command(
                app=app,
                user=user,
                exception_code="e7f2d91a",
                input_handle_exception=handle_exception,
                input_command=cmd,
            ),
        )

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=enum.ServiceType.OMOP,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )

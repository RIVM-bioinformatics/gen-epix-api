"""Expose seqdb api.file API adapters and request representations."""

import base64
from collections.abc import Callable
from typing import Any, NoReturn
from uuid import UUID

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.util import copy_model_field


class CreateFileRequestBody(PydanticBaseModel):
    """Represent a base64-encoded file creation request."""

    content: str = Field(description="The content of the file as base64 encoded bytes.")
    format: enum.FileFormat = copy_model_field(command.CreateFileCommand, "format")
    compression: enum.FileCompression = copy_model_field(
        command.CreateFileCommand, "compression"
    )


def create_file_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    """Register file creation and CRUD transport endpoints.

    Args:
        router: Router or application receiving the endpoints.
        app: Application that dispatches file commands.
        handle_exception: Handler for command-processing exceptions.
        **kwargs: Additional endpoint-generation configuration.
    """
    assert handle_exception
    app_impl: AppImplDetails = app.impl
    registered_user_dependency = app_impl.registered_user_dependency

    @router.post(
        "/create/file",
        operation_id="create__file",
        name="CreateFile",
        description=command.CreateFileCommand.__doc__,
    )
    async def create__file(
        user: registered_user_dependency,
        request_body: CreateFileRequestBody,  # type: ignore
    ) -> UUID:
        """Create a file from decoded request content through its command."""
        try:
            retval: UUID = app.handle(
                command.CreateFileCommand(
                    user=user,
                    file=model.File(
                        content=base64.b64decode(request_body.content),
                    ),
                    format=request_body.format,
                    compression=request_body.compression,
                )
            )
        except Exception as exception:
            handle_exception("a8f9d24e", user, exception, request_ids=request_body.seq_ids)  # type: ignore
        return retval

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=enum.ServiceType.FILE,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )

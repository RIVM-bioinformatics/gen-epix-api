"""Transport adapters for OmopDB person upload, retrieval, and CRUD endpoints."""

from collections.abc import Callable
from typing import Any, NoReturn, cast
from uuid import UUID

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.commondb.api.exc import handle_command
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.fastapp import App
from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator
from gen_epix.omopdb.domain import command, enum, model
from gen_epix.util import copy_model_field


class RetrievePersonsByIdsRequestBody(PydanticBaseModel):
    """Carry unique person identifiers for a full-person retrieval request."""

    person_ids: list[UUID] = copy_model_field(
        command.RetrievePersonsByIdCommand, "person_ids"
    )


class RetrieveSpecimenIdsByCohortIdsRequestBody(PydanticBaseModel):
    """Carry cohort identifiers for a cohort-to-specimen retrieval request."""

    cohort_definition_id: UUID = copy_model_field(
        command.RetrieveSpecimenIdsByCohortIdsCommand, "cohort_definition_id"
    )
    cohort_ids: list[UUID] = copy_model_field(
        command.RetrieveSpecimenIdsByCohortIdsCommand, "cohort_ids"
    )


def create_omop_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    """Register OMOP upload, retrieval, and generated CRUD transport endpoints."""
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
        """Delegate a person-upload command for the authenticated user."""
        cmd.user = user
        return cast(
            model.PersonBatchUploadResult,
            await handle_command(
                app=app,
                user=user,
                exception_code="d98e5b2",
                input_handle_exception=handle_exception,
                input_command=cmd,
            ),
        )

    @router.post(
        "/retrieve/person_ids_by_query",
        operation_id="retrieve__person_ids_by_query",
        name="Retrieve person IDs by query",
        description=command.RetrievePersonsByQueryCommand.__doc__,
    )
    async def retrieve__person_ids_by_query(
        user: registered_user_dependency,  # type: ignore
        request_body: model.PersonQuery,
    ) -> model.PersonQueryResult:
        """Delegate a person-query retrieval command for the authenticated user."""
        return cast(
            model.PersonQueryResult,
            await handle_command(
                app=app,
                user=user,
                exception_code="93656cdf",
                input_handle_exception=handle_exception,
                input_command=command.RetrievePersonsByQueryCommand(
                    user=user,
                    person_query=request_body,
                ),
            ),
        )

    @router.post(
        "/retrieve/persons_by_ids",
        operation_id="retrieve__persons_by_ids",
        name="Retrieve persons by IDs",
        description=command.RetrievePersonsByIdCommand.__doc__,
    )
    async def retrieve__persons_by_ids(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrievePersonsByIdsRequestBody,
    ) -> list[model.FullPerson]:
        """Delegate a full-person retrieval command for the authenticated user."""
        return cast(
            list[model.FullPerson],
            await handle_command(
                app=app,
                user=user,
                exception_code="e7f2d91b",
                input_handle_exception=handle_exception,
                input_command=command.RetrievePersonsByIdCommand(
                    user=user,
                    person_ids=request_body.person_ids,
                ),
            ),
        )

    @router.post(
        "/retrieve/specimen_ids_by_cohort_ids",
        operation_id="retrieve__specimen_ids_by_cohort_ids",
        name="Retrieve specimen IDs by cohort IDs",
        description=command.RetrieveSpecimenIdsByCohortIdsCommand.__doc__,
    )
    async def retrieve__specimen_ids_by_cohort_ids(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveSpecimenIdsByCohortIdsRequestBody,
    ) -> model.SpecimenIdsByCohortResult:
        """Delegate a cohort specimen-ID retrieval command for the user."""
        return cast(
            model.SpecimenIdsByCohortResult,
            await handle_command(
                app=app,
                user=user,
                exception_code="fac4d7a7",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveSpecimenIdsByCohortIdsCommand(
                    user=user,
                    cohort_definition_id=request_body.cohort_definition_id,
                    cohort_ids=request_body.cohort_ids,
                ),
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

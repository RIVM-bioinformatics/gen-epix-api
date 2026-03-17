from collections.abc import Callable
from typing import Any, NoReturn
from uuid import UUID

from fastapi import APIRouter, FastAPI
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.fastapp import App
from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator


class UpdateDiseaseEtiologicalAgentRequestBody(PydanticBaseModel):
    etiologies: list[model.Etiology]


def create_ontology_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    assert handle_exception
    app_impl: AppImplDetails = app.impl
    registered_user_dependency = app_impl.registered_user_dependency

    @router.put(
        "/diseases/{disease_id}/etiological_agents",
        operation_id="diseases__put__etiological_agents",
        name="Disease_EtiologicalAgent",
        description=command.DiseaseEtiologicalAgentUpdateAssociationCommand.__doc__,
    )
    async def diseases__put__concepts(
        user: registered_user_dependency,  # type: ignore
        disease_id: UUID,
        request_body: UpdateDiseaseEtiologicalAgentRequestBody,
    ) -> list[model.Etiology]:
        try:
            cmd = command.DiseaseEtiologicalAgentUpdateAssociationCommand(
                user=user,
                obj_id1=disease_id,
                association_objs=request_body.etiologies,
                props={"return_id": False},
            )
            retval: list[model.Etiology] = await run_in_threadpool(app.handle, cmd)
        except Exception as exception:
            handle_exception("d5459ee4", user, exception)
        return retval

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=enum.ServiceType.ONTOLOGY,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )

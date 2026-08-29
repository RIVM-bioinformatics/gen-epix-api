from collections.abc import Callable
from typing import Any, NoReturn
from uuid import UUID

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain.literal import MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH
from gen_epix.fastapp import App
from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator
from gen_epix.util import copy_model_field


class DiseaseEtiologicalAgentUpdateAssociationRequestBody(PydanticBaseModel):
    etiologies: list[model.Etiology] = copy_model_field(
        command.DiseaseEtiologicalAgentUpdateAssociationCommand,
        "association_objs",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


def create_ontology_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    """Register all non-CRUD ontology endpoints on the given router."""
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
        user: registered_user_dependency,  # type: ignore[valid-type]
        disease_id: UUID,
        request_body: DiseaseEtiologicalAgentUpdateAssociationRequestBody,
    ) -> list[model.Etiology]:
        """See router description."""
        try:
            cmd = command.DiseaseEtiologicalAgentUpdateAssociationCommand(
                user=user,
                obj_id1=disease_id,
                association_objs=request_body.etiologies,
            )
            retval: list[model.Etiology] = app.handle(cmd)
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

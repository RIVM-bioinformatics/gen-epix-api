from typing import Any, Callable, NoReturn
from uuid import UUID

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.casedb.domain import command, enum, model
from gen_epix.fastapp import App
from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator
from gen_epix.fastapp.enum import LogLevel


class UpdateConceptSetConceptRequestBody(PydanticBaseModel):
    concept_set_members: list[model.ConceptSetMember]


class UpdateDiseaseEtiologicalAgentRequestBody(PydanticBaseModel):
    etiologies: list[model.Etiology]


def create_ontology_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    assert handle_exception

    @router.put(
        "/concept_sets/{concept_set_id}/concepts",
        operation_id="concept_sets__put__concepts",
        name="ConceptSet_Concept",
    )
    async def concept_sets__put__concepts(
        user: registered_user_dependency,  # type: ignore
        concept_set_id: UUID,
        request_body: UpdateConceptSetConceptRequestBody,
    ) -> list[model.ConceptSetMember]:
        try:
            cmd = command.ConceptSetConceptUpdateAssociationCommand(
                user=user,
                obj_id1=concept_set_id,
                association_objs=request_body.concept_set_members,
                props={"return_id": False},
            )
            retval: list[model.ConceptSetMember] = app.handle(cmd)
        except Exception as exception:
            handle_exception("da821eb5", user, exception)
        return retval

    @router.put(
        "/diseases/{disease_id}/etiological_agents",
        operation_id="diseases__put__etiological_agents",
        name="Disease_EtiologicalAgent",
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

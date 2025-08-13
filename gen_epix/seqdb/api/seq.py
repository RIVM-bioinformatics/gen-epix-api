from typing import Any, Callable, NoReturn
from uuid import UUID

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.fastapp.enum import LogLevel
from gen_epix.seqdb.domain import command, enum, model


class RetrievePhylogeneticTreeRequestBody(PydanticBaseModel):
    seq_distance_protocol_id: UUID
    tree_algorithm: enum.TreeAlgorithm
    seq_ids: list[UUID]
    leaf_codes: list[str] | None


class RetrieveSeqRequestBody(PydanticBaseModel):
    seq_ids: list[UUID]


class RetrieveAlleleProfileRequestBody(PydanticBaseModel):
    seq_ids: list[UUID]
    locus_set_id: UUID


def create_seq_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    assert handle_exception

    @router.post(
        "/retrieve/phylogenetic_tree", operation_id="retrieve__phylogenetic_tree"
    )
    async def retrieve__phylogenetic_tree(
        user: registered_user_dependency, request_body: RetrievePhylogeneticTreeRequestBody  # type: ignore
    ) -> model.PhylogeneticTree:
        try:
            retval: model.PhylogeneticTree = app.handle(
                command.RetrievePhylogeneticTreeCommand(
                    user=user,
                    seq_distance_protocol_id=request_body.seq_distance_protocol_id,
                    tree_algorithm=request_body.tree_algorithm,
                    seq_ids=request_body.seq_ids,
                    leaf_names=request_body.leaf_codes,
                )
            )
        except Exception as exception:
            handle_exception("dc71bce0", user, exception, request_ids=request_body.seq_ids)  # type: ignore
        return retval

    @router.post("/retrieve/seq", operation_id="retrieve__seq")
    async def retrieve__seq(
        user: registered_user_dependency, request_body: RetrieveSeqRequestBody  # type: ignore
    ) -> list[model.CompleteSeq]:
        try:
            retval: list[model.CompleteSeq] = app.handle(
                command.RetrieveCompleteSeqCommand(
                    user=user,
                    seq_ids=request_body.seq_ids,
                )
            )
        except Exception as exception:
            handle_exception("ac218f73", user, exception, request_ids=request_body.seq_ids)  # type: ignore
        return retval

    @router.post("/retrieve/allele_profile", operation_id="retrieve__allele_profile")
    async def retrieve__allele_profile(
        user: registered_user_dependency, request_body: RetrieveAlleleProfileRequestBody  # type: ignore
    ) -> list[model.CompleteAlleleProfile]:
        try:
            retval: list[model.CompleteAlleleProfile] = app.handle(
                command.RetrieveCompleteAlleleProfileCommand(
                    user=user,
                    seq_ids=request_body.seq_ids,
                    locus_set_id=request_body.locus_set_id,
                )
            )
        except Exception as exception:
            handle_exception("f1d282b4", user, exception, request_ids=request_body.seq_ids)  # type: ignore
        return retval

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=enum.ServiceType.SEQ,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )

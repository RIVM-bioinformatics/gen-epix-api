from collections.abc import Callable, Iterable
from typing import Any, NoReturn
from uuid import UUID

from fastapi import APIRouter, FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.util import copy_model_field
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.seqdb.domain import command, enum, model


class RetrievePhylogeneticTreeRequestBody(PydanticBaseModel):
    seq_distance_protocol_id: UUID
    tree_algorithm: enum.TreeAlgorithm
    seq_ids: list[UUID]
    leaf_codes: list[str] | None = None


class RetrieveSeqRequestBody(PydanticBaseModel):
    seq_ids: list[UUID]


class RetrieveSeqFastaRequestBody(PydanticBaseModel):

    seq_ids: list[UUID] = Field(
        description="List of sequence IDs to retrieve in FASTA format.",
    )

    file_name: str = Field(
        description="The desired filename for the FASTA download.",
    )


class RetrieveAlleleProfileRequestBody(PydanticBaseModel):
    seq_ids: list[UUID]
    locus_set_id: UUID


class UpsertCompleteSamplesRequestBody(command.UpsertCompleteSamplesCommand):
    alleles: list[model.Allele] | None = copy_model_field(
        command.UpsertCompleteSamplesCommand, "alleles"
    )
    complete_samples: list[model.CompleteSample] = copy_model_field(
        command.UpsertCompleteSamplesCommand, "complete_samples"
    )


def create_seq_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    assert handle_exception
    app_impl: AppImplDetails = app.impl
    registered_user_dependency = app_impl.registered_user_dependency

    @router.post(
        "/retrieve/phylogenetic_tree",
        operation_id="retrieve__phylogenetic_tree",
        name="RetrievePhylogeneticTree",
        description=command.RetrievePhylogeneticTreeCommand.__doc__,
    )
    async def retrieve__phylogenetic_tree(
        # user: registered_user_dependency, request_body: RetrievePhylogeneticTreeRequestBody  # type: ignore
        user: registered_user_dependency,
        request_body: RetrievePhylogeneticTreeRequestBody,  # type: ignore
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

    @router.post(
        "/retrieve/seq",
        operation_id="retrieve__seq",
        name="RetrieveSeq",
        description=command.RetrieveCompleteSeqCommand.__doc__,
    )
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

    @router.post(
        "/retrieve/seq_fasta",
        operation_id="retrieve__seq_fasta",
        name="RetrieveSeqFasta",
        description=command.RetrieveSeqFastaCommand.__doc__,
    )
    async def retrieve__seq_fasta(
        user: registered_user_dependency, request_body: RetrieveSeqFastaRequestBody
    ) -> StreamingResponse:
        try:
            fasta_iterable: Iterable[str] = app.handle(
                command.RetrieveSeqFastaCommand(
                    user=user,
                    seq_ids=request_body.seq_ids,
                )
            )
        except Exception as exception:
            handle_exception(
                "e4f3b8c1", user, exception, request_ids=request_body.seq_ids
            )

        return StreamingResponse(
            fasta_iterable,
            media_type="application/x-fasta",
            headers={
                "Content-Disposition": f'attachment; filename="{request_body.file_name}"'
            },
        )

    @router.post(
        "/retrieve/allele_profile",
        operation_id="retrieve__allele_profile",
        name="RetrieveAlleleProfile",
        description=command.RetrieveCompleteAlleleProfileCommand.__doc__,
    )
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

    @router.post(
        "/upsert/complete_samples",
        operation_id="upsert__complete_samples",
        name="UpsertCompleteSamples",
        description=command.UpsertCompleteSamplesCommand.__doc__,
    )
    async def upsert__complete_samples(
        user: registered_user_dependency, request_body: UpsertCompleteSamplesRequestBody  # type: ignore
    ) -> list[UUID]:
        try:
            retval: list[UUID] = app.handle(
                command.UpsertCompleteSamplesCommand(
                    user=user,
                    **request_body.model_dump(),
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

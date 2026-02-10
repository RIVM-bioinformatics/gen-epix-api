from collections.abc import Callable, Iterable
from typing import Any, NoReturn
from uuid import UUID

from fastapi import APIRouter, FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.seqdb.domain import command, enum, model


class UploadSamplesRequestBody(command.UploadSamplesCommand):
    pass


class RetrievePhylogeneticTreeRequestBody(PydanticBaseModel):
    seq_distance_protocol_id: UUID
    tree_algorithm: enum.TreeAlgorithm
    profile_ids: list[UUID]
    leaf_codes: list[str] | None = None


class GetSimilarProfilesRequestBody(PydanticBaseModel):
    seq_distance_protocol_id: UUID
    profile_ids: list[UUID]
    max_distance: float


class RetrieveSamplesRequestBody(PydanticBaseModel):
    sample_ids: list[UUID]


class RetrieveSeqFastaRequestBody(PydanticBaseModel):

    seq_ids: list[UUID] = Field(
        description="List of sequence IDs to retrieve in FASTA format.",
    )

    file_name: str = Field(
        description="The desired filename for the FASTA download.",
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
                    profile_ids=request_body.profile_ids,
                    leaf_names=request_body.leaf_codes,
                )
            )
        except Exception as exception:
            handle_exception("dc71bce0", user, exception, request_ids=request_body.profile_ids)  # type: ignore
        return retval

    @router.post(
        "/get_similar_profiles",
        operation_id="get_similar_profiles",
        name="GetSimilarProfiles",
        description=command.GetSimilarProfilesCommand.__doc__,
    )
    async def get_similar_profiles(
        user: registered_user_dependency,
        request_body: GetSimilarProfilesRequestBody,  # type: ignore
    ) -> list[UUID]:
        try:
            retval: list[UUID] = app.handle(
                command.GetSimilarProfilesCommand(
                    user=user,
                    seq_distance_protocol_id=request_body.seq_distance_protocol_id,
                    profile_ids=request_body.profile_ids,
                    max_distance=request_body.max_distance,
                )
            )
        except Exception as exception:
            handle_exception("b1c8e5d9", user, exception, request_ids=request_body.profile_ids)  # type: ignore
        return retval

    @router.post(
        "/retrieve/samples",
        operation_id="retrieve__samples",
        name="RetrieveSamples",
        description=command.RetrieveSamplesCommand.__doc__,
    )
    async def retrieve__samples(
        user: registered_user_dependency, request_body: RetrieveSamplesRequestBody  # type: ignore
    ) -> list[model.SampleForUpload]:
        try:
            retval: list[model.SampleForUpload] = app.handle(
                command.RetrieveSamplesCommand(
                    user=user,
                    sample_ids=request_body.sample_ids,
                )
            )
        except Exception as exception:
            handle_exception("ac218f73", user, exception, request_ids=request_body.sample_ids)  # type: ignore
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
        "/upload/samples",
        operation_id="upload__samples",
        name="UploadSamples",
        description=command.UploadSamplesCommand.__doc__,
    )
    async def upload__samples(
        user: registered_user_dependency, request_body: UploadSamplesRequestBody  # type: ignore
    ) -> model.SampleBatchUploadResult:
        try:
            retval: model.SampleBatchUploadResult = app.handle(
                command.UploadSamplesCommand(
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

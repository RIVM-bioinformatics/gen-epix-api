from collections.abc import Callable, Iterable
from datetime import datetime
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
from gen_epix.util import copy_model_field


class UploadSamplesRequestBody(command.UploadSamplesCommand):
    pass


class CalculatePhylogeneticTreeRequestBody(PydanticBaseModel):
    protocol_id: UUID
    tree_algorithm: enum.TreeAlgorithm
    profile_ids: list[UUID]
    leaf_codes: list[str] | None = None


class RetrieveSimilarProfilesRequestBody(PydanticBaseModel):
    protocol_id: UUID
    profile_ids: list[UUID]
    max_distance: float


class UpdateSeqDistancesRequestBody(PydanticBaseModel):
    protocol_id: UUID


class RetrieveSamplesByIdsRequestBody(PydanticBaseModel):
    sample_ids: list[UUID]


class RetrieveSampleIdentifiersByIdsRequestBody(PydanticBaseModel):
    sample_ids: list[UUID]


class RetrieveSeqFastaRequestBody(PydanticBaseModel):

    seq_ids: list[UUID] = Field(
        description="List of sequence IDs to retrieve in FASTA format.",
    )

    file_name: str = Field(
        description="The desired filename for the FASTA download.",
    )


class RetrieveBestSeqPerSampleRequestBody(PydanticBaseModel):

    protocol_ids: set[UUID] | None = copy_model_field(
        command.RetrieveBestSeqPerSampleCommand, "protocol_ids"
    )
    sample_ids: set[UUID] | None = copy_model_field(
        command.RetrieveBestSeqPerSampleCommand, "sample_ids"
    )


class RetrieveBestSeqProfilePerSampleRequestBody(PydanticBaseModel):

    protocol_ids: set[UUID] = copy_model_field(
        command.RetrieveBestSeqProfilePerSampleCommand, "protocol_ids"
    )
    sample_ids: set[UUID] | None = copy_model_field(
        command.RetrieveBestSeqProfilePerSampleCommand, "sample_ids"
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
        "/calculate/phylogenetic_tree",
        operation_id="retrieve__phylogenetic_tree",
        name="RetrievePhylogeneticTree",
        description=command.CalculatePhylogeneticTreeCommand.__doc__,
    )
    async def retrieve__phylogenetic_tree(
        # user: registered_user_dependency, request_body: RetrievePhylogeneticTreeRequestBody  # type: ignore
        user: registered_user_dependency,  # type: ignore
        request_body: CalculatePhylogeneticTreeRequestBody,  # type: ignore
    ) -> model.PhylogeneticTree:
        try:
            retval: model.PhylogeneticTree = app.handle(
                command.CalculatePhylogeneticTreeCommand(
                    user=user,
                    protocol_id=request_body.protocol_id,
                    tree_algorithm=request_body.tree_algorithm,
                    seq_profile_ids=request_body.profile_ids,
                    leaf_names=request_body.leaf_codes,
                )
            )
        except Exception as exception:
            handle_exception("dc71bce0", user, exception, request_ids=request_body.profile_ids)  # type: ignore
        return retval

    @router.post(
        "/retrieve/similar_profiles",
        operation_id="retrieve__similar_profiles",
        name="RetrieveSimilarProfiles",
        description=command.RetrieveSimilarProfilesCommand.__doc__,
    )
    async def retrieve__similar_profiles(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveSimilarProfilesRequestBody,  # type: ignore
    ) -> list[UUID]:
        try:
            retval: list[UUID] = app.handle(
                command.RetrieveSimilarProfilesCommand(
                    user=user,
                    protocol_id=request_body.protocol_id,
                    profile_ids=request_body.profile_ids,
                    max_distance=request_body.max_distance,
                )
            )
        except Exception as exception:
            handle_exception("b1c8e5d9", user, exception, request_ids=request_body.profile_ids)  # type: ignore
        return retval

    @router.post(
        "/retrieve/sample_ids_by_query",
        operation_id="retrieve__sample_ids_by_query",
        name="RetrieveSampleIDsByQuery",
        description=command.RetrieveSamplesByQueryCommand.__doc__,
    )
    async def retrieve__sample_ids_by_query(
        user: registered_user_dependency,  # type: ignore
        request_body: model.SampleQuery,
    ) -> model.SampleQueryResult:
        try:
            retval: model.SampleQueryResult = app.handle(
                command.RetrieveSamplesByQueryCommand(
                    user=user,
                    sample_query=request_body,
                )
            )
        except Exception as exception:
            handle_exception("8f3a1c7d", user, exception)  # type: ignore
        return retval

    @router.post(
        "/retrieve/samples_by_ids",
        operation_id="retrieve__samples_by_ids",
        name="RetrieveSamplesByIDs",
        description=command.RetrieveSamplesByIdCommand.__doc__,
    )
    async def retrieve__samples_by_ids(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveSamplesByIdsRequestBody,  # type: ignore
    ) -> list[model.FullSample]:
        try:
            retval: list[model.FullSample] = app.handle(
                command.RetrieveSamplesByIdCommand(
                    user=user,
                    sample_ids=request_body.sample_ids,
                )
            )
        except Exception as exception:
            handle_exception("ac218f73", user, exception, request_ids=request_body.sample_ids)  # type: ignore
        return retval

    @router.post(
        "/retrieve/sample_identifiers_by_ids",
        operation_id="retrieve__sample_identifiers_by_ids",
        name="RetrieveSampleIdentifiersByIDs",
        description=command.RetrieveSampleIdentifiersByIdCommand.__doc__,
    )
    async def retrieve__sample_identifiers_by_ids(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveSampleIdentifiersByIdsRequestBody,  # type: ignore
    ) -> list[model.SampleIdentifier]:
        try:
            retval: list[model.SampleIdentifier] = app.handle(
                command.RetrieveSampleIdentifiersByIdCommand(
                    user=user,
                    sample_ids=request_body.sample_ids,
                )
            )
        except Exception as exception:
            handle_exception("b3f91a2e", user, exception, request_ids=request_body.sample_ids)  # type: ignore
        return retval

    @router.post(
        "/retrieve/seq_fasta",
        operation_id="retrieve__seq_fasta",
        name="RetrieveSeqFasta",
        description=command.RetrieveSeqFastaCommand.__doc__,
    )
    async def retrieve__seq_fasta(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveSeqFastaRequestBody,
    ) -> StreamingResponse:
        try:
            fasta_iterable: Iterable[str] = app.handle(
                command.RetrieveSeqFastaCommand(
                    user=user,
                    seq_ids=request_body.seq_ids,
                )
            )
        except Exception as exception:
            handle_exception("e4f3b8c1", user, exception)  # type: ignore

        return StreamingResponse(
            fasta_iterable,
            media_type="application/x-fasta",
            headers={
                "Content-Disposition": f'attachment; filename="{request_body.file_name}"'
            },
        )

    @router.post(
        "/retrieve/seq_distance_last_modified/{protocol_id}",
        operation_id="retrieve__seq_distance_last_modified",
        name="RetrieveSeqDistanceLastModified",
        description=command.RetrieveSeqDistanceLastModifiedCommand.__doc__,
    )
    async def retrieve__seq_distance_last_modified(
        user: registered_user_dependency,  # type: ignore
        protocol_id: UUID,
    ) -> datetime | None:
        try:
            retval: datetime | None = app.handle(
                command.RetrieveSeqDistanceLastModifiedCommand(
                    user=user,
                    protocol_id=protocol_id,
                )
            )
        except Exception as exception:
            handle_exception("d9e5f4a7", user, exception)  # type: ignore
        return retval

    @router.post(
        "/update/seq_distances",
        operation_id="update__seq_distances",
        name="UpdateSeqDistances",
        description=command.UpdateSeqDistancesCommand.__doc__,
    )
    async def update__seq_distances(
        user: registered_user_dependency,  # type: ignore
        request_body: UpdateSeqDistancesRequestBody,
    ) -> list[model.CalculateSeqDistancesResult]:
        try:
            retval: list[model.CalculateSeqDistancesResult] = app.handle(
                command.UpdateSeqDistancesCommand(
                    user=user,
                    protocol_id=request_body.protocol_id,
                )
            )
        except Exception as exception:
            handle_exception("a7b3c1d2", user, exception)  # type: ignore
        return retval

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
                    **request_body.model_dump(exclude={"user"}),
                )
            )
        except Exception as exception:
            handle_exception("f1d282b4", user, exception)  # type: ignore
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

    @router.post(
        "/retrieve/best_seq_per_sample",
        operation_id="retrieve__best_seq_per_sample",
        name="RetrieveBestSeqPerSample",
        description=command.RetrieveBestSeqPerSampleCommand.__doc__,
    )
    async def retrieve__best_seq_per_sample(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveBestSeqPerSampleRequestBody,  # type: ignore
    ) -> dict[UUID, UUID]:
        try:
            retval: dict[UUID, UUID] = app.handle(
                command.RetrieveBestSeqPerSampleCommand(
                    user=user,
                    protocol_ids=request_body.protocol_ids,
                    sample_ids=request_body.sample_ids,
                )
            )
        except Exception as exception:
            handle_exception("c3f7a9e1", user, exception, request_ids=request_body.sample_ids)  # type: ignore
        return retval

    @router.post(
        "/retrieve/best_seq_profile_per_sample",
        operation_id="retrieve__best_seq_profile_per_sample",
        name="RetrieveBestSeqProfilePerSample",
        description=command.RetrieveBestSeqProfilePerSampleCommand.__doc__,
    )
    async def retrieve__best_seq_profile_per_sample(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveBestSeqProfilePerSampleRequestBody,  # type: ignore
    ) -> dict[UUID, UUID]:
        try:
            retval: dict[UUID, UUID] = app.handle(
                command.RetrieveBestSeqProfilePerSampleCommand(
                    user=user,
                    protocol_ids=request_body.protocol_ids,
                    sample_ids=request_body.sample_ids,
                )
            )
        except Exception as exception:
            handle_exception("e2b4d8f6", user, exception, request_ids=request_body.sample_ids)  # type: ignore
        return retval

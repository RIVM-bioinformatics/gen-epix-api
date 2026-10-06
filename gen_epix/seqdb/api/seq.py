"""Expose seqdb api.seq API adapters and request representations."""

from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Any, NoReturn
from uuid import UUID

from fastapi import APIRouter, FastAPI
from fastapi.responses import StreamingResponse

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator

# The request and response models stay importable from this module
# pylint: disable=useless-import-alias, unused-import
from gen_epix.seqdb.api.seq_schema import (
    CalculatePhylogeneticTreeRequestBody as CalculatePhylogeneticTreeRequestBody,
)
from gen_epix.seqdb.api.seq_schema import (
    ConvertSeqFormatRequestBody as ConvertSeqFormatRequestBody,
)
from gen_epix.seqdb.api.seq_schema import (
    RetrieveBestSeqClassificationPerSampleRequestBody as RetrieveBestSeqClassificationPerSampleRequestBody,
)
from gen_epix.seqdb.api.seq_schema import (
    RetrieveBestSeqPerSampleRequestBody as RetrieveBestSeqPerSampleRequestBody,
)
from gen_epix.seqdb.api.seq_schema import (
    RetrieveBestSeqProfilePerSampleRequestBody as RetrieveBestSeqProfilePerSampleRequestBody,
)
from gen_epix.seqdb.api.seq_schema import (
    RetrieveSampleIdentifiersByIdsRequestBody as RetrieveSampleIdentifiersByIdsRequestBody,
)
from gen_epix.seqdb.api.seq_schema import (
    RetrieveSamplesByIdsRequestBody as RetrieveSamplesByIdsRequestBody,
)
from gen_epix.seqdb.api.seq_schema import (
    RetrieveSeqFastaRequestBody as RetrieveSeqFastaRequestBody,
)
from gen_epix.seqdb.api.seq_schema import (
    RetrieveSimilarProfilesRequestBody as RetrieveSimilarProfilesRequestBody,
)
from gen_epix.seqdb.api.seq_schema import (
    UpdateSeqDistancesRequestBody as UpdateSeqDistancesRequestBody,
)
from gen_epix.seqdb.api.seq_schema import (
    UploadSamplesRequestBody as UploadSamplesRequestBody,
)
from gen_epix.seqdb.domain import command, enum, model


def create_seq_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    """Register all non-CRUD seqdb endpoints on the given router."""
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
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: CalculatePhylogeneticTreeRequestBody,
    ) -> model.PhylogeneticTree:
        """See router description."""
        try:
            retval: model.PhylogeneticTree = app.handle(
                command.CalculatePhylogeneticTreeCommand(
                    user=user,
                    protocol_id=request_body.protocol_id,
                    tree_algorithm=request_body.tree_algorithm,
                    seq_profile_ids=request_body.seq_profile_ids,
                    leaf_names=request_body.leaf_names,
                )
            )
        except Exception as exception:
            handle_exception(
                "dc71bce0", user, exception, request_ids=request_body.seq_profile_ids  # type: ignore[call-arg]
            )
        return retval

    @router.post(
        "/retrieve/similar_profiles",
        operation_id="retrieve__similar_profiles",
        name="RetrieveSimilarProfiles",
        description=command.RetrieveSimilarProfilesCommand.__doc__,
    )
    async def retrieve__similar_profiles(
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: RetrieveSimilarProfilesRequestBody,
    ) -> list[UUID]:
        """See router description."""
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
            handle_exception("b1c8e5d9", user, exception, request_ids=request_body.profile_ids)  # type: ignore[call-arg]
        return retval

    @router.post(
        "/retrieve/sample_ids_by_query",
        operation_id="retrieve__sample_ids_by_query",
        name="RetrieveSampleIDsByQuery",
        description=command.RetrieveSamplesByQueryCommand.__doc__,
    )
    async def retrieve__sample_ids_by_query(
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: model.SampleQuery,
    ) -> model.SampleQueryResult:
        """See router description."""
        try:
            retval: model.SampleQueryResult = app.handle(
                command.RetrieveSamplesByQueryCommand(
                    user=user,
                    sample_query=request_body,
                )
            )
        except Exception as exception:
            handle_exception("8f3a1c7d", user, exception)  # type: ignore[call-arg]
        return retval

    @router.post(
        "/retrieve/samples_by_ids",
        operation_id="retrieve__samples_by_ids",
        name="RetrieveSamplesByIDs",
        description=command.RetrieveSamplesByIdCommand.__doc__,
    )
    async def retrieve__samples_by_ids(
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: RetrieveSamplesByIdsRequestBody,
    ) -> list[model.FullSample]:
        """See router description."""
        try:
            retval: list[model.FullSample] = app.handle(
                command.RetrieveSamplesByIdCommand(
                    user=user,
                    sample_ids=request_body.sample_ids,
                )
            )
        except Exception as exception:
            handle_exception("ac218f73", user, exception, request_ids=request_body.sample_ids)  # type: ignore[call-arg]
        return retval

    @router.post(
        "/retrieve/sample_identifiers_by_ids",
        operation_id="retrieve__sample_identifiers_by_ids",
        name="RetrieveSampleIdentifiersByIDs",
        description=command.RetrieveSampleIdentifiersByIdCommand.__doc__,
    )
    async def retrieve__sample_identifiers_by_ids(
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: RetrieveSampleIdentifiersByIdsRequestBody,
    ) -> list[model.SampleIdentifier]:
        """See router description."""
        try:
            retval: list[model.SampleIdentifier] = app.handle(
                command.RetrieveSampleIdentifiersByIdCommand(
                    user=user,
                    sample_ids=request_body.sample_ids,
                )
            )
        except Exception as exception:
            handle_exception("b3f91a2e", user, exception, request_ids=request_body.sample_ids)  # type: ignore[call-arg]
        return retval

    @router.post(
        "/retrieve/seq_fasta",
        operation_id="retrieve__seq_fasta",
        name="RetrieveSeqFasta",
        description=command.RetrieveSeqFastaCommand.__doc__,
    )
    async def retrieve__seq_fasta(
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: RetrieveSeqFastaRequestBody,
    ) -> StreamingResponse:
        """See router description."""
        try:
            fasta_iterable: Iterable[str] = app.handle(
                command.RetrieveSeqFastaCommand(
                    user=user,
                    seq_ids=request_body.seq_ids,
                )
            )
        except Exception as exception:
            handle_exception("e4f3b8c1", user, exception)  # type: ignore[call-arg]

        return StreamingResponse(
            fasta_iterable,
            media_type="application/x-fasta",
            headers={
                "Content-Disposition": f'attachment; filename="{request_body.file_name}"'
            },
        )

    @router.post(
        "/convert/seq_format",
        operation_id="convert__seq_format",
        name="ConvertSeqFormat",
        description=command.ConvertSeqFormatCommand.__doc__,
    )
    async def convert__seq_format(
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: ConvertSeqFormatRequestBody,
    ) -> list[UUID]:
        """See router description."""
        try:
            retval: list[UUID] = app.handle(
                command.ConvertSeqFormatCommand(
                    user=user,
                    seq_ids=request_body.seq_ids,
                    from_format=request_body.from_format,
                    to_format=request_body.to_format,
                )
            )
        except Exception as exception:
            handle_exception(
                "b8c4d2e1", user, exception, request_ids=request_body.seq_ids  # type: ignore[call-arg]
            )
        return retval

    @router.post(
        "/retrieve/seq_distance_last_modified/{protocol_id}",
        operation_id="retrieve__seq_distance_last_modified",
        name="RetrieveSeqDistanceLastModified",
        description=command.RetrieveSeqDistanceLastModifiedCommand.__doc__,
    )
    async def retrieve__seq_distance_last_modified(
        user: registered_user_dependency,  # type: ignore[valid-type]
        protocol_id: UUID,
    ) -> datetime | None:
        """See router description."""
        try:
            retval: datetime | None = app.handle(
                command.RetrieveSeqDistanceLastModifiedCommand(
                    user=user,
                    protocol_id=protocol_id,
                )
            )
        except Exception as exception:
            handle_exception("d9e5f4a7", user, exception)  # type: ignore[call-arg]
        return retval

    @router.post(
        "/update/seq_distances",
        operation_id="update__seq_distances",
        name="UpdateSeqDistances",
        description=command.UpdateSeqDistancesCommand.__doc__,
    )
    async def update__seq_distances(
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: UpdateSeqDistancesRequestBody,
    ) -> list[model.CalculateSeqDistancesEtlResult]:
        """See router description."""
        try:
            retval: list[model.CalculateSeqDistancesEtlResult] = app.handle(
                command.UpdateSeqDistancesCommand(
                    user=user,
                    protocol_id=request_body.protocol_id,
                    limit=request_body.limit,
                    existing_chunk_size=request_body.existing_chunk_size,
                    use_numpy_allele_distance=request_body.use_numpy_allele_distance,
                )
            )
        except Exception as exception:
            handle_exception("a7b3c1d2", user, exception)  # type: ignore[call-arg]
        return retval

    @router.post(
        "/upload/samples",
        operation_id="upload__samples",
        name="UploadSamples",
        description=command.UploadSamplesCommand.__doc__,
    )
    async def upload__samples(
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: UploadSamplesRequestBody,
    ) -> model.SampleBatchUploadResult:
        """See router description."""
        try:
            retval: model.SampleBatchUploadResult = app.handle(
                command.UploadSamplesCommand(
                    user=user,
                    **request_body.model_dump(exclude={"user"}),
                )
            )
        except Exception as exception:
            handle_exception("f1d282b4", user, exception)  # type: ignore[call-arg]
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
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: RetrieveBestSeqPerSampleRequestBody,
    ) -> dict[UUID, UUID]:
        """See router description."""
        try:
            retval: dict[UUID, UUID] = app.handle(
                command.RetrieveBestSeqPerSampleCommand(
                    user=user,
                    protocol_ids=request_body.protocol_ids,
                    sample_ids=request_body.sample_ids,
                )
            )
        except Exception as exception:
            handle_exception("c3f7a9e1", user, exception, request_ids=request_body.sample_ids)  # type: ignore[call-arg]
        return retval

    @router.post(
        "/retrieve/best_seq_profile_per_sample",
        operation_id="retrieve__best_seq_profile_per_sample",
        name="RetrieveBestSeqProfilePerSample",
        description=command.RetrieveBestSeqProfilePerSampleCommand.__doc__,
    )
    async def retrieve__best_seq_profile_per_sample(
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: RetrieveBestSeqProfilePerSampleRequestBody,
    ) -> dict[UUID, UUID]:
        """See router description."""
        try:
            retval: dict[UUID, UUID] = app.handle(
                command.RetrieveBestSeqProfilePerSampleCommand(
                    user=user,
                    protocol_ids=request_body.protocol_ids,
                    sample_ids=request_body.sample_ids,
                )
            )
        except Exception as exception:
            handle_exception("e2b4d8f6", user, exception, request_ids=request_body.sample_ids)  # type: ignore[call-arg]
        return retval

    @router.post(
        "/retrieve/best_seq_classification_per_sample",
        operation_id="retrieve__best_seq_classification_per_sample",
        name="RetrieveBestSeqClassificationPerSample",
        description=command.RetrieveBestSeqClassificationPerSampleCommand.__doc__,
    )
    async def retrieve__best_seq_classification_per_sample(
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: RetrieveBestSeqClassificationPerSampleRequestBody,
    ) -> dict[UUID, UUID]:
        """See router description."""
        try:
            retval: dict[UUID, UUID] = app.handle(
                command.RetrieveBestSeqClassificationPerSampleCommand(
                    user=user,
                    protocol_ids=request_body.protocol_ids,
                    sample_ids=request_body.sample_ids,
                    ranking_strategy=request_body.ranking_strategy,
                    return_primary_category_id=request_body.return_primary_category_id,
                )
            )
        except Exception as exception:
            handle_exception("a6f1c3d9", user, exception, request_ids=request_body.sample_ids)  # type: ignore[call-arg]
        return retval

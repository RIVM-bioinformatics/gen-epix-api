"""Expose seqdb api.seq API adapters and request representations."""

from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Any, NoReturn, Self
from uuid import UUID

from fastapi import APIRouter, FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, model_validator

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain.literal import (
    MAX_CODE_FIELD_LENGTH,
    MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
)
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.util import copy_model_field


class UploadSamplesRequestBody(command.UploadSamplesCommand):
    """Docstring assigned programmatically."""

    __doc__ = command.UploadSamplesCommand.__doc__

    # TODO: SampleBatchForUpload.samples should be restricted in length as well as any other subfields to harden against large payloads.
    sample_batch: model.SampleBatchForUpload = copy_model_field(
        command.UploadSamplesCommand, "sample_batch"
    )
    calculate_distances: bool = copy_model_field(
        command.UploadSamplesCommand, "calculate_distances"
    )
    seq_distance_last_modified_at: datetime | None = copy_model_field(
        command.UploadSamplesCommand, "seq_distance_last_modified_at"
    )
    # TODO: is a temporary option, to be removed once the memory handling is handled properly server-side
    existing_chunk_size: int | None = copy_model_field(
        command.UploadSamplesCommand, "existing_chunk_size"
    )
    # TODO: is a temporary option, to be removed once the numpy-vectorised ALLELE distance calculation (or any other that is eventually chosen) is fully validated and deployed. It is intended to allow testing of the new implementation without affecting existing behaviour.
    use_numpy_allele_distance: bool = copy_model_field(
        command.UploadSamplesCommand, "use_numpy_allele_distance"
    )


class CalculatePhylogeneticTreeRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.CalculatePhylogeneticTreeCommand.__doc__

    protocol_id: UUID = copy_model_field(
        command.CalculatePhylogeneticTreeCommand, "protocol_id"
    )
    tree_algorithm: enum.TreeAlgorithm = copy_model_field(
        command.CalculatePhylogeneticTreeCommand, "tree_algorithm"
    )
    seq_profile_ids: list[UUID] = copy_model_field(
        command.CalculatePhylogeneticTreeCommand,
        "seq_profile_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    leaf_names: list[str] | None = copy_model_field(
        command.CalculatePhylogeneticTreeCommand,
        "leaf_names",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveSimilarProfilesRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveSimilarProfilesCommand.__doc__

    protocol_id: UUID = copy_model_field(
        command.RetrieveSimilarProfilesCommand, "protocol_id"
    )
    profile_ids: list[UUID] = copy_model_field(
        command.RetrieveSimilarProfilesCommand,
        "profile_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    max_distance: float = copy_model_field(
        command.RetrieveSimilarProfilesCommand, "max_distance"
    )


class UpdateSeqDistancesRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.UpdateSeqDistancesCommand.__doc__
    protocol_id: UUID = copy_model_field(
        command.UpdateSeqDistancesCommand, "protocol_id"
    )
    # TODO: remove max_new_profiles usage and replace by limit
    max_new_profiles: int | None = copy_model_field(
        command.UpdateSeqDistancesCommand, "limit"
    )
    limit: int | None = copy_model_field(command.UpdateSeqDistancesCommand, "limit")
    existing_chunk_size: int | None = copy_model_field(
        command.UpdateSeqDistancesCommand, "existing_chunk_size"
    )
    use_numpy_allele_distance: bool = copy_model_field(
        command.UpdateSeqDistancesCommand, "use_numpy_allele_distance"
    )

    # TODO: remove max_new_profiles usage and replace by limit
    @model_validator(mode="after")
    def validate_limit(self) -> Self:
        """Normalize the deprecated maximum-profile field into ``limit``."""
        if self.limit is None:
            self.limit = self.max_new_profiles
        return self


class RetrieveSamplesByIdsRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveSamplesByIdCommand.__doc__
    sample_ids: list[UUID] = copy_model_field(
        command.RetrieveSamplesByIdCommand,
        "sample_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveSampleIdentifiersByIdsRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveSampleIdentifiersByIdCommand.__doc__
    sample_ids: list[UUID] = copy_model_field(
        command.RetrieveSampleIdentifiersByIdCommand,
        "sample_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveSeqDistancesBySeqProfilesRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveSeqDistancesBySeqProfilesCommand.__doc__

    seq_profile_ids: list[UUID] = copy_model_field(
        command.RetrieveSeqDistancesBySeqProfilesCommand,
        "seq_profile_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    protocol_id: UUID = copy_model_field(
        command.RetrieveSeqDistancesBySeqProfilesCommand, "protocol_id"
    )


class RetrieveSeqFastaRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveSeqFastaCommand.__doc__

    seq_ids: list[UUID] = copy_model_field(
        command.RetrieveSeqFastaCommand,
        "seq_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    wrap: int = copy_model_field(command.RetrieveSeqFastaCommand, "wrap")
    file_name: str = Field(
        description="The desired filename for the FASTA download.",
        max_length=MAX_CODE_FIELD_LENGTH,
    )


class ConvertSeqFormatRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.ConvertSeqFormatCommand.__doc__

    seq_ids: list[UUID] = copy_model_field(
        command.ConvertSeqFormatCommand,
        "seq_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    from_format: enum.SeqFormat = copy_model_field(
        command.ConvertSeqFormatCommand, "from_format"
    )
    to_format: enum.SeqFormat = copy_model_field(
        command.ConvertSeqFormatCommand, "to_format"
    )


class RetrieveBestSeqPerSampleRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveBestSeqPerSampleCommand.__doc__

    protocol_ids: set[UUID] | None = copy_model_field(
        command.RetrieveBestSeqPerSampleCommand,
        "protocol_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    sample_ids: set[UUID] | None = copy_model_field(
        command.RetrieveBestSeqPerSampleCommand,
        "sample_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveBestSeqProfilePerSampleRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveBestSeqProfilePerSampleCommand.__doc__

    protocol_ids: set[UUID] = copy_model_field(
        command.RetrieveBestSeqProfilePerSampleCommand,
        "protocol_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    sample_ids: set[UUID] | None = copy_model_field(
        command.RetrieveBestSeqProfilePerSampleCommand,
        "sample_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveBestSeqClassificationPerSampleRequestBody(PydanticBaseModel):
    """Docstring assigned programmatically."""

    __doc__ = command.RetrieveBestSeqClassificationPerSampleCommand.__doc__

    protocol_ids: set[UUID] = copy_model_field(
        command.RetrieveBestSeqClassificationPerSampleCommand,
        "protocol_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    sample_ids: set[UUID] | None = copy_model_field(
        command.RetrieveBestSeqClassificationPerSampleCommand,
        "sample_ids",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    ranking_strategy: enum.SeqClassificationRankingStrategy = copy_model_field(
        command.RetrieveBestSeqClassificationPerSampleCommand, "ranking_strategy"
    )
    return_primary_category_id: bool = copy_model_field(
        command.RetrieveBestSeqClassificationPerSampleCommand,
        "return_primary_category_id",
    )


def _handle_seq_command(
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn],
    error_code: str,
    user: Any,
    cmd: Any,
    request_ids: Any | None = None,
) -> Any:
    """Dispatch one SeqDB command and forward failures to the API adapter."""
    try:
        return app.handle(cmd)
    except Exception as exception:
        if request_ids is None:
            handle_exception(error_code, user, exception)
        else:
            handle_exception(
                error_code, user, exception, request_ids=request_ids  # type: ignore[call-arg]
            )


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
        retval: model.PhylogeneticTree = _handle_seq_command(
            app,
            handle_exception,
            "dc71bce0",
            user,
            command.CalculatePhylogeneticTreeCommand(
                user=user,
                protocol_id=request_body.protocol_id,
                tree_algorithm=request_body.tree_algorithm,
                seq_profile_ids=request_body.seq_profile_ids,
                leaf_names=request_body.leaf_names,
            ),
            request_ids=request_body.seq_profile_ids,
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
        retval: list[UUID] = _handle_seq_command(
            app,
            handle_exception,
            "b1c8e5d9",
            user,
            command.RetrieveSimilarProfilesCommand(
                user=user,
                protocol_id=request_body.protocol_id,
                profile_ids=request_body.profile_ids,
                max_distance=request_body.max_distance,
            ),
            request_ids=request_body.profile_ids,
        )
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
        retval: model.SampleQueryResult = _handle_seq_command(
            app,
            handle_exception,
            "8f3a1c7d",
            user,
            command.RetrieveSamplesByQueryCommand(
                user=user,
                sample_query=request_body,
            ),
        )
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
        retval: list[model.FullSample] = _handle_seq_command(
            app,
            handle_exception,
            "ac218f73",
            user,
            command.RetrieveSamplesByIdCommand(
                user=user,
                sample_ids=request_body.sample_ids,
            ),
            request_ids=request_body.sample_ids,
        )
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
        retval: list[model.SampleIdentifier] = _handle_seq_command(
            app,
            handle_exception,
            "b3f91a2e",
            user,
            command.RetrieveSampleIdentifiersByIdCommand(
                user=user,
                sample_ids=request_body.sample_ids,
            ),
            request_ids=request_body.sample_ids,
        )
        return retval

    @router.post(
        "/retrieve/seq_distances_by_seq_profiles",
        operation_id="retrieve__seq_distances_by_seq_profiles",
        name="RetrieveSeqDistancesBySeqProfiles",
        description=command.RetrieveSeqDistancesBySeqProfilesCommand.__doc__,
    )
    async def retrieve__seq_distances_by_seq_profiles(
        user: registered_user_dependency,  # type: ignore[valid-type]
        request_body: RetrieveSeqDistancesBySeqProfilesRequestBody,
    ) -> list[model.SeqDistance]:
        """See router description."""
        try:
            retval: list[model.SeqDistance] = app.handle(
                command.RetrieveSeqDistancesBySeqProfilesCommand(
                    user=user,
                    seq_profile_ids=request_body.seq_profile_ids,
                    protocol_id=request_body.protocol_id,
                )
            )
        except Exception as exception:
            handle_exception("f1c2d3e4", user, exception, request_ids=request_body.seq_profile_ids)  # type: ignore[call-arg]
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
        fasta_iterable: Iterable[str] = _handle_seq_command(
            app,
            handle_exception,
            "e4f3b8c1",
            user,
            command.RetrieveSeqFastaCommand(
                user=user,
                seq_ids=request_body.seq_ids,
                wrap=request_body.wrap,
            ),
        )

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
        retval: list[UUID] = _handle_seq_command(
            app,
            handle_exception,
            "b8c4d2e1",
            user,
            command.ConvertSeqFormatCommand(
                user=user,
                seq_ids=request_body.seq_ids,
                from_format=request_body.from_format,
                to_format=request_body.to_format,
            ),
            request_ids=request_body.seq_ids,
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
        retval: datetime | None = _handle_seq_command(
            app,
            handle_exception,
            "d9e5f4a7",
            user,
            command.RetrieveSeqDistanceLastModifiedCommand(
                user=user,
                protocol_id=protocol_id,
            ),
        )
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
        retval: list[model.CalculateSeqDistancesEtlResult] = _handle_seq_command(
            app,
            handle_exception,
            "a7b3c1d2",
            user,
            command.UpdateSeqDistancesCommand(
                user=user,
                protocol_id=request_body.protocol_id,
                limit=request_body.limit,
                existing_chunk_size=request_body.existing_chunk_size,
                use_numpy_allele_distance=request_body.use_numpy_allele_distance,
            ),
        )
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
        retval: model.SampleBatchUploadResult = _handle_seq_command(
            app,
            handle_exception,
            "f1d282b4",
            user,
            command.UploadSamplesCommand(
                user=user,
                **request_body.model_dump(exclude={"user"}),
            ),
        )
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
        retval: dict[UUID, UUID] = _handle_seq_command(
            app,
            handle_exception,
            "c3f7a9e1",
            user,
            command.RetrieveBestSeqPerSampleCommand(
                user=user,
                protocol_ids=request_body.protocol_ids,
                sample_ids=request_body.sample_ids,
            ),
            request_ids=request_body.sample_ids,
        )
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
        retval: dict[UUID, UUID] = _handle_seq_command(
            app,
            handle_exception,
            "e2b4d8f6",
            user,
            command.RetrieveBestSeqProfilePerSampleCommand(
                user=user,
                protocol_ids=request_body.protocol_ids,
                sample_ids=request_body.sample_ids,
            ),
            request_ids=request_body.sample_ids,
        )
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
        retval: dict[UUID, UUID] = _handle_seq_command(
            app,
            handle_exception,
            "a6f1c3d9",
            user,
            command.RetrieveBestSeqClassificationPerSampleCommand(
                user=user,
                protocol_ids=request_body.protocol_ids,
                sample_ids=request_body.sample_ids,
                ranking_strategy=request_body.ranking_strategy,
                return_primary_category_id=request_body.return_primary_category_id,
            ),
            request_ids=request_body.sample_ids,
        )
        return retval

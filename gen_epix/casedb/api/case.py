import base64
from collections.abc import Callable
from typing import Annotated, Any, NoReturn, cast
from uuid import UUID

from fastapi import APIRouter, FastAPI, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_serializer

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.api.exc import handle_command
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.fastapp.services.auth.service import AuthService
from gen_epix.filter.datetime_range import TypedDatetimeRangeFilter
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model
from gen_epix.util import copy_model_field


class UpdateCaseTypeSetCaseTypesRequestBody(PydanticBaseModel):
    case_type_set_members: list[model.CaseTypeSetMember] = Field(
        description="The members of the CaseTypeSet."
    )


class UpdateColSetColsRequestBody(PydanticBaseModel):
    col_set_members: list[model.ColSetMember] = Field(
        description="The members of the ColSet."
    )


class CreateCaseSetRequestBody(PydanticBaseModel):
    case_set: model.CaseSet
    data_collection_ids: set[UUID] = Field(
        default_factory=set,
        description="The data collections in which the case set will be put initially",
    )
    case_ids: set[UUID] | None = Field(
        default=None, description="The cases to be added to the case set, if any."
    )


class RetrieveCaseRightsRequestBody(PydanticBaseModel):
    case_type_id: UUID = copy_model_field(
        command.RetrieveCaseRightsCommand, "case_type_id"
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrieveCaseRightsCommand, "case_ids"
    )


class RetrieveCasesByIdsRequestBody(PydanticBaseModel):
    case_type_id: UUID = copy_model_field(
        command.RetrieveCasesByIdCommand, "case_type_id"
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrieveCasesByIdCommand, "case_ids"
    )


class RetrieveCaseCohortLinksByCaseTypeRequestBody(PydanticBaseModel):
    case_type_id: UUID = copy_model_field(
        command.RetrieveCaseCohortLinksByCaseTypeCommand, "case_type_id"
    )


class RetrievePhylogeneticTreeRequestBody(PydanticBaseModel):
    case_type_id: UUID = copy_model_field(
        command.RetrievePhylogeneticTreeByCasesCommand, "case_type_id"
    )
    genetic_distance_col_id: UUID = copy_model_field(
        command.RetrievePhylogeneticTreeByCasesCommand,
        "genetic_distance_col_id",
    )
    tree_algorithm_code: enum.TreeAlgorithmType = copy_model_field(
        command.RetrievePhylogeneticTreeByCasesCommand, "tree_algorithm"
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrievePhylogeneticTreeByCasesCommand, "case_ids"
    )


class RetrieveSimilarCasesRequestBody(PydanticBaseModel):
    case_type_id: UUID = copy_model_field(
        command.RetrieveSimilarCasesCommand, "case_type_id"
    )
    max_distance: float = copy_model_field(
        command.RetrieveSimilarCasesCommand, "max_distance"
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrieveSimilarCasesCommand, "case_ids"
    )
    genetic_distance_col_id: UUID = copy_model_field(
        command.RetrieveSimilarCasesCommand, "genetic_distance_col_id"
    )


class RetrieveCaseTypeStatsRequestBody(PydanticBaseModel):
    case_type_ids: set[UUID] | None = Field(
        default=None,
        description="The CaseType IDs to retrieve stats for, if not all.",
    )
    datetime_range_filter: TypedDatetimeRangeFilter | None = Field(
        default=None,
        description="The datetime range to filter cases by, if any. The key attribute fo the filter should be left empty.",
    )


class RetrieveCaseSetStatsRequestBody(PydanticBaseModel):
    case_set_ids: set[UUID] = Field(
        description="The case set IDs to retrieve stats for, if not all.",
    )


class CreateFileForReadSetRequestBody(PydanticBaseModel):
    file_content: str = Field(
        description="The content of the file to create as base64 encoded bytes."
    )
    is_fwd: bool = Field(
        description="Whether the file is for the forward reads (True) or reverse reads (False).",
    )
    file_format: seqdb_enum.ReadsFileFormat = copy_model_field(
        command.CreateFileForReadSetCommand, "file_format"
    )
    file_compression: seqdb_enum.FileCompression = copy_model_field(
        command.CreateFileForReadSetCommand, "file_compression"
    )


class CreateFileForSeqRequestBody(PydanticBaseModel):
    file_content: str = Field(
        description="The content of the file to create as base64 encoded bytes."
    )
    file_format: seqdb_enum.SeqFileFormat = copy_model_field(
        command.CreateFileForSeqCommand, "file_format"
    )
    file_compression: seqdb_enum.FileCompression = copy_model_field(
        command.CreateFileForSeqCommand, "file_compression"
    )


class RefColValidationRulesResponseBody(PydanticBaseModel):
    """
    The additional validation rules that a RefCol instance must comply with.
    """

    valid_col_types_by_dim_type: dict[enum.DimType, set[enum.ColType]] = Field(
        default={enum.DimType[x.name]: set(x.value) for x in enum.DimColTypeSet},
        description="The RefCol.col_type values that are allowed depending on the RefCol.ref_dim.dim_type.",
    )

    @field_serializer("valid_col_types_by_dim_type")
    def serialize_valid_col_types_by_dim_type(
        self, value: dict[enum.DimType, set[enum.ColType]]
    ) -> dict[str, list[str]]:
        return {x.value: [z.value for z in y] for x, y in value.items()}


def create_case_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    assert handle_exception
    app_impl: AppImplDetails = app.impl
    registered_user_dependency = app_impl.registered_user_dependency

    # Specific endpoints - Case
    @router.put(
        "/case_type_sets/{case_type_set_id}/case_types",
        operation_id="case_type_sets__put__case_types",
        name="Update association between CaseTypeSet and CaseType",
        description=command.CaseTypeSetCaseTypeUpdateAssociationCommand.__doc__,
    )
    async def case_type_sets__put__case_types(
        user: registered_user_dependency,  # type: ignore
        case_type_set_id: UUID,
        request_body: UpdateCaseTypeSetCaseTypesRequestBody,
    ) -> list[model.CaseSetMember]:
        return cast(
            list[model.CaseSetMember],
            handle_command(
                app=app,
                user=user,
                exception_code="fbe272b9",
                input_handle_exception=handle_exception,
                input_command=command.CaseTypeSetCaseTypeUpdateAssociationCommand(
                    user=user,
                    obj_id1=case_type_set_id,
                    association_objs=request_body.case_type_set_members,
                    return_id=False,
                ),
            ),
        )

    @router.put(
        "/col_sets/{col_set_id}/cols",
        operation_id="col_sets__put__cols",
        name="Update association between ColSet and Col",
        description=command.ColSetColUpdateAssociationCommand.__doc__,
    )
    async def col_sets__put__cols(
        user: registered_user_dependency,  # type: ignore
        col_set_id: UUID,
        request_body: UpdateColSetColsRequestBody,
    ) -> list[model.ColSetMember]:
        return cast(
            list[model.ColSetMember],
            handle_command(
                app=app,
                user=user,
                exception_code="ab010768",
                input_handle_exception=handle_exception,
                input_command=command.ColSetColUpdateAssociationCommand(
                    user=user,
                    obj_id1=col_set_id,
                    association_objs=request_body.col_set_members,
                    return_id=False,
                ),
            ),
        )

    @router.get(
        "/complete_case_types",
        operation_id="complete_case_types__get_one",
        name="Retrieve complete CaseType",
        description=command.RetrieveCompleteCaseTypeCommand.__doc__,
    )
    async def complete_case_types__get_one(
        user: registered_user_dependency,  # type: ignore
        case_type_id: UUID,
    ) -> model.CompleteCaseType:
        return cast(
            model.CompleteCaseType,
            handle_command(
                app=app,
                user=user,
                exception_code="c6c17125",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveCompleteCaseTypeCommand(
                    user=user, case_type_id=case_type_id
                ),
            ),
        )

    @router.post(
        "/upload/cases",
        operation_id="upload__cases",
        name="Upload cases",
        description=command.UploadCasesCommand.__doc__,
    )
    async def upload__cases(
        user: registered_user_dependency,  # type: ignore
        cmd: command.UploadCasesCommand,
    ) -> model.CaseBatchUploadResult:
        cmd.user = user
        return cast(
            model.CaseBatchUploadResult,
            handle_command(
                app=app,
                user=user,
                exception_code="b413ab76",
                input_handle_exception=handle_exception,
                input_command=cmd,
            ),
        )

    @router.post(
        "/create/case_set",
        operation_id="create__case_set",
        name="Create case set",
        description=command.CreateCaseSetCommand.__doc__,
    )
    async def create__case_set(
        user: registered_user_dependency,  # type: ignore
        request_body: CreateCaseSetRequestBody,
    ) -> model.CaseSet:
        return cast(
            model.CaseSet,
            handle_command(
                app=app,
                user=user,
                exception_code="c39c42f9",
                input_handle_exception=handle_exception,
                input_command=command.CreateCaseSetCommand(
                    user=user,
                    case_set=request_body.case_set,
                    data_collection_ids=request_body.data_collection_ids,
                    case_ids=request_body.case_ids,
                ),
            ),
        )

    @router.post(
        "/retrieve/case_type_stats",
        operation_id="retrieve__case_type_stats",
        name="Retrieve CaseType statistics",
        description=command.RetrieveCaseStatsCommand.__doc__,
    )
    async def retrieve__case_type_stats(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveCaseTypeStatsRequestBody,
    ) -> list[model.CaseStats]:
        return cast(
            list[model.CaseStats],
            handle_command(
                app=app,
                user=user,
                exception_code="80c99f53",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveCaseStatsCommand(
                    user=user,
                    case_type_ids=request_body.case_type_ids,
                    datetime_range_filter=request_body.datetime_range_filter,
                ),
            ),
        )

    @router.post(
        "/retrieve/case_set_stats",
        operation_id="retrieve__case_set_stats",
        name="Retrieve case set statistics",
        description=command.RetrieveCaseStatsCommand.__doc__,
    )
    async def retrieve__case_set_stats(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveCaseSetStatsRequestBody,
    ) -> list[model.CaseStats]:
        return cast(
            list[model.CaseStats],
            handle_command(
                app=app,
                user=user,
                exception_code="be54843e",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveCaseStatsCommand(
                    user=user,
                    case_set_ids=(
                        None
                        if not request_body.case_set_ids
                        else list(request_body.case_set_ids)
                    ),
                ),
            ),
        )

    @router.post(
        "/retrieve/case_ids_by_query",
        operation_id="retrieve__case_ids_by_query",
        name="Retrieve case IDs by query",
        description=command.RetrieveCasesByQueryCommand.__doc__,
    )
    async def retrieve__case_ids_by_query(
        user: registered_user_dependency,  # type: ignore
        request_body: model.CaseQuery,
    ) -> model.CaseQueryResult:
        return cast(
            model.CaseQueryResult,
            handle_command(
                app=app,
                user=user,
                exception_code="a8f773fe",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveCasesByQueryCommand(
                    user=user,
                    case_query=request_body,
                ),
            ),
        )

    @router.post(
        "/retrieve/case_cohort_links_by_case_type",
        operation_id="retrieve__case_cohort_links_by_case_type",
        name="Retrieve case cohort IDs by case type",
        description=command.RetrieveCaseCohortLinksByCaseTypeCommand.__doc__,
    )
    async def retrieve__case_cohort_links_by_case_type(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveCaseCohortLinksByCaseTypeRequestBody,
    ) -> list[model.CaseCohortLink]:
        return cast(
            list[model.CaseCohortLink],
            handle_command(
                app=app,
                user=user,
                exception_code="b3c912d7",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveCaseCohortLinksByCaseTypeCommand(
                    user=user,
                    case_type_id=request_body.case_type_id,
                ),
            ),
        )

    @router.post(
        "/retrieve/cases_by_ids",
        operation_id="retrieve__cases_by_ids",
        name="Retrieve cases by IDs",
        description=command.RetrieveCasesByIdCommand.__doc__,
    )
    async def retrieve__cases_by_ids(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveCasesByIdsRequestBody,
    ) -> list[model.Case]:
        return cast(
            list[model.Case],
            handle_command(
                app=app,
                user=user,
                exception_code="f6d423fe",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveCasesByIdCommand(
                    user=user,
                    case_type_id=request_body.case_type_id,
                    case_ids=request_body.case_ids,
                ),
            ),
        )

    @router.post(
        "/retrieve/case_rights",
        operation_id="retrieve__case_rights",
        name="Retrieve case rights",
        description=command.RetrieveCaseRightsCommand.__doc__,
    )
    async def retrieve__case_rights(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveCaseRightsRequestBody,
    ) -> list[model.CaseRights]:
        return cast(
            list[model.CaseRights],
            handle_command(
                app=app,
                user=user,
                exception_code="c6f4b3c2",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveCaseRightsCommand(
                    user=user,
                    case_type_id=request_body.case_type_id,
                    case_ids=request_body.case_ids,
                ),
            ),
        )

    @router.post(
        "/retrieve/case_set_rights",
        operation_id="retrieve__case_set_rights",
        name="Retrieve case set rights",
        description=command.RetrieveCaseSetRightsCommand.__doc__,
    )
    async def retrieve__case_set_rights(
        user: registered_user_dependency,  # type: ignore
        request_body: list[UUID],
    ) -> list[model.CaseSetRights]:
        return cast(
            list[model.CaseSetRights],
            handle_command(
                app=app,
                user=user,
                exception_code="b9c49fe1",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveCaseSetRightsCommand(
                    user=user,
                    case_set_ids=request_body,
                ),
            ),
        )

    @router.post(
        "/calculate/phylogenetic_tree",
        operation_id="retrieve__phylogenetic_tree",
        name="Retrieve phylogenetic tree",
        description=command.RetrievePhylogeneticTreeByCasesCommand.__doc__,
    )
    async def retrieve__phylogenetic_tree(
        user: registered_user_dependency, request_body: RetrievePhylogeneticTreeRequestBody  # type: ignore
    ) -> model.PhylogeneticTree:
        return cast(
            model.PhylogeneticTree,
            handle_command(
                app=app,
                user=user,
                exception_code="45219a88",
                input_handle_exception=handle_exception,
                input_command=command.RetrievePhylogeneticTreeByCasesCommand(
                    user=user,
                    case_type_id=request_body.case_type_id,
                    genetic_distance_col_id=request_body.genetic_distance_col_id,
                    tree_algorithm=request_body.tree_algorithm_code,
                    case_ids=request_body.case_ids,
                ),
            ),
        )

    @router.post(
        "/retrieve/similar_cases",
        operation_id="retrieve__similar_cases",
        name="Retrieve similar cases",
        description=command.RetrieveSimilarCasesCommand.__doc__,
    )
    async def retrieve__similar_cases(
        user: registered_user_dependency, request_body: RetrieveSimilarCasesRequestBody  # type: ignore
    ) -> list[UUID]:
        return cast(
            list[UUID],
            handle_command(
                app=app,
                user=user,
                exception_code="e4c2e1b2",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveSimilarCasesCommand(
                    user=user,
                    case_type_id=request_body.case_type_id,
                    max_distance=request_body.max_distance,
                    case_ids=request_body.case_ids,
                    genetic_distance_col_id=request_body.genetic_distance_col_id,
                ),
            ),
        )

    @router.post(
        "/retrieve/genetic_sequence/fasta",
        operation_id="retrieve__genetic_sequence__fasta",
        name="Retrieve genetic sequence by case, in fasta format and streamed",
        description=command.RetrieveGeneticSequenceFastaByCaseCommand.__doc__,
    )
    async def retrieve__genetic_sequence_fasta(
        token: Annotated[str, Form()],
        case_type_id: Annotated[UUID, Form()],
        genetic_sequence_col_id: Annotated[UUID, Form()],
        case_ids: Annotated[list[UUID], Form()],
        file_name: Annotated[str, Form()],
    ) -> StreamingResponse:
        user: model.User | None = None
        app_impl: AppImplDetails = app.impl
        try:
            auth_service: AuthService = app_impl.services[
                enum.ServiceType.AUTH
            ]  # type: ignore[assignment]
            user = await auth_service.get_existing_user_from_token(token=token)  # type: ignore[assignment]
            fasta_iterable = app.handle(
                command.RetrieveGeneticSequenceFastaByCaseCommand(
                    user=user,
                    case_type_id=case_type_id,
                    genetic_sequence_col_id=(genetic_sequence_col_id),
                    case_ids=case_ids,
                )
            )
        except Exception as exception:
            handle_exception(  # type: ignore[call-arg]
                "d4c2e1b1",
                user,
                exception,
            )

        return StreamingResponse(
            fasta_iterable,
            media_type="application/x-fasta",
            headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
        )

    @router.post(
        "/create_file_for_read_set/{case_id}/{col_id}",
        operation_id="create_file_for_read_set",
        name="Create file for reads set",
        description=command.CreateFileForReadSetCommand.__doc__,
    )
    async def create_file_for_read_set(
        user: registered_user_dependency,  # type: ignore
        case_id: UUID,
        col_id: UUID,
        request_body: CreateFileForReadSetRequestBody,
    ) -> UUID:
        return cast(
            UUID,
            handle_command(
                app=app,
                user=user,
                exception_code="d3f4e2b1",
                input_handle_exception=handle_exception,
                input_command=command.CreateFileForReadSetCommand(
                    user=user,
                    file_content=base64.b64decode(request_body.file_content),
                    case_id=case_id,
                    col_id=col_id,
                    is_fwd=request_body.is_fwd,
                ),
            ),
        )

    @router.post(
        "/create_file_for_seq/{case_id}/{col_id}",
        operation_id="create_file_for_seq",
        name="Create file for sequence",
        description=command.CreateFileForSeqCommand.__doc__,
    )
    async def create_file_for_seq(
        user: registered_user_dependency,  # type: ignore
        case_id: UUID,
        col_id: UUID,
        request_body: CreateFileForSeqRequestBody,
    ) -> UUID:
        return cast(
            UUID,
            handle_command(
                app=app,
                user=user,
                exception_code="b5c6d7e8",
                input_handle_exception=handle_exception,
                input_command=command.CreateFileForSeqCommand(
                    user=user,
                    file_content=base64.b64decode(request_body.file_content),
                    case_id=case_id,
                    col_id=col_id,
                ),
            ),
        )

    @router.get(
        "/retrieve/sequencing_protocols",
        operation_id="retrieve__sequencing_protocols",
        name="Retrieve sequencing protocols",
        description=command.RetrieveProtocolsCommand.__doc__,
    )
    async def retrieve__sequencing_protocols(
        user: registered_user_dependency,  # type: ignore
    ) -> list[seqdb_model.Protocol]:
        return cast(
            list[seqdb_model.Protocol],
            handle_command(
                app=app,
                user=user,
                exception_code="e7f8a9b0",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveProtocolsCommand(
                    user=user,
                    protocol_type=seqdb_enum.ProtocolType.SEQUENCING,
                ),
            ),
        )

    @router.get(
        "/retrieve/assembly_protocols",
        operation_id="retrieve__assembly_protocols",
        name="Retrieve assembly protocols",
        description=command.RetrieveProtocolsCommand.__doc__,
    )
    async def retrieve__assembly_protocols(
        user: registered_user_dependency,  # type: ignore
    ) -> list[seqdb_model.Protocol]:
        return cast(
            list[seqdb_model.Protocol],
            handle_command(
                app=app,
                user=user,
                exception_code="c1d2e3f4",
                input_handle_exception=handle_exception,
                input_command=command.RetrieveProtocolsCommand(
                    user=user,
                    protocol_type=seqdb_enum.ProtocolType.ASSEMBLY,
                ),
            ),
        )

    @router.get(
        "/" + model.RefCol.ENTITY.snake_case_plural_name + "/validation_rules",
        operation_id=model.RefCol.ENTITY.snake_case_plural_name + "__validation_rules",
        name="RefCol validation rules",
        description=RefColValidationRulesResponseBody.__doc__,
    )
    async def get__ref_col__validation_rules(
        user: registered_user_dependency,  # type: ignore
    ) -> RefColValidationRulesResponseBody:
        try:
            retval = RefColValidationRulesResponseBody()
        except Exception as exception:
            handle_exception("f2a4b8c6", user, exception)
        return retval

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=enum.ServiceType.CASE,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )

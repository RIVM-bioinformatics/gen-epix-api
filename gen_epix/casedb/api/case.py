import base64
from collections.abc import Callable
from typing import Annotated, Any, NoReturn
from uuid import UUID

from fastapi import APIRouter, FastAPI, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_serializer, model_validator

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.fastapp.services.auth.service import AuthService
from gen_epix.filter.datetime_range import TypedDatetimeRangeFilter
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.util import copy_model_field


class UpdateCaseTypeSetCaseTypesRequestBody(PydanticBaseModel):
    case_type_set_members: list[model.CaseTypeSetMember] = Field(
        description="The members of the case type set."
    )


class UpdateCaseTypeColSetCaseTypeColsRequestBody(PydanticBaseModel):
    case_type_col_set_members: list[model.CaseTypeColSetMember] = Field(
        description="The members of the case type col set."
    )


class ValidateCasesRequestBody(PydanticBaseModel):
    case_type_id: UUID = copy_model_field(command.ValidateCasesCommand, "case_type_id")
    created_in_data_collection_id: UUID = copy_model_field(
        command.ValidateCasesCommand, "created_in_data_collection_id"
    )
    data_collection_ids: set[UUID] = copy_model_field(
        command.ValidateCasesCommand, "data_collection_ids"
    )
    is_update: bool = copy_model_field(command.ValidateCasesCommand, "is_update")
    cases_set: model.CasesSetForUpload = copy_model_field(
        command.ValidateCasesCommand, "cases_set"
    )


class UploadCasesRequestBody(PydanticBaseModel):
    case_type_id: UUID = copy_model_field(command.UploadCasesCommand, "case_type_id")
    created_in_data_collection_id: UUID = copy_model_field(
        command.UploadCasesCommand, "created_in_data_collection_id"
    )
    data_collection_ids: set[UUID] = copy_model_field(
        command.UploadCasesCommand, "data_collection_ids"
    )
    is_update: bool = copy_model_field(command.UploadCasesCommand, "is_update")
    cases_set: model.CasesSetForUpload = copy_model_field(
        command.UploadCasesCommand, "cases_set"
    )


class CreateCaseSetRequestBody(PydanticBaseModel):
    case_set: model.CaseSet
    data_collection_ids: set[UUID] = Field(
        default=set(),
        description="The data collections in which the case set will be put initially",
    )
    case_ids: set[UUID] | None = Field(
        default=None, description="The cases to be added to the case set, if any."
    )


class RetrieveOrganizationContactRequestBody(PydanticBaseModel):
    organization_ids: list[UUID] | None = Field(
        default=None, description="The organization IDs to retrieve contacts for."
    )
    site_ids: list[UUID] | None = Field(
        default=None, description="The site IDs to retrieve contacts for."
    )
    contact_ids: list[UUID] | None = Field(
        default=None, description="The contact IDs to retrieve contacts for."
    )
    props: dict[str, Any] = Field(
        default_factory=dict, description="Additional properties for the request."
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Any:
        if (
            sum(
                [
                    self.organization_ids is not None,
                    self.site_ids is not None,
                    self.contact_ids is not None,
                ]
            )
            != 1
        ):
            raise ValueError(
                "Exactly one of organization_ids, site_ids or contact_ids must be "
                "provided"
            )
        return self


class RetrieveCasesByIdsRequestBody(PydanticBaseModel):
    case_type_id: UUID = copy_model_field(
        command.RetrieveCasesByIdCommand, "case_type_id"
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrieveCasesByIdCommand, "case_ids"
    )


class RetrievePhylogeneticTreeRequestBody(PydanticBaseModel):
    genetic_distance_case_type_col_id: UUID = copy_model_field(
        command.RetrievePhylogeneticTreeByCasesCommand,
        "genetic_distance_case_type_col_id",
    )
    tree_algorithm_code: enum.TreeAlgorithmType = copy_model_field(
        command.RetrievePhylogeneticTreeByCasesCommand, "tree_algorithm"
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrievePhylogeneticTreeByCasesCommand, "case_ids"
    )


class RetrieveGeneticSequenceRequestBody(PydanticBaseModel):
    genetic_sequence_case_type_col_id: UUID = copy_model_field(
        command.RetrieveGeneticSequenceByCaseCommand,
        "genetic_sequence_case_type_col_id",
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrieveGeneticSequenceByCaseCommand, "case_ids"
    )


class RetrieveAlleleProfileRequestBody(PydanticBaseModel):
    genetic_sequence_case_type_col_id: UUID = copy_model_field(
        command.RetrieveGeneticSequenceByCaseCommand,
        "genetic_sequence_case_type_col_id",
    )
    case_ids: list[UUID] = copy_model_field(
        command.RetrieveGeneticSequenceByCaseCommand, "case_ids"
    )


class RetrieveCaseTypeStatsRequestBody(PydanticBaseModel):
    case_type_ids: set[UUID] | None = Field(
        default=None,
        description="The case type ids to retrieve stats for, if not all.",
    )
    datetime_range_filter: TypedDatetimeRangeFilter | None = Field(
        default=None,
        description="The datetime range to filter cases by, if any. The key attribute fo the filter should be left empty.",
    )


class RetrieveCaseSetStatsRequestBody(PydanticBaseModel):
    case_set_ids: set[UUID] | None = Field(
        default=None,
        description="The case set ids to retrieve stats for, if not all.",
    )


class CreateFileForForReadSetRequestBody(PydanticBaseModel):
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


class ColValidationRulesResponseBody(PydanticBaseModel):
    """
    The additional validation rules that a Col instance must comply with.
    """

    valid_col_types_by_dim_type: dict[enum.DimType, set[enum.ColType]] = Field(
        default={enum.DimType[x.name]: set(x.value) for x in enum.DimColTypeSet},
        description="The Col.col_type values that are allowed depending on the Col.dim.dim_type.",
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
        try:
            cmd = command.CaseTypeSetCaseTypeUpdateAssociationCommand(
                user=user,
                obj_id1=case_type_set_id,
                association_objs=request_body.case_type_set_members,
                props={"return_id": False},
            )
            retval: list[model.CaseSetMember] = app.handle(cmd)
        except Exception as exception:
            handle_exception("fbe272b9", user, exception)
        return retval

    @router.put(
        "/case_type_col_sets/{case_type_col_set_id}/case_type_cols",
        operation_id="case_type_col_sets__put__case_type_cols",
        name="Update association between CaseTypeColSet and CaseTypeCol",
        description=command.CaseTypeColSetCaseTypeColUpdateAssociationCommand.__doc__,
    )
    async def case_type_col_sets__put__case_type_cols(
        user: registered_user_dependency,  # type: ignore
        case_type_col_set_id: UUID,
        request_body: UpdateCaseTypeColSetCaseTypeColsRequestBody,
    ) -> list[model.CaseTypeColSetMember]:
        try:
            cmd = command.CaseTypeColSetCaseTypeColUpdateAssociationCommand(
                user=user,
                obj_id1=case_type_col_set_id,
                association_objs=request_body.case_type_col_set_members,
                props={"return_id": False},
            )
            retval: list[model.CaseTypeColSetMember] = app.handle(cmd)
        except Exception as exception:
            handle_exception("ab010768", user, exception)
        return retval

    @router.get(
        "/complete_case_types",
        operation_id="complete_case_types__get_one",
        name="Retrieve complete case type",
        description=command.RetrieveCompleteCaseTypeCommand.__doc__,
    )
    async def complete_case_types__get_one(
        user: registered_user_dependency,  # type: ignore
        case_type_id: UUID,
    ) -> model.CompleteCaseType:
        try:
            cmd = command.RetrieveCompleteCaseTypeCommand(
                user=user, case_type_id=case_type_id
            )
            retval: model.CompleteCaseType = app.handle(cmd)
        except Exception as exception:
            handle_exception("c6c17125", user, exception)
        return retval

    @router.post(
        "/validate/cases",
        operation_id="validate__cases",
        name="Validate cases",
        description=command.ValidateCasesCommand.__doc__,
    )
    async def validate__cases(
        user: registered_user_dependency,  # type: ignore
        request_body: ValidateCasesRequestBody,
    ) -> model.CaseValidationReport:
        try:
            cmd = command.ValidateCasesCommand(
                user=user,
                case_type_id=request_body.case_type_id,
                created_in_data_collection_id=request_body.created_in_data_collection_id,
                data_collection_ids=request_body.data_collection_ids,
                is_update=request_body.is_update,
                cases_set=request_body.cases_set,
            )
            retval: model.CaseValidationReport = app.handle(cmd)
        except Exception as exception:
            handle_exception("9f8e7d6c", user, exception)
        return retval

    @router.post(
        "/create/cases",
        operation_id="create__cases",
        name="Create cases",
        description=command.UploadCasesCommand.__doc__,
    )
    async def create__cases(
        user: registered_user_dependency,  # type: ignore
        request_body: UploadCasesRequestBody,
    ) -> list[model.Case]:
        try:
            cmd = command.UploadCasesCommand(
                user=user,
                case_type_id=request_body.case_type_id,
                created_in_data_collection_id=request_body.created_in_data_collection_id,
                data_collection_ids=request_body.data_collection_ids,
                is_update=request_body.is_update,
                cases_set=request_body.cases_set,
            )
            retval: list[model.Case] = app.handle(cmd)
        except Exception as exception:
            handle_exception("b413ab76", user, exception)
        return retval

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
        try:
            cmd = command.CreateCaseSetCommand(
                user=user,
                case_set=request_body.case_set,
                data_collection_ids=request_body.data_collection_ids,
                case_ids=request_body.case_ids,
            )
            retval: model.CaseSet = app.handle(cmd)
        except Exception as exception:
            handle_exception("c39c42f9", user, exception)
        return retval

    @router.post(
        "/retrieve/case_type_stats",
        operation_id="retrieve__case_type_stats",
        name="Retrieve case type statistics",
        description=command.RetrieveCaseTypeStatsCommand.__doc__,
    )
    async def retrieve__case_type_stats(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveCaseTypeStatsRequestBody,
    ) -> list[model.CaseTypeStat]:
        try:
            cmd = command.RetrieveCaseTypeStatsCommand(
                user=user,
                case_type_ids=request_body.case_type_ids,
                datetime_range_filter=request_body.datetime_range_filter,
            )
            retval: list[model.CaseTypeStat] = app.handle(cmd)
        except Exception as exception:
            handle_exception("80c99f53", user, exception)
        return retval

    @router.post(
        "/retrieve/case_set_stats",
        operation_id="retrieve__case_set_stats",
        name="Retrieve case set statistics",
        description=command.RetrieveCaseSetStatsCommand.__doc__,
    )
    async def retrieve__case_set_stats(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveCaseSetStatsRequestBody,
    ) -> list[model.CaseSetStat]:
        try:
            cmd = command.RetrieveCaseSetStatsCommand(
                user=user,
                case_set_ids=(
                    None
                    if not request_body.case_set_ids
                    else list(request_body.case_set_ids)
                ),
            )
            retval: list[model.CaseSetStat] = app.handle(cmd)
        except Exception as exception:
            handle_exception("be54843e", user, exception)
        return retval

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
        try:
            retval: model.CaseQueryResult = app.handle(
                command.RetrieveCasesByQueryCommand(
                    user=user,
                    case_query=request_body,
                )
            )
        except Exception as exception:
            handle_exception("a8f773fe", user, exception)
        return retval

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
        try:
            retval: list[model.Case] = app.handle(
                command.RetrieveCasesByIdCommand(
                    user=user,
                    case_type_id=request_body.case_type_id,
                    case_ids=request_body.case_ids,
                )
            )
        except Exception as exception:
            handle_exception("f6d423fe", user, exception)
        return retval

    @router.post(
        "/retrieve/case_rights",
        operation_id="retrieve__case_rights",
        name="Retrieve case rights",
        description=command.RetrieveCaseRightsCommand.__doc__,
    )
    async def retrieve__case_rights(
        user: registered_user_dependency,  # type: ignore
        request_body: list[UUID],
    ) -> list[model.CaseRights]:
        try:
            retval: list[model.CaseRights] = app.handle(
                command.RetrieveCaseRightsCommand(
                    user=user,
                    case_ids=request_body,
                )
            )
        except Exception as exception:
            handle_exception("c6f4b3c2", user, exception)
        return retval

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
        try:
            retval: list[model.CaseSetRights] = app.handle(
                command.RetrieveCaseSetRightsCommand(
                    user=user,
                    case_set_ids=request_body,
                )
            )
        except Exception as exception:
            handle_exception("b9c49fe1", user, exception)
        return retval

    @router.post(
        "/retrieve/organization_contact",
        operation_id="retrieve__organization_contact",
        name="Retrieve organization contact",
        description=command.RetrieveOrganizationContactCommand.__doc__,
    )
    async def retrieve__organization_contact(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveOrganizationContactRequestBody,
    ) -> list[model.Contact]:
        try:
            retval: list[model.Contact] = app.handle(
                command.RetrieveOrganizationContactCommand(
                    user=user,
                    organization_ids=request_body.organization_ids,
                    site_ids=request_body.site_ids,
                    contact_ids=request_body.contact_ids,
                    props=request_body.props,
                )
            )
        except Exception as exception:
            handle_exception(  # type:ignore[call-arg]
                "b8172f62",
                user,
                exception,
                request_ids=(request_body.organization_ids or [])
                + (request_body.site_ids or [])
                + (request_body.contact_ids or []),
            )
        return retval

    @router.post(
        "/retrieve/phylogenetic_tree",
        operation_id="retrieve__phylogenetic_tree",
        name="Retrieve phylogenetic tree",
        description=command.RetrievePhylogeneticTreeByCasesCommand.__doc__,
    )
    async def retrieve__phylogenetic_tree(
        user: registered_user_dependency, request_body: RetrievePhylogeneticTreeRequestBody  # type: ignore
    ) -> model.PhylogeneticTree:
        try:
            retval: model.PhylogeneticTree = app.handle(
                command.RetrievePhylogeneticTreeByCasesCommand(
                    user=user,
                    genetic_distance_case_type_col_id=request_body.genetic_distance_case_type_col_id,
                    tree_algorithm=request_body.tree_algorithm_code,
                    case_ids=request_body.case_ids,
                )
            )
        except Exception as exception:
            handle_exception(  # type:ignore[call-arg]
                "45219a88", user, exception, request_ids=request_body.case_ids
            )
        return retval

    @router.post(
        "/retrieve/genetic_sequence",
        operation_id="retrieve__genetic_sequence",
        name="Retrieve genetic sequence by case",
        description=command.RetrieveGeneticSequenceByCaseCommand.__doc__,
    )
    async def retrieve__genetic_sequence(
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveGeneticSequenceRequestBody,
    ) -> list[model.GeneticSequence]:
        try:
            retval: list[model.GeneticSequence] = app.handle(
                command.RetrieveGeneticSequenceByCaseCommand(
                    user=user,
                    genetic_sequence_case_type_col_id=request_body.genetic_sequence_case_type_col_id,
                    case_ids=request_body.case_ids,
                )
            )
        except Exception as exception:
            handle_exception(  # type:ignore[call-arg]
                "1238afb2", user, exception, request_ids=request_body.case_ids
            )
        return retval

    @router.post(
        "/retrieve/genetic_sequence/fasta",
        operation_id="retrieve__genetic_sequence__fasta",
        name="Retrieve genetic sequence by case, in fasta format and streamed",
        description=command.RetrieveGeneticSequenceFastaByCaseCommand.__doc__,
    )
    async def retrieve__genetic_sequence_fasta(
        token: Annotated[str, Form()],
        genetic_sequence_case_type_col_id: Annotated[UUID, Form()],
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
                    genetic_sequence_case_type_col_id=(
                        genetic_sequence_case_type_col_id
                    ),
                    case_ids=case_ids,
                )
            )
        except Exception as exception:
            handle_exception(  # type:ignore[call-arg]
                "d4c2e1b1",
                user,
                exception,
                request_ids=case_ids,
            )

        return StreamingResponse(
            fasta_iterable,
            media_type="application/x-fasta",
            headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
        )

    @router.post(
        "/retrieve/allele_profile",
        operation_id="retrieve__allele_profile",
        name="Retrieve allele profile",
        description=command.RetrieveAlleleProfileCommand.__doc__,
    )
    async def retrieve__allele_profile(
        user: registered_user_dependency, request_body: RetrieveAlleleProfileRequestBody  # type: ignore
    ) -> list[model.AlleleProfile]:
        try:
            retval: list[model.AlleleProfile] = app.handle(
                command.RetrieveAlleleProfileCommand(
                    user=user,
                    genetic_distance_case_type_col_id=request_body.genetic_sequence_case_type_col_id,
                    case_ids=request_body.case_ids,
                )
            )
        except Exception as exception:
            handle_exception(  # type:ignore[call-arg]
                "a4c03b54", user, exception, request_ids=request_body.case_ids
            )
        return retval

    @router.post(
        "/create_read_sets_for_cases",
        operation_id="create__read_sets_for_cases",
        name="Create reads sets for cases",
        description=command.CreateReadSetsForCasesCommand.__doc__,
    )
    async def create__read_sets_for_cases(
        user: registered_user_dependency,  # type: ignore
        read_sets: list[model.ReadSetForUpload],
    ) -> list[model.ReadSet]:
        try:
            created_read_sets: list[model.ReadSet] = app.handle(
                command.CreateReadSetsForCasesCommand(
                    user=user,
                    read_sets=read_sets,
                )
            )
        except Exception as exception:
            handle_exception("e3d4f5a6", user, exception)
        return created_read_sets

    @router.post(
        "/create_file_for_read_set/{case_id}/{case_type_col_id}",
        operation_id="create_file_for_read_set",
        name="Create file for reads set",
        description=command.CreateFileForReadSetCommand.__doc__,
    )
    async def create_file_for_read_set(
        user: registered_user_dependency,  # type: ignore
        case_id: UUID,
        case_type_col_id: UUID,
        request_body: CreateFileForForReadSetRequestBody,
    ) -> UUID:
        try:
            created_file_id: UUID = app.handle(
                command.CreateFileForReadSetCommand(
                    user=user,
                    file_content=base64.b64decode(request_body.file_content),
                    case_id=case_id,
                    case_type_col_id=case_type_col_id,
                    is_fwd=request_body.is_fwd,
                )
            )
        except Exception as exception:
            handle_exception("d3f4e2b1", user, exception)
        return created_file_id

    @router.post(
        "/create_seqs_for_cases",
        operation_id="create_seqs_for_cases",
        name="Create sequences for cases",
        description=command.CreateSeqsForCasesCommand.__doc__,
    )
    async def create_seqs_for_cases(
        user: registered_user_dependency,  # type: ignore
        case_seqs: list[model.SeqForUpload],
    ) -> list[model.Seq]:
        try:
            created_seqs: list[model.Seq] = app.handle(
                command.CreateSeqsForCasesCommand(
                    user=user,
                    case_seqs=case_seqs,
                )
            )
        except Exception as exception:
            handle_exception("a1b2c3d4", user, exception)
        return created_seqs

    @router.post(
        "/create_file_for_seq/{case_id}/{case_type_col_id}",
        operation_id="create_file_for_seq",
        name="Create file for sequence",
        description=command.CreateFileForSeqCommand.__doc__,
    )
    async def create_file_for_seq(
        user: registered_user_dependency,  # type: ignore
        case_id: UUID,
        case_type_col_id: UUID,
        request_body: CreateFileForSeqRequestBody,
    ) -> UUID:
        try:
            created_file_id: UUID = app.handle(
                command.CreateFileForSeqCommand(
                    user=user,
                    file_content=base64.b64decode(request_body.file_content),
                    case_id=case_id,
                    case_type_col_id=case_type_col_id,
                )
            )
        except Exception as exception:
            handle_exception("b5c6d7e8", user, exception)
        return created_file_id

    @router.get(
        "/retrieve/sequencing_protocols",
        operation_id="retrieve__sequencing_protocols",
        name="Retrieve sequencing protocols",
        description=command.RetrieveSequencingProtocolsCommand.__doc__,
    )
    async def retrieve__sequencing_protocols(
        user: registered_user_dependency,  # type: ignore
    ) -> list[model.SequencingProtocol]:
        try:
            retval: list[model.SequencingProtocol] = app.handle(
                command.RetrieveSequencingProtocolsCommand(
                    user=user,
                )
            )
        except Exception as exception:
            handle_exception("e7f8a9b0", user, exception)
        return retval

    @router.get(
        "/retrieve/assembly_protocols",
        operation_id="retrieve__assembly_protocols",
        name="Retrieve assembly protocols",
        description=command.RetrieveAssemblyProtocolsCommand.__doc__,
    )
    async def retrieve__assembly_protocols(
        user: registered_user_dependency,  # type: ignore
    ) -> list[model.AssemblyProtocol]:
        try:
            retval: list[model.AssemblyProtocol] = app.handle(
                command.RetrieveAssemblyProtocolsCommand(
                    user=user,
                )
            )
        except Exception as exception:
            handle_exception("c1d2e3f4", user, exception)
        return retval

    @router.get(
        "/" + model.Col.ENTITY.snake_case_plural_name + "/validation_rules",
        operation_id=model.Col.ENTITY.snake_case_plural_name + "__validation_rules",
        name="Col validation rules",
        description=ColValidationRulesResponseBody.__doc__,
    )
    async def get__col__validation_rules(
        user: registered_user_dependency,  # type: ignore
    ) -> ColValidationRulesResponseBody:
        try:
            retval = ColValidationRulesResponseBody()
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

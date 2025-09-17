from typing import Any, Callable, NoReturn, Self
from uuid import UUID

from fastapi import APIRouter, FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, model_validator

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.util import copy_model_field
from gen_epix.fastapp import App
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.filter.datetime_range import TypedDatetimeRangeFilter


class UpdateCaseTypeSetCaseTypesRequestBody(PydanticBaseModel):
    case_type_set_members: list[model.CaseTypeSetMember]


class UpdateCaseTypeColSetCaseTypeColsRequestBody(PydanticBaseModel):
    case_type_col_set_members: list[model.CaseTypeColSetMember]


class ValidateCasesRequestBody(PydanticBaseModel):
    case_type_id: UUID = copy_model_field(command.ValidateCasesCommand, "case_type_id")
    created_in_data_collection_id: UUID = copy_model_field(
        command.ValidateCasesCommand, "created_in_data_collection_id"
    )
    data_collection_ids: set[UUID] = copy_model_field(
        command.ValidateCasesCommand, "data_collection_ids"
    )
    is_update: bool = copy_model_field(command.ValidateCasesCommand, "is_update")
    cases: list[model.CaseForCreateUpdate] = copy_model_field(
        command.ValidateCasesCommand, "cases"
    )

    @model_validator(mode="after")
    def _validate_cases(self) -> Self:
        if self.created_in_data_collection_id in self.data_collection_ids:
            raise ValueError(
                "The created in data collection ID may not be in the additional data collection IDs."
            )
        if self.is_update and any(x.id is None for x in self.cases):
            raise ValueError("All cases must have an ID when updating")
        return self


class CreateCasesRequestBody(PydanticBaseModel):
    case_type_id: UUID = copy_model_field(command.CreateCasesCommand, "case_type_id")
    created_in_data_collection_id: UUID = copy_model_field(
        command.CreateCasesCommand, "created_in_data_collection_id"
    )
    data_collection_ids: set[UUID] = copy_model_field(
        command.CreateCasesCommand, "data_collection_ids"
    )
    is_update: bool = copy_model_field(command.CreateCasesCommand, "is_update")
    cases: list[model.CaseForCreateUpdate] = copy_model_field(
        command.CreateCasesCommand, "cases"
    )

    @model_validator(mode="after")
    def _validate_cases(self) -> Self:
        if self.created_in_data_collection_id in self.data_collection_ids:
            raise ValueError(
                "The created in data collection ID may not be in the additional data collection IDs."
            )
        if self.is_update and any(x.id is None for x in self.cases):
            raise ValueError("All cases must have an ID when updating")
        return self


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
    organization_ids: list[UUID] | None = None
    site_ids: list[UUID] | None = None
    contact_ids: list[UUID] | None = None
    props: dict[str, Any] = {}


class RetrievePhylogeneticTreeRequestBody(PydanticBaseModel):
    genetic_distance_case_type_col_id: UUID
    tree_algorithm_code: enum.TreeAlgorithmType
    case_ids: list[UUID]


class RetrieveGeneticSequenceRequestBody(PydanticBaseModel):
    genetic_sequence_case_type_col_id: UUID = Field(
        description="The case type column that contains the genetic sequences to retrieve.",
    )
    case_ids: list[UUID] = Field(
        description="The case ids to retrieve genetic sequences for.",
    )


class RetrieveGeneticSequenceFastaRequestBody(PydanticBaseModel):
    genetic_sequence_case_type_col_id: UUID = Field(
        description="The case type column that contains the genetic sequences to retrieve.",
    )
    case_ids: list[UUID] = Field(
        description="The case ids to retrieve genetic sequences for.",
    )
    file_name: str = Field(
        description="The desired filename for the FASTA download.",
    )


class RetrieveAlleleProfileRequestBody(PydanticBaseModel):
    sequence_ids: list[UUID]
    props: dict[str, Any] = {}


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


def create_case_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:
    assert handle_exception

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
                is_update=request_body.is_update,
                cases=request_body.cases,
                data_collection_ids=request_body.data_collection_ids,
            )
            retval: model.CaseValidationReport = app.handle(cmd)
        except Exception as exception:
            handle_exception("9f8e7d6c", user, exception)
        return retval

    @router.post(
        "/create/cases",
        operation_id="create__cases",
        name="Create cases",
        description=command.CreateCasesCommand.__doc__,
    )
    async def create__cases(
        user: registered_user_dependency,  # type: ignore
        request_body: CreateCasesRequestBody,
    ) -> list[model.Case]:
        try:
            cmd = command.CreateCasesCommand(
                user=user,
                cases=request_body.cases,
                data_collection_ids=request_body.data_collection_ids,
                case_type_id=request_body.case_type_id,
                created_in_data_collection_id=request_body.created_in_data_collection_id,
                is_update=request_body.is_update,
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
    ) -> list[UUID]:
        try:
            retval: list[UUID] = app.handle(
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
        request_body: list[UUID],
    ) -> list[model.Case]:
        try:
            retval: list[model.Case] = app.handle(
                command.RetrieveCasesByIdCommand(
                    user=user,
                    case_ids=request_body,
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
        user: registered_user_dependency,  # type: ignore
        request_body: RetrieveGeneticSequenceFastaRequestBody,
    ) -> StreamingResponse:
        try:
            fasta_iterable = app.handle(
                command.RetrieveGeneticSequenceFastaByCaseCommand(
                    user=user,
                    genetic_sequence_case_type_col_id=(
                        request_body.genetic_sequence_case_type_col_id
                    ),
                    case_ids=request_body.case_ids,
                )
            )
        except Exception as exception:
            handle_exception(  # type:ignore[call-arg]
                "d4c2e1b1",
                user,
                exception,
                request_ids=request_body.case_ids,
            )
            # TODO: next line should be deleted since handle_exception always raises (returns NoReturn)
            return StreamingResponse(iter(()), media_type="text/plain")

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
                    sequence_ids=request_body.sequence_ids,
                    props=request_body.props,
                )
            )
        except Exception as exception:
            handle_exception(  # type:ignore[call-arg]
                "a4c03b54", user, exception, request_ids=request_body.sequence_ids
            )
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

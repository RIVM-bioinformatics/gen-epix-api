import datetime

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.domain.service import BaseCaseService as DomainBaseCaseService
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.case_date import (
    case_service_calculate_case_date,
    case_service_get_case_date_case_type_col_mappers_from_cols,
)
from gen_epix.fastapp import CrudOperation


def case_service_create_cases(
    self: BaseCaseService, cmd: command.CreateCasesCommand
) -> list[model.Case] | None:
    # Special case: zero cases to be created
    if not cmd.cases:
        return []

    # Get case type and created_in data collection IDs
    case_type_id = cmd.case_type_id
    created_in_data_collection_id = cmd.created_in_data_collection_id

    # @ABAC: verify if case set or cases may be created in the given data collection(s)
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None
    is_allowed = case_abac.is_allowed(
        case_type_id,
        enum.CaseRight.ADD_CASE,
        True,
        created_in_data_collection_id=created_in_data_collection_id,
        tgt_data_collection_ids=cmd.data_collection_ids,
    )
    if not is_allowed:
        assert cmd.user is not None
        raise exc.UnauthorizedAuthError(
            f"User {cmd.user.id} is not allowed to create cases in the given data collection(s)"
        )

    # Convert cases for create update to cases
    # TODO: validate content and add derived values
    now = datetime.datetime.now()
    cases: list[model.Case] = [
        model.Case(
            id=x.id,
            case_type_id=cmd.case_type_id,
            subject_id=x.subject_id,
            created_in_data_collection_id=cmd.created_in_data_collection_id,
            case_date=now,
            content={y: z for y, z in x.content.items() if z is not None},
        )
        for x in cmd.cases
    ]

    # Get complete case type
    sub_cmd = command.RetrieveCompleteCaseTypeCommand(
        user=cmd.user, case_type_id=case_type_id
    )
    sub_cmd._policies.extend(cmd._policies)
    complete_case_type: model.CompleteCaseType = self.retrieve_complete_case_type(
        sub_cmd
    )

    # Create cases and case data collection links
    with self.repository.uow() as uow:
        # Validate case data
        case_validation_report = self.validate_cases(cmd)
        for validated_case in case_validation_report.validated_cases:
            if any(
                x.data_rule in enum.CaseColDataRuleSet.PREVENTS_UPLOAD.value
                for x in validated_case.data_issues
            ):
                raise exc.InvalidArgumentsError(
                    f"Some cases have invalid data. None will be created."
                )

        # Calculate case date where possible
        case_date_case_type_dim_id = complete_case_type.case_date_case_type_dim_id
        if case_date_case_type_dim_id is None:
            case_date_case_type_col_mappers = {}
        else:
            case_type_cols = [
                complete_case_type.case_type_cols[x]
                for x in complete_case_type.ordered_case_type_col_ids_by_dim[
                    case_date_case_type_dim_id
                ]
            ]
            case_date_case_type_col_mappers = (
                case_service_get_case_date_case_type_col_mappers_from_cols(
                    case_type_cols,
                    complete_case_type.cols,
                )
            )
        case_service_calculate_case_date(cases, case_date_case_type_col_mappers)

        # Create cases, using the parent class method to avoid ABAC
        # restrictions
        cases = super(DomainBaseCaseService, self).crud(  # type: ignore[assignment]
            command.CaseCrudCommand(
                user=cmd.user,
                operation=CrudOperation.CREATE_SOME,
                objs=cases,  # type: ignore[arg-type]
                props=cmd.props,
            )
        )
        # Associate cases with data collections
        curr_cmd = command.CaseDataCollectionLinkCrudCommand(
            user=cmd.user,
            operation=CrudOperation.CREATE_SOME,
            objs=[
                model.CaseDataCollectionLink(
                    case_id=x.id, data_collection_id=y  # type: ignore[arg-type]
                )
                for x in cases
                for y in cmd.data_collection_ids
            ],
        )
        curr_cmd._policies.extend(cmd._policies)
        case_data_collection_links = self.crud(curr_cmd)
    return cases


def case_service_create_case_set(
    self: BaseCaseService, cmd: command.CreateCaseSetCommand
) -> model.CaseSet | None:
    # Get case type and created_in data collection IDs
    case_type_id = cmd.case_set.case_type_id
    created_in_data_collection_id = cmd.case_set.created_in_data_collection_id

    # @ABAC: verify if case set or cases may be created in the given data collection(s)
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None
    is_allowed = case_abac.is_allowed(
        case_type_id,
        enum.CaseRight.ADD_CASE_SET,
        True,
        created_in_data_collection_id=created_in_data_collection_id,
        tgt_data_collection_ids=cmd.data_collection_ids,
    )
    if not is_allowed:
        assert cmd.user is not None
        raise exc.UnauthorizedAuthError(
            f"User {cmd.user.id} is not allowed to create a case set in the given data collection(s)"
        )

    # Create case set, case set data collection links, and optionally
    # case set members
    with self.repository.uow() as uow:
        # Create case set, using the parent class method to avoid ABAC
        # restrictions
        case_set: model.CaseSet = super(DomainBaseCaseService, self).crud(  # type: ignore[assignment]
            command.CaseSetCrudCommand(
                user=cmd.user,
                operation=CrudOperation.CREATE_ONE,
                objs=cmd.case_set,
                props=cmd.props,
            )
        )
        # Associate case set/cases with data collections
        assert case_set.id is not None
        curr_cmd = command.CaseSetDataCollectionLinkCrudCommand(
            user=cmd.user,
            operation=CrudOperation.CREATE_SOME,
            objs=[
                model.CaseSetDataCollectionLink(
                    case_set_id=case_set.id, data_collection_id=x
                )
                for x in cmd.data_collection_ids
            ],
        )
        curr_cmd._policies.extend(cmd._policies)
        case_set_data_collection_links = self.crud(curr_cmd)
        # Associate case set with cases if necessary
        if cmd.case_ids:
            curr_cmd2: command.CaseSetMemberCrudCommand = (
                command.CaseSetMemberCrudCommand(
                    user=cmd.user,
                    operation=CrudOperation.CREATE_SOME,
                    objs=[
                        model.CaseSetMember(case_set_id=case_set.id, case_id=x)
                        for x in cmd.case_ids
                    ],
                )
            )
            curr_cmd2._policies.extend(cmd._policies)
            case_set_members = self.crud(curr_cmd2)
    return case_set

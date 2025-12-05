import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.domain.service import BaseCaseService as DomainBaseCaseService
from gen_epix.casedb.services.case.base import BaseCaseService
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
    cases: list[model.Case] = [
        model.Case(
            id=x.id,
            case_type_id=cmd.case_type_id,
            subject_id=x.subject_id,
            created_in_data_collection_id=cmd.created_in_data_collection_id,
            case_date=x.case_date,
            content={y: z for y, z in x.content.items() if z is not None},
        )
        for x in cmd.cases
    ]

    # Create cases and case data collection links
    with self.repository.uow() as uow:
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

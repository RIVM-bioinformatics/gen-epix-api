"""Create case sets together with their collection and case associations.

The module provides the case-service handler that authorizes and persists a case
set and its requested links within one case repository unit of work.
"""

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy import BasePolicyDecisionPoint
from gen_epix.casedb.domain.service import BaseCaseService as DomainBaseCaseService
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp import CrudOperation


def case_service_create_case_set(
    self: BaseCaseService, cmd: command.CreateCaseSetCommand
) -> model.CaseSet | None:
    """Authorize and create a case set and its requested associations.

    The case set, data-collection links, and optional members are created within one
    case repository unit of work. The command's policy instances are propagated to
    the nested link and member commands.

    Args:
        self: Case service handling the command.
        cmd: Command containing the case set and requested associations.

    Returns:
        The created case set.

    Raises:
        UnauthorizedAuthError: If the user may not add the case set to all requested
            data collections.
    """
    # @ABAC: verify if case set or cases may be created in the given data collection(s)
    pdp: BasePolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
    if not pdp.is_allowed(cmd):
        assert cmd.user is not None
        raise exc.UnauthorizedAuthError(
            "806a155b",
            f"User {cmd.user.id} is not allowed to create a case set in the given data collection(s)",
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

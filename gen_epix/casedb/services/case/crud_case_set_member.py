"""Handle CRUD operations for case-set-member entities.

Complex association entity with extensive ABAC logic.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy.pdp import BasePolicyDecisionPoint
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    get_case_abac_from_command,
)
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_case_set_member(
    self: BaseCaseService, cmd: command.CaseSetMemberCrudCommand
) -> (
    list[model.CaseSetMember]
    | model.CaseSetMember
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseSetMember entities."""
    with self.repository.uow() as uow:
        pdp: BasePolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
        if pdp.is_exempted(cmd):
            _crud_cascade_delete(self, uow, cmd)
            return _crud_case_set_member_without_abac(self, uow, cmd)
        return _crud_case_set_member_with_abac(self, uow, cmd)


def _crud_case_set_member_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetMemberCrudCommand,
) -> (
    list[model.CaseSetMember]
    | model.CaseSetMember
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseSetMember admin command handling."""
    # Non-ABAC restrictions not enforced anywhere else
    if cmd.is_create() or cmd.is_update():
        # Verify that the case set and case have the same CaseType
        self._verify_case_set_member_case_type(cmd.user, cmd.get_objs())

    _crud_cascade_delete(self, uow, cmd)
    return self.crud(cmd)  # type: ignore[return-value]


def _crud_case_set_member_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetMemberCrudCommand,
) -> (
    list[model.CaseSetMember]
    | model.CaseSetMember
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle case-set membership under current user restrictions.

    Commands without case ABAC metadata delegate directly. Otherwise unrestricted
    bulk reads, updates, and bulk deletes are rejected, and member reads are filtered
    to rows whose case and case set are both accessible.

    Args:
        self: Case service handling the command.
        uow: Active unit of work reserved for CRUD coordination.
        cmd: Case-set-member CRUD command.

    Returns:
        Result returned by delegated CRUD handling.

    Raises:
        UnauthorizedAuthError: If a restricted user requests an unsupported bulk
            operation or the returned rows cannot be verified.
    """
    # Initialize some
    assert cmd.user is not None and cmd.user.id is not None

    # Only read/exists some and read/exists one allowed, other operations need to be performed through other commands
    if not cmd.is_read() or cmd.is_read_all():
        raise exc.UnauthorizedAuthError(
            "85539cf8",
            f"Operation {cmd.operation.value} not allowed for case set members for this user",
        )

    case_abac = get_case_abac_from_command(cmd)
    if case_abac is None:
        return self.crud(cmd)  # type: ignore[return-value]

    retval = self.crud(cmd)
    if not cmd.is_read():
        return retval  # type: ignore[return-value]
    if retval is None:
        return None

    if cmd.return_id:
        if not isinstance(retval, list) or any(
            not isinstance(member_id, UUID) for member_id in retval
        ):
            raise exc.UnauthorizedAuthError(
                "9ef9c356", "Unable to verify access to case set members"
            )
        if not retval:
            return retval  # type: ignore[return-value]
        member_ids = retval
        member_cmd = cmd.model_copy(
            update={
                "operation": CrudOperation.READ_SOME,
                "obj_ids": member_ids,
                "query_filter": None,
                "return_id": False,
                "limit": 0,
                "offset": 0,
            }
        )
        member_result = self.crud(member_cmd)
        if not isinstance(member_result, list) or any(
            not isinstance(member, model.CaseSetMember) for member in member_result
        ):
            raise exc.UnauthorizedAuthError(
                "9ef9c356", "Unable to verify access to case set members"
            )
        members = member_result
    elif isinstance(retval, list):
        if any(not isinstance(member, model.CaseSetMember) for member in retval):
            raise exc.UnauthorizedAuthError(
                "9ef9c356", "Unable to verify access to case set members"
            )
        members = retval
        member_ids = []
    elif isinstance(retval, model.CaseSetMember):
        members = [retval]
        member_ids = []
    else:
        raise exc.UnauthorizedAuthError(
            "9ef9c356", "Unable to verify access to case set members"
        )

    if not members:
        return [] if isinstance(retval, list) else None  # type: ignore[return-value]

    case_ids = {member.case_id for member in members}
    case_set_ids = {member.case_set_id for member in members}
    assert cmd.user is not None and cmd.user.id is not None
    cases = self.repository.crud(
        uow,
        cmd.user.id,
        model.Case,
        CrudOperation.READ_SOME,
        obj_ids=case_ids,
    )
    case_sets = self.repository.crud(
        uow,
        cmd.user.id,
        model.CaseSet,
        CrudOperation.READ_SOME,
        obj_ids=case_set_ids,
    )
    cases_by_id = {case.id: case for case in cases}
    case_sets_by_id = {case_set.id: case_set for case_set in case_sets}
    case_data_collection_map = self._retrieve_case_data_collections_map(
        uow, cmd.user.id, case_ids=case_ids
    )
    case_set_data_collection_map = self._retrieve_case_set_data_collections_map(
        uow, cmd.user.id, case_set_ids=case_set_ids
    )

    accessible_member_ids: set[UUID] = set()
    for member in members:
        case = cases_by_id.get(member.case_id)
        case_set = case_sets_by_id.get(member.case_set_id)
        if case is None or case_set is None:
            continue
        case_data_collection_ids = case_data_collection_map.get(case.id, set()) | {
            case.created_in_data_collection_id
        }
        case_set_data_collection_ids = case_set_data_collection_map.get(
            case_set.id, set()
        ) | {case_set.created_in_data_collection_id}
        if case_abac.is_allowed(
            case.case_type_id,
            case.created_in_data_collection_id,
            enum.CaseRight.READ_CASE,
            current_data_collection_ids=case_data_collection_ids,
        ) and case_abac.is_allowed(
            case_set.case_type_id,
            case_set.created_in_data_collection_id,
            enum.CaseRight.READ_CASE_SET,
            current_data_collection_ids=case_set_data_collection_ids,
        ):
            if member.id is not None:
                accessible_member_ids.add(member.id)

    accessible_members = [
        member for member in members if member.id in accessible_member_ids
    ]
    if cmd.return_id:
        return [  # type: ignore[return-value]
            member_id for member_id in member_ids if member_id in accessible_member_ids
        ]
    if isinstance(retval, list):
        return accessible_members
    return accessible_members[0] if accessible_members else None  # type: ignore[return-value]

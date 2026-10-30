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
    is_bounded_query,
)
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import UuidSetFilter

BOUNDED_QUERY_KEYS = frozenset({"case_id", "case_set_id"})


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

    Bulk reads require an explicit case or case-set UUID selection. Reads are
    filtered to accessible cases and case sets. Creation requires readable cases,
    writable case sets, and matching case types before any rows are persisted.
    Missing ABAC metadata and other writes are rejected.

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

    is_create = cmd.is_create()
    bounded_query = is_bounded_query(cmd.query_filter, BOUNDED_QUERY_KEYS)
    if (not cmd.is_read() and not is_create) or (
        cmd.is_read_all() and not bounded_query
    ):
        raise exc.UnauthorizedAuthError(
            "85539cf8",
            f"Operation {cmd.operation.value} not allowed for case set members for this user",
        )

    case_abac = get_case_abac_from_command(cmd)
    if case_abac is None:
        raise exc.UnauthorizedAuthError(
            "58bcfdde", "Case ABAC metadata is required for case set members"
        )

    is_exists = cmd.operation in (CrudOperation.EXISTS_ONE, CrudOperation.EXISTS_SOME)
    requested_ids = cmd.get_obj_ids() if is_exists else None
    if is_exists:
        assert isinstance(requested_ids, list)
        if not requested_ids:
            return []
        retval = self.crud(
            cmd.model_copy(
                update={
                    "operation": CrudOperation.READ_ALL,
                    "obj_ids": None,
                    "query_filter": UuidSetFilter(key="id", members=set(requested_ids)),
                    "return_id": False,
                    "limit": 0,
                    "offset": 0,
                }
            )
        )
    elif is_create:
        retval = cmd.get_objs()
    else:
        retval = self.crud(cmd)
    if is_exists and not isinstance(retval, list):
        raise exc.UnauthorizedAuthError(
            "9ef9c356", "Unable to verify access to case set members"
        )
    if retval is None:
        return None

    if cmd.return_id and not is_create:
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

    if not members and is_exists:
        assert requested_ids is not None
        return (
            False
            if cmd.operation == CrudOperation.EXISTS_ONE
            else [False for _ in requested_ids]
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
    accessible_members = []
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
            (
                enum.CaseRight.WRITE_CASE_SET
                if is_create
                else enum.CaseRight.READ_CASE_SET
            ),
            current_data_collection_ids=case_set_data_collection_ids,
        ):
            accessible_members.append(member)
            if member.id is not None:
                accessible_member_ids.add(member.id)

    if is_create:
        if len(accessible_members) != len(members):
            raise exc.UnauthorizedAuthError(
                "65b21905",
                "Creating members requires readable cases and writable case sets",
            )
        self._verify_case_set_member_case_type(cmd.user, members)
        return self.crud(cmd)  # type: ignore[return-value]

    if is_exists:
        assert requested_ids is not None
        exists_results = [
            member_id in accessible_member_ids for member_id in requested_ids
        ]
        return (
            exists_results[0]
            if cmd.operation == CrudOperation.EXISTS_ONE
            else exists_results
        )
    if cmd.return_id:
        return [  # type: ignore[return-value]
            member_id for member_id in member_ids if member_id in accessible_member_ids
        ]
    if isinstance(retval, list):
        return accessible_members
    return accessible_members[0] if accessible_members else None  # type: ignore[return-value]


def _is_bounded_query(query_filter: Filter | None) -> bool:
    """Check whether a query filter limits members to explicit case or case-set IDs.

    A non-inverted UUID set filter on ``case_id`` or ``case_set_id`` is bounded.
    A non-inverted composite filter is bounded when its result cannot exceed that
    of a bounded filter: ``AND`` needs at least one bounded child and ``OR``
    needs all children bounded. Other filters and operators are unbounded.

    Args:
        query_filter: Query filter of the case-set-member command.

    Returns:
        Whether the filter restricts the query to explicit parent IDs.
    """
    if isinstance(query_filter, UuidSetFilter):
        return not query_filter.invert and query_filter.key in BOUNDED_QUERY_KEYS
    if isinstance(query_filter, CompositeFilter) and not query_filter.invert:
        if query_filter.operator == LogicalOperator.AND:
            return any(_is_bounded_query(x) for x in query_filter.filters)
        if query_filter.operator == LogicalOperator.OR:
            return all(_is_bounded_query(x) for x in query_filter.filters)
    return False

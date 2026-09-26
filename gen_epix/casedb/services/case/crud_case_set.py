"""Handle CRUD operations for case-set entities."""

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
from gen_epix.fastapp.enum import CrudOperationSet, OnException
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.base import Filter


def case_service_crud_case_set(
    self: BaseCaseService, cmd: command.CaseSetCrudCommand
) -> list[model.CaseSet] | model.CaseSet | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for CaseSet entities."""
    # Start unit of work
    with self.repository.uow() as uow:
        _crud_cascade_delete(self, uow, cmd)
        pdb: BasePolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
        if pdb.is_exempted(cmd):
            return _crud_case_set_without_abac(self, uow, cmd)
        return _crud_case_set_with_abac(self, uow, cmd)


def _crud_case_set_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetCrudCommand,
) -> list[model.CaseSet] | model.CaseSet | list[UUID] | UUID | list[bool] | bool | None:
    """CaseSet admin command handling, no ABAC applied."""
    # Any other operation
    return self.crud(cmd)  # type: ignore[return-value]


def _crud_case_set_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetCrudCommand,
) -> list[model.CaseSet] | model.CaseSet | list[UUID] | UUID | list[bool] | bool | None:
    """Handle case-set CRUD with operation-specific content rights.

    Reads are access-filtered, updates require write access, and deletes require
    remove access across all associated collections. Commands without case ABAC
    metadata delegate directly.

    Args:
        self: Case service handling the command.
        uow: Active unit of work used for access checks.
        cmd: Case-set CRUD command.

    Returns:
        Access-filtered read results or the delegated write result.

    Raises:
        UnauthorizedAuthError: If deletion is too broad or remove access is missing.
        AssertionError: If creation or an unknown operation reaches this handler.
    """
    # @ABAC: get case abac
    case_abac: model.CaseAbac | None = get_case_abac_from_command(cmd)

    # Special case: no policy, allows for internal commands to retrieve all
    pdp: BasePolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
    if case_abac is None:
        # No policy: allows for internal commands to retrieve all
        return self.crud(cmd)  # type: ignore[return-value]

    # Initialise some
    assert cmd.user is not None and cmd.user.id is not None

    # Determine valid CaseTypes and data collections
    case_set_ids: list[UUID] | None = cmd.get_obj_ids()  # type: ignore[assignment]
    if cmd.is_create():
        # Implemented through separate create case set command
        raise AssertionError("Unexpected operation")
    elif cmd.is_read():
        # At least one data collection with read access is required
        retval = _retrieve_case_sets_with_content_right(
            self,
            uow,
            cmd,
            pdp,
            enum.CaseRight.READ_CASE_SET,
            case_set_ids=case_set_ids,
            filter=cmd.query_filter,
        )
        return retval[0] if cmd.operation in CrudOperationSet.ANY_ONE.value else retval
    elif cmd.is_update():
        # At least one data collection with write access is required
        _retrieve_case_sets_with_content_right(
            self,
            uow,
            cmd,
            pdp,
            enum.CaseRight.WRITE_CASE_SET,
            case_set_ids=case_set_ids,
        )
        return self.crud(cmd)  # type: ignore[return-value]
    elif cmd.is_delete():
        # All linked data collections have remove right
        _validate_case_set_deletion(
            self, uow, cmd, case_abac, cmd.is_delete_all(), case_set_ids
        )
        # Delete with cascade
        return self.crud(cmd)  # type: ignore[return-value]
    else:
        raise AssertionError("Unexpected operation")


def _retrieve_case_sets_with_content_right(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetCrudCommand,
    pdp: BasePolicyDecisionPoint,
    right: enum.CaseRight,
    case_set_ids: list[UUID] | None = None,
    filter: Filter | None = None,
) -> list[model.CaseSet]:
    """Retrieve case sets for which the user has the specified access right.

    Args:
        self: Case service used for repository and association access.
        uow: Active unit of work for all validation reads.
        cmd: Case set CRUD command containing the acting user.
        pdp: Policy decision point used to evaluate access rights.
        # case_abac is derived from the command
        right: Access right required for the retrieval.
        case_set_ids: Explicit identifiers of case sets to retrieve.
        filter: Optional filter to apply to the retrieval.

    Returns:
        List of case sets for which the user has the specified access right.
    """
    user_id = pdp.get_command_user_id(cmd)
    # Determine if we are reading all (allowed) case sets or a specific subset
    is_read_all = case_set_ids is None
    if is_read_all:
        # Get IDs of all case sets
        case_set_ids = self.repository.crud(
            uow,
            user_id,
            model.CaseSet,
            CrudOperation.READ_ALL,
            filter=filter,
            return_id=True,
        )

    # Get dict[case_set_id, frozenset[data_collection_ids]]
    case_set_data_collection_ids = self._retrieve_case_set_data_collections_map(
        uow,
        user_id,
        case_set_ids=case_set_ids,
    )

    # Get dict[case_set_id, case_type_id]
    assert case_set_ids is not None
    case_type_ids: list[UUID] = self.repository.read_fields(  # type: ignore[assignment]
        uow,
        user_id,
        model.CaseSet,
        obj_ids=case_set_ids,
        field_names=["case_type_id"],
    )
    case_set_case_type_ids: dict[UUID, UUID] = dict(zip(case_set_ids, case_type_ids))

    # Create Iterable of tuples (case_set, frozenset[data_collection_ids])
    abac_iterable: list[tuple[UUID, UUID, frozenset[UUID]]] = [
        (x, case_set_case_type_ids[x], frozenset(y))
        for x, y in case_set_data_collection_ids.items()
    ]

    # @ABAC PEP: Verify rights on each case set by filtering the list of case set IDs on accessibility
    case_set_ids = list(
        pdp.filter_case_set_ids(
            cmd,
            abac_iterable,
            right,
            on_filtered=OnException.SKIP if is_read_all else OnException.RAISE,
        )
    )

    # Read accessible case sets
    allowed_case_sets: list[model.CaseSet] = self.repository.crud(
        uow,
        user_id,
        model.CaseSet,
        CrudOperation.READ_SOME,
        obj_ids=case_set_ids,
    )

    return allowed_case_sets


def _validate_case_set_deletion(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetCrudCommand,
    case_abac: model.CaseAbac,
    is_delete_all: bool,
    case_set_ids: list[UUID] | None,
) -> None:
    """Require remove access for every collection of each requested case set.

    Args:
        self: Case service used for repository and association access.
        uow: Active unit of work for all validation reads.
        cmd: Delete command providing the acting user and operation.
        case_abac: Case access metadata used to evaluate remove rights.
        is_delete_all: Whether the command requests deletion of all case sets.
        case_set_ids: Explicit identifiers requested for deletion.

    Raises:
        UnauthorizedAuthError: If deleting all or if any case set cannot be removed
            from all of its associated collections.
    """
    if is_delete_all:
        # Delete all not allowed due to potential large number of case sets
        raise exc.UnauthorizedAuthError(
            "b5a9806f",
            f"Operation {cmd.operation.value} not allowed for case sets for this user",
        )
    assert case_set_ids is not None
    # Get all case sets and data collection links
    case_sets: list[model.CaseSet] = self.repository.crud(
        uow,
        cmd.user.id,  # type: ignore[union-attr]
        model.CaseSet,
        CrudOperation.READ_SOME,
        obj_ids=case_set_ids,
    )
    case_set_data_collection_map: dict[UUID, set[UUID]] = (
        self._retrieve_case_set_data_collections_map(
            uow,
            cmd.user.id,  # type: ignore[arg-type,union-attr]
            case_set_ids=case_set_ids,
        )
    )
    # Check if the user has access to all data collections of all requested
    # case sets
    for case_set in case_sets:
        assert case_set.id is not None
        data_collection_ids: set[UUID] = case_set_data_collection_map.get(
            case_set.id, set()
        )
        is_allowed = case_abac.is_allowed(
            case_set.case_type_id,
            case_set.created_in_data_collection_id,
            enum.CaseRight.REMOVE_CASE_SET,
            True,
            current_data_collection_ids=data_collection_ids,
        )
        if not is_allowed:
            raise exc.UnauthorizedAuthError(
                "020c35a9",
                f"User {cmd.user.id} is not allowed to delete case set {case_set.id}",  # type: ignore[union-attr]
            )

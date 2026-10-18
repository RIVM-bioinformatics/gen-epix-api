"""Handle case-identifier CRUD with admin bypass and user restrictions."""

from typing import cast
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import enum, exc
from gen_epix.casedb.domain.policy.pdp import BasePolicyDecisionPoint
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
)
from gen_epix.fastapp.enum import CrudOperation, OnException
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.uuid_set import UuidSetFilter


def case_service_crud_case_identifier(
    self: BaseCaseService, cmd: command.CaseIdentifierCrudCommand
) -> (
    list[model.CaseIdentifier]
    | model.CaseIdentifier
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseIdentifier entities."""
    with self.repository.uow() as uow:
        pdp: BasePolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
        if pdp.is_exempted(cmd):
            _crud_cascade_delete(self, uow, cmd)
            return _crud_case_identifier_without_abac(self, uow, cmd)
        return _crud_case_identifier_with_abac(self, uow, cmd)


def _crud_case_identifier_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseIdentifierCrudCommand,
) -> (
    list[model.CaseIdentifier]
    | model.CaseIdentifier
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseIdentifier CRUD command handling, no ABAC applied."""
    return self.crud(cmd)  # type: ignore[return-value]


def _crud_case_identifier_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseIdentifierCrudCommand,
) -> (
    list[model.CaseIdentifier]
    | model.CaseIdentifier
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseIdentifier CRUD command handling, ABAC applied.

    Args:
        self: Case service handling the command.
        uow: Active unit of work reserved for CRUD coordination.
        cmd: Case-identifier CRUD command.

    Returns:
        Result returned by delegated CRUD handling.

    Raises:
        UnauthorizedAuthError: If a restricted user requests an unsupported bulk
            read, update, or delete operation.
    """
    # Only read/exists some and read/exists one allowed, other operations need to be performed through other commands
    if not cmd.is_read() or cmd.is_read_all():
        raise exc.UnauthorizedAuthError(
            "f648da79",
            f"Operation {cmd.operation.value} not allowed for case identifiers for this user",
        )

    is_exists = cmd.is_exists()
    requested_ids = None
    if is_exists:
        requested_ids = cmd.get_obj_ids()
        assert isinstance(requested_ids, list)
        case_identifier_or_list = self.crud(
            cmd.model_copy(
                update={
                    "operation": CrudOperation.READ_SOME,
                    "obj_ids": requested_ids,
                    "return_id": False,
                }
            )
        )
    elif cmd.return_id:
        case_identifier_or_list = self.crud(cmd.model_copy(update={"return_id": False}))
    else:
        case_identifier_or_list = self.crud(cmd)
    return_list = isinstance(case_identifier_or_list, list)
    case_identifiers: list[model.CaseIdentifier]
    if not return_list:
        case_identifiers = [case_identifier_or_list]
    else:
        case_identifiers = case_identifier_or_list
    if not case_identifiers and is_exists:
        assert requested_ids is not None
        exists_results = [False for _ in requested_ids]
        return (
            exists_results[0]
            if cmd.operation == CrudOperation.EXISTS_ONE
            else exists_results
        )
    if not case_identifiers:
        return []

    # Retrieve allowed DataCollections per Case
    all_case_ids = [x.internal_id for x in case_identifiers]
    all_case_ids_set = frozenset(all_case_ids)
    case_props_list = self.repository.read_fields(
        uow,
        cmd.user.id if cmd.user else None,
        model.Case,
        ["id", "case_type_id", "created_in_data_collection_id"],
        filter=UuidSetFilter(key="id", members=all_case_ids_set),
    )
    case_case_type_map: dict[UUID, UUID] = {x[0]: x[1] for x in case_props_list}
    case_created_in_data_collection_map: dict[UUID, UUID] = {
        x[0]: x[2] for x in case_props_list
    }

    # Get DataCollections per case
    user_id = None if cmd.user is None else cast(UUID, cmd.user.id)
    assert user_id is not None
    case_data_collections_map: dict[UUID, frozenset[UUID]] = self._retrieve_case_data_collections_map(  # type: ignore[assignment]
        uow,
        user_id,
        list(all_case_ids),
        frozen=True,
    )
    for case_id in all_case_ids:
        if case_id not in case_data_collections_map:
            case_data_collections_map[case_id] = frozenset(
                {case_created_in_data_collection_map[case_id]}
            )
        else:
            case_data_collections_map[case_id] = frozenset(
                case_data_collections_map[case_id]
                | {case_created_in_data_collection_map[case_id]}
            )

    # Get filtered Case IDs
    pdp: BasePolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
    case_ids = set(
        pdp.filter_case_ids(
            cmd,
            [
                (
                    x,
                    case_case_type_map[x],
                    case_data_collections_map.get(x, frozenset()),
                )
                for x in all_case_ids
            ],
            enum.CaseRight.READ_CASE,
            on_filtered=OnException.SKIP if cmd.is_read_all() else OnException.RAISE,
        )
    )

    # Filter CaseIdentifiers
    filtered_case_identifiers = [
        x for x in case_identifiers if x.internal_id in case_ids
    ]

    if is_exists:
        assert requested_ids is not None
        existing_ids = {cast(UUID, x.id) for x in filtered_case_identifiers}
        exists_results = [x in existing_ids for x in requested_ids]
        return (
            exists_results[0]
            if cmd.operation == CrudOperation.EXISTS_ONE
            else exists_results
        )

    # Return
    if cmd.return_id:
        retval: list[UUID] = [cast(UUID, x.id) for x in filtered_case_identifiers]
        return retval if return_list else retval[0]
    return filtered_case_identifiers if return_list else filtered_case_identifiers[0]

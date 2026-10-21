"""Handle CRUD operations for case-set-to-data-collection links.

Complex association entity with extensive ABAC logic.
"""

from typing import cast
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy.pdp import BasePolicyDecisionPoint
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    get_case_abac_from_command,
)
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.uuid_set import UuidSetFilter


def case_service_crud_case_set_data_collection_link(
    self: BaseCaseService, cmd: command.CaseSetDataCollectionLinkCrudCommand
) -> (
    list[model.CaseSetDataCollectionLink]
    | model.CaseSetDataCollectionLink
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseSetDataCollectionLink entities."""
    with self.repository.uow() as uow:
        pdp: BasePolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
        if pdp.is_exempted(cmd):
            _crud_cascade_delete(self, uow, cmd)
            return _crud_case_set_data_collection_link_without_abac(self, uow, cmd)
        return _crud_case_set_data_collection_link_with_abac(self, uow, cmd)


def _crud_case_set_data_collection_link_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetDataCollectionLinkCrudCommand,
) -> (
    list[model.CaseSetDataCollectionLink]
    | model.CaseSetDataCollectionLink
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseSetDataCollectionLink admin command handling."""
    _crud_cascade_delete(self, uow, cmd)
    return self.crud(cmd)  # type: ignore[return-value]


def _crud_case_set_data_collection_link_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseSetDataCollectionLinkCrudCommand,
) -> (
    list[model.CaseSetDataCollectionLink]
    | model.CaseSetDataCollectionLink
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle case-set collection links under current user restrictions.

    Bulk queries require a non-inverted CaseSet UUID selection. Unrestricted
    reads, updates, and bulk deletes are rejected.
    Reads are verified against the case-set read permission in each linked
    collection.

    Args:
        self: Case service handling the command.
        uow: Active unit of work reserved for CRUD coordination.
        cmd: Case-set collection-link CRUD command.

    Returns:
        Result returned by delegated CRUD handling.

    Raises:
        UnauthorizedAuthError: If a restricted user requests an unsupported bulk
            read, update, or delete operation.
    """
    # Reads require explicit link IDs or a bounded CaseSet selection.
    bounded_query = (
        isinstance(cmd.query_filter, UuidSetFilter)
        and not cmd.query_filter.invert
        and cmd.query_filter.key == "case_set_id"
    )
    if not cmd.is_read() or (cmd.is_read_all() and not bounded_query):
        raise exc.UnauthorizedAuthError(
            "8c5c07be",
            f"Operation {cmd.operation.value} not allowed for case set data collection links for this user",
        )

    is_exists = cmd.is_exists()
    requested_ids = None
    if is_exists:
        requested_ids = cmd.get_obj_ids()
        assert isinstance(requested_ids, list)
        case_set_data_collection_links = self.crud(
            cmd.model_copy(
                update={
                    "operation": CrudOperation.READ_SOME,
                    "obj_ids": requested_ids,
                    "return_id": False,
                }
            )
        )
    elif cmd.return_id:
        case_set_data_collection_links = self.crud(
            cmd.model_copy(update={"return_id": False})
        )
    else:
        case_set_data_collection_links = self.crud(cmd)
    if not case_set_data_collection_links:
        if is_exists:
            assert requested_ids is not None
            exists_results = [False for _ in requested_ids]
            return (
                exists_results[0]
                if cmd.operation == CrudOperation.EXISTS_ONE
                else exists_results
            )
        return case_set_data_collection_links  # type: ignore[return-value]
    return_list = isinstance(case_set_data_collection_links, list)
    if not return_list:
        case_set_data_collection_links = [case_set_data_collection_links]

    all_case_set_ids = frozenset(
        {x.case_set_id for x in case_set_data_collection_links}
    )
    case_set_case_type_list = self.repository.read_fields(
        uow,
        cmd.user.id if cmd.user else None,
        model.CaseSet,
        ["id", "case_type_id"],
        filter=UuidSetFilter(key="id", members=all_case_set_ids),
    )
    case_set_case_type_map: dict[UUID, UUID] = {
        x[0]: x[1] for x in case_set_case_type_list
    }
    case_abac = get_case_abac_from_command(cmd)
    if case_abac is None:
        raise AssertionError("Case ABAC metadata is required for this operation.")

    filtered_case_set_data_collection_links = []
    for case_set_data_collection_link in case_set_data_collection_links:
        case_set_id = case_set_data_collection_link.case_set_id
        case_type_id = case_set_case_type_map.get(case_set_id)
        data_collection_id = case_set_data_collection_link.data_collection_id
        case_type_access_abac: model.CaseTypeAccessAbac | None = (
            case_abac.case_type_access_abacs.get(case_type_id, {}).get(
                data_collection_id
            )
        )
        if case_type_access_abac is None:
            raise exc.UnauthorizedAuthError(
                "8fd08706",
                f"User is not allowed to read case set data collection link for case set {case_set_id} in data collection {data_collection_id}",
            )
        if not case_type_access_abac.read_case_set:
            raise exc.UnauthorizedAuthError(
                "8fd08706",
                f"User is not allowed to read case set data collection link for case set {case_set_id} in data collection {data_collection_id}",
            )
        filtered_case_set_data_collection_links.append(case_set_data_collection_link)

    if is_exists:
        assert requested_ids is not None
        existing_ids = {
            (x.case_set_id, x.data_collection_id)
            for x in filtered_case_set_data_collection_links
        }
        exists_results = [x in existing_ids for x in requested_ids]
        return (
            exists_results[0]
            if cmd.operation == CrudOperation.EXISTS_ONE
            else exists_results
        )

    if cmd.return_id:
        retval: list[tuple[UUID, UUID]] = [
            (
                cast(UUID, x.case_set_id),
                cast(UUID, x.data_collection_id),
            )
            for x in filtered_case_set_data_collection_links
        ]
        return retval if return_list else retval[0]
    return (
        filtered_case_set_data_collection_links
        if return_list
        else filtered_case_set_data_collection_links[0]
    )

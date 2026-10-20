"""Handle CRUD operations for case-to-data-collection links.

Complex association entity with extensive ABAC logic.
"""

from typing import cast
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.enum import CaseRight
from gen_epix.casedb.domain.policy.pdp import BasePolicyDecisionPoint
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    get_case_abac_from_command,
)
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.uuid_set import UuidSetFilter


def case_service_crud_case_data_collection_link(
    self: BaseCaseService, cmd: command.CaseDataCollectionLinkCrudCommand
) -> (
    list[model.CaseDataCollectionLink]
    | model.CaseDataCollectionLink
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseDataCollectionLink entities."""
    with self.repository.uow() as uow:
        pdp: BasePolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
        if pdp.is_exempted(cmd):
            _crud_cascade_delete(self, uow, cmd)
            return _crud_case_data_collection_link_without_abac(self, uow, cmd)
        return _crud_case_data_collection_link_with_abac(self, uow, cmd)


def _crud_case_data_collection_link_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseDataCollectionLinkCrudCommand,
) -> (
    list[model.CaseDataCollectionLink]
    | model.CaseDataCollectionLink
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseDataCollectionLink admin command handling."""
    return self.crud(cmd)  # type: ignore[return-value]


def _crud_case_data_collection_link_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseDataCollectionLinkCrudCommand,
) -> (
    list[model.CaseDataCollectionLink]
    | model.CaseDataCollectionLink
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CaseCollectionLink CRUD operations with ABAC applied.

    Creating links requires case write access and permission to add each case to
    its target collection. Every requested link is checked before persistence.
    Other writes and unrestricted bulk reads remain unsupported.

    Args:
        self: Case service handling the command.
        uow: Active unit of work reserved for CRUD coordination.
        cmd: Case-collection-link CRUD command.

    Returns:
        Result returned by delegated CRUD handling.

    Raises:
        UnauthorizedAuthError: If a restricted user requests an unsupported bulk
            read, update, or delete operation, or lacks sharing permission.
    """
    if cmd.is_create():
        assert cmd.user is not None and cmd.user.id is not None
        links = cmd.get_objs()
        case_ids = {link.case_id for link in links}
        cases = self.repository.crud(
            uow, cmd.user.id, model.Case, CrudOperation.READ_SOME, obj_ids=case_ids
        )
        cases_by_id = {case.id: case for case in cases}
        collections = self._retrieve_case_data_collections_map(
            uow, cmd.user.id, case_ids=case_ids
        )
        case_abac = get_case_abac_from_command(cmd)
        for link in links:
            case = cases_by_id.get(link.case_id)
            current_ids = collections.get(link.case_id, set())
            if (
                case_abac is None
                or case is None
                or not case_abac.is_allowed(
                    case.case_type_id,
                    case.created_in_data_collection_id,
                    CaseRight.WRITE_CASE,
                    current_data_collection_ids=current_ids
                    | {case.created_in_data_collection_id},
                )
                or not case_abac.is_allowed(
                    case.case_type_id,
                    case.created_in_data_collection_id,
                    CaseRight.ADD_CASE,
                    current_data_collection_ids=current_ids,
                    tgt_data_collection_ids={link.data_collection_id},
                )
            ):
                raise exc.UnauthorizedAuthError(
                    "6422d2ea",
                    "Sharing requires case write access and target add permission",
                )
        return self.crud(cmd)  # type: ignore[return-value]

    # Other writes and unrestricted reads are unsupported.
    if not cmd.is_read() or cmd.is_read_all():
        raise exc.UnauthorizedAuthError(
            "7fe2e531",
            f"Operation {cmd.operation.value} not allowed for case data collection links for this user",
        )

    is_exists = cmd.is_exists()
    requested_ids = None
    if is_exists:
        requested_ids = cmd.get_obj_ids()
        assert isinstance(requested_ids, list)
        case_data_collection_links = self.crud(
            cmd.model_copy(
                update={
                    "operation": CrudOperation.READ_SOME,
                    "obj_ids": requested_ids,
                    "return_id": False,
                }
            )
        )
    elif cmd.return_id:
        case_data_collection_links = self.crud(
            cmd.model_copy(update={"return_id": False})
        )
    else:
        case_data_collection_links = self.crud(cmd)
    if not case_data_collection_links:
        if is_exists:
            assert requested_ids is not None
            exists_results = [False for _ in requested_ids]
            return (
                exists_results[0]
                if cmd.operation == CrudOperation.EXISTS_ONE
                else exists_results
            )
        return case_data_collection_links  # type: ignore[return-value]
    return_list = isinstance(case_data_collection_links, list)
    if not return_list:
        case_data_collection_links = [case_data_collection_links]

    # Retrieve allowed DataCollections per Case
    all_case_ids = frozenset({x.case_id for x in case_data_collection_links})
    case_case_type_list = self.repository.read_fields(
        uow,
        cmd.user.id if cmd.user else None,
        model.Case,
        ["id", "case_type_id"],
        filter=UuidSetFilter(key="id", members=all_case_ids),
    )
    case_case_type_map: dict[UUID, UUID] = {x[0]: x[1] for x in case_case_type_list}
    case_abac = get_case_abac_from_command(cmd)
    if case_abac is None:
        raise AssertionError("Case ABAC metadata is required for this operation.")
    filtered_case_data_collection_links = []
    for case_data_collection_link in case_data_collection_links:
        case_id = case_data_collection_link.case_id
        case_type_id = case_case_type_map.get(case_id)
        data_collection_id = case_data_collection_link.data_collection_id
        case_type_access_abac: model.CaseTypeAccessAbac | None = (
            case_abac.case_type_access_abacs.get(case_type_id, {}).get(
                data_collection_id
            )
        )
        if case_type_access_abac is None:
            raise exc.UnauthorizedAuthError(
                "47d2cad9",
                f"User is not allowed to read case data collection link for case {case_id} in data collection {data_collection_id}",
            )
        if not case_type_access_abac.read_col_ids:
            raise exc.UnauthorizedAuthError(
                "aa139569",
                f"User is not allowed to read case data collection link for case {case_id} in data collection {data_collection_id}",
            )
        filtered_case_data_collection_links.append(case_data_collection_link)

    if is_exists:
        assert requested_ids is not None
        existing_ids = {
            (x.case_id, x.data_collection_id)
            for x in filtered_case_data_collection_links
        }
        exists_results = [x in existing_ids for x in requested_ids]
        return (
            exists_results[0]
            if cmd.operation == CrudOperation.EXISTS_ONE
            else exists_results
        )

    # Return
    if cmd.return_id:
        retval: list[UUID] = [
            cast(UUID, x.id) for x in filtered_case_data_collection_links
        ]
        return retval if return_list else retval[0]
    return (
        filtered_case_data_collection_links
        if return_list
        else filtered_case_data_collection_links[0]
    )

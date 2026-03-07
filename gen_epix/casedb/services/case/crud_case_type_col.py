"""
CRUD operations for CaseTypeCol entities.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    crud_with_access_filter,
    get_ref_data_access_from_command,
    is_refdata_admin_or_above,
)
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_case_type_col(
    self: BaseCaseService, cmd: command.CaseTypeColCrudCommand
) -> (
    list[model.CaseTypeCol]
    | model.CaseTypeCol
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseTypeCol entities."""

    # Start unit of work
    with self.repository.uow() as uow:
        assert cmd.user is not None and cmd.user.id is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_refdata_admin_or_above(self, cmd.user):
            return _crud_case_type_col_without_abac(self, uow, cmd)
        return _crud_case_type_col_with_abac(self, uow, cmd)


def _crud_case_type_col_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeColCrudCommand,
) -> (
    list[model.CaseTypeCol]
    | model.CaseTypeCol
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeCol admin command handling, no ABAC applied."""
    # (CREATE) Validate the linked case_type_dim belongs to the same case_type
    _validate_case_type_cols(self, uow, cmd)
    return self.crud(cmd)


def _crud_case_type_col_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeColCrudCommand,
) -> (
    list[model.CaseTypeCol]
    | model.CaseTypeCol
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeCol user command handling, ABAC applied."""
    ref_data_access = get_ref_data_access_from_command(cmd)
    if ref_data_access is None or ref_data_access.is_full_access:
        # Special case: no policy (implies full access) or explicit full access
        return self.crud(cmd)  # type: ignore[return-value]
    access_filter = ref_data_access.get_case_type_col_filter("id")
    # No cascade delete to force conscious decision to delete from other models
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]


def _validate_case_type_cols(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeColCrudCommand,
) -> None:
    """Validate CaseTypeCol entities before creation or update."""

    if cmd.is_write():
        user = cmd.user
        assert user is not None and user.id is not None
        case_type_cols: list[model.CaseTypeCol] = cmd.get_objs()  # type: ignore[assignment]

        # Get case type dims
        case_type_dim_ids = list({x.case_type_dim_id for x in case_type_cols})
        case_type_dims: list[model.CaseTypeDim] = (
            self.repository.crud(  # type: ignore[assignment]
                uow,
                user.id,
                model.CaseTypeDim,
                None,
                case_type_dim_ids,
                CrudOperation.READ_SOME,
            )
        )
        case_type_dim_map: dict[UUID, model.CaseTypeDim] = {  # type: ignore[assignment]
            x.id: x for x in case_type_dims
        }

        # Get cols
        col_ids: list[UUID] = list({x.col_id for x in case_type_cols})
        cols: list[model.Col] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            col_ids,
            CrudOperation.READ_SOME,
        )
        col_map: dict[UUID, model.Col] = {
            x.id: x for x in cols
        }  # type: ignore[assignment]

        # Verify each case_type_col
        for case_type_col in case_type_cols:
            case_type_dim = case_type_dim_map[case_type_col.case_type_dim_id]
            col = col_map[case_type_col.col_id]
            if case_type_col.case_type_id != case_type_dim.case_type_id:
                raise exc.InvalidArgumentsError(
                    "case_type_id must match case_type_id of CaseTypeDim",
                    ids=[case_type_col.case_type_dim_id],
                )
            if col.dim_id != case_type_dim.dim_id:
                raise exc.InvalidArgumentsError(
                    "col.dim_id must match dim_id of CaseTypeDim",
                    ids=[case_type_col.col_id],
                )  # type: ignore[return-value]

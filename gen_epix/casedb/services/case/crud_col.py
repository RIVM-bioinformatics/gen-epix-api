"""
CRUD operations for Col entities.
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


def case_service_crud_col(
    self: BaseCaseService, cmd: command.ColCrudCommand
) -> list[model.Col] | model.Col | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for Col entities."""

    # Start unit of work
    with self.repository.uow() as uow:
        assert cmd.user is not None and cmd.user.id is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_refdata_admin_or_above(self, cmd.user):
            return _crud_col_without_abac(self, uow, cmd)
        return _crud_col_with_abac(self, uow, cmd)


def _crud_col_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.ColCrudCommand,
) -> list[model.Col] | model.Col | list[UUID] | UUID | list[bool] | bool | None:
    """Col admin command handling, no ABAC applied."""
    # (CREATE) Validate the linked Dim belongs to the same case_type
    _validate_cols(self, uow, cmd)
    return self.crud(cmd)


def _crud_col_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.ColCrudCommand,
) -> list[model.Col] | model.Col | list[UUID] | UUID | list[bool] | bool | None:
    """Col user command handling, ABAC applied."""
    ref_data_access = get_ref_data_access_from_command(cmd)
    if ref_data_access is None or ref_data_access.is_full_access:
        # Special case: no policy (implies full access) or explicit full access
        return self.crud(cmd)  # type: ignore[return-value]
    access_filter = ref_data_access.get_col_filter("id")
    # No cascade delete to force conscious decision to delete from other models
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]


def _validate_cols(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.ColCrudCommand,
) -> None:
    """Validate Col entities before creation or update."""

    if cmd.is_write():
        user = cmd.user
        assert user is not None and user.id is not None
        cols: list[model.Col] = cmd.get_objs()  # type: ignore[assignment]

        # Get Dims
        dim_ids = list({x.dim_id for x in cols})
        dims: list[model.Dim] = self.repository.crud(
            uow,
            user.id,
            model.Dim,
            CrudOperation.READ_SOME,
            obj_ids=dim_ids,
        )
        dim_map: dict[UUID, model.Dim] = {  # type: ignore[assignment]
            x.id: x for x in dims
        }

        # Get RefCols
        ref_col_ids: list[UUID] = list({x.ref_col_id for x in cols})
        ref_cols: list[model.RefCol] = self.repository.crud(
            uow,
            user.id,
            model.RefCol,
            CrudOperation.READ_SOME,
            obj_ids=ref_col_ids,
        )
        ref_col_map: dict[UUID, model.RefCol] = {
            x.id: x for x in ref_cols
        }  # type: ignore[assignment]

        # Verify each Col
        for col in cols:
            dim = dim_map[col.dim_id]
            ref_col = ref_col_map[col.ref_col_id]
            if col.case_type_id != dim.case_type_id:
                raise exc.InvalidArgumentsError(
                    "0b7ce2a3",
                    "case_type_id must match case_type_id of Dim",
                    ids=[col.dim_id],
                )
            if ref_col.ref_dim_id != dim.ref_dim_id:
                raise exc.InvalidArgumentsError(
                    "6636b283",
                    "ref_col.ref_dim_id must match ref_dim_id of Dim",
                    ids=[col.ref_col_id],
                )  # type: ignore[return-value]

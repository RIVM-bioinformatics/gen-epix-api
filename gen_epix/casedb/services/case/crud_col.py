"""
CRUD operations for Col entities.
This is a simple metadata entity with no ABAC restrictions.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    crud_with_access_filter,
    get_ref_data_access_from_command,
)
from gen_epix.fastapp import CrudOperation


def case_service_crud_col(
    self: BaseCaseService, cmd: command.ColCrudCommand
) -> list[model.Col] | model.Col | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for Col entities."""
    assert cmd.user is not None and cmd.user.id is not None

    if cmd.is_read():
        ref_data_access = get_ref_data_access_from_command(cmd)
        if ref_data_access is None or ref_data_access.is_full_access:
            # Special case: no policy (implies full access) or explicit full access
            return self.crud(cmd)  # type: ignore[return-value]
        access_filter = ref_data_access.get_col_filter("id")
        # No cascade delete to force conscious decision to delete from other models
        with self.repository.uow() as uow:
            retval = crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]
        return retval

    if cmd.is_delete():
        return self.crud(cmd)  # type: ignore[return-value]

    # Perform some validation on CREATE/UPDATE
    cols: list[model.Col] = cmd.get_objs()  # type: ignore[assignment]
    if cmd.is_create():
        with self.repository.uow() as uow:
            # Get dims
            dim_ids = list({x.dim_id for x in cols})
            dims: list[model.Dim] = self.repository.crud(  # type: ignore[assignment]
                uow,
                cmd.user.id,
                model.Dim,
                None,
                dim_ids,
                CrudOperation.READ_SOME,
            )
            dim_map: dict[UUID, model.Dim] = {
                x.id: x for x in dims
            }  # type: ignore[assignment]

            # Verify col_type corresponds to dim_type
            invalid_cols = [
                x
                for x in cols
                if x.col_type
                not in enum.DimColTypeSet[dim_map[x.dim_id].dim_type.value].value
            ]
            if invalid_cols:
                invalid_cols_ids = [x.id for x in invalid_cols if x.id is not None]
                raise exc.InvalidArgumentsError(
                    "col_type must correspond to Dim.dim_type",
                    ids=invalid_cols_ids,
                )
        return self.crud(cmd)  # type: ignore[return-value]

    if cmd.is_update():
        with self.repository.uow() as uow:
            existing_cols: list[model.Col] = self.repository.crud(  # type: ignore[assignment]
                uow,
                cmd.user.id,
                model.Col,
                None,
                [x.id for x in cols],
                CrudOperation.READ_SOME,
            )
            if any(x.dim_id != y.dim_id for x, y in zip(cols, existing_cols)):
                invalid_cols = [
                    x.id for x, y in zip(cols, existing_cols) if x.dim_id != y.dim_id
                ]
                raise exc.InvalidArgumentsError(
                    "dim_id is immutable and cannot be updated", ids=invalid_cols
                )
            if any(x.col_type != y.col_type for x, y in zip(cols, existing_cols)):
                invalid_cols = [
                    x.id
                    for x, y in zip(cols, existing_cols)
                    if x.col_type != y.col_type
                ]
                raise exc.InvalidArgumentsError(
                    "col_type is immutable and cannot be updated", ids=invalid_cols
                )
        return self.crud(cmd)  # type: ignore[return-value]

    raise exc.InvalidArgumentsError(f"Unsupported operation: {cmd.operation}")

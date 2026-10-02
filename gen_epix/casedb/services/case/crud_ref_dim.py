"""Handle CRUD operations for reference-dimension entities.

This is a simple metadata entity with no ABAC restrictions.
"""

from typing import cast
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import enum
from gen_epix.casedb.policies.pdp import PolicyDecisionPoint
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    crud_with_access_filter,
)
from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.uuid_set import UuidSetFilter


def case_service_crud_ref_dim(
    self: BaseCaseService, cmd: command.RefDimCrudCommand
) -> list[model.RefDim] | model.RefDim | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for RefDim entities."""

    if cmd.is_read():
        pdp: PolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
        if pdp.is_exempted(cmd):
            return self.crud(cmd)  # type: ignore[return-value]
        access_filter = pdp.get_ref_dim_id_filter(cmd, ref_dim_id_field_name="id")
        with self.repository.uow() as uow:
            retval = crud_with_access_filter(self, uow, cmd, access_filter)
        return retval  # type: ignore[return-value]

    assert cmd.user is not None and cmd.user.id is not None

    if cmd.is_delete():
        return self.crud(cmd)  # type: ignore[return-value]

    if cmd.is_create():
        return self.crud(cmd)  # type: ignore[return-value]

    # Perform some validation on UPDATE
    if cmd.is_update():
        ref_dims: list[model.RefDim] = cmd.get_objs()  # type: ignore[assignment]
        ref_dim_ids = [cast(UUID, x.id) for x in ref_dims if x.id is not None]
        ref_dim_map: dict[UUID, model.RefDim] = {
            cast(UUID, x.id): x for x in ref_dims
        }  # type: ignore[assignment]
        with self.repository.uow() as uow:
            # Get RefCols
            ref_cols: list[model.RefCol] = self.repository.crud(
                uow,
                cmd.user.id,
                model.RefCol,
                CrudOperation.READ_ALL,
                filter=UuidSetFilter(key="ref_dim_id", members=frozenset(ref_dim_ids)),
            )

            # Verify col_type corresponds to dim_type
            invalid_ref_dims = []
            for ref_col in ref_cols:
                ref_dim = ref_dim_map[ref_col.ref_dim_id]
                if (
                    ref_col.col_type
                    not in enum.DimColTypeSet[ref_dim.dim_type.value].value
                ):
                    invalid_ref_dims.append(ref_dim)
            if invalid_ref_dims:
                invalid_ref_dim_ids = list(
                    {cast(UUID, x.id) for x in invalid_ref_dims if x.id is not None}
                )
                raise exc.InvalidArgumentsError(
                    "7ad7a294",
                    "RefDim.dim_type must correspond to dependentRefCols.col_type",
                    ids=invalid_ref_dim_ids,
                )

        return self.crud(cmd)  # type: ignore[return-value]

    raise exc.InvalidArgumentsError(
        "0a65acec", f"Unsupported operation: {cmd.operation}"
    )

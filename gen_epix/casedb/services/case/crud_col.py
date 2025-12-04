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
from gen_epix.fastapp import CrudOperation, CrudOperationSet


def _col_type_matches_dim_type(col_type: enum.ColType, dim_type: enum.DimType) -> bool:
    # Map required correspondence between Dim.dim_type and Col.col_type families
    if dim_type == enum.DimType.TIME:
        return col_type in enum.ColTypeSet.TIME.value
    if dim_type == enum.DimType.GEO:
        return col_type in enum.ColTypeSet.GEO.value
    # Default: any non-TIME/GEO types are considered valid
    return True


def case_service_crud_col(
    self: BaseCaseService, cmd: command.ColCrudCommand
) -> list[model.Col] | model.Col | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for Col entities."""
    if (
        cmd.operation in CrudOperationSet.CREATE.value
        or cmd.operation in CrudOperationSet.UPDATE.value
    ):
        assert cmd.user is not None and cmd.user.id is not None
        cols: list[model.Col] = cmd.get_objs()  # type: ignore[assignment]
        with self.repository.uow() as uow:
            for col in cols:
                # On UPDATE, prevent changing linked Dim (write-once)
                if cmd.operation in CrudOperationSet.UPDATE.value:
                    existing_cols: list[model.Col] = self.repository.crud(  # type: ignore[assignment]
                        uow,
                        cmd.user.id,
                        model.Col,
                        None,
                        [col.id],
                        CrudOperation.READ_SOME,
                    )
                    if not existing_cols:
                        raise exc.InvalidIdsError(
                            f"Invalid Col id provided: {col.id}", ids=[col.id]
                        )
                    existing = existing_cols[0]
                    if col.dim_id != existing.dim_id:
                        raise exc.InvalidArgumentsError(
                            "dim_id is immutable and cannot be updated", ids=[col.id]
                        )

                # Validate col_type matches linked Dim.dim_type
                existing_dims: list[model.Dim] = self.repository.crud(  # type: ignore[assignment]
                    uow,
                    cmd.user.id,
                    model.Dim,
                    None,
                    [col.dim_id],
                    CrudOperation.READ_SOME,
                )
                if not existing_dims:
                    raise exc.InvalidIdsError(
                        f"Invalid dim_id provided: {col.dim_id}", ids=[col.dim_id]
                    )
                dim = existing_dims[0]
                if not _col_type_matches_dim_type(col.col_type, dim.dim_type):
                    raise exc.InvalidArgumentsError(
                        f"col_type {col.col_type.value} must correspond to Dim.dim_type {dim.dim_type.value}",
                        ids=(
                            [col.id]
                            if cmd.operation in CrudOperationSet.UPDATE.value
                            else None
                        ),
                    )
    # Col entities have no ABAC restrictions - use direct crud
    return self.crud(cmd)  # type: ignore[return-value]

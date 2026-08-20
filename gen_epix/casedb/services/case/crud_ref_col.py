"""
CRUD operations for RefCol entities.
This is a simple metadata entity with no ABAC restrictions.
"""

from typing import cast
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


def case_service_crud_ref_col(
    self: BaseCaseService, cmd: command.RefColCrudCommand
) -> list[model.RefCol] | model.RefCol | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for RefCol entities."""
    assert cmd.user is not None and cmd.user.id is not None

    if cmd.is_read():
        ref_data_access = get_ref_data_access_from_command(cmd)
        if ref_data_access is None or ref_data_access.is_full_access:
            # Special case: no policy (implies full access) or explicit full access
            return self.crud(cmd)  # type: ignore[return-value]
        access_filter = ref_data_access.get_ref_col_filter("id")
        # No cascade delete to force conscious decision to delete from other models
        with self.repository.uow() as uow:
            retval = crud_with_access_filter(self, uow, cmd, access_filter)
        return retval  # type: ignore[return-value]

    if cmd.is_delete():
        return self.crud(cmd)  # type: ignore[return-value]

    # Perform some validation on CREATE/UPDATE
    ref_cols: list[model.RefCol] = cmd.get_objs()  # type: ignore[assignment]
    if cmd.is_create():
        with self.repository.uow() as uow:
            # Get dims
            ref_dim_ids = list({x.ref_dim_id for x in ref_cols})
            ref_dims: list[model.RefDim] = self.repository.crud(
                uow,
                cmd.user.id,
                model.RefDim,
                CrudOperation.READ_SOME,
                obj_ids=ref_dim_ids,
            )
            ref_dim_map: dict[UUID, model.RefDim] = {
                x.id: x for x in ref_dims
            }  # type: ignore[assignment]

            # Verify col_type corresponds to dim_type
            invalid_ref_cols = [
                x
                for x in ref_cols
                if x.col_type
                not in enum.DimColTypeSet[
                    ref_dim_map[x.ref_dim_id].dim_type.value
                ].value
            ]
            if invalid_ref_cols:
                invalid_ref_col_ids = [
                    cast(UUID, x.id) for x in invalid_ref_cols if x.id is not None
                ]
                raise exc.InvalidArgumentsError(
                    "f3ddee46",
                    "col_type must correspond to RefDim.dim_type",
                    ids=invalid_ref_col_ids,
                )

            # Verify that unit, if set, corresponds to ConceptSet unit
            _verify_ref_col_concept_set_unit(self, cmd, ref_cols)

        return self.crud(cmd)  # type: ignore[return-value]

    if cmd.is_update():
        with self.repository.uow() as uow:
            existing_ref_cols: list[model.RefCol] = self.repository.crud(
                uow,
                cmd.user.id,
                model.RefCol,
                CrudOperation.READ_SOME,
                obj_ids=[x.id for x in ref_cols],
            )
            for field_name in model.RefCol.IMMUTABLE_FIELDS:  # type: ignore[attr-defined]
                if any(
                    getattr(x, field_name) != getattr(y, field_name)
                    for x, y in zip(ref_cols, existing_ref_cols)
                ):
                    invalid_ref_col_ids = [
                        cast(UUID, x.id)
                        for x, y in zip(ref_cols, existing_ref_cols)
                        if getattr(x, field_name) != getattr(y, field_name)
                    ]
                    raise exc.InvalidArgumentsError(
                        "e9033c17",
                        f"{field_name} is immutable and cannot be updated",
                        ids=invalid_ref_col_ids,
                    )
        return self.crud(cmd)  # type: ignore[return-value]

    raise exc.InvalidArgumentsError(
        "d4d29edb", f"Unsupported operation: {cmd.operation}"
    )


def _verify_ref_col_concept_set_unit(
    self, cmd: command.ConceptSetCrudCommand, ref_cols: list[model.RefCol]
) -> None:
    units = {x.unit for x in ref_cols if x.unit is not None}
    if units:
        concept_set_ids = list(
            {x.concept_set_id for x in ref_cols if x.concept_set_id is not None}
        )
        concept_sets: list[model.ConceptSet] = self.app.handle(
            command.ConceptSetCrudCommand(
                user=cmd.user,
                operation=CrudOperation.READ_SOME,
                obj_ids=concept_set_ids,
            )
        )
        concept_set_map: dict[UUID, model.ConceptSet] = {
            cast(UUID, x.id): x for x in concept_sets
        }
        invalid_ref_cols = [
            x
            for x in ref_cols
            if x.unit is not None
            and x.concept_set_id is not None
            and concept_set_map[x.concept_set_id].unit != x.unit
        ]
        if invalid_ref_cols:
            invalid_ref_col_ids = [x.id for x in invalid_ref_cols if x.id is not None]
            raise exc.InvalidArgumentsError(
                "f3ddee47",
                "RefCol.unit must correspond to ConceptSet.unit",
                ids=invalid_ref_col_ids,
            )

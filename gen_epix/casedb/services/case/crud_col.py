"""Handle CRUD operations for case column entities."""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy.pdp import BasePolicyDecisionPoint
from gen_epix.casedb.policies.pdp import PolicyDecisionPoint
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    crud_with_access_filter,
)
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_col(
    self: BaseCaseService, cmd: command.ColCrudCommand
) -> list[model.Col] | model.Col | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for Col entities."""
    # Start unit of work
    with self.repository.uow() as uow:
        _crud_cascade_delete(self, uow, cmd)
        pdp: BasePolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
        if pdp.is_exempted(cmd):
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
    pdp: PolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
    access_filter = pdp.get_col_id_filter(cmd, col_id_field_name="id")
    # No cascade delete to force conscious decision to delete from other models
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]


def _validate_cols(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.ColCrudCommand,
) -> None:
    """Validate column dimension and reference-column relationships for writes.

    Args:
        self: Case service used for metadata retrieval.
        uow: Active unit of work for validation reads.
        cmd: Column CRUD command to validate.

    Raises:
        InvalidArgumentsError: If a column and dimension have different case types or
            their reference dimension identifiers do not match.
    """
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

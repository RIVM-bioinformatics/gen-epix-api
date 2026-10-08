"""Handle CRUD operations for case-type entities."""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain.policy.pdp import BasePolicyDecisionPoint
from gen_epix.casedb.policies.pdp import PolicyDecisionPoint
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    crud_with_access_filter,
)
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_case_type(
    self: BaseCaseService, cmd: command.CaseTypeCrudCommand
) -> (
    list[model.CaseType] | model.CaseType | list[UUID] | UUID | list[bool] | bool | None
):
    """Handle CRUD operations for CaseType entities."""
    # Start unit of work
    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)
        pdp: BasePolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
        if pdp.is_exempted(cmd):
            result = _crud_case_type_without_abac(self, uow, cmd)
        else:
            result = _crud_case_type_with_abac(self, uow, cmd)

    if not cmd.is_read():
        # Clear retrieve_complete_case_type cache as data has changed, to prevent stale data in subsequent calls
        self._RETRIEVE_COMPLETE_CASE_TYPE_CACHE.clear()  # type: ignore[attr-defined]

    return result


def _crud_case_type_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeCrudCommand,
) -> (
    list[model.CaseType] | model.CaseType | list[UUID] | UUID | list[bool] | bool | None
):
    """CaseType admin command handling, no ABAC applied."""
    return self.crud(cmd)  # type: ignore[return-value]


def _crud_case_type_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeCrudCommand,
) -> (
    list[model.CaseType] | model.CaseType | list[UUID] | UUID | list[bool] | bool | None
):
    """CaseType user command handling, ABAC applied."""
    pdp: PolicyDecisionPoint = self.app.pdp  # type: ignore[assignment]
    access_filter = pdp.get_case_type_id_filter(cmd, case_type_id_field_name="id")
    # No cascade delete to force conscious decision to delete from other models
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]

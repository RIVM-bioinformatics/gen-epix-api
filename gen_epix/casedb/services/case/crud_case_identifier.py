from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    get_case_abac_from_command,
    is_app_admin_or_above,
)
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_case_identifier(
    self: BaseCaseService, cmd: command.CaseIdentifierCrudCommand
) -> (
    list[model.CaseIdentifier]
    | model.CaseIdentifier
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseIdentifier entities."""

    with self.repository.uow() as uow:
        _crud_cascade_delete(self, uow, cmd)
        if cmd.user is None or is_app_admin_or_above(self, cmd.user):
            return _crud_case_identifier_without_abac(self, uow, cmd)
        return _crud_case_identifier_with_abac(self, uow, cmd)


def _crud_case_identifier_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseIdentifierCrudCommand,
) -> (
    list[model.CaseIdentifier]
    | model.CaseIdentifier
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseIdentifier user command handling, no ABAC applied."""
    return self.crud(cmd)  # type: ignore[return-value]


def _crud_case_identifier_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseIdentifierCrudCommand,
) -> (
    list[model.CaseIdentifier]
    | model.CaseIdentifier
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseIdentifier user command handling, ABAC applied."""
    case_abac = get_case_abac_from_command(cmd)

    if case_abac is None:
        return self.crud(cmd)  # type: ignore[return-value]

    # Read all without filter and delete all not allowed due to potential large
    # number of case identifiers
    if (
        (cmd.is_read_all() and not cmd.query_filter)
        or cmd.is_delete_all()
        or cmd.is_update()
    ):
        raise exc.UnauthorizedAuthError(
            "f648da79",
            f"Operation {cmd.operation.value} not allowed for case identifiers for this user",
        )

    # For now, delegate to the main crud method with extensive logic
    # TODO: Implement the complex ABAC logic from the main crud.py file
    # This includes checking case access rights, data collection rights, etc.
    # from gen_epix.casedb.services.case.crud import _crud_data_by_non_admin

    # return _crud_data_by_non_admin(self, uow, cmd)  # type: ignore[return-value]

    # !FIXME: Temporary workaround until the complex ABAC logic is implemented
    return self.crud(cmd)  # type: ignore[return-value]
    return self.crud(cmd)  # type: ignore[return-value]

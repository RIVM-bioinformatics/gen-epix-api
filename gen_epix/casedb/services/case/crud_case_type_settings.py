"""
CRUD operations for CaseTypeSettings entities.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    crud_with_access_filter,
    get_case_abac_from_command,
    is_metadata_admin_or_above,
)
from gen_epix.fastapp import CrudOperation, CrudOperationSet
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_case_type_settings(
    self: BaseCaseService, cmd: command.CaseTypeSettingsCrudCommand
) -> (
    list[model.CaseTypeSettings]
    | model.CaseTypeSettings
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseTypeSettings entities."""

    # Start unit of work
    with self.repository.uow() as uow:
        assert cmd.user is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_metadata_admin_or_above(self, cmd.user):
            return _crud_case_type_settings_by_admin(self, uow, cmd)
        return _crud_case_type_settings_by_non_admin(self, uow, cmd)


def _crud_case_type_settings_by_admin(
    self: BaseCaseService,
    uow,
    cmd: command.CaseTypeSettingsCrudCommand,
) -> (
    list[model.CaseTypeSettings]
    | model.CaseTypeSettings
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeSettings admin command handling, no ABAC applied."""
    # Validate CaseTypeSettings on create/update
    if (
        cmd.operation in CrudOperationSet.CREATE.value
        or cmd.operation in CrudOperationSet.UPDATE.value
    ):
        assert cmd.user is not None and cmd.user.id is not None
        settings_list: list[model.CaseTypeSettings] = cmd.get_objs()  # type: ignore[assignment]
        for settings in settings_list:
            _validate_case_type_settings(self, uow, cmd.user.id, settings)

    # Perform the primary CRUD operation
    retval = self.crud(cmd)
    return retval  # type:ignore[return-value]


def _crud_case_type_settings_by_non_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeSettingsCrudCommand,
) -> (
    list[model.CaseTypeSettings]
    | model.CaseTypeSettings
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeSettings user command handling, ABAC applied."""
    # @ABAC: get case abac
    case_abac = get_case_abac_from_command(cmd)

    # Special case: no policy, allows for internal commands to retrieve all
    if not case_abac:
        # No policy: allows for internal commands to retrieve all
        return self.crud(cmd)  # type:ignore[return-value]

    # Initialize some
    is_read = cmd.operation in CrudOperationSet.READ_OR_EXISTS.value

    if not is_read:
        # Only read operations are allowed for metadata commands for these
        # users
        raise AssertionError("Unexpected operation")

    # Allow reading settings only for case types the user has any rights to
    valid_case_type_ids = case_abac.get_case_types_with_any_rights()
    access_filter = self._compose_id_filter(("case_type_id", valid_case_type_ids))
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]


def _validate_case_type_settings(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    user_id: UUID,
    settings: model.CaseTypeSettings,
) -> None:
    """Validate CaseTypeSettings for TIME and GEO dimensions."""
    case_type_cols: list[model.CaseTypeCol] = self.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.CaseTypeCol,
        None,
        None,
        CrudOperation.READ_ALL,
        filter=self._compose_id_filter(("case_type_id", {settings.case_type_id})),
    )
    col_ids = {x.col_id for x in case_type_cols}

    def _read_col(col_id: UUID) -> model.Col:
        cols: list[model.Col] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user_id,
            model.Col,
            None,
            [col_id],
            CrudOperation.READ_SOME,
        )
        if not cols:
            raise exc.InvalidIdsError(
                f"Invalid col id provided: {col_id}", ids=[col_id]
            )
        return cols[0]

    # Both dims (TIME/GEO) must belong to a Col used by at least one CaseTypeCol
    # of the specified CaseType, and must have the correct dim_type (TIME/GEO).
    # Validate TIME dim
    if settings.stats_time_case_type_col_id is not None:
        if settings.stats_time_case_type_col_id not in col_ids:
            raise exc.InvalidArgumentsError(
                f"stats_time_dim_id {settings.stats_time_case_type_col_id} must belong to a column of the case type",
                ids=[settings.stats_time_case_type_col_id],
            )
        col_time = _read_col(settings.stats_time_case_type_col_id)
        if col_time.col_type not in {
            x for x in enum.ColType if x.name.startswith("TIME_")
        }:
            raise exc.InvalidArgumentsError(
                f"stats_time_dim_id {settings.stats_time_case_type_col_id} must reference a TIME dimension",
                ids=[settings.stats_time_case_type_col_id],
            )

    # Validate GEO dim
    if settings.stats_geo_case_type_col_id is not None:
        if settings.stats_geo_case_type_col_id not in col_ids:
            raise exc.InvalidArgumentsError(
                f"stats_geo_dim_id {settings.stats_geo_case_type_col_id} must belong to a column of the case type",
                ids=[settings.stats_geo_case_type_col_id],
            )
        col_geo = _read_col(settings.stats_geo_case_type_col_id)
        if col_geo.col_type not in {
            x for x in enum.ColType if x.name.startswith("GEO_")
        }:
            raise exc.InvalidArgumentsError(
                f"stats_geo_dim_id {settings.stats_geo_case_type_col_id} must reference a GEO dimension",
                ids=[settings.stats_geo_case_type_col_id],
            )

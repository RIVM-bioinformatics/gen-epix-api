from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    crud_with_access_filter,
    get_case_abac_from_command,
    is_metadata_admin_or_above,
)
from gen_epix.fastapp import CrudOperation, CrudOperationSet
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_case_type_dim(
    self: BaseCaseService, cmd: command.CaseTypeDimCrudCommand
) -> (
    list[model.CaseTypeDim]
    | model.CaseTypeDim
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for CaseTypeDim entities."""

    with self.repository.uow() as uow:
        assert cmd.user is not None and cmd.user.id is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_metadata_admin_or_above(self, cmd.user):
            return _crud_case_type_dim_by_admin(self, uow, cmd)
        return _crud_case_type_dim_by_non_admin(self, uow, cmd)


def _crud_case_type_dim_by_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeDimCrudCommand,
) -> (
    list[model.CaseTypeDim]
    | model.CaseTypeDim
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeDim admin command handling, no ABAC applied."""
    case_type_dim_list: list[model.CaseTypeDim] = cmd.get_objs()  # type: ignore[assignment]
    if cmd.operation in CrudOperationSet.CREATE.value:
        _crud_create_case_type_dim(case_type_dim_list, cmd, self, uow)

    if cmd.operation in CrudOperationSet.UPDATE.value:
        _crud_update_case_type_dim(case_type_dim_list, cmd, self, uow)

    # Perform the primary CRUD operation
    retval = self.crud(cmd)
    return retval  # type:ignore[return-value]


def _crud_create_case_type_dim(
    case_type_dim_list: list[model.CaseTypeDim],
    cmd: command.CaseTypeDimCrudCommand,
    self: BaseCaseService,
    uow: BaseUnitOfWork,
) -> None:
    """
    Apply validation logic for CaseTypeDim creation:
    - Check if other CaseTypeDims for the same CaseType and Dim exist
    - Check if is_time_stats_dim or is_geo_stats_dim is True
        and that the linked Dim is of correct type
    - Check if another CaseTypeDim for the same CaseType has
        is_time_stats_dim or is_geo_stats_dim set to True
    """
    for case_type_dim in case_type_dim_list:
        existing_dims: list[model.CaseTypeDim] = (
            self.repository.crud(  # type:ignore[assignment]
                uow,
                cmd.user.id,
                model.CaseTypeDim,
                None,
                None,
                CrudOperation.READ_ALL,
                filter=self._compose_id_filter(
                    ("case_type_id", {case_type_dim.case_type_id}),
                    ("dim_id", {case_type_dim.dim_id}),
                ),
            )
        )

        if not existing_dims:
            case_type_dim.occurrence = 1
        else:
            max_occ = max(x.occurrence for x in existing_dims)
            case_type_dim.occurrence = max_occ + 1

        # Dim type check for stats dims
        if case_type_dim.is_time_stats_dim or case_type_dim.is_geo_stats_dim:
            dim: model.Dim | None = None
            dim_list: list[model.Dim] = self.repository.crud(  # type:ignore[assignment]
                uow,
                cmd.user.id,
                model.Dim,
                None,
                [case_type_dim.dim_id],
                CrudOperation.READ_SOME,
            )
            if not dim_list:
                raise exc.InvalidIdsError(
                    f"Invalid dim_id provided: {case_type_dim.dim_id}",
                    ids=[case_type_dim.dim_id],
                )
            dim = dim_list[0]
            if case_type_dim.is_time_stats_dim and dim.dim_type != enum.DimType.TIME:
                raise exc.InvalidArgumentsError(
                    f"Dim {dim.code} must be of type TIME for is_time_stats_dim=True",
                    ids=[case_type_dim.dim_id],
                )
            if case_type_dim.is_geo_stats_dim and dim.dim_type != enum.DimType.GEO:
                raise exc.InvalidArgumentsError(
                    f"Dim {dim.code} must be of type GEO for is_geo_stats_dim=True",
                    ids=[case_type_dim.dim_id],
                )

        # Only one stats dim per case type
        if case_type_dim.is_time_stats_dim:
            other_time_dims: list[model.CaseTypeDim] = (
                self.repository.crud(  # type:ignore[assignment]
                    uow,
                    cmd.user.id,
                    model.CaseTypeDim,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    filter=self._compose_id_filter(
                        ("case_type_id", {case_type_dim.case_type_id})
                    ),
                )
            )
            # filter columns that have is_time_stats_dim = True
            other_time_dims = [x for x in other_time_dims if x.is_time_stats_dim]
            for other in other_time_dims:
                if other.id != case_type_dim.id:
                    # Set other to False
                    other.is_time_stats_dim = False
                    self.repository.crud(
                        uow,
                        cmd.user.id,
                        model.CaseTypeDim,
                        other,
                        [other.id],
                        CrudOperation.UPDATE_ONE,
                    )
        if case_type_dim.is_geo_stats_dim:
            other_geo_dims: list[model.CaseTypeDim] = (
                self.repository.crud(  # type:ignore[assignment]
                    uow,
                    cmd.user.id,
                    model.CaseTypeDim,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    filter=self._compose_id_filter(
                        ("case_type_id", {case_type_dim.case_type_id}),
                    ),
                )
            )
            # filter columns that have is_geo_stats_dim = True
            other_geo_dims = [x for x in other_geo_dims if x.is_geo_stats_dim]
            for other in other_geo_dims:
                if other.id != case_type_dim.id:
                    other.is_geo_stats_dim = False
                    self.repository.crud(
                        uow,
                        cmd.user.id,
                        model.CaseTypeDim,
                        other,
                        [other.id],
                        CrudOperation.UPDATE_ONE,
                    )


def _crud_update_case_type_dim(
    case_type_dim_list: list[model.CaseTypeDim],
    cmd: command.CaseTypeDimCrudCommand,
    self: BaseCaseService,
    uow: BaseUnitOfWork,
) -> None:
    """
    Apply validation logic for CaseTypeDim updates:
    - Check if the linked Dim may not be updated (write-once)
    - Check if another CaseTypeDim for the same CaseType has
        is_time_stats_dim or is_geo_stats_dim set to True
    """
    for updated in case_type_dim_list:
        # Read current stored entity to compare immutable fields
        existing_list: list[model.CaseTypeDim] = (
            self.repository.crud(  # type:ignore[assignment]
                uow,
                cmd.user.id,
                model.CaseTypeDim,
                None,
                [updated.id],
                CrudOperation.READ_SOME,
            )
        )
        if not existing_list:
            raise exc.InvalidIdsError(
                f"Invalid CaseTypeDim id provided: {updated.id}", ids=[updated.id]
            )
        existing = existing_list[0]

        # Prevent changing linked Dim (write-once)
        if updated.dim_id != existing.dim_id:
            raise exc.InvalidArgumentsError(
                "dim_id is immutable and cannot be updated", ids=[updated.id]
            )

        # Ensure exclusivity for is_time_stats_dim within same CaseType
        if updated.is_time_stats_dim:
            other_time_dims: list[model.CaseTypeDim] = (
                self.repository.crud(  # type:ignore[assignment]
                    uow,
                    cmd.user.id,
                    model.CaseTypeDim,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    filter=self._compose_id_filter(
                        ("case_type_id", {existing.case_type_id}),
                    ),
                )
            )
            # filter dims that have is_time_stats_dim = True
            other_time_dims = [x for x in other_time_dims if x.is_time_stats_dim]
            for other in other_time_dims:
                if other.id != updated.id:
                    other.is_time_stats_dim = False
                    self.repository.crud(
                        uow,
                        cmd.user.id,
                        model.CaseTypeDim,
                        other,
                        [other.id],
                        CrudOperation.UPDATE_ONE,
                    )

        # Ensure exclusivity for is_geo_stats_dim within same CaseType
        if updated.is_geo_stats_dim:
            other_geo_dims: list[model.CaseTypeDim] = (
                self.repository.crud(  # type:ignore[assignment]
                    uow,
                    cmd.user.id,
                    model.CaseTypeDim,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    filter=self._compose_id_filter(
                        ("case_type_id", {existing.case_type_id}),
                    ),
                )
            )
            # filter dims that have is_geo_stats_dim = True
            other_geo_dims = [x for x in other_geo_dims if x.is_geo_stats_dim]
            for other in other_geo_dims:
                if other.id != updated.id:
                    other.is_geo_stats_dim = False
                    self.repository.crud(
                        uow,
                        cmd.user.id,
                        model.CaseTypeDim,
                        other,
                        [other.id],
                        CrudOperation.UPDATE_ONE,
                    )


def _crud_case_type_dim_by_non_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CaseTypeDimCrudCommand,
) -> (
    list[model.CaseTypeDim]
    | model.CaseTypeDim
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """CaseTypeDim user command handling, ABAC applied."""
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

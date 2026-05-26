from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.crud_common import (
    _crud_cascade_delete,
    _verify_is_read_operation,
    crud_with_access_filter,
    get_ref_data_access_from_command,
    is_refdata_admin_or_above,
)
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_crud_dim(
    self: BaseCaseService, cmd: command.DimCrudCommand
) -> list[model.Dim] | model.Dim | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for Dim entities."""

    with self.repository.uow() as uow:
        assert cmd.user is not None and cmd.user.id is not None
        _crud_cascade_delete(self, uow, cmd)
        if is_refdata_admin_or_above(self, cmd.user):
            return _crud_dim_without_abac(self, uow, cmd)
        return _crud_dim_with_abac(self, uow, cmd)


def _crud_dim_without_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.DimCrudCommand,
) -> list[model.Dim] | model.Dim | list[UUID] | UUID | list[bool] | bool | None:
    """Dim admin command handling, no ABAC applied."""
    dims: list[model.Dim] = cmd.get_objs()  # type: ignore[assignment]
    if cmd.is_create():
        _crud_create_dim(dims, cmd, self, uow)

    if cmd.is_update():
        _crud_update_dim(dims, cmd, self, uow)

    # Perform the primary CRUD operation
    retval = self.crud(cmd)
    return retval  # type: ignore[return-value]


def _crud_create_dim(
    dims: list[model.Dim],
    cmd: command.DimCrudCommand,
    self: BaseCaseService,
    uow: BaseUnitOfWork,
) -> None:
    """
    Apply validation logic for Dim creation:
    - Check if other Dims for the same CaseType and RefDim exist
    - Check if is_time_stats_dim or is_geo_stats_dim is True
        and that the linked RefDim is of correct type
    - Check if another Dim for the same CaseType has
        is_time_stats_dim or is_geo_stats_dim set to True
    """
    for dim in dims:
        existing_dims = _load_existing_dims(self, cmd, uow, dim)
        _set_dim_occurrence(dim, existing_dims)
        # Dimension type check for case date Dim
        if dim.is_case_date_dim:
            _validate_case_date_dim(self, cmd, uow, dim)
        # Only one case date Dim per CaseType
        if dim.is_case_date_dim:
            _verify_one_case_date_dim(self, cmd, uow, dim)


def _verify_one_case_date_dim(
    self: BaseCaseService,
    cmd: command.DimCrudCommand,
    uow: BaseUnitOfWork,
    dim: model.Dim,
) -> None:
    """
    Method to ensure only one case_date_dim per CaseType.
    If another is found, set its is_case_date_dim to False.
    """
    other_time_dims: list[model.Dim] = self.repository.crud(
        uow,
        cmd.user.id,
        model.Dim,
        CrudOperation.READ_ALL,
        filter=self._compose_id_filter(("case_type_id", {dim.case_type_id})),
    )
    # filter columns that have is_case_date_dim = True
    other_time_dims = [x for x in other_time_dims if x.is_case_date_dim]
    for other in other_time_dims:
        if other.id != dim.id:
            # Set other to False
            other.is_case_date_dim = False
            self.repository.crud(
                uow,
                cmd.user.id,
                model.Dim,
                CrudOperation.UPDATE_ONE,
                objs=other,
            )


def _validate_case_date_dim(
    self: BaseCaseService,
    cmd: command.DimCrudCommand,
    uow: BaseUnitOfWork,
    dim: model.Dim,
) -> None:
    ref_dim: model.RefDim | None = None
    ref_dim_list: list[model.RefDim] = self.repository.crud(
        uow,
        cmd.user.id,
        model.RefDim,
        CrudOperation.READ_SOME,
        obj_ids=[dim.ref_dim_id],
    )
    if not ref_dim_list:
        raise exc.InvalidIdsError(
            "15c892da",
            f"Invalid ref_dim_id provided: {dim.ref_dim_id}",
            ids=[dim.ref_dim_id],
        )
    ref_dim = ref_dim_list[0]
    if dim.is_case_date_dim and ref_dim.dim_type != enum.DimType.TIME:
        raise exc.InvalidArgumentsError(
            "4cb4593f",
            f"RefDim {ref_dim.code} must be of type TIME for is_case_date_dim=True",
            ids=[dim.ref_dim_id],
        )


def _set_dim_occurrence(dim: model.Dim, existing_dims: list[model.Dim]) -> None:
    if not existing_dims:
        dim.occurrence = 1
    else:
        max_occ = max(x.occurrence for x in existing_dims)
        dim.occurrence = max_occ + 1


def _load_existing_dims(
    self: BaseCaseService,
    cmd: command.DimCrudCommand,
    uow: BaseUnitOfWork,
    dim: model.Dim,
) -> list[model.Dim]:
    existing_dims: list[model.Dim] = self.repository.crud(
        uow,
        cmd.user.id,
        model.Dim,
        CrudOperation.READ_ALL,
        filter=self._compose_id_filter(
            ("case_type_id", {dim.case_type_id}),
            ("ref_dim_id", {dim.ref_dim_id}),
        ),
    )

    return existing_dims


def _crud_update_dim(
    dims: list[model.Dim],
    cmd: command.DimCrudCommand,
    self: BaseCaseService,
    uow: BaseUnitOfWork,
) -> None:
    """
    Apply validation logic for Dim updates:
    - Check if the linked RefDim may not be updated (write-once)
    - Check if another Dim for the same CaseType has
        is_time_stats_dim or is_geo_stats_dim set to True
    """
    for updated_dim in dims:
        # Read current stored entity to compare immutable fields
        existing_dim = _get_existing_dim(self, cmd, uow, updated_dim)
        # Prevent changing linked RefDim (write-once)
        if updated_dim.ref_dim_id != existing_dim.ref_dim_id:
            raise exc.InvalidArgumentsError(
                "1e9e2644",
                "ref_dim_id is immutable and cannot be updated",
                ids=[updated_dim.id],
            )
        # Ensure exclusivity for is_case_date_dim within same CaseType
        if updated_dim.is_case_date_dim:
            _verify_one_case_date_dim(self, cmd, uow, updated_dim)

        # TODO: Implement is_geo_dim field in Dim
        # # Ensure exclusivity for is_geo_stats_dim within same CaseType
        # if updated_dim.is_geo_stats_dim:
        #     other_geo_dims: list[model.Dim] = (
        #         self.repository.crud(  # type:ignore[assignment]
        #             uow,
        #             cmd.user.id,
        #             model.Dim,
        #             None,
        #             None,
        #             CrudOperation.READ_ALL,
        #             filter=self._compose_id_filter(
        #                 ("case_type_id", {existing_dim.case_type_id}),
        #             ),
        #         )
        #     )
        #     # filter dims that have is_geo_stats_dim = True
        #     other_geo_dims = [x for x in other_geo_dims if x.is_geo_stats_dim]
        #     for other in other_geo_dims:
        #         if other.id != updated_dim.id:
        #             other.is_geo_stats_dim = False
        #             self.repository.crud(
        #                 uow,
        #                 cmd.user.id,
        #                 model.Dim,
        #                 other,
        #                 [other.id],
        #                 CrudOperation.UPDATE_ONE,
        #             )


def _get_existing_dim(
    self: BaseCaseService,
    cmd: command.DimCrudCommand,
    uow: BaseUnitOfWork,
    updated: model.Dim,
) -> model.Dim:
    existing_list: list[model.Dim] = self.repository.crud(
        uow,
        cmd.user.id,
        model.Dim,
        CrudOperation.READ_SOME,
        obj_ids=[updated.id],
    )
    if not existing_list:
        raise exc.InvalidIdsError(
            "0813d763", f"Invalid Dim ID provided: {updated.id}", ids=[updated.id]
        )
    existing = existing_list[0]
    return existing


def _crud_dim_with_abac(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.DimCrudCommand,
) -> list[model.Dim] | model.Dim | list[UUID] | UUID | list[bool] | bool | None:
    """Dim user command handling, ABAC applied."""
    ref_data_access = get_ref_data_access_from_command(cmd)
    if ref_data_access is None or ref_data_access.is_full_access:
        # Special case: no policy (implies full access) or explicit full access
        return self.crud(cmd)  # type: ignore[return-value]
    _verify_is_read_operation(cmd)
    # Perform CRUD with access filter applied
    access_filter = ref_data_access.get_dim_filter("id")
    return crud_with_access_filter(self, uow, cmd, access_filter)  # type: ignore[return-value]

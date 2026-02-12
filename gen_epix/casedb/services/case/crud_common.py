"""
Common utilities and functions for CRUD operations across all case entities.
This module contains shared logic that can be used by multiple CRUD operations.
"""

from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.domain.service import BaseCaseService as DomainBaseCaseService
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.commondb.enum import RoleSet as CommonRoleSet
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation, CrudOperationSet
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.filter import CompositeFilter, Filter, LogicalOperator


def get_case_abac_from_command(cmd: command.CrudCommand) -> model.CaseAbac | None:
    """Get case ABAC policy from command."""
    return BaseCaseAbacPolicy.get_case_abac_from_command(cmd)


def is_metadata_admin_or_above(service: BaseCaseService, user: model.User) -> bool:
    """Check if user has metadata admin or above privileges."""
    return bool(
        user.roles.intersection(service.role_set_map[CommonRoleSet.GE_REFDATA_ADMIN])
    )


def is_app_admin_or_above(service: BaseCaseService, user: model.User) -> bool:
    """Check if user has app admin or above privileges."""
    return bool(
        user.roles.intersection(service.role_set_map[CommonRoleSet.GE_APP_ADMIN])
    )


def is_no_abac_command(cmd: command.CrudCommand) -> bool:
    """Check if command has no ABAC restrictions."""
    return any(
        isinstance(cmd, x) for x in DomainBaseCaseService.NO_ABAC_COMMAND_CLASSES
    )


def is_metadata_command(cmd: command.CrudCommand) -> bool:
    """Check if command is a metadata command."""
    return any(
        isinstance(cmd, x) for x in DomainBaseCaseService.ABAC_METADATA_COMMAND_CLASSES
    )


def is_data_command(cmd: command.CrudCommand) -> bool:
    """Check if command is a data command."""
    return any(
        isinstance(cmd, x) for x in DomainBaseCaseService.ABAC_DATA_COMMAND_CLASSES
    )


def crud_with_access_filter(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CrudCommand,
    access_filter: Filter | None = None,
    cascade_if_delete: bool = False,
) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
    """Execute CRUD operation with access filter applied."""
    # Set access filter if any and call generic crud
    orig_access_filter = cmd.access_filter
    if access_filter:
        if cmd.access_filter:
            cmd.access_filter = CompositeFilter(
                filters=[cmd.access_filter, access_filter],
                operator=LogicalOperator.AND,
            )
        else:
            cmd.access_filter = access_filter
    if cascade_if_delete:
        _crud_cascade_delete(self, uow, cmd)
    retval = self.crud(cmd)
    cmd.access_filter = orig_access_filter
    return retval  # type: ignore[return-value]


def _crud_cascade_delete(
    self: BaseCaseService, uow: BaseUnitOfWork, cmd: command.CrudCommand
) -> None:
    """
    In case of a delete operation, cascade delete all instances of any
    linked_model_classes that are linked to the instances in cmd.
    """
    if cmd.operation not in CrudOperationSet.DELETE.value:
        return

    # Find linked model classes for cascade delete
    model_class: type[model.Model] = cmd.MODEL_CLASS  # type: ignore[assignment]
    link_model_classes = self.CASCADE_DELETE_MODEL_CLASSES.get(model_class)
    if link_model_classes is None:
        is_found = False
        matched_link_classes: tuple[type[model.Model], ...] | None = None
        for (
            model_base_class,
            link_model_classes,
        ) in self.CASCADE_DELETE_MODEL_CLASSES.items():
            if issubclass(model_class, model_base_class):
                is_found = True
                matched_link_classes = link_model_classes
                break
        if is_found and matched_link_classes is not None:
            self.CASCADE_DELETE_MODEL_CLASSES[model_class] = matched_link_classes
            link_model_classes = matched_link_classes
        else:
            self.CASCADE_DELETE_MODEL_CLASSES[model_class] = ()
            link_model_classes = ()

    # Handle no linked model classes to cascade delete
    if not link_model_classes:
        return

    # Go over each link_model_class and delete all instances that are linked to
    # the instances in cmd
    obj_ids: set[UUID] | None = cmd.get_obj_ids(as_set=True)  # type: ignore[assignment]
    assert cmd.user is not None and cmd.user.id is not None
    _cascade_delete_linked_models(
        self, uow, cmd, model_class, link_model_classes, obj_ids
    )


def _cascade_delete_linked_models(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CrudCommand,
    model_class: type[model.Model],
    link_model_classes: tuple[type[model.Model], ...],
    obj_ids: set[UUID] | None,
) -> None:
    for link_model_class in link_model_classes:
        entity: Entity = link_model_class.ENTITY  # type: ignore[assignment]
        for link in entity.links.values():
            if link.link_model_class != model_class:
                continue
            # Delete all linked instances
            self.repository.crud(
                uow,
                cmd.user.id,  # type: ignore[union-attr]
                link_model_class,
                None,
                None,
                CrudOperation.DELETE_ALL,
                filter=(
                    self._compose_id_filter((link.link_field_name, obj_ids))
                    if obj_ids is not None
                    else None
                ),
            )


def _get_linked_model_classes(
    self: BaseCaseService, model_class: type[model.Model]
) -> tuple[type[model.Model], ...]:
    link_model_classes = self.CASCADE_DELETE_MODEL_CLASSES.get(model_class)
    if link_model_classes is None:
        is_found = False
        for (
            model_base_class,
            link_model_classes,
        ) in self.CASCADE_DELETE_MODEL_CLASSES.items():
            if issubclass(model_class, model_base_class):
                # Add subclass to dict for next time
                is_found = True
                self.CASCADE_DELETE_MODEL_CLASSES[model_class] = link_model_classes
        if not is_found:
            # Add to dict for next time
            self.CASCADE_DELETE_MODEL_CLASSES[model_class] = ()

    assert link_model_classes is not None
    return link_model_classes

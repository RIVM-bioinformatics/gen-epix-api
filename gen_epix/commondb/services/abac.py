from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from cachetools import TTLCache, cached

from gen_epix.commondb import policies
from gen_epix.commondb import policies as policies
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, enum, exc, model, policy
from gen_epix.commondb.domain.policy import BaseReadOrganizationResultsOnlyPolicy
from gen_epix.commondb.domain.repository.abac import BaseAbacRepository
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.fastapp import App, CrudOperation
from gen_epix.fastapp.enum import EventTiming
from gen_epix.fastapp.model import Command, CrudCommand, Policy
from gen_epix.filter import (
    CompositeFilter,
    EqualsBooleanFilter,
    EqualsUuidFilter,
    LogicalOperator,
)


class AbacService(BaseAbacService):

    CACHE_INVALIDATION_COMMANDS: tuple[type[Command], ...] = tuple()

    def __init__(
        self,
        app: App,
        repository: BaseAbacRepository,
        logger: logging.Logger | None = None,
        setup_logger: logging.Logger | None = None,
        **kwargs: Any,
    ):
        super().__init__(
            app,
            repository=repository,
            logger=logger,
            setup_logger=setup_logger,
            **kwargs,
        )
        app_impl: AppImplDetails = app.impl
        self.organization_admin_policy_model_class: type[
            model.OrganizationAdminPolicy
        ] = app_impl.get_mapped_class(model.OrganizationAdminPolicy)
        self.user_crud_command_class: type[command.UserCrudCommand] = (
            app_impl.get_mapped_class(command.UserCrudCommand)
        )
        self.is_organization_admin_policy_class: type[
            policy.BaseIsOrganizationAdminPolicy
        ] = app_impl.get_mapped_class(policies.IsOrganizationAdminPolicy)
        self.read_organization_results_only_policy_class: type[
            policy.BaseReadOrganizationResultsOnlyPolicy
        ] = app_impl.get_mapped_class(policies.ReadOrganizationResultsOnlyPolicy)
        self.read_self_results_only_policy_class: type[
            policy.BaseReadSelfResultsOnlyPolicy
        ] = app_impl.get_mapped_class(policies.ReadSelfResultsOnlyPolicy)
        self.read_user_policy_class: type[policy.BaseReadUserPolicy] = (
            app_impl.get_mapped_class(policies.ReadUserPolicy)
        )
        self.update_user_policy_class: type[policy.BaseUpdateUserPolicy] = (
            app_impl.get_mapped_class(policies.UpdateUserPolicy)
        )
        self.role_map = app_impl.role_map
        self.role_set_map = app_impl.role_set_map

    def crud(self, cmd: CrudCommand) -> Any:
        retval = super().crud(cmd)
        # Invalidate cache
        if issubclass(type(cmd), AbacService.CACHE_INVALIDATION_COMMANDS):
            self._get_user_by_id_cached.cache_clear()
        return retval

    def register_policies(
        self,
        organization_admin_write_commands: set[type[Command]] | None = None,
        read_user_commands: set[type[Command]] | None = None,
        update_user_commands: set[type[Command]] | None = None,
        read_organization_results_only_commands: set[type[Command]] | None = None,
        read_self_results_only_commands: set[type[Command]] | None = None,
    ) -> None:
        organization_admin_write_commands = (
            organization_admin_write_commands or self.ORGANIZATION_ADMIN_WRITE_COMMANDS
        )
        read_user_commands = read_user_commands or self.READ_USER_COMMANDS
        update_user_commands = update_user_commands or self.UPDATE_USER_COMMANDS
        read_organization_results_only_commands = (
            read_organization_results_only_commands
            or self.READ_ORGANIZATION_RESULTS_ONLY_COMMANDS
        )
        read_self_results_only_commands = (
            read_self_results_only_commands or self.READ_SELF_RESULTS_ONLY_COMMANDS
        )
        f = self.app.register_policy
        policy: Policy
        command_class: type[Command]
        policy = self.is_organization_admin_policy_class(self)
        for command_class in organization_admin_write_commands:
            f(command_class, policy, EventTiming.BEFORE)
        policy = self.read_user_policy_class(self)
        for command_class in read_user_commands:
            f(command_class, policy, EventTiming.AFTER)
        policy = self.update_user_policy_class(self)
        for command_class in update_user_commands:
            f(command_class, policy, EventTiming.BEFORE)
        policy = self.read_organization_results_only_policy_class(self)
        for command_class in read_organization_results_only_commands:
            f(command_class, policy, EventTiming.DURING)
            f(command_class, policy, EventTiming.AFTER)
        policy = self.read_self_results_only_policy_class(self)
        for command_class in read_self_results_only_commands:
            f(command_class, policy, EventTiming.AFTER)

    def retrieve_organizations_under_admin(
        self, cmd: command.RetrieveOrganizationsUnderAdminCommand
    ) -> set[UUID]:
        assert cmd.user and cmd.user.id
        # Special case: user has a role that makes them admin of all organizations
        is_all_organizations = False
        for policy in cmd._policies:
            if isinstance(policy, BaseReadOrganizationResultsOnlyPolicy):
                is_all_organizations = (
                    len(
                        cmd.user.roles.intersection(
                            policy.role_set_map[enum.RoleSet.GE_APP_ADMIN]
                        )
                    )
                    > 0
                )
                break
        if is_all_organizations:
            organizations: list[model.Organization] = self.app.handle(
                command.OrganizationCrudCommand(
                    user=cmd.user,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                )
            )
            return {x.id for x in organizations}  # type: ignore[misc]
        # Retrieve organizations for which the user is an admin
        with self.repository.uow() as uow:
            organization_admin_policies: list[model.OrganizationAdminPolicy] = (
                self.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id=cmd.user.id,
                    model_class=self.organization_admin_policy_model_class,
                    objs=None,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    filter=CompositeFilter(
                        operator=LogicalOperator.AND,
                        filters=[
                            EqualsUuidFilter(key="user_id", value=cmd.user.id),
                            EqualsBooleanFilter(key="is_active", value=True),
                        ],
                    ),
                )
            )
        return set(x.organization_id for x in organization_admin_policies)

    def retrieve_organization_admin_name_emails(
        self,
        cmd: command.RetrieveOrganizationAdminNameEmailsCommand,
    ) -> list[model.UserNameEmail]:
        if not isinstance(cmd.user, model.User):
            raise exc.ServiceException(
                "Command has no or wrong user type: {cmd.user.__class__.__name__}"
            )
        with self.repository.uow() as uow:
            organization_admin_policies: list[model.OrganizationAdminPolicy] = (
                self.repository.crud(  # type: ignore[assignment]
                    uow,
                    user_id=cmd.user.id,
                    model_class=self.organization_admin_policy_model_class,
                    objs=None,
                    obj_ids=None,
                    operation=CrudOperation.READ_ALL,
                    filter=EqualsUuidFilter(
                        key="organization_id", value=cmd.user.organization_id
                    ),
                )
            )
        organization_admin_user_ids = {
            x.user_id
            for x in organization_admin_policies
            if x.organization_id == cmd.user.organization_id and x.is_active
        }
        users = self.app.handle(
            self.user_crud_command_class(
                user=cmd.user,
                obj_ids=list(organization_admin_user_ids),
                operation=CrudOperation.READ_SOME,
            )
        )
        return [
            model.UserNameEmail(
                id=x.id,
                name=x.name,
                email=x.email,
            )
            for x in users
        ]

    def update_user_own_organization(
        self,
        cmd: command.UpdateUserOwnOrganizationCommand,
    ) -> model.User:
        """
        Behaviour:
        - Update User.organization
        - Delete any OrganizationAdminPolicy for the user and their previous
          organization
        """
        if not self.app.get_feature_flag("update_own_organization"):
            raise exc.FeatureDisabledServiceError(
                "Updating own organization is disabled"
            )

        is_new_user = cmd.is_new_user
        tgt_organization_id = cmd.organization_id
        assert cmd.user is not None
        user: model.User = cmd.user
        assert user.id is not None

        # Special case: new organization is same as current
        if user.organization_id == tgt_organization_id and not is_new_user:
            return user

        with self.repository.uow() as uow:
            # Delete any OrganizationAdminPolicy for the user and their previous organization
            if not is_new_user:
                self.repository.crud(
                    uow,
                    user.id,
                    self.organization_admin_policy_model_class,
                    None,
                    None,
                    CrudOperation.DELETE_ALL,
                    filter=CompositeFilter(
                        operator=LogicalOperator.AND,
                        filters=[
                            EqualsUuidFilter(key="user_id", value=user.id),
                            EqualsUuidFilter(
                                key="organization_id", value=user.organization_id
                            ),
                        ],
                    ),
                )
            # Change the user organization
            updated_user = user.model_copy()
            updated_user.organization_id = tgt_organization_id
            user = self.app.handle(
                self.user_crud_command_class(
                    user=user,
                    objs=updated_user,
                    operation=CrudOperation.UPDATE_ONE,
                )
            )

        # Invalidate cache
        # TODO: develop general system for caching and cache invalidation
        self._get_user_by_id_cached.cache_clear()
        return user

    @cached(cache=TTLCache(maxsize=1024, ttl=300))
    def _get_user_by_id_cached(self, user_id: UUID) -> model.User:
        user: model.User = self.app.handle(
            self.user_crud_command_class(
                user=None,
                obj_ids=user_id,
                operation=CrudOperation.READ_ONE,
            )
        )
        return user

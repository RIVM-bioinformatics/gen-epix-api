from __future__ import annotations

import logging
from typing import Any, Type
from uuid import UUID

from cachetools import TTLCache, cached

from gen_epix.commondb import policies as policies
from gen_epix.commondb.domain import command, enum, exc, model, policy
from gen_epix.commondb.domain.repository.abac import BaseAbacRepository
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.commondb.policies.read_organization_results_only_policy import (
    ReadOrganizationResultsOnlyPolicy,
)
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.app import App
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
        organization_admin_policy_model_class: type[
            model.OrganizationAdminPolicy
        ] = model.OrganizationAdminPolicy,
        user_crud_command_class: type[
            command.UserCrudCommand
        ] = command.UserCrudCommand,
        is_organization_admin_policy_class: type[
            policy.BaseIsOrganizationAdminPolicy
        ] = policies.IsOrganizationAdminPolicy,
        read_organization_results_only_policy_class: type[
            policy.BaseReadOrganizationResultsOnlyPolicy
        ] = policies.ReadOrganizationResultsOnlyPolicy,
        read_self_results_only_policy_class: type[
            policy.BaseReadSelfResultsOnlyPolicy
        ] = policies.ReadSelfResultsOnlyPolicy,
        read_user_policy_class: type[
            policy.BaseReadUserPolicy
        ] = policies.ReadUserPolicy,
        update_user_policy_class: type[
            policy.BaseUpdateUserPolicy
        ] = policies.UpdateUserPolicy,
        logger: logging.Logger | None = None,
        **kwargs: Any,
    ):
        super().__init__(app, repository=repository, logger=logger, **kwargs)
        self.repository: BaseAbacRepository  # type:ignore[misc]
        self.organization_admin_policy_model_class = (
            organization_admin_policy_model_class
        )
        self.user_crud_command_class = user_crud_command_class
        self.is_organization_admin_policy_class = is_organization_admin_policy_class
        self.read_organization_results_only_policy_class = (
            read_organization_results_only_policy_class
        )
        self.read_self_results_only_policy_class = read_self_results_only_policy_class
        self.read_user_policy_class = read_user_policy_class
        self.update_user_policy_class = update_user_policy_class

    def crud(self, cmd: CrudCommand) -> Any:
        retval = super().crud(cmd)
        # Invalidate cache
        if issubclass(type(cmd), AbacService.CACHE_INVALIDATION_COMMANDS):
            self._get_user_by_id_cached.cache_clear()  # type:ignore[attr-defined]
        return retval

    def register_policies(
        self,
        organization_admin_write_commands: set[
            type[Command]
        ] = BaseAbacService.ORGANIZATION_ADMIN_WRITE_COMMANDS,
        read_user_commands: set[type[Command]] = BaseAbacService.READ_USER_COMMANDS,
        update_user_commands: set[type[Command]] = BaseAbacService.UPDATE_USER_COMMANDS,
        read_organization_results_only_commands: set[
            type[Command]
        ] = BaseAbacService.READ_ORGANIZATION_RESULTS_ONLY_COMMANDS,
        read_self_results_only_commands: set[
            type[Command]
        ] = BaseAbacService.READ_SELF_RESULTS_ONLY_COMMANDS,
    ) -> None:
        f = self.app.register_policy
        policy: Policy
        command_class: type[Command]
        policy = self.is_organization_admin_policy_class(self)  # type:ignore[call-arg]
        for command_class in organization_admin_write_commands:
            f(command_class, policy, EventTiming.BEFORE)
        policy = self.read_user_policy_class(self)  # type:ignore[call-arg]
        for command_class in read_user_commands:
            f(command_class, policy, EventTiming.AFTER)
        policy = self.update_user_policy_class(self)  # type:ignore[call-arg]
        for command_class in update_user_commands:
            f(command_class, policy, EventTiming.BEFORE)
        policy = self.read_organization_results_only_policy_class(
            self  # pyright:ignore[reportCallIssue]
        )  # type:ignore[call-arg]
        for command_class in read_organization_results_only_commands:
            f(command_class, policy, EventTiming.DURING)
            f(command_class, policy, EventTiming.AFTER)
        policy = self.read_self_results_only_policy_class(self)  # type:ignore[call-arg]
        for command_class in read_self_results_only_commands:
            f(command_class, policy, EventTiming.AFTER)

    def retrieve_organizations_under_admin(
        self, cmd: command.RetrieveOrganizationsUnderAdminCommand
    ) -> set[UUID]:
        assert cmd.user and cmd.user.id
        # Special case: user has a role that makes them admin of all organizations
        is_all_organizations = False
        for policy in cmd._policies:
            if isinstance(policy, ReadOrganizationResultsOnlyPolicy):
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
                self.repository.crud(  # type:ignore[assignment]
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
        return {x.organization_id for x in organization_admin_policies}

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
                self.repository.crud(  # type:ignore[assignment]
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

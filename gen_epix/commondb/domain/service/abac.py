import abc
import logging
import uuid
from typing import Any, Type

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.enum import ServiceType
from gen_epix.commondb.domain.repository import BaseAbacRepository
from gen_epix.fastapp import BaseService
from gen_epix.fastapp.app import App
from gen_epix.fastapp.enum import EventTiming
from gen_epix.fastapp.model import Command, Policy


class BaseAbacService(BaseService):
    SERVICE_TYPE = ServiceType.ABAC

    COMMON_ORGANIZATION_ADMIN_WRITE_COMMANDS: set[Type[Command]] = {
        command.ContactCrudCommand,
        command.SiteCrudCommand,
    }

    COMMON_READ_USER_COMMANDS: set[Type[Command]] = {
        command.UserCrudCommand,
    }

    COMMON_UPDATE_USER_COMMANDS: set[Type[Command]] = {
        command.InviteUserCommand,
        command.UpdateUserCommand,
    }

    COMMON_READ_ORGANIZATION_RESULTS_ONLY_COMMANDS: set[Type[Command]] = {
        command.OrganizationAdminPolicyCrudCommand,
        command.UserInvitationCrudCommand,
        command.RetrieveInviteUserConstraintsCommand,
    }

    COMMON_READ_SELF_RESULTS_ONLY_COMMANDS: set[Type[Command]] = set()

    def __init__(
        self,
        app: App,
        repository: BaseAbacRepository,
        organization_admin_policy_model_class: Type[
            model.OrganizationAdminPolicy
        ] = model.OrganizationAdminPolicy,
        user_crud_command_class: Type[
            command.UserCrudCommand
        ] = command.UserCrudCommand,
        is_organization_admin_policy_class: Type[Policy] = Policy,
        read_organization_results_only_policy_class: Type[Policy] = Policy,
        read_self_results_only_policy_class: Type[Policy] = Policy,
        read_user_policy_class: Type[Policy] = Policy,
        update_user_policy_class: Type[Policy] = Policy,
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

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseAbacRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        self.register_default_crud_handlers()
        f = self.app.register_handler
        f(
            command.RetrieveOrganizationAdminNameEmailsCommand,
            self.retrieve_organization_admin_name_emails,
        )
        f(
            command.RetrieveOrganizationsUnderAdminCommand,
            self.retrieve_organizations_under_admin,
        )
        f(
            command.UpdateUserOwnOrganizationCommand,
            self.temp_update_user_own_organization,
        )

    @abc.abstractmethod
    def register_policies(
        self,
        organization_admin_write_commands: set[
            Type[Command]
        ] = COMMON_ORGANIZATION_ADMIN_WRITE_COMMANDS,
        read_user_commands: set[Type[Command]] = COMMON_READ_USER_COMMANDS,
        update_user_commands: set[Type[Command]] = COMMON_UPDATE_USER_COMMANDS,
        read_organization_results_only_commands: set[
            Type[Command]
        ] = COMMON_READ_ORGANIZATION_RESULTS_ONLY_COMMANDS,
        read_self_results_only_commands: set[
            Type[Command]
        ] = COMMON_READ_SELF_RESULTS_ONLY_COMMANDS,
    ) -> None:
        f = self.app.register_policy
        policy: Policy
        command_class: Type[Command]
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

    @abc.abstractmethod
    def retrieve_organization_admin_name_emails(
        self,
        cmd: command.RetrieveOrganizationAdminNameEmailsCommand,
    ) -> list[model.UserNameEmail]:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_organizations_under_admin(
        self, cmd: command.RetrieveOrganizationsUnderAdminCommand
    ) -> set[uuid.UUID]:
        raise NotImplementedError

    def temp_update_user_own_organization(
        self,
        cmd: command.UpdateUserOwnOrganizationCommand,
    ) -> model.User:
        raise NotImplementedError

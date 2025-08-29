import abc
import uuid
from typing import Type

from gen_epix.common.domain import command, model
from gen_epix.common.domain.enum import ServiceType
from gen_epix.common.domain.repository import BaseAbacRepository
from gen_epix.fastapp import BaseService
from gen_epix.fastapp.model import Command


class BaseAbacService(BaseService):
    SERVICE_TYPE = ServiceType.ABAC

    ORGANIZATION_ADMIN_WRITE_COMMANDS: set[Type[Command]] = {
        command.ContactCrudCommand,
        command.SiteCrudCommand,
    }

    UPDATE_USER_COMMANDS: set[Type[Command]] = {
        command.InviteUserCommand,
        command.UpdateUserCommand,
    }

    READ_ORGANIZATION_RESULTS_ONLY_COMMANDS: set[Type[Command]] = {
        command.UserCrudCommand,
        command.OrganizationAdminPolicyCrudCommand,
        command.UserInvitationCrudCommand,
    }

    READ_SELF_RESULTS_ONLY_COMMANDS: set[Type[Command]] = {
        command.UserCrudCommand,
    }

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseAbacRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(
            command.RetrieveOrganizationAdminNameEmailsCommand,
            self.retrieve_organization_admin_name_emails,
        )
        f(
            command.UpdateUserOwnOrganizationCommand,
            self.temp_update_user_own_organization,
        )

    @abc.abstractmethod
    def register_policies(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_organization_admin_name_emails(
        self,
        cmd: command.RetrieveOrganizationAdminNameEmailsCommand,
    ) -> list[model.UserNameEmail]:
        raise NotImplementedError

    @abc.abstractmethod
    def temp_update_user_own_organization(
        self,
        cmd: command.UpdateUserOwnOrganizationCommand,
    ) -> model.User:
        raise NotImplementedError

    @abc.abstractmethod
    def get_organizations_under_admin(self, user: model.User) -> set[uuid.UUID]:
        raise NotImplementedError

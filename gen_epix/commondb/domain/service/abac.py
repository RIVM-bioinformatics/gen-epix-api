import abc
import uuid

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.enum import ServiceType
from gen_epix.commondb.domain.repository import BaseAbacRepository
from gen_epix.fastapp import BaseService
from gen_epix.fastapp.model import Command


class BaseAbacService(BaseService):
    SERVICE_TYPE = ServiceType.ABAC

    ORGANIZATION_ADMIN_WRITE_COMMANDS: set[type[Command]] = {
        command.ContactCrudCommand,
        command.SiteCrudCommand,
    }

    READ_USER_COMMANDS: set[type[Command]] = {
        command.UserCrudCommand,
    }

    UPDATE_USER_COMMANDS: set[type[Command]] = {
        command.InviteUserCommand,
        command.UpdateUserCommand,
    }

    READ_ORGANIZATION_RESULTS_ONLY_COMMANDS: set[type[Command]] = {
        command.OrganizationAdminPolicyCrudCommand,
        command.UserInvitationCrudCommand,
        command.RetrieveInviteUserConstraintsCommand,
    }

    READ_SELF_RESULTS_ONLY_COMMANDS: set[type[Command]] = set()

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

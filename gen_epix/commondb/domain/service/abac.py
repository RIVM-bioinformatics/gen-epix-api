"""Define the commondb ABAC service contract and registered command handlers."""

import abc
import uuid

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.enum import ServiceType
from gen_epix.commondb.domain.repository import BaseAbacRepository
from gen_epix.fastapp import BaseService
from gen_epix.fastapp.model import Command


class BaseAbacService(BaseService[BaseAbacRepository]):
    """Encapsulates ABAC operations that resolve organization administration and scope."""

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
        command.OrganizationIdentifierIssuerLinkCrudCommand,
        command.UserInvitationCrudCommand,
        command.RetrieveInviteUserConstraintsCommand,
    }

    READ_SELF_RESULTS_ONLY_COMMANDS: set[type[Command]] = set()

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseAbacRepository:  # type: ignore
        """Return the ABAC repository with its concrete interface type."""
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        """Register ABAC retrieval and self-organization update command handlers."""
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
            self.update_user_own_organization,
        )

    @abc.abstractmethod
    def retrieve_organization_admin_name_emails(
        self,
        cmd: command.RetrieveOrganizationAdminNameEmailsCommand,
    ) -> list[model.UserNameEmail]:
        """Retrieve display identities of administrators for an organization.

        Args:
            cmd: Command identifying the organization.

        Returns:
            Display identities of the organization's administrators.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_organizations_under_admin(
        self, cmd: command.RetrieveOrganizationsUnderAdminCommand
    ) -> set[uuid.UUID]:
        """Retrieve IDs of organizations administered by the command's user.

        Args:
            cmd: Command whose user defines the administration scope.

        Returns:
            IDs of organizations administered by the user.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    def update_user_own_organization(
        self,
        cmd: command.UpdateUserOwnOrganizationCommand,
    ) -> model.User:
        """Update the executing user's organization affiliation.

        Args:
            cmd: Command identifying the user and target organization.

        Returns:
            Updated user.

        Raises:
            NotImplementedError: Always; concrete services implement the update.
        """
        raise NotImplementedError()

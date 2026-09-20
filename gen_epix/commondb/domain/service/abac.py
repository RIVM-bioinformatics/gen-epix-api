"""Define the commondb ABAC service contract and registered command handlers."""

import uuid
from abc import abstractmethod
from typing import Any

from gen_epix.commondb.domain import command, enum, model
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

    ABAC_EXEMPTED_ROLE_SET_MAP: dict[type[command.Command], enum.RoleSet] = {}

    # Property overridden to provide narrower return value to support linter
    @property
    def repository(self) -> BaseAbacRepository:  # type: ignore[return-type]
        """Return the ABAC repository with its concrete interface type."""
        return super().repository

    @repository.setter
    def repository(self, repository: BaseAbacRepository) -> None:
        """Set the ABAC repository."""
        self._repository = repository

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

    @abstractmethod
    def register_policies(self, **kwargs: Any) -> None:
        """Register ABAC policies for the service."""
        raise NotImplementedError()

    @abstractmethod
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

    @abstractmethod
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

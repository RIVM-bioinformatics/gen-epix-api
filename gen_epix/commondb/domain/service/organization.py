"""Define the commondb organization service contract and command handlers."""

import abc
import uuid
from typing import Any

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.enum import ServiceType
from gen_epix.commondb.domain.repository.organization import BaseOrganizationRepository
from gen_epix.fastapp import BaseService
from gen_epix.fastapp.model import UpdateAssociationCommand


class BaseOrganizationService(BaseService[BaseOrganizationRepository]):
    """Encapsulates organization, invitation, and user lifecycle operations."""

    SERVICE_TYPE = ServiceType.ORGANIZATION

    def register_handlers(self) -> None:
        """Register organization CRUD, association, invitation, and user handlers."""
        f = self.app.register_handler
        self.register_default_crud_handlers()
        for command_class in self.app.domain.get_commands_for_service_type(
            self.service_type, base_class=UpdateAssociationCommand
        ):
            f(command_class, self.update_association)
        f(
            command.RetrieveOrganizationContactsCommand,
            self.retrieve_organization_contacts,
        )
        f(command.InviteUserCommand, self.invite_user)
        f(
            command.RetrieveInviteUserConstraintsCommand,
            self.retrieve_invite_user_constraints,
        )
        f(command.RegisterInvitedUserCommand, self.register_invited_user)
        f(command.UpdateUserCommand, self.update_user)
        f(command.AnonymizeUserCommand, self.anonymize_user)

    @abc.abstractmethod
    def retrieve_organization_contacts(
        self,
        cmd: command.RetrieveOrganizationContactsCommand,
    ) -> model.OrganizationContacts:
        """Retrieve organization contact information.

        Args:
            cmd: Command identifying the organization.

        Returns:
            Requested organization contacts.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_user_by_key(self, user_key: str) -> model.User:
        """Retrieve a user by their unique key.

        Args:
            user_key: Normalized user key to resolve.

        Returns:
            Matching user.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def invite_user(
        self,
        cmd: command.InviteUserCommand,
    ) -> model.UserInvitation:
        """Create an invitation for a user.

        Args:
            cmd: Command containing invitation details.

        Returns:
            Created user invitation.

        Raises:
            NotImplementedError: Always; concrete services implement invitations.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_invite_user_constraints(
        self, cmd: command.RetrieveInviteUserConstraintsCommand
    ) -> model.UserInvitationConstraints:
        """Retrieve constraints for a user invitation.

        Args:
            cmd: Command whose user determines available constraints.

        Returns:
            Roles and organizations available for invitation.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def register_invited_user(
        self, cmd: command.RegisterInvitedUserCommand
    ) -> model.User:
        """Register a user from an invitation.

        Args:
            cmd: Command carrying the invitation token.

        Returns:
            Registered user.

        Raises:
            NotImplementedError: Always; concrete services implement registration.
        """
        raise NotImplementedError()

    def generate_user_invitation_token(self, **kwargs: Any) -> str:
        """Generate a random token used to identify a user invitation.

        Args:
            **kwargs: Reserved extension configuration.

        Returns:
            A UUID-formatted invitation token.
        """
        return str(uuid.uuid4())

    @abc.abstractmethod
    def update_user(
        self,
        cmd: command.UpdateUserCommand,
    ) -> model.User:
        """Update user information.

        Args:
            cmd: Command identifying the user and requested changes.

        Returns:
            Updated user.

        Raises:
            NotImplementedError: Always; concrete services implement updates.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def anonymize_user(self, cmd: command.AnonymizeUserCommand) -> model.User:
        """Anonymize user information.

        Args:
            cmd: Command identifying the user to anonymize.

        Returns:
            Anonymized user.

        Raises:
            NotImplementedError: Always; concrete services implement anonymization.
        """
        raise NotImplementedError()

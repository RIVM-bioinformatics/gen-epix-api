import abc
import uuid
from typing import Any

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.enum import ServiceType
from gen_epix.commondb.domain.repository.organization import BaseOrganizationRepository
from gen_epix.fastapp import BaseService
from gen_epix.fastapp.model import UpdateAssociationCommand


class BaseOrganizationService(BaseService[BaseOrganizationRepository]):
    SERVICE_TYPE = ServiceType.ORGANIZATION

    def register_handlers(self) -> None:
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
        """Retrieve organization contact information."""
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_user_by_key(self, user_key: str) -> model.User:
        """Retrieve user by their unique key."""
        raise NotImplementedError()

    @abc.abstractmethod
    def invite_user(
        self,
        cmd: command.InviteUserCommand,
    ) -> model.UserInvitation:
        """Send invitation to user."""
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_invite_user_constraints(
        self, cmd: command.RetrieveInviteUserConstraintsCommand
    ) -> model.UserInvitationConstraints:
        """Retrieve constraints for user invitation."""
        raise NotImplementedError()

    @abc.abstractmethod
    def register_invited_user(
        self, cmd: command.RegisterInvitedUserCommand
    ) -> model.User:
        """Register user from invitation."""
        raise NotImplementedError()

    def generate_user_invitation_token(self, **kwargs: Any) -> str:
        return str(uuid.uuid4())

    @abc.abstractmethod
    def update_user(
        self,
        cmd: command.UpdateUserCommand,
    ) -> model.User:
        """Update user information."""
        raise NotImplementedError()

    @abc.abstractmethod
    def anonymize_user(self, cmd: command.AnonymizeUserCommand) -> model.User:
        """Anonymize user information."""
        raise NotImplementedError()

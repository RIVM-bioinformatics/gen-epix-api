import abc
import uuid

from gen_epix.fastapp import BaseService
from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.domain.enum import ServiceType
from gen_epix.omopdb.domain.repository.organization import BaseOrganizationRepository


class BaseOrganizationService(BaseService):
    SERVICE_TYPE = ServiceType.ORGANIZATION

    UPDATE_USER_COMMANDS = {
        command.InviteUserCommand,
        command.UpdateUserCommand,
    }

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseOrganizationRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        for command_class in self.app.domain.get_crud_commands_for_service_type(
            self.service_type
        ):
            f(command_class, self.crud)
        f(command.InviteUserCommand, self.invite_user)
        f(command.RegisterInvitedUserCommand, self.register_invited_user)
        f(command.RetrieveCompleteUserCommand, self.retrieve_complete_user)
        f(command.UpdateUserCommand, self.update_user)

    @abc.abstractmethod
    def register_policies(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_user_by_key(self, user_key: str) -> model.User:
        raise NotImplementedError()

    @abc.abstractmethod
    def invite_user(
        self,
        cmd: command.InviteUserCommand,
    ) -> model.UserInvitation:
        raise NotImplementedError

    @abc.abstractmethod
    def register_invited_user(
        self, cmd: command.RegisterInvitedUserCommand
    ) -> model.User:
        raise NotImplementedError

    def generate_user_invitation_token(self, **kwargs: dict) -> str:
        return str(uuid.uuid4())

    @abc.abstractmethod
    def retrieve_complete_user(
        self, cmd: command.RetrieveCompleteUserCommand
    ) -> model.organization.CompleteUser:
        raise NotImplementedError

    @abc.abstractmethod
    def update_user(
        self,
        cmd: command.UpdateUserCommand,
    ) -> model.User:
        raise NotImplementedError

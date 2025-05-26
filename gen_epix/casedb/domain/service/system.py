import abc

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp import BaseService


class BaseSystemService(BaseService):
    SERVICE_TYPE = ServiceType.SYSTEM

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseSystemRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        for command_class in self.app.domain.get_crud_commands_for_service_type(
            self.service_type
        ):
            f(command_class, self.crud)
        f(command.RetrieveOutagesCommand, self.retrieve_outages)

    @abc.abstractmethod
    def register_policies(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_outages(
        self, cmd: command.RetrieveOutagesCommand
    ) -> list[model.Outage]:
        raise NotImplementedError

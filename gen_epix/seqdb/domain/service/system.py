import abc

from gen_epix.fastapp import BaseService
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.enum import ServiceType


class BaseSystemService(BaseService):
    SERVICE_TYPE = ServiceType.SYSTEM

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

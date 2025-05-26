import abc

from gen_epix.fastapp import BaseService
from gen_epix.seqdb.domain.enum import ServiceType


class BaseAbacService(BaseService):
    SERVICE_TYPE = ServiceType.ABAC

    def register_handlers(self) -> None:
        f = self.app.register_handler
        for command_class in self.app.domain.get_crud_commands_for_service_type(
            self.service_type
        ):
            f(command_class, self.crud)

    @abc.abstractmethod
    def register_policies(self) -> None:
        raise NotImplementedError

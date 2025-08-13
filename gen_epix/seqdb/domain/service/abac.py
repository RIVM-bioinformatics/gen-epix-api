import abc

from gen_epix.fastapp import BaseService
from gen_epix.seqdb.domain.enum import ServiceType


class BaseAbacService(BaseService):
    SERVICE_TYPE = ServiceType.ABAC

    def register_handlers(self) -> None:
        self.register_default_crud_handlers()

    @abc.abstractmethod
    def register_policies(self) -> None:
        raise NotImplementedError

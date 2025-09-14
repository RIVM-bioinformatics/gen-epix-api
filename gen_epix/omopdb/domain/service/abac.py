import abc

from gen_epix.commondb.services import AbacService as CommonAbacService
from gen_epix.omopdb.domain.enum import ServiceType


class BaseAbacService(CommonAbacService):
    SERVICE_TYPE = ServiceType.ABAC

    def register_handlers(self) -> None:
        self.register_default_crud_handlers()

    @abc.abstractmethod
    def register_policies(self) -> None:
        raise NotImplementedError

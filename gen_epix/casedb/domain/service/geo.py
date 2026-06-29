import abc

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository import BaseGeoRepository
from gen_epix.fastapp import BaseService


class BaseGeoService(BaseService[BaseGeoRepository]):
    SERVICE_TYPE = ServiceType.GEO

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(command.RetrieveContainingRegionCommand, self.retrieve_containing_region)

    @abc.abstractmethod
    def retrieve_containing_region(
        self, cmd: command.RetrieveContainingRegionCommand
    ) -> list[model.Region | None]: ...

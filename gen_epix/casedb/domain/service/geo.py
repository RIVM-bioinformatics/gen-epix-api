import abc

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository import BaseGeoRepository
from gen_epix.fastapp import BaseService


class BaseGeoService(BaseService):
    SERVICE_TYPE = ServiceType.GEO

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseGeoRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(command.RetrieveContainingRegionCommand, self.retrieve_containing_region)

    @abc.abstractmethod
    def retrieve_containing_region(
        self, cmd: command.RetrieveContainingRegionCommand
    ) -> list[model.Region | None]:
        raise NotImplementedError()

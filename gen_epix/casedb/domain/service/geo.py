import abc

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository.geo import BaseGeoRepository
from gen_epix.fastapp import BaseService


class BaseGeoService(BaseService):
    SERVICE_TYPE = ServiceType.GEO

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseGeoRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        for command_class in self.app.domain.get_crud_commands_for_service_type(
            self.service_type
        ):
            f(command_class, self.crud)
        f(command.RetrieveContainingRegionCommand, self.retrieve_containing_region)

    @abc.abstractmethod
    def retrieve_containing_region(
        self, cmd: command.RetrieveContainingRegionCommand
    ) -> list[model.Region | None]:
        raise NotImplementedError()

import abc

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.enum import ServiceType
from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp import BaseService


class BaseSystemService(BaseService):
    SERVICE_TYPE = ServiceType.SYSTEM

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseSystemRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(command.RetrieveOutagesCommand, self.retrieve_outages)
        f(command.RetrieveLicensesCommand, self.retrieve_licenses)

    @abc.abstractmethod
    def register_policies(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_outages(
        self, cmd: command.RetrieveOutagesCommand
    ) -> list[model.Outage]:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_licenses(
        self, cmd: command.RetrieveLicensesCommand
    ) -> list[model.PackageMetadata]:
        raise NotImplementedError

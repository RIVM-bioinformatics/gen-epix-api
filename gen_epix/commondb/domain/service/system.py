import abc
from collections.abc import Hashable

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.enum import ServiceType
from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp import BaseService


class BaseSystemService(BaseService[BaseSystemRepository]):
    SERVICE_TYPE = ServiceType.SYSTEM

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(command.RetrieveOutagesCommand, self.retrieve_outages)
        f(command.RetrieveLicensesCommand, self.retrieve_licenses)
        f(command.RetrieveFeatureFlagsCommand, self.retrieve_feature_flags)
        f(command.UpdateLogLevelCommand, self.update_log_level)

    @abc.abstractmethod
    def register_policies(self) -> None:
        """Register system policies."""
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_outages(
        self, cmd: command.RetrieveOutagesCommand
    ) -> list[model.Outage]:
        """Retrieve system outages."""
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_licenses(
        self, cmd: command.RetrieveLicensesCommand
    ) -> list[model.PackageMetadata]:
        """Retrieve package licenses."""
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_feature_flags(
        self, cmd: command.RetrieveFeatureFlagsCommand
    ) -> dict[Hashable, bool]:
        """Retrieve feature flags configuration."""
        raise NotImplementedError()

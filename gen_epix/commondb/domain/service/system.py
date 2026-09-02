"""Define the commondb system service contract and command handlers."""

import abc
from collections.abc import Hashable

from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.enum import ServiceType
from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp import BaseService


class BaseSystemService(BaseService[BaseSystemRepository]):
    """Encapsulates system-outage, package-license, and feature-flag operations."""

    SERVICE_TYPE = ServiceType.SYSTEM

    def register_handlers(self) -> None:
        """Register CRUD, outage, package-license, and feature-flag handlers."""
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(command.RetrieveOutagesCommand, self.retrieve_outages)
        f(command.RetrieveLicensesCommand, self.retrieve_licenses)
        f(command.RetrieveFeatureFlagsCommand, self.retrieve_feature_flags)

    @abc.abstractmethod
    def register_policies(self) -> None:
        """Register policies that enforce current system outage constraints.

        Raises:
            NotImplementedError: Always; concrete services register their policies.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_outages(
        self, cmd: command.RetrieveOutagesCommand
    ) -> list[model.Outage]:
        """Retrieve active and scheduled system outages.

        Args:
            cmd: Command requesting system outages.

        Returns:
            Active and scheduled outages.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_licenses(
        self, cmd: command.RetrieveLicensesCommand
    ) -> list[model.PackageMetadata]:
        """Retrieve license metadata for installed packages.

        Args:
            cmd: Command requesting package license metadata.

        Returns:
            Installed package license metadata.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_feature_flags(
        self, cmd: command.RetrieveFeatureFlagsCommand
    ) -> dict[Hashable, bool]:
        """Retrieve the application's feature-flag configuration.

        Args:
            cmd: Command requesting feature flags.

        Returns:
            Feature flags keyed by their names.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

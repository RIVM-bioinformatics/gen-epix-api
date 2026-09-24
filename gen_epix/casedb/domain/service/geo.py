"""Define geographic command handlers implemented by Casedb services."""

import abc

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository import BaseGeoRepository
from gen_epix.fastapp import BaseService


class BaseGeoService(BaseService[BaseGeoRepository]):
    """Encapsulates geographic CRUD dispatch and containment queries."""

    SERVICE_TYPE = ServiceType.GEO

    def register_handlers(self) -> None:
        """Register default geographic CRUD and region-containment handlers.

        This mutates the application dispatch table during service
        initialization.
        """
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(command.RetrieveContainingRegionCommand, self.retrieve_containing_region)

    @abc.abstractmethod
    def retrieve_containing_region(
        self, cmd: command.RetrieveContainingRegionCommand
    ) -> list[model.Region | None]:
        """Retrieve the containing region for each location in a command.

        Args:
            cmd: Containment query carrying the locations to resolve.

        Returns:
            Regions aligned with the requested locations, using ``None`` where
            no containing region is found.
        """
        ...

"""Implement casedb geographic region service behavior."""

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.service import BaseGeoService


class GeoService(BaseGeoService):
    """Encapsulates geographic command handling for casedb regions."""

    def retrieve_containing_region(
        self, cmd: command.RetrieveContainingRegionCommand
    ) -> list[model.Region | None]:
        """See base method."""
        # TODO: LSP-3893 For a containment command with locations, the base
        # contract expects aligned Region/None entries, but this returns None.
        # Confirm whether casedb should resolve containment here or delegate.
        ...

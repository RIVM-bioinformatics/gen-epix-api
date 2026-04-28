from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.service import BaseGeoService


class GeoService(BaseGeoService):
    def retrieve_containing_region(
        self, cmd: command.RetrieveContainingRegionCommand
    ) -> list[model.Region | None]: ...

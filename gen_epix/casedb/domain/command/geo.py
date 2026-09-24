"""Define casedb commands for geographic regions and region sets."""

from typing import ClassVar
from uuid import UUID

from pydantic import Field

import gen_epix.casedb.domain.model.geo as model
from gen_epix.commondb.domain.command import Command, CrudCommand

# Non-CRUD


class RetrieveContainingRegionCommand(Command):
    """Represent a request for regions containing specified regions."""

    region_ids: list[UUID] = Field(
        description="The IDs of the regions to retrieve containing regions for."
    )
    region_set_id: UUID = Field(
        description="The ID of the region set to that containing regions must belong to."
    )
    level: int = Field(description="The level of the region to retrieve.")


# CRUD


class RegionSetCrudCommand(CrudCommand):
    """Represent CRUD operations for geographic region sets."""

    MODEL_CLASS: ClassVar = model.RegionSet


class RegionCrudCommand(CrudCommand):
    """Represent CRUD operations for geographic regions."""

    MODEL_CLASS: ClassVar = model.Region


class RegionRelationCrudCommand(CrudCommand):
    """Represent CRUD operations for relationships between regions."""

    MODEL_CLASS: ClassVar = model.RegionRelation


class RegionSetShapeCrudCommand(CrudCommand):
    """Represent CRUD operations for shapes associated with region sets."""

    MODEL_CLASS: ClassVar = model.RegionSetShape

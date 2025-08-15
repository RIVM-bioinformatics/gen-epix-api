from typing import ClassVar
from uuid import UUID

import gen_epix.casedb.domain.model.geo as model
from gen_epix.casedb.domain import enum
from gen_epix.common.domain.command import Command, CrudCommand

# Non-CRUD


class RetrieveContainingRegionCommand(Command):

    region_ids: list[UUID]
    region_set_id: UUID
    level: int


# CRUD


class RegionSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RegionSet


class RegionCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Region


class RegionRelationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RegionRelation


class RegionSetShapeCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.RegionSetShape

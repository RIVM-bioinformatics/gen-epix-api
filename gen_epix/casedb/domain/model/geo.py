# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links


class RegionSet(Model):
    """
    Set of regions that do not overlap geographically
    or otherwise did not exist at the same moment in time.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="region_sets",
        table_name="region_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
    )
    code: str = Field(description="The code of the region set.", max_length=255)
    name: str = Field(
        description="The name of the region set.",
        max_length=255,
    )
    region_code_as_label: bool = Field(
        description=(
            "Whether the region's code should be used as the label."
            " E.g. in case of postal code the code "
            "could be used instead of the name of the region."
        ),
    )


class RegionSetShape(Model):
    """
    Geographical shape representation for a region set.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="region_set_shapes",
        table_name="region_set_shape",
        persistable=True,
        keys=create_keys({1: ("region_set_id", "scale")}),
        links=create_links(
            {
                1: ("region_set_id", RegionSet, "region_set"),
            }
        ),
    )
    region_set_id: UUID
    region_set: RegionSet | None = None
    scale: float
    geo_json: str


class Region(Model):
    """
    Geographical representation of a region.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="regions",
        table_name="region",
        persistable=True,
        keys=create_keys(
            {
                1: ("region_set_id", "code"),
                # 2: ("region_set_id", "name"),
                # # postal codes in NL can have the same name
            }
        ),
        links=create_links(
            {
                1: ("region_set_id", RegionSet, "region_set"),
            }
        ),
    )
    region_set_id: UUID = Field(description="The ID of the region set. FOREIGN KEY")
    region_set: RegionSet | None = Field(
        default=None, description="The region set to which the region belongs."
    )
    code: str = Field(description="The code of the region.", max_length=255)
    name: str = Field(
        description="The name of the region.",
        max_length=255,
    )
    centroid_lat: float = Field(description="The latitude of the region's centroid.")
    centroid_lon: float = Field(description="The longitude of the region's centroid.")
    center_lat: float = Field(description="The latitude of the region's center.")
    center_lon: float = Field(description="The longitude of the region's center.")


class RegionRelation(Model):
    """
    Geographical relation between two regions.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="region_relations",
        table_name="region_relation",
        persistable=True,
        keys=create_keys({1: ("from_region_id", "to_region_id")}),
        links=create_links(
            {
                1: ("from_region_id", Region, "from_region"),
                2: ("to_region_id", Region, "to_region"),
            }
        ),
    )
    from_region_id: UUID = Field(description="The ID of the source region. FOREIGN KEY")
    from_region: Region | None = Field(default=None, description="The source region.")
    to_region_id: UUID = Field(description="The ID of the target region. FOREIGN KEY")
    to_region: Region | None = Field(default=None, description="The target region.")
    relation: enum.RegionRelationType = Field(
        description="The type of relation between the regions."
    )

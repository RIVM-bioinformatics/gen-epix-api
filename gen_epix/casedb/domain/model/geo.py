"""Define casedb geographic reference models.

The module provides region sets, their shapes, individual regions, and directed
relations between regions for persistence through the shared domain model layer.
"""

# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_serializer, field_validator

from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links


class RegionSet(Model):
    """Represents a geographically and temporally non-overlapping region set."""

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
    resolution: float = Field(
        gt=0,
        description=(
            "The geographic resolution; higher values indicate higher resolution."
        ),
    )


class RegionSetShape(Model):
    """Represents a geographic shape for a region set at a given scale."""

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
    region_set_id: UUID = Field(description="The ID of the region set. FOREIGN KEY")
    region_set: RegionSet | None = Field(
        default=None, description="The region set to which the region belongs."
    )
    scale: float = Field(description="The scale of the shape representation.")
    geo_json: str = Field(
        description="The GeoJSON representation of the region set shape."
    )


class Region(Model):
    """Represents a named geographic region within a region set."""

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
    """Represents a directed geographic relation between two regions."""

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
        description=(
            "The relation type. Accepts an enum member or its string value and "
            "is serialized as that string value."
        )
    )

    @field_validator("relation", mode="before")
    @classmethod
    def _validate_relation(
        cls, value: enum.RegionRelationType | str
    ) -> enum.RegionRelationType:
        """Normalize a string relation value to its enum member."""
        if isinstance(value, str):
            value = enum.RegionRelationType(value)
        return value

    @field_serializer("relation", mode="plain")
    def _serialize_relation(self, value: enum.RegionRelationType) -> str:
        """Serialize the relation type as its string value."""
        return value.value

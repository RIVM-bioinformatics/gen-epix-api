# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import Type
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.casedb.repositories.sa_model.util import (
    create_mapped_column,
    create_table_args,
)

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.GEO.value)


class RegionSet(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.RegionSet)

    code: Mapped[str] = create_mapped_column(model.RegionSet, "code")
    name: Mapped[str] = create_mapped_column(model.RegionSet, "name")
    region_code_as_label: Mapped[bool] = create_mapped_column(
        model.RegionSet, "region_code_as_label"
    )


class RegionSetShape(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.RegionSetShape)

    region_set_id: Mapped[UUID] = create_mapped_column(
        model.RegionSetShape, "region_set_id"
    )
    scale: Mapped[float] = create_mapped_column(model.RegionSetShape, "scale")
    geo_json: Mapped[str] = create_mapped_column(model.RegionSetShape, "geo_json")

    region_set: Mapped[model.RegionSet] = relationship(
        RegionSet, foreign_keys=[region_set_id]
    )


class Region(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Region)

    region_set_id: Mapped[UUID] = create_mapped_column(model.Region, "region_set_id")
    code: Mapped[str] = create_mapped_column(model.Region, "code")
    name: Mapped[str] = create_mapped_column(model.Region, "name")
    centroid_lat: Mapped[float] = create_mapped_column(model.Region, "centroid_lat")
    centroid_lon: Mapped[float] = create_mapped_column(model.Region, "centroid_lon")
    center_lat: Mapped[float] = create_mapped_column(model.Region, "center_lat")
    center_lon: Mapped[float] = create_mapped_column(model.Region, "center_lon")

    region_set: Mapped[model.RegionSet] = relationship(
        RegionSet, foreign_keys=[region_set_id]
    )


class RegionRelation(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.RegionRelation)

    from_region_id: Mapped[UUID] = create_mapped_column(
        model.RegionRelation, "from_region_id"
    )
    to_region_id: Mapped[UUID] = create_mapped_column(
        model.RegionRelation, "to_region_id"
    )
    relation: Mapped[enum.RegionRelationType] = create_mapped_column(
        model.RegionRelation, "relation"
    )

    from_region: Mapped[model.Region] = relationship(
        Region, foreign_keys=[from_region_id]
    )
    to_region: Mapped[model.Region] = relationship(Region, foreign_keys=[to_region_id])

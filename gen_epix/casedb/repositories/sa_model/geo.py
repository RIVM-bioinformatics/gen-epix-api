# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import Type
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from gen_epix.casedb.domain import DOMAIN, enum, model
from gen_epix.common.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.GEO.value)


class RegionSet(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.RegionSet)

    code: Mapped[str] = create_mapped_column(DOMAIN, model.RegionSet, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.RegionSet, "name")
    region_code_as_label: Mapped[bool] = create_mapped_column(
        DOMAIN, model.RegionSet, "region_code_as_label"
    )


class RegionSetShape(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.RegionSetShape)

    region_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.RegionSetShape, "region_set_id"
    )
    scale: Mapped[float] = create_mapped_column(DOMAIN, model.RegionSetShape, "scale")
    geo_json: Mapped[str] = create_mapped_column(
        DOMAIN, model.RegionSetShape, "geo_json"
    )

    region_set: Mapped[model.RegionSet] = relationship(
        RegionSet, foreign_keys=[region_set_id]
    )


class Region(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Region)

    region_set_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Region, "region_set_id"
    )
    code: Mapped[str] = create_mapped_column(DOMAIN, model.Region, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.Region, "name")
    centroid_lat: Mapped[float] = create_mapped_column(
        DOMAIN, model.Region, "centroid_lat"
    )
    centroid_lon: Mapped[float] = create_mapped_column(
        DOMAIN, model.Region, "centroid_lon"
    )
    center_lat: Mapped[float] = create_mapped_column(DOMAIN, model.Region, "center_lat")
    center_lon: Mapped[float] = create_mapped_column(DOMAIN, model.Region, "center_lon")

    region_set: Mapped[model.RegionSet] = relationship(
        RegionSet, foreign_keys=[region_set_id]
    )


class RegionRelation(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.RegionRelation)

    from_region_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.RegionRelation, "from_region_id"
    )
    to_region_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.RegionRelation, "to_region_id"
    )
    relation: Mapped[enum.RegionRelationType] = create_mapped_column(
        DOMAIN, model.RegionRelation, "relation"
    )

    from_region: Mapped[model.Region] = relationship(
        Region, foreign_keys=[from_region_id]
    )
    to_region: Mapped[model.Region] = relationship(Region, foreign_keys=[to_region_id])

import datetime
from typing import Type

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from gen_epix.seqdb.domain import enum, model
from gen_epix.seqdb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.seqdb.repositories.sa_model.util import (
    create_mapped_column,
    create_table_args,
)

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.SYSTEM.value)


class Outage(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Outage)

    description: Mapped[str | None] = create_mapped_column(model.Outage, "description")
    active_from: Mapped[datetime.datetime | None] = create_mapped_column(
        model.Outage, "active_from"
    )
    active_to: Mapped[datetime.datetime | None] = create_mapped_column(
        model.Outage, "active_to"
    )
    visible_from: Mapped[datetime.datetime | None] = create_mapped_column(
        model.Outage, "visible_from"
    )
    visible_to: Mapped[datetime.datetime | None] = create_mapped_column(
        model.Outage, "visible_to"
    )
    is_active: Mapped[bool | None] = create_mapped_column(model.Outage, "is_active")
    is_visible: Mapped[bool | None] = create_mapped_column(model.Outage, "is_visible")

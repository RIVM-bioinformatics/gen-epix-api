import datetime

import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped, declarative_mixin

from gen_epix.commondb.domain import DOMAIN, enum, model
from gen_epix.commondb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.commondb.repositories.sa_model.util import (
    create_mapped_column,
    create_table_args,
)

Base: type = orm.declarative_base(name=enum.ServiceType.SYSTEM.value)


@declarative_mixin
class OutageMixin(RowMetadataMixin):
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Outage, "description"
    )
    active_from: Mapped[datetime.datetime | None] = create_mapped_column(
        DOMAIN, model.Outage, "active_from"
    )
    active_to: Mapped[datetime.datetime | None] = create_mapped_column(
        DOMAIN, model.Outage, "active_to"
    )
    visible_from: Mapped[datetime.datetime | None] = create_mapped_column(
        DOMAIN, model.Outage, "visible_from"
    )
    visible_to: Mapped[datetime.datetime | None] = create_mapped_column(
        DOMAIN, model.Outage, "visible_to"
    )
    is_active: Mapped[bool | None] = create_mapped_column(
        DOMAIN, model.Outage, "is_active"
    )
    is_visible: Mapped[bool | None] = create_mapped_column(
        DOMAIN, model.Outage, "is_visible"
    )


class Outage(Base, OutageMixin):
    __tablename__, __table_args__ = create_table_args(model.Outage)

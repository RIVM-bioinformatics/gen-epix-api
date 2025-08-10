import datetime

from sqlalchemy.orm import Mapped, declarative_mixin

from gen_epix.casedb.domain import model
from gen_epix.common.domain import DOMAIN
from gen_epix.common.repositories.sa_model.base import RowMetadataMixin
from gen_epix.common.repositories.sa_model.util import create_mapped_column


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

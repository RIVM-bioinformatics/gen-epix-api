from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.commondb.repositories.sa_model import (
    NoIdRowMetadataMixin as NoIdRowMetadataMixin,
)


@declarative_mixin
class DataLineageMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    provenance_id: Mapped[UUID | None] = mapped_column(UUIDType(), nullable=True)
    source_traceback: Mapped[str | None] = mapped_column(sa.Unicode(255), nullable=True)

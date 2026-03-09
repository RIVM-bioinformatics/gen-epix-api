import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.fastapp.repositories.sa import ServerUtcCurrentTime


# TODO: 2953 - consider removing
# This is a duplicate of the same mixin in gen_epix.commondb.domain.model.base,
#  but we want to avoid importing from the domain layer into the repository layer, so we duplicate it here.
@declarative_mixin
class NoIdRowMetadataMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime, nullable=False, server_default=ServerUtcCurrentTime()
    )
    modified_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
        nullable=False,
        server_default=ServerUtcCurrentTime(),
        onupdate=ServerUtcCurrentTime(),
    )
    modified_by: Mapped[UUID] = mapped_column(UUIDType(), nullable=True)
    # _version: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1)
    # __mapper_args__ = {"version_id_col": _version}


@declarative_mixin
class DataLineageMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    provenance_id: Mapped[UUID | None] = mapped_column(UUIDType(), nullable=True)
    source_traceback: Mapped[str | None] = mapped_column(sa.Unicode(255), nullable=True)
    # Note: seems to be duplicated
    # provenance_id: Mapped[UUID | None] = mapped_column(UUIDType(), nullable=True)
    # source_traceback: Mapped[str | None] = mapped_column(sa.Unicode(255), nullable=True)

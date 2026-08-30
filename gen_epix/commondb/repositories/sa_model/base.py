"""Define reusable SQLAlchemy audit metadata mixins for commondb rows."""

import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.fastapp.repositories.sa import ServerUtcCurrentTime, UTCDateTime


@declarative_mixin
class RowMetadataMixin:
    """Add ID, creation, modification, and modifying-user fields to a row."""

    id: Mapped[UUID] = mapped_column(UUIDType(), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        UTCDateTime, nullable=False, server_default=ServerUtcCurrentTime()
    )
    modified_at: Mapped[datetime.datetime] = mapped_column(
        UTCDateTime,
        nullable=False,
        server_default=ServerUtcCurrentTime(),
        onupdate=ServerUtcCurrentTime(),
    )
    modified_by: Mapped[UUID] = mapped_column(UUIDType(), nullable=True)


@declarative_mixin
class NoIdRowMetadataMixin:
    """Add audit metadata fields to a row with a nonstandard primary key."""

    created_at: Mapped[datetime.datetime] = mapped_column(
        UTCDateTime, nullable=False, server_default=ServerUtcCurrentTime()
    )
    modified_at: Mapped[datetime.datetime] = mapped_column(
        UTCDateTime,
        nullable=False,
        server_default=ServerUtcCurrentTime(),
        onupdate=ServerUtcCurrentTime(),
    )
    modified_by: Mapped[UUID] = mapped_column(UUIDType(), nullable=True)

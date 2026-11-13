"""Define reusable SQLAlchemy audit metadata mixins for commondb rows."""

import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.fastapp.repositories.sa import ServerUtcCurrentTime, UTCDateTime


@declarative_mixin
class RowMetadataMixin:
    """Encapsulates ID, creation, modification, and modifying-user fields to a row."""

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
    # TODO: LSP-3893 A persisted NULL modified_by is allowed by nullable=True, but this
    # annotation advertises UUID rather than None; confirm whether nulls are valid
    # existing audit data or whether the column should instead be non-nullable.
    modified_by: Mapped[UUID] = mapped_column(UUIDType(), nullable=True)


@declarative_mixin
class NoIdRowMetadataMixin:
    """Encapsulates audit metadata fields to a row with a nonstandard primary key."""

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

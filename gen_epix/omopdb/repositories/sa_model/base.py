"""Provide shared SQLAlchemy mixins for OmopDB table mappings.

`DataLineageMixin` adds optional provenance and source-traceback columns, while
`NoIdRowMetadataMixin` re-exports the common no-ID row metadata mixin. These
declarations are composed into mapped tables by the OMOP repository models.
"""

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.commondb.repositories.sa_model import (
    NoIdRowMetadataMixin,
)

__all__ = ["DataLineageMixin", "NoIdRowMetadataMixin"]


@declarative_mixin
class DataLineageMixin:  # type: ignore[too-few-public-methods]
    """Encapsulates a SQLAlchemy model mixin for adding a number of standard fields."""

    provenance_id: Mapped[UUID | None] = mapped_column(UUIDType(), nullable=True)
    source_traceback: Mapped[str | None] = mapped_column(sa.Unicode(255), nullable=True)

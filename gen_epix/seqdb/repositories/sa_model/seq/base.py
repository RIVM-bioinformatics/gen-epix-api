"""Define SQLAlchemy persistence mappings for SeqDB repositories.sa_model.seq.base."""

from enum import IntEnum
from uuid import UUID

import sqlalchemy as sa
from pydantic import Json
from sqlalchemy.orm import Mapped
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.commondb.repositories.sa_model import get_mixin_mapped_column
from gen_epix.commondb.repositories.sa_model.util import create_mapped_column
from gen_epix.seqdb.domain import DOMAIN, enum, model


class ContentMixin[FormatType: IntEnum]:
    """
    SQLAlchemy model mixin for adding content-related fields to a model.
    """

    format: Mapped[FormatType] = get_mixin_mapped_column(
        model.ContentMixin, "format", sa.Integer
    )
    content_hash: Mapped[UUID] = get_mixin_mapped_column(
        model.ContentMixin, "content_hash", UUIDType
    )
    content: Mapped[str] = get_mixin_mapped_column(
        model.ContentMixin, "content", sa.Text
    )
    content2: Mapped[str | None] = get_mixin_mapped_column(
        model.ContentMixin, "content2", sa.Text, nullable=True
    )


class QualityMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    qc_result: Mapped[enum.QualityControlResult] = get_mixin_mapped_column(
        model.QualityMixin, "qc_result", sa.String
    )
    qc_score: Mapped[float] = get_mixin_mapped_column(
        model.QualityMixin, "qc_score", sa.Float
    )
    qc_report: Mapped[Json | None] = get_mixin_mapped_column(
        model.QualityMixin, "qc_report", sa.JSON, nullable=True
    )


class SeqMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    seq: Mapped[str] = create_mapped_column(DOMAIN, model.BaseSeq, "seq")
    seq_format: Mapped[enum.SeqFormat] = create_mapped_column(
        DOMAIN, model.BaseSeq, "seq_format"
    )
    length: Mapped[int] = create_mapped_column(DOMAIN, model.BaseSeq, "length")

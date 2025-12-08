from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.commondb.repositories.sa_model import get_mixin_mapped_column
from gen_epix.seqdb.domain import model


class CodeMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    code: Mapped[str] = get_mixin_mapped_column(model.CodeMixin, "code", sa.String)


class QualityMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    quality_score: Mapped[float] = get_mixin_mapped_column(
        model.QualityMixin, "quality_score", sa.Float
    )
    quality: Mapped[str] = get_mixin_mapped_column(
        model.QualityMixin, "quality", sa.String
    )


class SeqMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    seq: Mapped[str] = get_mixin_mapped_column(model.SeqMixin, "seq", sa.Text)
    seq_format: Mapped[str] = get_mixin_mapped_column(
        model.SeqMixin, "seq_format", sa.String
    )
    seq_hash: Mapped[UUID] = get_mixin_mapped_column(
        model.SeqMixin, "seq_hash", UUIDType
    )
    length: Mapped[int] = get_mixin_mapped_column(model.SeqMixin, "length", sa.Integer)


class AlignmentMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    aln: Mapped[str] = get_mixin_mapped_column(model.AlignmentMixin, "aln", sa.Text)
    aln_format: Mapped[str] = get_mixin_mapped_column(
        model.AlignmentMixin, "aln_format", sa.String
    )
    aln_hash: Mapped[UUID] = get_mixin_mapped_column(
        model.AlignmentMixin, "aln_hash", UUIDType
    )


class ProtocolMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    code: Mapped[str] = get_mixin_mapped_column(model.ProtocolMixin, "code", sa.String)
    name: Mapped[str] = get_mixin_mapped_column(model.ProtocolMixin, "name", sa.String)
    version: Mapped[str] = get_mixin_mapped_column(
        model.ProtocolMixin, "version", sa.String
    )
    description: Mapped[str] = get_mixin_mapped_column(
        model.ProtocolMixin, "description", sa.Text
    )
    props: Mapped[dict[str, str]] = get_mixin_mapped_column(
        model.ProtocolMixin, "props", sa.JSON
    )

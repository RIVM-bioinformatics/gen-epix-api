from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.commondb.repositories.sa_model import get_mixin_mapped_column
from gen_epix.commondb.repositories.sa_model.util import create_mapped_column
from gen_epix.seqdb.domain import DOMAIN, enum, model


class CodeMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    code: Mapped[str] = get_mixin_mapped_column(model.CodeMixin, "code", sa.String)


class QualityMixin:
    """
    SQLAlchemy model mixin for adding a number of standard fields.
    """

    qc_score: Mapped[float] = get_mixin_mapped_column(
        model.QualityMixin, "qc_score", sa.Float
    )
    qc_result: Mapped[enum.QualityControlResult] = get_mixin_mapped_column(
        model.QualityMixin, "qc_result", sa.String
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

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from gen_epix.commondb.repositories.sa_model import get_mixin_mapped_column
from gen_epix.seqdb.domain import model


class CodeMixin:
    code: Mapped[str] = get_mixin_mapped_column(model.CodeMixin, "code", sa.String)


class QualityMixin:
    quality_score: Mapped[float] = get_mixin_mapped_column(
        model.QualityMixin, "quality_score", sa.Float
    )
    quality: Mapped[str] = get_mixin_mapped_column(
        model.QualityMixin, "quality", sa.String
    )


class SeqMixin:
    seq: Mapped[str] = get_mixin_mapped_column(model.SeqMixin, "seq", sa.Text)
    seq_format: Mapped[str] = get_mixin_mapped_column(
        model.SeqMixin, "seq_format", sa.String
    )
    seq_hash_sha256: Mapped[bytes] = get_mixin_mapped_column(
        model.SeqMixin, "seq_hash_sha256", sa.LargeBinary
    )
    length: Mapped[int] = get_mixin_mapped_column(model.SeqMixin, "length", sa.Integer)


class AlignmentMixin:
    aln: Mapped[str] = get_mixin_mapped_column(model.AlignmentMixin, "aln", sa.Text)
    aln_format: Mapped[str] = get_mixin_mapped_column(
        model.AlignmentMixin, "aln_format", sa.String
    )
    aln_hash_sha256: Mapped[bytes] = get_mixin_mapped_column(
        model.AlignmentMixin, "aln_hash_sha256", sa.LargeBinary
    )


class ProtocolMixin:
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

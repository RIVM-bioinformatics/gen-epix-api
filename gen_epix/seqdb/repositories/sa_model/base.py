import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column


class CodeMixin:
    code: Mapped[str] = mapped_column(sa.String, nullable=False)


class QualityMixin:
    quality_score: Mapped[float] = mapped_column(sa.Float, nullable=True)
    quality: Mapped[str] = mapped_column(sa.String, nullable=True)


class SeqMixin:
    seq: Mapped[str] = mapped_column(sa.String, nullable=False)
    seq_format: Mapped[str] = mapped_column(sa.String, nullable=False)
    seq_hash_sha256: Mapped[bytes] = mapped_column(
        sa.LargeBinary(length=32), nullable=False
    )
    length: Mapped[int] = mapped_column(sa.Integer, nullable=False)


class AlignmentMixin:
    aln: Mapped[str] = mapped_column(sa.String, nullable=False)
    aln_format: Mapped[str] = mapped_column(sa.String, nullable=False)
    aln_hash_sha256: Mapped[bytes] = mapped_column(
        sa.LargeBinary(length=32), nullable=False
    )


class ProtocolMixin:
    code: Mapped[str] = mapped_column(sa.String, nullable=False)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    version: Mapped[str] = mapped_column(sa.String, nullable=True)
    description: Mapped[str] = mapped_column(sa.String, nullable=True)
    props: Mapped[dict[str, str]] = mapped_column(sa.JSON(), nullable=True)

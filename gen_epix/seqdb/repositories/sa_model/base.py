import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.fastapp.repositories.sa import ServerUtcCurrentTime
from gen_epix.seqdb.domain import DOMAIN


class RowMetadataMixin:
    id: Mapped[UUID] = mapped_column(UUIDType(), primary_key=True)
    _created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime, nullable=False, server_default=ServerUtcCurrentTime()
    )
    _modified_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
        nullable=False,
        server_default=ServerUtcCurrentTime(),
        onupdate=ServerUtcCurrentTime(),
    )
    _modified_by: Mapped[UUID] = mapped_column(UUIDType(), nullable=True)
    _version: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1)
    __mapper_args__ = {"version_id_col": _version}


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


SERVICE_METADATA_FIELDS = {
    model_class: ["_modified_by"] for model_class in DOMAIN.models
}

DB_METADATA_FIELDS = {
    model_class: [
        "_created_at",
        "_modified_at",
        "_version",
    ]
    for model_class in DOMAIN.models
}

GENERATE_SERVICE_METADATA = {
    model_class: lambda x, y: {
        "_modified_by": y,
    }
    for model_class in DOMAIN.models
}

import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.casedb.domain import DOMAIN
from gen_epix.fastapp.repositories.sa import ServerUtcCurrentTime


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

# pylint: disable=too-few-public-methods

import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped

from gen_epix.commondb.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)
from gen_epix.seqdb.domain import DOMAIN, enum, model

Base: type = orm.declarative_base(name=enum.ServiceType.FILE.value)


class File(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.File)

    content: Mapped[bytes] = create_mapped_column(DOMAIN, model.File, "content")

# pylint: disable=too-few-public-methods

from typing import Type
from uuid import UUID

import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped

from gen_epix.commondb.repositories.sa_model import (
    create_mapped_column,
    create_table_args,
)
from gen_epix.seqdb.domain import DOMAIN, enum, model

Base: Type = orm.declarative_base(name=enum.ServiceType.FILE.value)


class File(Base):
    __tablename__, __table_args__ = create_table_args(model.File)

    id: Mapped[UUID] = create_mapped_column(DOMAIN, model.File, "id")
    content: Mapped[bytes] = create_mapped_column(DOMAIN, model.File, "content")

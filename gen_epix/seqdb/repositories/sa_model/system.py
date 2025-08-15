from typing import Type

import sqlalchemy as sa

from gen_epix.common.repositories.sa_model import OutageMixin, create_table_args
from gen_epix.seqdb.domain import enum, model

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.SYSTEM.value)


class Outage(Base, OutageMixin):
    __tablename__, __table_args__ = create_table_args(model.Outage)

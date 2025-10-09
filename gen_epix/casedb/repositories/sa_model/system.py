
import sqlalchemy.orm as orm

from gen_epix.casedb.domain import enum, model
from gen_epix.commondb.repositories.sa_model import OutageMixin, create_table_args

Base: type = orm.declarative_base(name=enum.ServiceType.SYSTEM.value)


class Outage(Base, OutageMixin):
    __tablename__, __table_args__ = create_table_args(model.Outage)

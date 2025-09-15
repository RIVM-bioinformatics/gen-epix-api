from typing import Type

import sqlalchemy.orm as orm

from gen_epix.commondb.repositories.sa_model import (
    OrganizationAdminPolicyMixin,
    create_table_args,
)
from gen_epix.omopdb.domain import enum, model

Base: Type = orm.declarative_base(name=enum.ServiceType.ABAC.value)


class OrganizationAdminPolicy(Base, OrganizationAdminPolicyMixin):
    __tablename__, __table_args__ = create_table_args(model.OrganizationAdminPolicy)

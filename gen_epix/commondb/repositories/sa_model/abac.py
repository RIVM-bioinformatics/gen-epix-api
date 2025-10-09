
import sqlalchemy.orm as orm
from sqlalchemy.orm import declarative_mixin

from gen_epix.commondb.domain import DOMAIN, enum, model
from gen_epix.commondb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.commondb.repositories.sa_model.util import (
    create_mapped_column,
    create_table_args,
)

Base: type = orm.declarative_base(name=enum.ServiceType.ABAC.value)


@declarative_mixin
class OrganizationAdminPolicyMixin(RowMetadataMixin):
    organization_id = create_mapped_column(
        DOMAIN, model.OrganizationAdminPolicy, "organization_id"
    )
    user_id = create_mapped_column(DOMAIN, model.OrganizationAdminPolicy, "user_id")
    is_active = create_mapped_column(DOMAIN, model.OrganizationAdminPolicy, "is_active")


class OrganizationAdminPolicy(Base, OrganizationAdminPolicyMixin):
    __tablename__, __table_args__ = create_table_args(model.OrganizationAdminPolicy)

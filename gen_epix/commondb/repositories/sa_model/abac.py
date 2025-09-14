# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from sqlalchemy.orm import declarative_mixin

from gen_epix.commondb.domain import DOMAIN, model
from gen_epix.commondb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.commondb.repositories.sa_model.util import create_mapped_column


@declarative_mixin
class OrganizationAdminPolicyMixin(RowMetadataMixin):
    organization_id = create_mapped_column(
        DOMAIN, model.OrganizationAdminPolicy, "organization_id"
    )
    user_id = create_mapped_column(DOMAIN, model.OrganizationAdminPolicy, "user_id")
    is_active = create_mapped_column(DOMAIN, model.OrganizationAdminPolicy, "is_active")

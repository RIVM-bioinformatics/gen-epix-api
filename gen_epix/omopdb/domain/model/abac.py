from typing import ClassVar

from gen_epix.commondb.domain import model as common_model
from gen_epix.commondb.util import copy_model_field
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.omopdb.domain.model.organization import User


class OrganizationAdminPolicy(common_model.OrganizationAdminPolicy):
    """"""

    __doc__ = common_model.OrganizationAdminPolicy.__doc__

    ENTITY: ClassVar = Entity(
        **common_model.OrganizationAdminPolicy.ENTITY.model_dump(
            exclude_unset=True,
            exclude_defaults=True,
            exclude={"schema_name", "links", "_model_class"},
        ),
        links=create_links(
            {
                1: ("organization_id", common_model.Organization, "organization"),
                2: ("user_id", User, "user"),
            }
        ),
    )
    user: User | None = copy_model_field(common_model.OrganizationAdminPolicy, "user")

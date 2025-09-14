from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import Organization, User
from gen_epix.fastapp.domain import Entity, create_keys, create_links


class OrganizationAdminPolicy(Model):
    """
    Defines whether a user is an admin for an organization. If so, and if the
    user has the role ORG_ADMIN, they will be able to:
    1) Invite new users of this organization.
    2) Manage the case and case set access and share rights of these users.

    The user will not be able to:
    1) Perform the operations above for any other organization for which there
       is no corresponding admin policy.
    2) Set the case and case set access and share case rights for the
       organization itself. This has to be done by a user with role APP_ADMIN.

    Users with role APP_ADMIN or above do not require an admin policy to perform
    these actions. They are de facto organization admin for all organizations.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="organization_admin_policies",
        table_name="organization_admin_policy",
        persistable=True,
        keys=create_keys({1: ("organization_id", "user_id")}),
        links=create_links(
            {
                1: ("organization_id", Organization, "organization"),
                2: ("user_id", User, "user"),
            }
        ),
    )
    organization_id: UUID = Field(description="The ID of the organization. FOREIGN KEY")
    organization: Organization | None = Field(
        default=None, description="The organization"
    )
    user_id: UUID = Field(description="The ID of the user. FOREIGN KEY")
    user: User | None = Field(default=None, description="The user")
    is_active: bool = Field(
        description="Whether the user is an admin for the organization"
    )

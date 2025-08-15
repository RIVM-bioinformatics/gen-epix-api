from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.case.case import CaseTypeColSet, CaseTypeSet
from gen_epix.casedb.domain.model.organization import _ENTITY_KWARGS, User
from gen_epix.common.domain.model import DataCollection, Model, Organization
from gen_epix.fastapp.domain import Entity, create_keys, create_links

_SERVICE_TYPE = enum.ServiceType.ABAC
_ENTITY_KWARGS = {
    "schema_name": _SERVICE_TYPE.value.lower(),
}


class OrganizationAdminPolicy(Model):
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
        **_ENTITY_KWARGS,
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


class BaseCasePolicy(Model):
    data_collection_id: UUID = Field(
        description="The ID of the data collection. FOREIGN KEY"
    )
    data_collection: DataCollection | None = Field(
        default=None, description="The data collection"
    )
    case_type_set_id: UUID = Field(
        description="The ID of the case type set. FOREIGN KEY",
    )
    case_type_set: CaseTypeSet | None = Field(
        default=None, description="The case type set"
    )
    is_active: bool = Field(description="Whether the right is active")
    add_case: bool = Field(
        description="Whether cases may be added to the data collection"
    )
    remove_case: bool = Field(
        description="Whether cases may be removed from the data collection"
    )
    add_case_set: bool = Field(
        description="Whether case sets may be added to the data collection"
    )
    remove_case_set: bool = Field(
        description="Whether case sets may be removed from the data collection"
    )


class OrganizationAccessCasePolicy(BaseCasePolicy):
    """
    Stores the access rights of an organization to a particular data collection.
    If an organization does not have a policy to a data collection, it has no access
    rights to that data collection.

    The access rights are limited to the case types in the case type set. If a case type
    is not in the case type set, the organization has no access rights to that data
    collection for that case type.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="organization_access_case_policies",
        table_name="organization_access_case_policy",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "organization_id",
                    "data_collection_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("organization_id", Organization, "organization"),
                2: ("data_collection_id", DataCollection, "data_collection"),
                3: ("case_type_set_id", CaseTypeSet, "case_type_set"),
                4: (
                    "read_case_type_col_set_id",
                    CaseTypeColSet,
                    "read_case_type_col_set",
                ),
                5: (
                    "write_case_type_col_set_id",
                    CaseTypeColSet,
                    "write_case_type_col_set",
                ),
            }
        ),
        **_ENTITY_KWARGS,
    )
    organization_id: UUID = Field(description="The ID of the organization. FOREIGN KEY")
    organization: Organization | None = Field(
        default=None, description="The organization"
    )
    is_private: bool = Field(
        description="Whether the data collection is private, limited to the case types in the case type set. When true, add/remove case and add/remove case set are considered (i) as the right to create/delete a case or case set in this data collection (setting case.created_in_data_collection to this data collection) and (ii) as the right to share the case or case set further in other data collections. Deleting a case or case set is only allowed when it can or has been removed from all other data collections as well."
    )
    read_case_type_col_set_id: UUID | None = Field(
        default=None,
        description="The ID of the case type column set for which values can be read, limited to the case types in the case type set. If empty, there are no read rights. FOREIGN KEY",
    )
    read_case_type_col_set: CaseTypeColSet | None = Field(
        default=None, description="The case type column set with read access"
    )
    write_case_type_col_set_id: UUID | None = Field(
        default=None,
        description="The ID of the case type column set for which values can be updated, limited to the case types in the case type set.  If empty, there are no write rights. FOREIGN KEY",
    )
    write_case_type_col_set: CaseTypeColSet | None = Field(
        default=None, description="The case type column set with write access"
    )
    read_case_set: bool = Field(
        description="Whether case set be read, limited to the case types in the case type set"
    )
    write_case_set: bool = Field(
        description="Whether case set be updated, limited to the case types in the case type set"
    )


class UserAccessCasePolicy(BaseCasePolicy):
    """
    Stores the maximum access rights of a user to a particular data collection,
    analogous to the organization access case policy.

    The actual access rights of a user are derived as the intersection of their maximum
    access rights stored here, and the access rights of the organization to which they
    belong.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="user_access_case_policies",
        table_name="user_access_case_policy",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "user_id",
                    "data_collection_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("user_id", User, "user"),
                2: ("data_collection_id", DataCollection, "data_collection"),
                3: ("case_type_set_id", CaseTypeSet, "case_type_set"),
                4: (
                    "read_case_type_col_set_id",
                    CaseTypeColSet,
                    "read_case_type_col_set",
                ),
                5: (
                    "write_case_type_col_set_id",
                    CaseTypeColSet,
                    "write_case_type_col_set",
                ),
            }
        ),
        **_ENTITY_KWARGS,
    )
    user_id: UUID = Field(description="The ID of the user. FOREIGN KEY")
    user: User | None = Field(default=None, description="The user")
    read_case_type_col_set_id: UUID | None = Field(
        default=None,
        description="The ID of the case type column set for which values can be read, limited to the case types in the case type set.  If empty, there are no read rights. FOREIGN KEY",
    )
    read_case_type_col_set: CaseTypeColSet | None = Field(
        default=None, description="The case type column set with read access"
    )
    write_case_type_col_set_id: UUID | None = Field(
        default=None,
        description="The ID of the case type column set for which values can be updated, limited to the case types in the case type set.  If empty, there are no write rights. FOREIGN KEY",
    )
    write_case_type_col_set: CaseTypeColSet | None = Field(
        default=None, description="The case type column set with write access"
    )
    read_case_set: bool = Field(
        description="Whether case set be read, limited to the case types in the case type set"
    )
    write_case_set: bool = Field(
        description="Whether case set be updated, limited to the case types in the case type set"
    )


class OrganizationShareCasePolicy(BaseCasePolicy):
    """
    Stores any additional case or case set share rights of an organization to a
    particular data collection, if the case or case set is already in a particular
    other data collection.

    The share rights are limited to the case types in the case type set. If a case type
    is not in the case type set, the organization has no share rights to that data
    collection for that case type.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="organization_share_case_policies",
        table_name="organization_share_case_policy",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "organization_id",
                    "data_collection_id",
                    "from_data_collection_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("organization_id", Organization, "organization"),
                2: ("data_collection_id", DataCollection, "data_collection"),
                3: ("case_type_set_id", CaseTypeSet, "case_type_set"),
                4: ("from_data_collection_id", DataCollection, "from_data_collection"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    organization_id: UUID = Field(description="The ID of the organization. FOREIGN KEY")
    organization: Organization | None = Field(
        default=None, description="The organization"
    )
    from_data_collection_id: UUID = Field(
        description="The ID of the data collection from which the case type set is shared. FOREIGN KEY"
    )
    from_data_collection: DataCollection | None = Field(
        default=None,
        description="The data collection from which the case type set is shared",
    )


class UserShareCasePolicy(BaseCasePolicy):
    """
    Stores the maximum share rights of a user to a particular data collection,
    analogous to the organization share case policy.

    The actual share rights of a user are derived as the intersection of their maximum
    share rights stored here, and the share rights of the organization to which they
    belong.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="user_share_case_policies",
        table_name="user_share_case_policy",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "user_id",
                    "data_collection_id",
                    "from_data_collection_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("user_id", User, "user"),
                2: ("data_collection_id", DataCollection, "data_collection"),
                3: ("case_type_set_id", CaseTypeSet, "case_type_set"),
                4: ("from_data_collection_id", DataCollection, "from_data_collection"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    user_id: UUID = Field(description="The ID of the user. FOREIGN KEY")
    user: User | None = Field(default=None, description="The user")
    from_data_collection_id: UUID = Field(
        description="The ID of the data collection from which the case type set is shared. FOREIGN KEY"
    )
    from_data_collection: DataCollection | None = Field(
        default=None,
        description="The data collection from which the case type set is shared",
    )

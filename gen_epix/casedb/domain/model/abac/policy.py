"""Define persistent organization and user ABAC policy records for cases.

Access policies grant rights within one data collection. Share policies grant
additional rights to move cases or case sets to or from a target collection when
they are already present in an allowed source collection.
"""

from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.casedb.domain.model.case import CaseTypeSet, ColSet
from gen_epix.commondb.domain import model as common_model
from gen_epix.fastapp.domain import Entity, create_keys, create_links


class BaseCasePolicy(common_model.Model):
    """Represents common case and case-set rights for a case-type set."""

    data_collection_id: UUID = Field(
        description="The ID of the data collection. FOREIGN KEY"
    )
    data_collection: common_model.DataCollection | None = Field(
        default=None, description="The data collection"
    )
    case_type_set_id: UUID = Field(
        description="The ID of the CaseTypeSet. FOREIGN KEY",
    )
    case_type_set: CaseTypeSet | None = Field(
        default=None, description="The CaseTypeSet"
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
    """Represents an organization's access rights in one data collection.

    If an organization does not have a policy to a data collection, it has no
    access rights to that data collection.

    The access rights are limited to the CaseTypes in the CaseTypeSet. If a
    CaseType is not in the CaseTypeSet, the organization has no access
    rights to that data collection for that CaseType.
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
                1: ("organization_id", common_model.Organization, "organization"),
                2: (
                    "data_collection_id",
                    common_model.DataCollection,
                    "data_collection",
                ),
                3: ("case_type_set_id", CaseTypeSet, "case_type_set"),
                4: (
                    "read_col_set_id",
                    ColSet,
                    "read_col_set",
                ),
                5: (
                    "write_col_set_id",
                    ColSet,
                    "write_col_set",
                ),
            }
        ),
    )
    organization_id: UUID = Field(description="The ID of the organization. FOREIGN KEY")
    organization: common_model.Organization | None = Field(
        default=None, description="The organization"
    )
    is_private: bool = Field(
        description="Whether the data collection is private, limited to the CaseTypes in the CaseTypeSet. When true, add/remove case and add/remove case set are considered (i) as the right to create/delete a case or case set in this data collection (setting case.created_in_data_collection to this data collection) and (ii) as the right to share the case or case set further in other data collections. Deleting a case or case set is only allowed when it can or has been removed from all other data collections as well."
    )
    read_col_set_id: UUID | None = Field(
        default=None,
        description="The ID of the column set for which values can be read, limited to the CaseTypes in the CaseTypeSet. If empty, there are no read rights. FOREIGN KEY",
    )
    read_col_set: ColSet | None = Field(
        default=None, description="The column set with read access"
    )
    write_col_set_id: UUID | None = Field(
        default=None,
        description="The ID of the column set for which values can be updated, limited to the CaseTypes in the CaseTypeSet.  If empty, there are no write rights. FOREIGN KEY",
    )
    write_col_set: ColSet | None = Field(
        default=None, description="The column set with write access"
    )
    read_case_set: bool = Field(
        description="Whether case set be read, limited to the CaseTypes in the CaseTypeSet"
    )
    write_case_set: bool = Field(
        description="Whether case set be updated, limited to the CaseTypes in the CaseTypeSet"
    )


class UserAccessCasePolicy(BaseCasePolicy):
    """Represents a user's maximum access rights in one data collection.

    The rights are
    analogous to the organization access case policy.

    The actual access rights of a user are derived as the intersection of their
    maximum access rights stored here, and the access rights of the organization
    to which they belong.
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
                1: ("user_id", common_model.User, "user"),
                2: (
                    "data_collection_id",
                    common_model.DataCollection,
                    "data_collection",
                ),
                3: ("case_type_set_id", CaseTypeSet, "case_type_set"),
                4: (
                    "read_col_set_id",
                    ColSet,
                    "read_col_set",
                ),
                5: (
                    "write_col_set_id",
                    ColSet,
                    "write_col_set",
                ),
            }
        ),
    )
    user_id: UUID = Field(description="The ID of the user. FOREIGN KEY")
    user: common_model.User | None = Field(default=None, description="The user")
    read_col_set_id: UUID | None = Field(
        default=None,
        description="The ID of the column set for which values can be read, limited to the CaseTypes in the CaseTypeSet.  If empty, there are no read rights. FOREIGN KEY",
    )
    read_col_set: ColSet | None = Field(
        default=None, description="The column set with read access"
    )
    write_col_set_id: UUID | None = Field(
        default=None,
        description="The ID of the column set for which values can be updated, limited to the CaseTypes in the CaseTypeSet.  If empty, there are no write rights. FOREIGN KEY",
    )
    write_col_set: ColSet | None = Field(
        default=None, description="The column set with write access"
    )
    read_case_set: bool = Field(
        description="Whether case set be read, limited to the CaseTypes in the CaseTypeSet"
    )
    write_case_set: bool = Field(
        description="Whether case set be updated, limited to the CaseTypes in the CaseTypeSet"
    )


class OrganizationShareCasePolicy(BaseCasePolicy):
    """Represents an organization's additional source-to-target share rights.

    Rights apply to the target ``data_collection_id`` when a case or case set is
    already present in ``from_data_collection_id``.

    The share rights are limited to the CaseTypes in the CaseTypeSet. If a
    CaseType is not in the CaseTypeSet, the organization has no share rights
    to that data collection for that CaseType.
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
                1: ("organization_id", common_model.Organization, "organization"),
                2: (
                    "data_collection_id",
                    common_model.DataCollection,
                    "data_collection",
                ),
                3: ("case_type_set_id", CaseTypeSet, "case_type_set"),
                4: (
                    "from_data_collection_id",
                    common_model.DataCollection,
                    "from_data_collection",
                ),
            }
        ),
    )
    organization_id: UUID = Field(description="The ID of the organization. FOREIGN KEY")
    organization: common_model.Organization | None = Field(
        default=None, description="The organization"
    )
    from_data_collection_id: UUID = Field(
        description="The ID of the data collection from which the CaseTypeSet is shared. FOREIGN KEY"
    )
    from_data_collection: common_model.DataCollection | None = Field(
        default=None,
        description="The data collection from which the CaseTypeSet is shared",
    )


class UserShareCasePolicy(BaseCasePolicy):
    """Represents a user's maximum source-to-target share rights.

    The rights are
    analogous to the organization share case policy.

    The actual share rights of a user are derived as the intersection of their
    maximum share rights stored here, and the share rights of the organization
    to which they belong.
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
                1: ("user_id", common_model.User, "user"),
                2: (
                    "data_collection_id",
                    common_model.DataCollection,
                    "data_collection",
                ),
                3: ("case_type_set_id", CaseTypeSet, "case_type_set"),
                4: (
                    "from_data_collection_id",
                    common_model.DataCollection,
                    "from_data_collection",
                ),
            }
        ),
    )
    user_id: UUID = Field(description="The ID of the user. FOREIGN KEY")
    user: common_model.User | None = Field(default=None, description="The user")
    from_data_collection_id: UUID = Field(
        description="The ID of the data collection from which the CaseTypeSet is shared. FOREIGN KEY"
    )
    from_data_collection: common_model.DataCollection | None = Field(
        default=None,
        description="The data collection from which the CaseTypeSet is shared",
    )

import datetime
import json
from enum import Enum
from typing import Any, ClassVar, Type
from uuid import UUID

from pydantic import Field, field_serializer, field_validator

from gen_epix.common.domain import enum
from gen_epix.common.domain.model.base import Model
from gen_epix.fastapp import User as ServiceUser
from gen_epix.fastapp.domain import Entity, create_keys, create_links

_SERVICE_TYPE = enum.ServiceType.ORGANIZATION
_ENTITY_KWARGS = {
    "schema_name": _SERVICE_TYPE.value.lower(),
}


class Organization(Model):
    """
    Represents an organization.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="organizations",
        table_name="organization",
        persistable=True,
        keys=create_keys({1: "name", 2: "legal_entity_code"}),
        **_ENTITY_KWARGS,
    )
    name: str = Field(
        description="The name of the organization, UNIQUE", max_length=255
    )
    legal_entity_code: str = Field(
        description="The legal entity code of the organization, UNIQUE", max_length=255
    )


class UserNameEmail(ServiceUser, Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="user_name_emails",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    id: UUID | None = Field(  # pyright: ignore[reportIncompatibleVariableOverride]
        default=None, description="The ID of the user"
    )
    name: str | None = Field(
        default=None, description="The full name of the user", max_length=255
    )
    email: str = Field(description="The email of the user", max_length=320)


class User(ServiceUser, Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="users",
        table_name="user",
        persistable=True,
        keys=create_keys({1: "email"}),
        links=create_links(
            {
                1: ("organization_id", Organization, "organization"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    ROLE_ENUM: ClassVar[Type[Enum]] = Enum
    id: UUID | None = Field(
        default=None, description="The ID of the user"
    )  # pyright: ignore[reportIncompatibleVariableOverride]
    email: str = Field(description="The email of the user, UNIQUE", max_length=320)
    name: str | None = Field(
        default=None, description="The full name of the user", max_length=255
    )

    is_active: bool = Field(
        default=True,
        description="Whether the user is active or not. An inactive user cannot perform any actions that require authorization.",
    )
    roles: set[Enum] = Field(description="The roles of the user", min_length=1)
    organization_id: UUID = Field(
        description="The ID of the organization of the user. FOREIGN KEY"
    )
    organization: Organization | None = Field(
        default=None, description="The organization of the user"
    )

    def get_key(self) -> str:
        return self.email

    @field_validator("roles", mode="before")
    @classmethod
    def _validate_roles(cls, value: set[Enum] | list[str] | str) -> set[Enum]:
        """
        Validate and convert roles representation to a set[Role]. When given as a
        string, it is assumed to be a JSON list of Role values.
        """
        if isinstance(value, str):
            return {cls.ROLE_ENUM[x] for x in json.loads(value)}
        if isinstance(value, list):
            return {cls.ROLE_ENUM[x] for x in value}
        return value

    # @field_serializer("id")
    # def _serialize_id(self, value: UUID | None, _info: Any) -> UUID | None:
    #     return value

    @field_serializer("roles")
    def serialize_roles(self, value: set[Enum], _info: Any) -> list[str]:
        return [x.value for x in value]


class OrganizationSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="organization_sets",
        table_name="organization_set",
        persistable=True,
        keys=create_keys({1: "name"}),
        **_ENTITY_KWARGS,
    )
    name: str = Field(description="The name of the organization set", max_length=255)
    description: str | None = Field(
        None, description="The description of the organization set."
    )


class OrganizationSetMember(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="organization_set_members",
        table_name="organization_set_member",
        persistable=True,
        keys=create_keys({1: ("organization_set_id", "organization_id")}),
        links=create_links(
            {
                1: ("organization_set_id", OrganizationSet, "organization_set"),
                2: ("organization_id", Organization, "organization"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    organization_set_id: UUID = Field(
        description="The ID of the organization set. FOREIGN KEY"
    )
    organization_set: OrganizationSet | None = Field(
        default=None, description="The organization set"
    )
    organization_id: UUID = Field(description="The ID of the organization. FOREIGN KEY")
    organization: Organization | None = Field(None, description="The organization")


class Site(Model):
    """
    Represents a physical site of an organization.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="sites",
        table_name="site",
        persistable=True,
        keys=create_keys({1: ("organization_id", "name")}),
        links=create_links(
            {
                1: ("organization_id", Organization, "organization"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    organization_id: UUID = Field(description="The ID of the organization. FOREIGN KEY")
    organization: Organization | None = Field(
        default=None, description="The organization corresponding to the ID"
    )
    name: str = Field(description="The name of an organization, UNIQUE", max_length=255)


class Contact(Model):
    """
    A class representing contact information for an organization.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="contacts",
        table_name="contact",
        persistable=True,
        keys=create_keys({1: ("site_id", "name")}),
        links=create_links(
            {
                1: ("site_id", Site, "site"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    # TODO: Temporary implementation, check established models for this
    site_id: UUID | None = Field(
        description="The ID of the site in case the contact is site-specific. FOREIGN KEY",
    )
    site: Site | None = Field(
        default=None, description="The site corresponding to the ID"
    )
    name: str = Field(description="The name of the contact, UNIQUE", max_length=255)
    email: str | None = Field(
        default=None, description="The email address of the contact", max_length=320
    )
    phone: str | None = Field(
        default=None, description="The phone number of the contact"
    )


class IdentifierIssuer(Model):
    """
    A system or process that issues identifiers.
    The combination (identifier_issuer, issued_identifier) is universally unique.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="identifier_issuers",
        table_name="identifier_issuer",
        persistable=True,
        **_ENTITY_KWARGS,
    )
    name: str = Field(description="The name of the issuer", max_length=255)


class DataCollection(Model):
    """
    Represents a collection of data.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="data_collections",
        table_name="data_collection",
        persistable=True,
        keys=create_keys({1: "name"}),
        **_ENTITY_KWARGS,
    )
    # TODO: Placeholder
    name: str = Field(
        description="The name of a data collection, UNIQUE", max_length=255
    )
    description: str | None = Field(
        default=None, description="The description of the data collection."
    )


class DataCollectionSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="data_collection_sets",
        table_name="data_collection_set",
        persistable=True,
        keys=create_keys({1: "name"}),
        **_ENTITY_KWARGS,
    )
    name: str = Field(description="The name of the data collection set", max_length=255)
    description: str | None = Field(
        default=None, description="The description of the data collection set."
    )


class DataCollectionSetMember(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="data_collection_set_members",
        table_name="data_collection_set_member",
        persistable=True,
        keys=create_keys(
            {1: ("data_collection_set_id", "data_collection_id")},
        ),
        links=create_links(
            {
                1: ("data_collection_set_id", DataCollectionSet, "data_collection_set"),
                2: ("data_collection_id", DataCollection, "data_collection"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    data_collection_set_id: UUID = Field(
        description="The ID of the data collection set. FOREIGN KEY"
    )
    data_collection_set: DataCollectionSet | None = Field(
        default=None, description="The data collection set"
    )
    data_collection_id: UUID = Field(
        description="The ID of the data collection. FOREIGN KEY"
    )
    data_collection: DataCollection | None = Field(
        default=None, description="The data collection"
    )


class UserInvitation(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="user_invitations",
        table_name="user_invitation",
        persistable=True,
        keys=create_keys({1: ("email", "expires_at")}),
        links=create_links(
            {
                1: ("organization_id", Organization, "organization"),
                2: ("invited_by_user_id", User, "invited_by_user"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    ROLE_ENUM: ClassVar[Type[Enum]] = Enum
    email: str = Field(description="The email of the user, UNIQUE", max_length=320)
    token: str = Field(description="The token of the invitation", max_length=255)
    expires_at: datetime.datetime = Field(
        description="The expiry date of the invitation"
    )
    roles: set[Enum] = Field(description="The initial roles of the user", min_length=1)
    invited_by_user_id: UUID = Field(
        description="The ID of the user who invited the user. FOREIGN KEY"
    )
    invited_by_user: User | None = Field(
        default=None, description="The user who invited the user"
    )
    organization_id: UUID = Field(
        description="The ID of the organization of the user. FOREIGN KEY"
    )
    organization: Organization | None = Field(
        default=None, description="The organization of the user"
    )

    @field_validator("roles", mode="before")
    @classmethod
    def _validate_roles(cls, value: set[Enum] | list[str] | str) -> set[Enum]:
        """
        Validate and convert roles representation to a set[Role]. When given as a
        string, it is assumed to be a JSON list of Role values.
        """
        if isinstance(value, str):
            return {cls.ROLE_ENUM[x] for x in json.loads(value)}
        if isinstance(value, list):
            return {cls.ROLE_ENUM[x] for x in value}
        return value

    @field_serializer("roles")
    def serialize_roles(self, value: set[Enum], _info) -> list[str]:
        return [x.value for x in value]

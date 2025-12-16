import datetime
import json
from enum import Enum
from typing import ClassVar, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from gen_epix import fastapp
from gen_epix.commondb.domain import enum
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.util import copy_model_field


class Organization(Model):
    """
    Represents an organization.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="organizations",
        table_name="organization",
        persistable=True,
        keys=create_keys({1: "name", 2: "legal_entity_code"}),
    )
    name: str = Field(
        description="The name of the organization, UNIQUE", max_length=255
    )
    legal_entity_code: str = Field(
        description="The legal entity code of the organization, UNIQUE", max_length=255
    )


class UserNameEmail(fastapp.Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="user_name_emails",
        persistable=False,
    )
    id: UUID | None = Field(  # pyright: ignore[reportIncompatibleVariableOverride]
        default=None, description="The ID of the user"
    )
    name: str | None = Field(
        default=None, description="The full name of the user", max_length=255
    )
    email: str | None = Field(description="The email of the user", max_length=320)


class User(fastapp.User, Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="users",
        table_name="user",
        persistable=True,
        keys=create_keys({1: "key"}),
        links=create_links(
            {
                1: ("organization_id", Organization, "organization"),
            }
        ),
    )
    id: UUID | None = Field(
        default=None, description="The ID of the user"
    )  # pyright: ignore[reportIncompatibleVariableOverride]
    key: str = Field(
        description="The key of the user, lowercase, UNIQUE", max_length=320
    )
    email: str | None = Field(
        default=None, description="The email of the user", max_length=320
    )
    name: str | None = Field(
        default=None, description="The full name of the user", max_length=255
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user is active or not. An inactive user cannot perform any actions that require authorization.",
    )
    roles: set[str] = Field(description="The roles of the user", min_length=1)
    organization_id: UUID = Field(
        description="The ID of the organization of the user. FOREIGN KEY"
    )
    organization: Organization | None = Field(
        default=None, description="The organization of the user"
    )

    @field_validator("key", mode="before")
    @classmethod
    def _validate_key(cls, value: str) -> str:
        return value.lower()

    def get_key(self) -> str:
        return self.key

    @field_validator("roles", mode="before")
    @classmethod
    def _validate_roles(cls, value: set[str] | list[str] | str) -> set[str]:
        """
        Validate and convert roles representation to a set[str]. When given as a
        string, it is assumed to be a JSON list.
        """
        if isinstance(value, str):
            return set(json.loads(value))
        if isinstance(value, list):
            return set(value)
        return value

    @field_serializer("roles", mode="plain")
    def _serialize_roles(self, value: set[str]) -> list[str]:
        return list(value)


class OrganizationSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="organization_sets",
        table_name="organization_set",
        persistable=True,
        keys=create_keys({1: "name"}),
    )
    name: str = Field(description="The name of the organization set", max_length=255)
    description: str | None = Field(
        None, description="The description of the organization set.", max_length=1000
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
    )
    # TODO: Temporary implementation, check established models for this
    site_id: UUID = Field(
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
        keys=create_keys({1: "code"}),
    )
    code: str = Field(description="The name of the issuer", max_length=255)
    name: str = Field(description="The name of the issuer", max_length=255)
    description: str | None = Field(
        default=None,
        description="The description of the identifier issuer.",
        max_length=1000,
    )


class DataCollection(Model):
    """
    Represents a collection of data.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="data_collections",
        table_name="data_collection",
        persistable=True,
        keys=create_keys({1: "name"}),
    )
    # TODO: Placeholder
    name: str = Field(
        description="The name of a data collection, UNIQUE", max_length=255
    )
    description: str | None = Field(
        default=None,
        description="The description of the data collection.",
        max_length=1000,
    )


class DataCollectionSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="data_collection_sets",
        table_name="data_collection_set",
        persistable=True,
        keys=create_keys({1: "name"}),
    )
    name: str = Field(description="The name of the data collection set", max_length=255)
    description: str | None = Field(
        default=None,
        description="The description of the data collection set.",
        max_length=1000,
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
    """
    Represents an invitation for a new user of a particular organization and
    with particular starting properties.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="user_invitations",
        table_name="user_invitation",
        persistable=True,
        keys=create_keys({1: ("key", "expires_at")}),
        links=create_links(
            {
                1: ("organization_id", Organization, "organization"),
                2: ("invited_by_user_id", User, "invited_by_user"),
            }
        ),
    )
    ROLE_ENUM: ClassVar[type[Enum]] = enum.Role
    key: str = copy_model_field(User, "key")
    email: str | None = copy_model_field(User, "email")
    name: str | None = copy_model_field(User, "name")
    token: str = Field(description="The token of the invitation", max_length=255)
    expires_at: datetime.datetime = Field(
        description="The expiry date of the invitation"
    )
    roles: set[str] = Field(
        description="The initial roles that the new user will have", min_length=1
    )
    invited_by_user_id: UUID = Field(
        description="The ID of the user who invited the new user. FOREIGN KEY"
    )
    invited_by_user: User | None = Field(
        default=None, description="The user who invited the new user"
    )
    organization_id: UUID = Field(
        description="The ID of the organization that the new user will belong to. FOREIGN KEY"
    )
    organization: Organization | None = Field(
        default=None, description="The organization that the new user will belong to"
    )

    @field_validator("roles", mode="before")
    @classmethod
    def _validate_roles(cls, value: set[str] | list[str] | str) -> set[str]:
        """
        Validate and convert roles representation to a set[str]. When given as a
        string, it is assumed to be a JSON list.
        """
        if isinstance(value, str):
            return set(json.loads(value))
        if isinstance(value, list):
            return set(value)
        return value

    @field_serializer("roles", mode="plain")
    def _serialize_roles(self, value: set[str]) -> list[str]:
        return list(value)


class UserInvitationConstraints(Model):
    """
    Represents the constraints for a user invitation.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="user_invitation_constraints",
        persistable=False,
    )
    ROLE_ENUM: ClassVar[type[Enum]] = enum.Role
    roles: set[str] = Field(
        description="The roles that the user may be assigned by the inviting user."
    )
    organization_ids: set[UUID] = Field(
        description="The organizations that the user may be assigned by the inviting user."
    )


class OrganizationIdentifierIssuerLink(Model):
    """
    The association between an organization and an identifier issuer.

    This information can be used to restrict which identifier issuers
    are available to users of a particular organization.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="organization_identifier_issuer_links",
        table_name="organization_identifier_issuer_link",
        persistable=True,
        keys=create_keys({1: ("organization_id", "identifier_issuer_id")}),
        links=create_links(
            {
                1: ("organization_id", Organization, "organization"),
                2: ("identifier_issuer_id", IdentifierIssuer, "identifier_issuer"),
            }
        ),
    )
    organization_id: UUID = Field(description="The ID of the organization. FOREIGN KEY")
    organization: Organization | None = Field(
        default=None, description="The organization corresponding to the ID"
    )
    identifier_issuer_id: UUID = Field(
        description="The ID of the identifier issuer. FOREIGN KEY"
    )
    identifier_issuer: IdentifierIssuer | None = Field(
        default=None, description="The identifier issuer corresponding to the ID"
    )


class ExternalIdentifier(Model):
    """
    An externally generated identifier of a particular type and its corresponding
    internal identifier. The externally generated identifier consists of the
    combination (identifier issuer, identifier)
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="external_identifiers",
        table_name="external_identifier",
        persistable=True,
        keys=create_keys(
            {
                1: ("identifier_type", "identifier_issuer_id", "external_id"),
                2: ("identifier_type", "internal_id"),
            }
        ),
        links=create_links(
            {
                1: ("identifier_issuer_id", IdentifierIssuer, "identifier_issuer"),
            }
        ),
    )
    identifier_type: enum.IdentifierType = Field(
        description="The type of external identifier"
    )
    identifier_issuer_id: UUID = Field(
        description="The UUID of the identifier issuer that issued the external identifier",
    )
    identifier_issuer: IdentifierIssuer | None = Field(
        default=None, description="The identifier issuer corresponding to the ID"
    )
    external_id: str = Field(description="The external identifier", max_length=255)
    internal_id: UUID = Field(
        description="The internal identifier. This identifier is not guaranteed to still exist, so operations using it should check this first."
    )


class ExternalIdentifierForUpload(BaseModel):
    """
    An external identifier, defined as the combination of
    (identifier issuer, identifier), intended for an upload operation.
    The identifier issuer can be given either as its code or ID to facilitate the
    upload operation where applicable.
    """

    identifier_issuer_id: UUID | None = Field(
        default=None,
        description="The UUID of the identifier issuer that issued the identifier. Must be present if the identifier_issuer_code is not present.",
    )
    identifier_issuer_code: str | None = Field(
        default=None,
        description="The code of the identifier issuer that issued the identifier. Must be present if the identifier_issuer_id is not present.",
        max_length=255,
    )
    identifier: str = Field(description="The external identifier", max_length=255)

    @model_validator(mode="after")
    def _validate_issuer_fields(self) -> Self:
        """Ensure that either identifier_issuer_id or identifier_issuer_code is set."""
        if self.identifier_issuer_id is None and self.identifier_issuer_code is None:
            raise ValueError(
                "Either identifier_issuer_id or identifier_issuer_code must be provided."
            )
        return self

    def __eq__(self, other: object) -> bool:
        """
        Check equality based on identifier_issuer_id, identifier_issuer_code, and identifier.
        Only when all three match, the objects are considered equal.
        """
        if not isinstance(other, ExternalIdentifierForUpload):
            return NotImplemented
        return (
            self.identifier_issuer_id == other.identifier_issuer_id
            and self.identifier_issuer_code == other.identifier_issuer_code
            and self.identifier == other.identifier
        )

    def __hash__(self) -> int:
        return hash(
            (self.identifier_issuer_id, self.identifier_issuer_code, self.identifier)
        )

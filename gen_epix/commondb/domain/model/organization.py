"""Define commondb organization, user, contact, and identifier models.

The models represent organizational membership and contact data, user
invitations, collections, and externally issued identifiers. They are shared
by services, policies, and repositories across application domains.
"""

import datetime
import hashlib
import json
from enum import Enum
from typing import Any, ClassVar, Self
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
    """Represent an organization that owns users and related domain data."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="organizations",
        table_name="organization",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
    )
    code: str = Field(
        description="The code of the organization, UNIQUE", max_length=255
    )
    name: str = Field(
        description="The name of the organization, UNIQUE", max_length=255
    )
    description: str | None = Field(
        default=None,
        description="The description of the organization.",
        max_length=1000,
    )


class UserNameEmail(fastapp.Model):
    """Expose a non-persisted user identity for display and lookup responses."""

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
    """Represent an authenticated commondb user and their organization membership.

    The user key is stored lower case for unique lookup. Inactive users retain
    their data but cannot perform operations that require authorization.
    """

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
    key: str | None = Field(
        default=None,
        description="Unique user key, normalized to lowercase.",
        max_length=320,
    )
    email: str | None = Field(
        default=None, description="The email of the user", max_length=320
    )
    name: str | None = Field(
        default=None, description="The full name of the user", max_length=255
    )
    description: str | None = Field(
        default=None,
        description="The description of the user.",
        max_length=1000,
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user is active or not. An inactive user cannot perform any actions that require authorization.",
    )
    roles: set[str] = Field(
        description="User roles, accepting a set, list, or JSON list string and serializing as a list.",
        min_length=1,
        max_length=255,
    )
    organization_id: UUID = Field(
        description="The ID of the organization of the user. FOREIGN KEY"
    )
    organization: Organization | None = Field(
        default=None, description="The organization of the user"
    )
    # TODO: potentially added is_anonymized field to indicate if the user has been anonymized. Then also add validation that is_active=True and is_anonymized=True is not allowed.

    @field_validator("key", mode="before")
    @classmethod
    def _validate_key(cls, value: str | None) -> str | None:
        """Normalize a supplied user key to lower case."""
        if value is None:
            return None
        return value.lower()

    def get_key(self) -> str:
        """Return the normalized key used to identify this user."""
        return self.key

    @field_validator("roles", mode="before")
    @classmethod
    def _validate_roles(cls, value: set[str] | list[str] | str) -> set[str]:
        """Normalize role input to a set."""
        if isinstance(value, str):
            return set(json.loads(value))
        if isinstance(value, list):
            return set(value)
        return value

    @field_serializer("roles", mode="plain")
    def _serialize_roles(self, value: set[str]) -> list[str]:
        """Serialize the user's role set as a JSON-compatible list."""
        return list(value)


class OrganizationSet(Model):
    """Represent a named, persisted collection of organizations."""

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
    """Associate one organization with a persisted organization set."""

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
    """Represent a physical site belonging to an organization."""

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
    """Represent contact information associated with an organization site."""

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
    """Represent a system or process that issues externally supplied identifiers.

    An identifier issuer combined with an identifier issued by it is a universally
    unique value.
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
    """Represent a named collection of data managed by commondb."""

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
    """Represent a named, persisted collection of data collections."""

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
    """Associate one data collection with a persisted data-collection set."""

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
    """Represent an expiring invitation with a user's initial organization and roles."""

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
    key: str | None = Field(
        default=None,
        description="Unique user key; an empty value is normalized to omitted.",
        max_length=320,
    )
    email: str | None = copy_model_field(User, "email")
    name: str | None = copy_model_field(User, "name")
    description: str | None = copy_model_field(User, "description")
    token: str = Field(description="The token of the invitation", max_length=255)
    expires_at: datetime.datetime = Field(
        description="The expiry date of the invitation"
    )
    roles: set[str] = Field(
        description="Initial roles, accepting a set, list, or JSON list string and serializing as a list.",
        min_length=1,
        max_length=255,
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

    @field_validator("key", mode="before")
    @classmethod
    def _validate_key(cls, value: str | None) -> str | None:
        """Convert an empty invitation user key to an omitted key."""
        if value == "":
            return None
        return value

    @field_validator("roles", mode="before")
    @classmethod
    def _validate_roles(cls, value: set[str] | list[str] | str) -> set[str]:
        """Normalize invitation role input to a set."""
        if isinstance(value, str):
            return set(json.loads(value))
        if isinstance(value, list):
            return set(value)
        return value

    @field_serializer("roles", mode="plain")
    def _serialize_roles(self, value: set[str]) -> list[str]:
        """Serialize the invitation's initial roles as a JSON-compatible list."""
        return list(value)


class UserInvitationConstraints(Model):
    """Constrain roles and organizations an inviting user may assign."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="user_invitation_constraints",
        persistable=False,
    )
    ROLE_ENUM: ClassVar[type[Enum]] = enum.Role
    roles: set[str] = Field(
        description="The roles that the user may be assigned by the inviting user.",
        max_length=255,
    )
    organization_ids: set[UUID] = Field(
        description="The organizations that the user may be assigned by the inviting user.",
        max_length=1000000,
    )


class OrganizationIdentifierIssuerLink(Model):
    """Associate an organization with an identifier issuer it may use.

    Services can use these links to restrict identifier issuers available to users
    of a particular organization.
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


class BaseIdentifier(Model):
    """Represent an identifier generated outside the system for an entity.

    It records an identifier issuer and the system's own
    identifier.

    Subclasses bind ``MODEL_CLASS`` to the related domain model. The identifier
    UUID is deterministically derived from the issuer UUID and normalized
    external identifier, making each issuer/external-ID pair unique.

    Model validation:
    A missing ``id`` is derived deterministically from ``identifier_issuer_id``
    and ``external_id``; a supplied ID must match that derived value.
    """

    ENTITY: ClassVar = Entity(persistable=False, id_field_name="id")

    # The model class associated with this base identifier, to be defined in subclasses
    MODEL_CLASS: ClassVar[type[fastapp.Model]] = None  # type: ignore[assignment]

    id: UUID | None = Field(
        default=None,
        description="The ID of the identifier. Computed as the UUID of the first 16 bytes of the SHA-256 hash of the concatenated identifier_issuer_id bytes and the external_id encoded as UTF-8. PRIMARY KEY",
    )
    identifier_issuer_id: UUID = Field(
        description="The UUID of the identifier issuer that issued the identifier",
    )
    identifier_issuer: IdentifierIssuer | None = Field(
        default=None, description="The identifier issuer corresponding to the ID"
    )
    external_id: str = Field(
        description="Issuer-provided identifier, normalized by stripping leading and trailing whitespace.",
        max_length=255,
    )
    internal_id: UUID = Field(description="The internal identifier.")

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        """Derive or validate the deterministic identifier UUID."""
        seq_id = self.id
        computed_id = UUID(
            hashlib.sha256(
                self.identifier_issuer_id.bytes + self.external_id.encode("utf-8")
            ).hexdigest()[:32]
        )
        # Set or verify seq_hash
        if seq_id is None:
            self.id = computed_id
        elif seq_id != computed_id:
            raise ValueError("Provided id does not match computed id")
        return self

    @field_validator("external_id", mode="after")
    @classmethod
    def _strip_external_id(cls, value: str) -> str:
        """Strip leading and trailing whitespace from an external identifier."""
        return value.strip()

    @classmethod
    def create_entity(
        cls,
        model_class: type[fastapp.Model],
        relationship_field_name: str | None = None,
        snake_case_plural_name: str | None = None,
        table_name: str | None = None,
        persistable: bool = True,
        **kwargs: Any,
    ) -> Entity:
        """Create persistence metadata for a derived external-identifier model.

        Args:
            model_class: The model identified by the derived identifier.
            relationship_field_name: The relationship name for ``internal_id``.
            snake_case_plural_name: The optional collection name.
            table_name: The optional persistence table name.
            persistable: Whether the derived model is persisted.
            **kwargs: Additional Entity configuration.

        Returns:
            Entity metadata keyed by issuer and external identifier.
        """
        entity = Entity(
            snake_case_plural_name=snake_case_plural_name,
            table_name=table_name,
            persistable=persistable,
            id_field_name="id",
            keys=create_keys(
                {
                    1: ("identifier_issuer_id", "external_id"),
                }
            ),
            links=create_links(
                {
                    1: ("identifier_issuer_id", IdentifierIssuer, "identifier_issuer"),
                    2: ("internal_id", model_class, relationship_field_name),
                }
            ),
            **kwargs,
        )
        return entity


class IdentifierForUpload(BaseModel, frozen=True):
    """Represent an external identifier used in an upload operation.

    It is defined as the combination of an identifier issuer and identifier.
    The identifier issuer can be given either as its code or ID to facilitate the
    upload operation where applicable.
    The model is immutable (frozen) to allow its use in sets and as dictionary keys.

    Model validation:
    At least one of ``identifier_issuer_id`` or ``identifier_issuer_code`` is required.
    """

    NAME: ClassVar[str] = "IdentifierForUpload"

    identifier_issuer_id: UUID | None = Field(
        default=None,
        description="Issuer UUID; at least this field or identifier_issuer_code is required.",
    )
    identifier_issuer_code: str | None = Field(
        default=None,
        description="Issuer code; at least this field or identifier_issuer_id is required.",
        max_length=255,
    )
    external_id: str = Field(description="The external identifier", max_length=255)

    @model_validator(mode="after")
    def _validate_issuer_fields(self) -> Self:
        """Require an issuer UUID or code."""
        if self.identifier_issuer_id is None and self.identifier_issuer_code is None:
            raise ValueError(
                "Either identifier_issuer_id or identifier_issuer_code must be provided."
            )
        return self

    def __eq__(self, other: object) -> bool:
        """Compare issuer references and external ID with another upload identifier."""
        if not isinstance(other, IdentifierForUpload):
            return False
        return (
            self.identifier_issuer_id == other.identifier_issuer_id
            and self.identifier_issuer_code == other.identifier_issuer_code
            and self.external_id == other.external_id
        )

    def __hash__(self) -> int:
        """Return a hash of the issuer references and external identifier."""
        return hash(
            (self.identifier_issuer_id, self.identifier_issuer_code, self.external_id)
        )


class OrganizationContacts(BaseModel):
    """Group an organization with its sites and site-specific contacts."""

    organization: Organization = Field(
        description="The organization corresponding to the contacts"
    )
    sites: list[Site] = Field(description="The list of sites for the organization")
    contacts: list[Contact] = Field(
        description="The list of contacts for the organization"
    )

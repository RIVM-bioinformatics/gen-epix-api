# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


import json
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import Field, field_serializer, field_validator

from gen_epix.fastapp import Permission
from gen_epix.fastapp import User as ServiceUser
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.omopdb.domain import DOMAIN, enum
from gen_epix.omopdb.domain.model.base import Model

_SERVICE_TYPE = enum.ServiceType.ORGANIZATION
_ENTITY_KWARGS = {
    "service_type": _SERVICE_TYPE,
    "schema_name": _SERVICE_TYPE.value.lower(),
}


class UserNameEmail(ServiceUser):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="user_name_emails",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    id: UUID | None = Field(default=None, description="The ID of the user")
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
        **_ENTITY_KWARGS,
    )
    id: UUID | None = Field(default=None, description="The ID of the user")
    email: str = Field(description="The email of the user, UNIQUE", max_length=320)
    name: str | None = Field(
        default=None, description="The full name of the user", max_length=255
    )

    is_active: bool = Field(
        default=True,
        description="Whether the user is active or not. An inactive user cannot perform any actions that require authorization.",
    )
    roles: set[enum.Role] = Field(description="The roles of the user", min_length=1)
    data_collection_ids: set[UUID] = Field(
        description="The data collections the user has access to"
    )

    def get_key(self) -> str:
        return self.email

    @field_validator("roles", mode="before")
    @classmethod
    def _validate_roles(cls, value: set[enum.Role] | list[str] | str) -> set[enum.Role]:
        """
        Validate and convert roles representation to a set[Role]. When given as a
        string, it is assumed to be a JSON list of Role values.
        """
        if isinstance(value, str):
            return {enum.Role[x] for x in json.loads(value)}
        if isinstance(value, list):
            return {enum.Role[x] for x in value}
        return value

    @field_validator("data_collection_ids", mode="before")
    @classmethod
    def _validate_data_collection_ids(
        cls, value: set[UUID] | list[str] | str
    ) -> set[UUID]:
        """
        Validate and convert data_collection_ids representation to a set[UUID].
        When given as a string, it is assumed to be a JSON list of UUIDs.
        """
        if isinstance(value, str):
            return {UUID(x) for x in json.loads(value)}
        if isinstance(value, list):
            return {UUID(x) for x in value}
        return value

    @field_serializer("roles")
    def serialize_roles(self, value: set[enum.Role], _info):
        return [x.value for x in value]

    @field_serializer("data_collection_ids")
    def serialize_data_collection_ids(self, value: set[UUID], _info):
        return [str(x) for x in value]


class UserInvitation(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="user_invitations",
        table_name="user_invitation",
        persistable=True,
        keys=create_keys({1: ("email", "expires_at")}),
        links=create_links(
            {
                1: ("invited_by_user_id", User, "invited_by_user"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    email: str = Field(description="The email of the user, UNIQUE", max_length=320)
    token: str = Field(description="The token of the invitation", max_length=255)
    expires_at: datetime = Field(description="The expiry date of the invitation")
    roles: set[enum.Role] = Field(description="The initial roles of the user")
    data_collection_ids: set[UUID] = Field(
        description="The data collections the user has access to"
    )
    invited_by_user_id: UUID = Field(
        description="The ID of the user who invited the user. FOREIGN KEY"
    )
    invited_by_user: User | None = Field(
        default=None, description="The user who invited the user"
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
    Represents a collection of data with legal relevance.
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


# Not persistable
class CompleteUser(User):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="complete_users",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    roles: set[enum.Role] = Field(description="The roles of the user")
    permissions: set[Permission] = Field(
        description="The union of all the permissions of the user"
    )
    data_collection_ids: set[UUID] = Field(
        description="The ids of the data collections the user has access to"
    )
    data_collections: set[DataCollection] = Field(
        description="The data collections the user has access to"
    )


DOMAIN.register_locals(locals(), service_type=_SERVICE_TYPE)

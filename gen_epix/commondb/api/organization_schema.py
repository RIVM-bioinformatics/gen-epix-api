"""Request and response models of the commondb organization API.

These models are kept apart from the routes that use them, so that a remote
client can import them without importing the web framework.
"""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from gen_epix.commondb.domain import DOMAIN, command, model
from gen_epix.commondb.domain.literal import MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH
from gen_epix.fastapp.enum import PermissionType
from gen_epix.fastapp.model import Permission
from gen_epix.util import copy_model_field

CommandName = Enum("CommandName", {x: x for x in DOMAIN.command_names})  # type: ignore[misc] # Dynamic Enum required


class ApiPermission(PydanticBaseModel, frozen=True):
    """Represents a domain permission in API request and response schemas."""

    command_name: CommandName = (  # pyright: ignore[reportInvalidTypeForm]
        copy_model_field(Permission, "command_name")
    )
    permission_type: PermissionType = copy_model_field(Permission, "permission_type")


class InviteUserRequestBody(PydanticBaseModel):
    """Define the request payload accepted by the user-invitation endpoint."""

    __doc__ = command.InviteUserCommand.__doc__
    key: str | None = copy_model_field(model.UserInvitation, "key")
    description: str | None = copy_model_field(model.UserInvitation, "description")
    roles: set[str] = copy_model_field(
        model.UserInvitation, "roles", max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH
    )
    organization_id: UUID = copy_model_field(model.UserInvitation, "organization_id")


class OrganizationSetOrganizationUpdateAssociationRequestBody(PydanticBaseModel):
    """Define members submitted when updating an organization-set association."""

    __doc__ = command.OrganizationSetOrganizationUpdateAssociationCommand.__doc__
    organization_set_members: list[model.OrganizationSetMember] = copy_model_field(
        command.OrganizationSetOrganizationUpdateAssociationCommand,
        "association_objs",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class DataCollectionSetDataCollectionUpdateAssociationRequestBody(PydanticBaseModel):
    """Define members submitted when updating a data-collection-set association."""

    __doc__ = command.DataCollectionSetDataCollectionUpdateAssociationCommand.__doc__
    data_collection_set_members: list[model.DataCollectionSetMember] = copy_model_field(
        command.DataCollectionSetDataCollectionUpdateAssociationCommand,
        "association_objs",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class UpdateUserRequestBody(PydanticBaseModel):
    """Define optional user fields accepted by the user-update endpoint."""

    __doc__ = command.UpdateUserCommand.__doc__
    is_active: bool | None = Field(
        description="The updated active status of the user. Not updated if not provided."
    )
    roles: set[str] | None = Field(
        description="The updated set of roles of the user. Not updated if not provided. If provided, should have at least one element.",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
    organization_id: UUID | None = Field(
        description="The updated organization ID of the user. Not updated if not provided."
    )


class UpdateUserOwnOrganizationRequestBody(PydanticBaseModel):
    """Define the organization change accepted by the self-service update endpoint."""

    __doc__ = command.UpdateUserOwnOrganizationCommand.__doc__
    organization_id: UUID = copy_model_field(model.User, "organization_id")


class OrganizationIdentifierIssuerUpdateAssociationRequestBody(PydanticBaseModel):
    """Define issuer links submitted when updating an organization association."""

    __doc__ = command.OrganizationIdentifierIssuerUpdateAssociationCommand.__doc__
    organization_identifier_issuer_links: list[
        model.OrganizationIdentifierIssuerLink
    ] = copy_model_field(
        command.OrganizationIdentifierIssuerUpdateAssociationCommand,
        "association_objs",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )


class RetrieveOrganizationContactsRequestBody(PydanticBaseModel):
    """Define the organization whose contacts are requested from the API."""

    __doc__ = command.RetrieveOrganizationContactsCommand.__doc__
    organization_id: UUID = copy_model_field(
        command.RetrieveOrganizationContactsCommand,
        "organization_id",
    )

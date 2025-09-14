from enum import Enum
from typing import ClassVar
from uuid import UUID

from pydantic import Field

import gen_epix.commondb.domain.model.organization as model
from gen_epix.commondb.domain.command.base import (
    Command,
    CrudCommand,
    UpdateAssociationCommand,
)
from gen_epix.commondb.util import copy_model_field

# Non-CRUD commands


class OrganizationSetOrganizationUpdateAssociationCommand(UpdateAssociationCommand):
    """
    Updates the association between an {organization_set}s and {organization}s.

    This command manages the many-to-many relationship by creating or updating
    {organization_set_member} associations between organization sets and
    individual organizations.
    """

    __doc__ = str(__doc__).format(
        organization_set=model.OrganizationSet.__name__,
        organization=model.Organization.__name__,
        organization_set_member=model.OrganizationSetMember.__name__,
    )

    ASSOCIATION_CLASS: ClassVar = model.OrganizationSetMember
    LINK_FIELD_NAME1: ClassVar = "organization_set_id"
    LINK_FIELD_NAME2: ClassVar = "organization_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.OrganizationSetMember]


class DataCollectionSetDataCollectionUpdateAssociationCommand(UpdateAssociationCommand):
    """
    Updates the association between {data_collection_set}s and {data_collection}s.

    This command manages the many-to-many relationship by creating or updating
    {data_collection_set_member} associations between data collection sets and
    individual data collections.
    """

    __doc__ = str(__doc__).format(
        data_collection_set=model.DataCollectionSet.__name__,
        data_collection=model.DataCollection.__name__,
        data_collection_set_member=model.DataCollectionSetMember.__name__,
    )

    ASSOCIATION_CLASS: ClassVar = model.DataCollectionSetMember
    LINK_FIELD_NAME1: ClassVar = "data_collection_set_id"
    LINK_FIELD_NAME2: ClassVar = "data_collection_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.DataCollectionSetMember]


class InviteUserCommand(Command):
    """
    Creates and returns a {user_invitation} for a new user with a particular
    email address, organization and initial role(s).

    A random unique token is added to the invitation, and to be provided to the
    new user for consuming the invitation.
    """

    __doc__ = str(__doc__).format(user_invitation=model.UserInvitation.__name__)

    email: str = copy_model_field(model.UserInvitation, "email")
    roles: set[Enum] = copy_model_field(model.UserInvitation, "roles")
    organization_id: UUID = copy_model_field(model.UserInvitation, "organization_id")


class RegisterInvitedUserCommand(Command):
    """
    Registers (creates) the user of the command. The email and token must match
    that of an existing {user_invitation}. The newly registered user is assigned
    the organization and roles from the invitation. The invitation is deleted.
    """

    __doc__ = str(__doc__).format(user_invitation=model.UserInvitation.__name__)

    token: str = copy_model_field(model.UserInvitation, "token")


class RetrieveOrganizationContactCommand(Command):
    """
    Retrieves {contact}s associated with organizations, sites, or specific contacts.

    Exactly one of organization_ids, site_ids, or contact_ids must be provided.
    Returns a list of contacts with their associated site and organization data
    cascaded.
    """

    __doc__ = str(__doc__).format(contact=model.Contact.__name__)

    organization_ids: list[UUID] | None = Field(
        default=None, description="List of organization IDs to retrieve contacts for"
    )
    site_ids: list[UUID] | None = Field(
        default=None, description="List of site IDs to retrieve contacts for"
    )
    contact_ids: list[UUID] | None = Field(
        default=None, description="List of contact IDs to retrieve contacts for"
    )


class UpdateUserCommand(Command):
    """
    Updates an existing {user} with new properties such as active status,
    roles, and organization membership.

    The target user is identified by tgt_user_id. Any field set to None will
    leave that property unchanged. Roles cannot be set to an empty set.
    Cache is invalidated after successful update.
    """

    __doc__ = str(__doc__).format(user=model.User.__name__)

    tgt_user_id: UUID = Field(description="The ID of the user to update")
    is_active: bool | None = copy_model_field(model.User, "is_active")
    roles: set[Enum] | None = copy_model_field(model.User, "roles")
    organization_id: UUID | None = Field(
        description="The organization ID the user belongs to"
    )


class UpdateUserOwnOrganizationCommand(Command):
    """
    Updates the current user's {organization} membership.

    This command allows a user to change their own organization association.
    The is_new_user flag indicates whether this is part of a new user
    registration process.
    """

    __doc__ = str(__doc__).format(organization=model.Organization.__name__)

    organization_id: UUID
    is_new_user: bool = False


class RetrieveInviteUserConstraintsCommand(Command):
    """
    Retrieves the constraints for inviting a user, such as valid roles and organizations.

    This command is used to gather the necessary information for the user invitation process.
    """

    pass


class RetrieveOrganizationAdminNameEmailsCommand(Command):
    """
    Retrieve the names and email addresses of all organization admins for the user's
    organization.
    """

    pass


# CRUD commands


class OrganizationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Organization


class UserCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.User


class UserInvitationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.UserInvitation


class OrganizationSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationSet


class OrganizationSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.OrganizationSetMember


class SiteCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Site


class ContactCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Contact


class IdentifierIssuerCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.IdentifierIssuer


class DataCollectionCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DataCollection


class DataCollectionSetCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DataCollectionSet


class DataCollectionSetMemberCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DataCollectionSetMember

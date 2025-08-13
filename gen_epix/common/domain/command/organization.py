from enum import Enum
from typing import ClassVar
from uuid import UUID

import gen_epix.common.domain.model.organization as model
from gen_epix.common.domain.command.base import (
    Command,
    CrudCommand,
    UpdateAssociationCommand,
)
from gen_epix.fastapp import PermissionTypeSet

# Non-CRUD commands


class OrganizationSetOrganizationUpdateAssociationCommand(UpdateAssociationCommand):
    ASSOCIATION_CLASS: ClassVar = model.OrganizationSetMember
    LINK_FIELD_NAME1: ClassVar = "organization_set_id"
    LINK_FIELD_NAME2: ClassVar = "organization_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.OrganizationSetMember]


class DataCollectionSetDataCollectionUpdateAssociationCommand(UpdateAssociationCommand):
    ASSOCIATION_CLASS: ClassVar = model.DataCollectionSetMember
    LINK_FIELD_NAME1: ClassVar = "data_collection_set_id"
    LINK_FIELD_NAME2: ClassVar = "data_collection_id"

    obj_id1: UUID | None = None
    obj_id2: UUID | None = None
    association_objs: list[model.DataCollectionSetMember]


class InviteUserCommand(Command):

    email: str
    roles: set[Enum]
    organization_id: UUID


class RegisterInvitedUserCommand(Command):

    token: str


class RetrieveOrganizationContactCommand(Command):

    organization_ids: list[UUID] | None = None
    site_ids: list[UUID] | None = None
    contact_ids: list[UUID] | None = None


class UpdateUserCommand(Command):

    tgt_user_id: UUID
    is_active: bool | None
    roles: set[Enum] | None
    organization_id: UUID | None


class UpdateUserOwnOrganizationCommand(Command):

    organization_id: UUID
    is_new_user: bool = False


# CRUD commands


class OrganizationCrudCommand(CrudCommand):
    PERMISSION_TYPE_SET: ClassVar = PermissionTypeSet.CRU
    MODEL_CLASS: ClassVar = model.Organization


class UserCrudCommand(CrudCommand):
    PERMISSION_TYPE_SET: ClassVar = PermissionTypeSet.CRU
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

# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import ClassVar
from uuid import UUID

from gen_epix.fastapp.services import auth
from gen_epix.omopdb.domain import DOMAIN, enum
from gen_epix.omopdb.domain.command.base import Command


# auth
class GetIdentityProvidersCommand(auth.GetIdentityProvidersCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.AUTH


# organization
class RetrieveCompleteUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION


class InviteUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION
    email: str
    roles: set[enum.Role]


class RegisterInvitedUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION
    token: str


class UpdateUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION

    tgt_user_id: UUID
    is_active: bool | None
    roles: set[enum.Role] | None
    data_collection_ids: set[UUID] | None
    organization_id: UUID | None


# system
class RetrieveOutagesCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.SYSTEM
    pass


DOMAIN.register_locals(locals())

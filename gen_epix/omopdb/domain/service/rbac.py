from gen_epix.fastapp import Command, PermissionType
from gen_epix.fastapp.services.rbac import BaseRbacService as ServiceBaseRbacService
from gen_epix.omopdb.domain import command, enum


class BaseRbacService(ServiceBaseRbacService):
    SERVICE_TYPE = enum.ServiceType.RBAC

    NO_RBAC_PERMISSIONS: set[tuple[type[Command], PermissionType]] = {
        # The RegisterInvitedUserCommand is a special case since it is used to create a
        # user and hence no existing user can be included in the command. The command
        # therefore does not require a permission policy, but the permissions can be
        # checked nonetheless through the implementing handler.
        (command.RegisterInvitedUserCommand, PermissionType.E),
        (command.GetIdentityProvidersCommand, PermissionType.E),
        (command.RetrieveOutagesCommand, PermissionType.E),
    }

    def register_handlers(self) -> None:
        self.register_default_crud_handlers()

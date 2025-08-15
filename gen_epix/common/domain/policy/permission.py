from gen_epix.common.domain import command
from gen_epix.common.domain.command import Command
from gen_epix.fastapp.enum import PermissionType

# Permissions on which no RBAC is required
NO_RBAC_PERMISSIONS: set[tuple[type[Command], PermissionType]] = {
    # Used to create a user and hence no existing user can be included in the
    # command.
    (command.RegisterInvitedUserCommand, PermissionType.EXECUTE),
    # Used to retrieve identity providers so that users can be authenticated and
    # subsequently provided with other commands.
    (command.GetIdentityProvidersCommand, PermissionType.EXECUTE),
    # Used to retrieve outages, which is a public operation since authentication
    # may also be offline.
    (command.RetrieveOutagesCommand, PermissionType.EXECUTE),
    # Used to update the user's own organization, which does not require RBAC
    # as a special case for development/testing purposes only.
    (command.UpdateUserOwnOrganizationCommand, PermissionType.EXECUTE),
}

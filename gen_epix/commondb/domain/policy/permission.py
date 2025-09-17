from enum import Enum
from typing import Type

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.command import Command
from gen_epix.commondb.domain.enum import Role
from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.enum import PermissionType
from gen_epix.fastapp.services.rbac import BaseRbacService

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
    # Used to retrieve licenses, which is a public operation.
    (command.RetrieveLicensesCommand, PermissionType.EXECUTE),
}


class RoleGenerator:

    ROLE_PERMISSION_SETS: dict[
        Role, set[tuple[Type[command.Command], PermissionTypeSet]]
    ] = {
        # TODO: remove UPDATE from association objects that do not have properties of their own such as CaseTypeSetMember
        Role.APP_ADMIN: {
            # abac
            (command.OrganizationAdminPolicyCrudCommand, PermissionTypeSet.CUD),
            # organization
            (command.OrganizationCrudCommand, PermissionTypeSet.CU),
            (
                command.OrganizationSetOrganizationUpdateAssociationCommand,
                PermissionTypeSet.E,
            ),
            (command.DataCollectionCrudCommand, PermissionTypeSet.CU),
            (
                command.DataCollectionSetCrudCommand,
                PermissionTypeSet.CRUD,
            ),  # TODO: READ permission can be set broader once this entity is actually used
            (
                command.DataCollectionSetMemberCrudCommand,
                PermissionTypeSet.CRUD,
            ),  # TODO: READ permission can be set broader once this entity is actually used
            # system
            (command.OutageCrudCommand, PermissionTypeSet.CRUD),
        },
        Role.REFDATA_ADMIN: {
            # organization
            (command.UserCrudCommand, PermissionTypeSet.R),
            (command.DataCollectionCrudCommand, PermissionTypeSet.R),
        },
        Role.ORG_ADMIN: {
            # organization
            (command.InviteUserCommand, PermissionTypeSet.E),
            (command.RetrieveInviteUserConstraintsCommand, PermissionTypeSet.E),
            (command.UpdateUserCommand, PermissionTypeSet.E),
            (command.UserInvitationCrudCommand, PermissionTypeSet.CRD),
            # abac
        },
        Role.ORG_USER: {
            # organization
            (command.UserCrudCommand, PermissionTypeSet.R),
            (command.DataCollectionCrudCommand, PermissionTypeSet.R),
            (command.OrganizationCrudCommand, PermissionTypeSet.R),
            (command.RetrieveOrganizationAdminNameEmailsCommand, PermissionTypeSet.E),
            (command.RetrieveOrganizationContactCommand, PermissionTypeSet.E),
            (command.UpdateUserOwnOrganizationCommand, PermissionTypeSet.E),
            # abac
            (command.OrganizationAdminPolicyCrudCommand, PermissionTypeSet.R),
        },
        Role.GUEST: {
            # organization
            (command.RetrieveOwnPermissionsCommand, PermissionTypeSet.E),
            # rbac
            (command.RetrieveSubRolesCommand, PermissionTypeSet.E),
            # system
            (command.RetrieveOutagesCommand, PermissionTypeSet.E),
        },
    }

    # Tree hierarchy of roles: each role can do everything the roles below it can do.
    # Hierarchy described here per role with union of all roles below it.
    ROLE_HIERARCHY: dict[Role, set[Role]] = {
        Role.ROOT: {
            Role.APP_ADMIN,
            Role.ORG_ADMIN,
            Role.REFDATA_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        },
        Role.APP_ADMIN: {
            Role.ORG_ADMIN,
            Role.REFDATA_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        },
        Role.ORG_ADMIN: {
            Role.ORG_USER,
            Role.GUEST,
        },
        Role.REFDATA_ADMIN: {Role.GUEST},
        Role.ORG_USER: {Role.GUEST},
        Role.GUEST: set(),
    }

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS  # type: ignore[arg-type]
    )


def map_common_role_permission_sets(
    role_map: dict[Enum, Enum],
    command_map: dict[Type, Type],
) -> dict[Enum, set[tuple[type, PermissionTypeSet]]]:
    role_permission_sets = RoleGenerator.ROLE_PERMISSION_SETS
    mapped_role_permission_sets: dict[Enum, set[tuple[type, PermissionTypeSet]]] = {}
    for role, permission_tuples in role_permission_sets.items():
        mapped_role = role_map[role]
        mapped_role_permission_sets.setdefault(mapped_role, set())
        mapped_role_permission_sets[mapped_role].update(
            {(command_map.get(x, x), y) for (x, y) in permission_tuples}
        )
    return mapped_role_permission_sets


def map_common_role_hierarchy(
    role_map: dict[Enum, Enum],
) -> dict[Enum, set[Enum]]:
    mapped_role_hierarchy: dict[Enum, set[Enum]] = {}
    for role, sub_roles in RoleGenerator.ROLE_HIERARCHY.items():
        mapped_role = role_map[role]
        mapped_role_hierarchy.setdefault(mapped_role, set())
        mapped_role_hierarchy[mapped_role].update({role_map[x] for x in sub_roles})
    return mapped_role_hierarchy

from typing import Type

from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService
from gen_epix.omopdb.domain import command
from gen_epix.omopdb.domain.enum import Role


class RoleGenerator:

    ROLE_PERMISSION_SETS: dict[
        Role, set[tuple[Type[command.Command], PermissionTypeSet]]
    ] = {
        Role.APP_ADMIN: {
            # organization
            (command.IdentifierIssuerCrudCommand, PermissionTypeSet.CU),
            (command.UserCrudCommand, PermissionTypeSet.R),
            (command.UserInvitationCrudCommand, PermissionTypeSet.CRD),
            (command.InviteUserCommand, PermissionTypeSet.E),
            (command.UpdateUserCommand, PermissionTypeSet.E),
            (command.OutageCrudCommand, PermissionTypeSet.CRUD),
            (command.DataCollectionCrudCommand, PermissionTypeSet.CRU),
            (command.DataCollectionSetCrudCommand, PermissionTypeSet.CRUD),
            (command.DataCollectionSetMemberCrudCommand, PermissionTypeSet.CRUD),
        },
        # TODO: fill in permissions
        Role.METADATA_ADMIN: set(),
        Role.ORG_USER: set(),
        Role.GUEST: set(),
    }

    # Tree hierarchy of roles: each role can do everything the roles below it can do.
    # Hierarchy described here per role with union of all roles below it.
    ROLE_HIERARCHY: dict[Role, set[Role]] = {
        Role.ROOT: {
            Role.APP_ADMIN,
            Role.METADATA_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        },
        Role.APP_ADMIN: {
            Role.METADATA_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        },
        Role.METADATA_ADMIN: {Role.GUEST},
        Role.ORG_USER: {Role.GUEST},
        Role.GUEST: set(),
    }

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS
    )

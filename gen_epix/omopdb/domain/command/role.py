from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService
from gen_epix.omopdb.domain import command
from gen_epix.omopdb.domain.enum import Role


class RoleGenerator:

    ROLE_PERMISSIONS = {
        Role.ADMIN: {  # type: ignore
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
        Role.REFDATA_ADMIN: {},  # type: ignore
        Role.DATA_READER: {},  # type: ignore
        Role.DATA_WRITER: {},  # type: ignore
        Role.GUEST: set(),  # type: ignore
    }

    # Tree hierarchy of roles: each role can do everything the roles below it can do.
    # Hierarchy described here per role with union of all roles below it.
    ROLE_HIERARCHY = {
        Role.ROOT: {  # type: ignore
            Role.ADMIN,
            Role.REFDATA_ADMIN,
            Role.DATA_READER,
            Role.DATA_WRITER,
            Role.GUEST,
        },
        Role.ADMIN: {  # type: ignore
            Role.REFDATA_ADMIN,
            Role.DATA_READER,
            Role.DATA_WRITER,
            Role.GUEST,
        },
        Role.REFDATA_ADMIN: {Role.GUEST},  # type: ignore
        Role.DATA_READER: {Role.GUEST},  # type: ignore
        Role.DATA_WRITER: {Role.DATA_READER, Role.GUEST},  # type: ignore
        Role.GUEST: set(),  # type: ignore
    }

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSIONS
    )

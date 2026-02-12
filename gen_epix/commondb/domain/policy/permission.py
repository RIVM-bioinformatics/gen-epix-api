from enum import Enum

from gen_epix import fastapp
from gen_epix.commondb.domain import command
from gen_epix.commondb.enum import Role, RoleSet
from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.enum import PermissionType
from gen_epix.fastapp.services.rbac import BaseRbacService

# Permissions on which no RBAC is required
NO_RBAC_PERMISSIONS: set[tuple[type[fastapp.Command], PermissionType]] = {
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

    COMMON_ROLE_ENUM_MAP: dict[Role, Enum] = {x: x for x in Role}

    EXTRA_ROLE_SET_MAP: dict[Enum, set[Enum]] = {}

    ROLE_PERMISSION_SETS: dict[
        Enum, set[tuple[type[fastapp.Command], PermissionTypeSet]]
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
            (command.IdentifierIssuerCrudCommand, PermissionTypeSet.CU),
            (
                command.OrganizationIdentifierIssuerLinkCrudCommand,
                PermissionTypeSet.CUD,
            ),
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
            (command.ContactCrudCommand, PermissionTypeSet.CUD),
            (command.SiteCrudCommand, PermissionTypeSet.CUD),
            # abac
        },
        Role.ORG_USER: {
            # organization
            (command.IdentifierIssuerCrudCommand, PermissionTypeSet.R),
            (
                command.OrganizationIdentifierIssuerLinkCrudCommand,
                PermissionTypeSet.R,
            ),
            (command.UserCrudCommand, PermissionTypeSet.R),
            (command.DataCollectionCrudCommand, PermissionTypeSet.R),
            (command.OrganizationCrudCommand, PermissionTypeSet.R),
            (command.ContactCrudCommand, PermissionTypeSet.R),
            (command.SiteCrudCommand, PermissionTypeSet.R),
            (command.RetrieveOrganizationAdminNameEmailsCommand, PermissionTypeSet.E),
            (command.RetrieveOrganizationContactCommand, PermissionTypeSet.E),
            (command.UpdateUserOwnOrganizationCommand, PermissionTypeSet.E),
            (
                command.OrganizationIdentifierIssuerLinkCrudCommand,
                PermissionTypeSet.R,
            ),
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
    ROLE_HIERARCHY: dict[Enum, set[Enum]] = {
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

    @staticmethod
    def map_from_common_role_permission_sets(
        common_role_enum_map: dict[Role, Enum],
        command_map: dict[type, type],
    ) -> dict[Enum, set[tuple[type, PermissionTypeSet]]]:
        """
        Helper method to map common permissions described using the commondb
        role enum and command classes to the same permissions described using
        the domain role enum and command classes. This allows easy reuse of
        common permission definitions across different domains.
        """
        role_permission_sets = RoleGenerator.ROLE_PERMISSION_SETS
        mapped_role_permission_sets: dict[Enum, set[tuple[type, PermissionTypeSet]]] = (
            {}
        )
        for role, permission_tuples in role_permission_sets.items():
            mapped_role = common_role_enum_map[role]
            mapped_role_permission_sets.setdefault(mapped_role, set())
            mapped_role_permission_sets[mapped_role].update(
                {(command_map.get(x, x), y) for (x, y) in permission_tuples}
            )
        return mapped_role_permission_sets

    @staticmethod
    def map_from_common_role_hierarchy(
        common_role_enum_map: dict[Role, Enum],
    ) -> dict[Enum, set[Enum]]:
        """
        Helper method to map common role hierarchy described using the commondb
        role enum to the same role hierarchy described using the domain role
        enum. This allows easy reuse of common role hierarchy definitions
        across different domains.
        """
        mapped_role_hierarchy: dict[Enum, set[Enum]] = {}
        for role, sub_roles in RoleGenerator.ROLE_HIERARCHY.items():
            mapped_role = common_role_enum_map[role]
            mapped_role_hierarchy.setdefault(mapped_role, set())
            mapped_role_hierarchy[mapped_role].update(
                {common_role_enum_map[x] for x in sub_roles}
            )
        return mapped_role_hierarchy

    @classmethod
    def get_role_map(cls) -> dict[Role | Enum, str]:
        """
        Get a mapping from domain role enum to role string value, whereby the
        domain role enums are replaced with their commondb equivalent where
        applicable. This allows use of commondb role enums in commondb code
        while still providing correct role string values for the domain.
        """
        rev_role_enum_map = {y: x for x, y in cls.COMMON_ROLE_ENUM_MAP.items()}
        enum_class = list(rev_role_enum_map.keys())[0].__class__
        rev_role_enum_map.update(
            {x: x for x in enum_class if x not in rev_role_enum_map}
        )
        return {y: x.value for x, y in rev_role_enum_map.items()}

    @classmethod
    def get_role_set_map(cls) -> dict[RoleSet | Enum, frozenset[str]]:
        """
        Get a mapping from domain role set enum to role set string value,
        whereby the domain role set enums are replaced with their commondb
        equivalent where applicable. This allows use of commondb role set enums
        in commondb code while still providing correct role set string values
        for the domain.
        """
        role_set_map: dict[RoleSet | Enum, frozenset[str]] = {}
        for x in RoleSet:
            role_set_map[x] = frozenset(
                [cls.COMMON_ROLE_ENUM_MAP.get(y, y).value for y in x.value]
            )
        role_set_map.update(
            {
                x: frozenset([z.value for z in y])
                for x, y in cls.EXTRA_ROLE_SET_MAP.items()
            }
        )
        return role_set_map

    @classmethod
    def get_role_permissions_map(
        cls,
    ) -> dict[str, set[tuple[type[fastapp.Command], PermissionType]]]:
        """
        Get a mapping from domain role string value to role permissions, whereby
        the domain role enums are replaced with their commondb equivalent where
        applicable. This allows use of commondb role enums in commondb code while
        still providing correct role permissions for the domain.
        """
        role_permissions_map: dict[
            str, set[tuple[type[fastapp.Command], PermissionType]]
        ] = {}
        for role_enum, permission_tuples in cls.ROLE_PERMISSIONS.items():
            role_permissions_map[role_enum.value] = permission_tuples
        return role_permissions_map

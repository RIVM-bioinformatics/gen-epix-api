from enum import Enum

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.enum import Role, RoleSet
from gen_epix.commondb.domain.policy.permission import (
    NO_RBAC_PERMISSIONS,
    RoleGenerator,
)
from gen_epix.fastapp import PermissionType, PermissionTypeSet


class _DomainRole(Enum):
    ROOT = "DOMAIN_ROOT"
    APP_ADMIN = "DOMAIN_APP_ADMIN"
    ORG_ADMIN = "DOMAIN_ORG_ADMIN"
    REFDATA_ADMIN = "DOMAIN_REFDATA_ADMIN"
    ORG_USER = "DOMAIN_ORG_USER"
    GUEST = "DOMAIN_GUEST"
    ANALYST = "DOMAIN_ANALYST"


def test_map_from_common_role_permission_sets_maps_roles_and_commands() -> None:
    common_role_enum_map = {
        role: _DomainRole[role.name] for role in Role if role.name != "ROLE1"
    }
    command_map = {command.OrganizationCrudCommand: command.RetrieveLicensesCommand}

    mapped = RoleGenerator.map_from_common_role_permission_sets(
        common_role_enum_map, command_map
    )

    assert (
        command.RetrieveLicensesCommand,
        PermissionTypeSet.CU,
    ) in mapped[_DomainRole.APP_ADMIN]
    assert (
        command.OrganizationSetCrudCommand,
        PermissionTypeSet.CU,
    ) in mapped[_DomainRole.APP_ADMIN]
    assert (
        command.OrganizationCrudCommand,
        PermissionTypeSet.CU,
    ) not in mapped[_DomainRole.APP_ADMIN]


def test_map_from_common_role_hierarchy_maps_every_role_and_subrole() -> None:
    common_role_enum_map = {
        role: _DomainRole[role.name] for role in Role if role.name != "ROLE1"
    }

    mapped = RoleGenerator.map_from_common_role_hierarchy(common_role_enum_map)

    assert mapped == {
        _DomainRole.ROOT: {
            _DomainRole.APP_ADMIN,
            _DomainRole.ORG_ADMIN,
            _DomainRole.REFDATA_ADMIN,
            _DomainRole.ORG_USER,
            _DomainRole.GUEST,
        },
        _DomainRole.APP_ADMIN: {
            _DomainRole.ORG_ADMIN,
            _DomainRole.REFDATA_ADMIN,
            _DomainRole.ORG_USER,
            _DomainRole.GUEST,
        },
        _DomainRole.ORG_ADMIN: {_DomainRole.ORG_USER, _DomainRole.GUEST},
        _DomainRole.REFDATA_ADMIN: {_DomainRole.GUEST},
        _DomainRole.ORG_USER: {_DomainRole.GUEST},
        _DomainRole.GUEST: set(),
    }


def test_get_role_map_includes_mapped_common_and_extra_domain_roles() -> None:
    class DomainRoleGenerator(RoleGenerator):
        COMMON_ROLE_ENUM_MAP = {Role.GUEST: _DomainRole.GUEST}

    assert DomainRoleGenerator.get_role_map() == {
        Role.GUEST: "DOMAIN_GUEST",
        _DomainRole.ROOT: "DOMAIN_ROOT",
        _DomainRole.APP_ADMIN: "DOMAIN_APP_ADMIN",
        _DomainRole.ORG_ADMIN: "DOMAIN_ORG_ADMIN",
        _DomainRole.REFDATA_ADMIN: "DOMAIN_REFDATA_ADMIN",
        _DomainRole.ORG_USER: "DOMAIN_ORG_USER",
        _DomainRole.ANALYST: "DOMAIN_ANALYST",
    }


def test_get_role_set_map_maps_common_and_extra_role_sets() -> None:
    class DomainRoleSet(Enum):
        ANALYSTS = frozenset({_DomainRole.ANALYST})

    class DomainRoleGenerator(RoleGenerator):
        COMMON_ROLE_ENUM_MAP = {Role.GUEST: _DomainRole.GUEST}
        EXTRA_ROLE_SET_MAP = {
            DomainRoleSet.ANALYSTS: {_DomainRole.ANALYST},
        }

    mapped = DomainRoleGenerator.get_role_set_map()

    assert mapped[RoleSet.ALL] == frozenset(
        {
            "COMMONDB_ROOT",
            "COMMONDB_APP_ADMIN",
            "COMMONDB_ORG_ADMIN",
            "COMMONDB_REFDATA_ADMIN",
            "COMMONDB_ORG_USER",
            "DOMAIN_GUEST",
        }
    )
    assert mapped[DomainRoleSet.ANALYSTS] == frozenset({"DOMAIN_ANALYST"})


def test_get_role_permissions_map_indexes_expanded_permissions_by_role_value() -> None:
    mapped = RoleGenerator.get_role_permissions_map()

    assert set(mapped) == {role.value for role in RoleGenerator.ROLE_PERMISSIONS}
    assert (
        command.OrganizationCrudCommand,
        PermissionType.UPDATE,
    ) in mapped[Role.APP_ADMIN.value]


def test_no_rbac_permissions_include_public_and_onboarding_commands() -> None:
    assert {
        (command.RegisterInvitedUserCommand, PermissionType.EXECUTE),
        (command.GetIdentityProvidersCommand, PermissionType.EXECUTE),
        (command.RetrieveOutagesCommand, PermissionType.EXECUTE),
        (command.RetrieveLicensesCommand, PermissionType.EXECUTE),
        (command.RetrieveFeatureFlagsCommand, PermissionType.EXECUTE),
    } <= NO_RBAC_PERMISSIONS

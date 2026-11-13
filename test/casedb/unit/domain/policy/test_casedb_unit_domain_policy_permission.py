import pytest

from gen_epix.casedb.domain import command
from gen_epix.casedb.domain.enum import Role
from gen_epix.casedb.domain.policy import permission
from gen_epix.casedb.domain.policy.permission import RoleGenerator
from gen_epix.commondb.domain import command as common_command
from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.domain.enum import RoleSet as CommonRoleSet
from gen_epix.commondb.domain.policy import RoleGenerator as CommonRoleGenerator
from gen_epix.fastapp import Command, PermissionTypeSet
from gen_epix.fastapp.enum import PermissionType

HIERARCHY_ROLES = [
    Role.ROOT,
    Role.APP_ADMIN,
    Role.ORG_ADMIN,
    Role.REFDATA_ADMIN,
    Role.ORG_USER,
    Role.GUEST,
]
PERMISSION_SET_ROLES = HIERARCHY_ROLES[1:]


def _expanded(permission_sets: set[tuple[type, PermissionTypeSet]]) -> set:
    return {(c, p) for c, s in permission_sets for p in s.value}


def test_module_exposes_role_generator() -> None:
    assert permission.RoleGenerator is RoleGenerator
    assert issubclass(RoleGenerator, CommonRoleGenerator)


def test_common_role_enum_map_maps_every_common_role_by_name() -> None:
    assert set(RoleGenerator.COMMON_ROLE_ENUM_MAP) == set(CommonRole)
    for common_role, role in RoleGenerator.COMMON_ROLE_ENUM_MAP.items():
        assert role is Role[common_role.name]


def test_extra_role_set_map_is_empty() -> None:
    assert not RoleGenerator.EXTRA_ROLE_SET_MAP


def test_common_role_permission_sets_use_casedb_roles_and_commands() -> None:
    sets = RoleGenerator.COMMON_ROLE_PERMISSION_SETS

    assert set(sets) == set(PERMISSION_SET_ROLES)
    substituted = {x: y for x, y in command.COMMON_COMMAND_MAP.items() if x is not y}
    assert substituted
    for permission_set in sets.values():
        commands = {c for c, _ in permission_set}
        assert not commands & set(substituted)
    assert (command.UserCrudCommand, PermissionTypeSet.R) in sets[Role.ORG_USER]
    assert (
        command.DeleteAllRefDataCommand,
        PermissionTypeSet.E,
    ) in sets[Role.APP_ADMIN]
    assert (
        common_command.DeleteAllRefDataCommand,
        PermissionTypeSet.E,
    ) not in sets[Role.APP_ADMIN]


def test_role_permission_sets_keys_exclude_root() -> None:
    assert set(RoleGenerator.ROLE_PERMISSION_SETS) == set(PERMISSION_SET_ROLES)


@pytest.mark.parametrize("role", PERMISSION_SET_ROLES)
def test_role_permission_sets_include_common_permissions(role: Role) -> None:
    assert (
        RoleGenerator.COMMON_ROLE_PERMISSION_SETS[role]
        <= RoleGenerator.ROLE_PERMISSION_SETS[role]
    )


def test_role_permission_sets_guest_adds_nothing_to_common() -> None:
    assert (
        RoleGenerator.ROLE_PERMISSION_SETS[Role.GUEST]
        == RoleGenerator.COMMON_ROLE_PERMISSION_SETS[Role.GUEST]
    )


@pytest.mark.parametrize("role", PERMISSION_SET_ROLES)
def test_role_permission_sets_are_valid_command_permission_pairs(role: Role) -> None:
    for cmd, permission_type_set in RoleGenerator.ROLE_PERMISSION_SETS[role]:
        assert issubclass(cmd, Command)
        assert isinstance(permission_type_set, PermissionTypeSet)


def test_role_hierarchy_maps_common_hierarchy_to_casedb_roles() -> None:
    hierarchy = RoleGenerator.ROLE_HIERARCHY

    assert set(hierarchy) == set(HIERARCHY_ROLES)
    assert hierarchy[Role.ROOT] == set(PERMISSION_SET_ROLES)
    assert hierarchy[Role.ORG_ADMIN] == {Role.ORG_USER, Role.GUEST}
    assert hierarchy[Role.REFDATA_ADMIN] == {Role.GUEST}
    assert hierarchy[Role.GUEST] == set()
    for sub_roles in hierarchy.values():
        assert all(isinstance(x, Role) for x in sub_roles)


def test_role_permissions_cover_every_hierarchy_role() -> None:
    assert set(RoleGenerator.ROLE_PERMISSIONS) == set(HIERARCHY_ROLES)


def test_role_permissions_inherit_from_sub_roles() -> None:
    perms = RoleGenerator.ROLE_PERMISSIONS
    for role, sub_roles in RoleGenerator.ROLE_HIERARCHY.items():
        for sub_role in sub_roles:
            assert perms[sub_role] <= perms[role]
    assert perms[Role.GUEST] < perms[Role.ORG_USER] < perms[Role.ORG_ADMIN]
    assert perms[Role.ORG_ADMIN] < perms[Role.APP_ADMIN]
    assert perms[Role.APP_ADMIN] == perms[Role.ROOT]


def test_role_permissions_contain_expanded_own_permissions() -> None:
    for role in PERMISSION_SET_ROLES:
        own = _expanded(RoleGenerator.ROLE_PERMISSION_SETS[role])
        assert own <= RoleGenerator.ROLE_PERMISSIONS[role]


def test_role_permissions_enforce_role_boundaries() -> None:
    perms = RoleGenerator.ROLE_PERMISSIONS
    create_case = (command.CaseCrudCommand, PermissionType.CREATE)
    upload = (command.UploadCasesCommand, PermissionType.EXECUTE)
    create_col = (command.ColCrudCommand, PermissionType.CREATE)
    delete_region_shape = (command.RegionSetShapeCrudCommand, PermissionType.DELETE)

    assert create_case in perms[Role.APP_ADMIN]
    assert create_case not in perms[Role.ORG_ADMIN]
    assert create_case not in perms[Role.ORG_USER]
    assert upload in perms[Role.ORG_USER]
    assert upload not in perms[Role.GUEST]
    assert create_col in perms[Role.REFDATA_ADMIN]
    assert create_col not in perms[Role.ORG_ADMIN]
    assert delete_region_shape in perms[Role.REFDATA_ADMIN]
    assert delete_region_shape not in perms[Role.ORG_USER]


def test_role_permissions_do_not_include_unregistered_roles() -> None:
    assert Role.ROLE1 not in RoleGenerator.ROLE_PERMISSIONS


def test_get_role_map_maps_common_roles_to_casedb_values() -> None:
    role_map = RoleGenerator.get_role_map()

    for common_role in CommonRole:
        if common_role is CommonRole.ROLE1:
            continue
        assert role_map[common_role] == Role[common_role.name].value
    assert role_map[CommonRole.ROLE1] == Role.ROLE1.value


def test_get_role_set_map_translates_common_role_sets() -> None:
    role_set_map = RoleGenerator.get_role_set_map()

    assert set(role_set_map) == set(CommonRoleSet)
    assert role_set_map[CommonRoleSet.GE_APP_ADMIN] == frozenset(
        {Role.ROOT.value, Role.APP_ADMIN.value}
    )


def test_get_role_permissions_map_is_keyed_by_casedb_role_values() -> None:
    perms_map = RoleGenerator.get_role_permissions_map()

    assert set(perms_map) == {x.value for x in HIERARCHY_ROLES}
    assert perms_map[Role.GUEST.value] == RoleGenerator.ROLE_PERMISSIONS[Role.GUEST]

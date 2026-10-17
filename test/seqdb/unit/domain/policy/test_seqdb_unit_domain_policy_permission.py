"""Verify SEQDB role mappings and command permissions."""

import pytest

from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.fastapp import PermissionType
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.enum import Role
from gen_epix.seqdb.domain.policy.permission import RoleGenerator


def test_common_roles_map_to_matching_seqdb_roles() -> None:
    """Map every shared role, including extension roles, by name."""
    assert RoleGenerator.COMMON_ROLE_ENUM_MAP == {
        common_role: Role[common_role.name] for common_role in CommonRole
    }


@pytest.mark.parametrize(
    ("role", "command_type", "expected_permissions"),
    [
        pytest.param(
            Role.REFDATA_ADMIN,
            command.LocusCodeMapCrudCommand,
            {
                PermissionType.CREATE,
                PermissionType.READ,
                PermissionType.UPDATE,
                PermissionType.DELETE,
            },
            id="reference-admin-manages-locus-code-maps",
        ),
        pytest.param(
            Role.ORG_USER,
            command.FileCrudCommand,
            {
                PermissionType.CREATE,
                PermissionType.READ,
                PermissionType.DELETE,
            },
            id="organization-user-file-permissions-exclude-update",
        ),
        pytest.param(
            Role.ORG_USER,
            command.SampleCrudCommand,
            {
                PermissionType.CREATE,
                PermissionType.READ,
                PermissionType.UPDATE,
                PermissionType.DELETE,
            },
            id="organization-user-manages-samples",
        ),
    ],
)
def test_role_permissions_match_explicit_domain_grants(
    role: Role,
    command_type: type,
    expected_permissions: set[PermissionType],
) -> None:
    """Expand explicit role grants into their individual permission actions."""
    assert RoleGenerator.ROLE_PERMISSIONS[role] & {
        (command_type, permission) for permission in PermissionType
    } == {(command_type, permission) for permission in expected_permissions}


def test_hierarchy_inherits_descendant_permissions_without_sibling_leakage() -> None:
    """Inherit organization-user grants while isolating reference-data access."""
    sample_read = (command.SampleCrudCommand, PermissionType.READ)

    assert sample_read in RoleGenerator.ROLE_PERMISSIONS[Role.ORG_ADMIN]
    assert sample_read not in RoleGenerator.ROLE_PERMISSIONS[Role.REFDATA_ADMIN]
    assert Role.ORG_USER in RoleGenerator.ROLE_HIERARCHY[Role.ORG_ADMIN]

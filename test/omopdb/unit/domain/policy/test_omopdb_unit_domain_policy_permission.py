import pytest

from gen_epix.fastapp.enum import PermissionType, PermissionTypeSet
from gen_epix.omopdb.domain import command
from gen_epix.omopdb.domain.enum import Role
from gen_epix.omopdb.domain.policy.permission import RoleGenerator


@pytest.mark.parametrize(
    ("role", "command_class", "expected_permissions"),
    [
        pytest.param(
            Role.APP_ADMIN,
            command.ConceptClassCrudCommand,
            {
                PermissionType.CREATE,
                PermissionType.READ,
                PermissionType.UPDATE,
            },
            id="app-admin-concept-class",
        ),
        pytest.param(
            Role.REFDATA_ADMIN,
            command.ConceptCrudCommand,
            {
                PermissionType.CREATE,
                PermissionType.READ,
                PermissionType.UPDATE,
            },
            id="refdata-admin-concept",
        ),
        pytest.param(
            Role.ORG_USER,
            command.PersonCrudCommand,
            {
                PermissionType.CREATE,
                PermissionType.READ,
                PermissionType.UPDATE,
                PermissionType.DELETE,
            },
            id="org-user-person",
        ),
        pytest.param(
            Role.ORG_USER,
            command.RetrievePersonsByIdCommand,
            {PermissionType.EXECUTE},
            id="org-user-person-retrieval",
        ),
    ],
)
def test_local_role_permission_sets(
    role: Role,
    command_class: type,
    expected_permissions: set[PermissionType],
) -> None:
    """Keep representative OMOP-specific role grants and action sets exact."""
    actual_permissions = {
        permission_type
        for mapped_command, permission_set in RoleGenerator.ROLE_PERMISSION_SETS[role]
        if mapped_command is command_class
        for permission_type in permission_set.value
    }

    assert actual_permissions == expected_permissions


def test_common_role_permissions_are_mapped_to_omop_commands() -> None:
    """Retain shared organization read access in the OMOP role map."""
    assert (
        command.OrganizationCrudCommand,
        PermissionTypeSet.R,
    ) in RoleGenerator.ROLE_PERMISSION_SETS[Role.ORG_USER]


def test_hierarchical_roles_include_permissions_of_subroles() -> None:
    """Include every sub-role's expanded permissions in each parent role."""
    role_permissions = RoleGenerator.ROLE_PERMISSIONS

    assert role_permissions[Role.ORG_USER] <= role_permissions[Role.ORG_ADMIN]
    assert role_permissions[Role.ORG_ADMIN] <= role_permissions[Role.APP_ADMIN]
    assert role_permissions[Role.REFDATA_ADMIN] <= role_permissions[Role.APP_ADMIN]
    assert role_permissions[Role.APP_ADMIN] <= role_permissions[Role.ROOT]
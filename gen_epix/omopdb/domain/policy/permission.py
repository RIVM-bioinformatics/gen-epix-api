from typing import Type

from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.domain.policy import (
    map_common_role_hierarchy,
    map_common_role_permission_sets,
)
from gen_epix.fastapp import PermissionTypeSet
from gen_epix.fastapp.services.rbac import BaseRbacService
from gen_epix.omopdb.domain import command
from gen_epix.omopdb.domain.enum import Role

COMMON_ROLE_MAP = {
    CommonRole.ROOT: Role.ROOT,
    CommonRole.APP_ADMIN: Role.APP_ADMIN,
    CommonRole.REFDATA_ADMIN: Role.REFDATA_ADMIN,
    CommonRole.ORG_ADMIN: Role.ORG_ADMIN,
    CommonRole.ORG_USER: Role.ORG_USER,
    CommonRole.GUEST: Role.GUEST,
}


class RoleGenerator:

    COMMON_ROLE_PERMISSION_SETS = map_common_role_permission_sets(
        COMMON_ROLE_MAP, command.COMMON_COMMAND_MAP  # type: ignore[arg-type]
    )

    ROLE_PERMISSION_SETS: dict[
        Role, set[tuple[Type[command.Command], PermissionTypeSet]]
    ] = {
        # TODO: fill in permissions
        Role.APP_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.APP_ADMIN] | set(),
        Role.REFDATA_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.REFDATA_ADMIN] | set(),
        Role.ORG_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.ORG_ADMIN] | set(),
        Role.ORG_USER: COMMON_ROLE_PERMISSION_SETS[Role.ORG_USER] | set(),
        Role.GUEST: COMMON_ROLE_PERMISSION_SETS[Role.GUEST] | set(),
    }

    ROLE_HIERARCHY: dict[Role, set[Role]] = map_common_role_hierarchy(COMMON_ROLE_MAP)  # type: ignore[assignment,arg-type]

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS  # type: ignore[arg-type]
    )

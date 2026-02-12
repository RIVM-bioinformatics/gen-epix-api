from gen_epix.commondb.enum import Role as CommonRole
from gen_epix.commondb.domain.policy import RoleGenerator as CommonRoleGenerator
from gen_epix.fastapp.services.rbac import BaseRbacService
from gen_epix.omopdb.domain import command
from gen_epix.omopdb.domain.enum import Role


class RoleGenerator(CommonRoleGenerator):

    COMMON_ROLE_ENUM_MAP = {x: Role[x.name] for x in CommonRole}

    EXTRA_ROLE_SET_MAP = {}

    COMMON_ROLE_PERMISSION_SETS = (
        CommonRoleGenerator.map_from_common_role_permission_sets(
            COMMON_ROLE_ENUM_MAP, command.COMMON_COMMAND_MAP
        )
    )

    ROLE_PERMISSION_SETS = {
        # TODO: fill in permissions
        Role.APP_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.APP_ADMIN] | set(),
        Role.REFDATA_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.REFDATA_ADMIN] | set(),
        Role.ORG_ADMIN: COMMON_ROLE_PERMISSION_SETS[Role.ORG_ADMIN] | set(),
        Role.ORG_USER: COMMON_ROLE_PERMISSION_SETS[Role.ORG_USER] | set(),
        Role.GUEST: COMMON_ROLE_PERMISSION_SETS[Role.GUEST] | set(),
    }

    ROLE_HIERARCHY = CommonRoleGenerator.map_from_common_role_hierarchy(
        COMMON_ROLE_ENUM_MAP
    )

    ROLE_PERMISSIONS = BaseRbacService.expand_hierarchical_role_permissions(
        ROLE_HIERARCHY, ROLE_PERMISSION_SETS
    )

from typing import Callable, Hashable

from gen_epix.fastapp.domain import Domain
from gen_epix.fastapp.model import Command, Permission, Policy, User


class RbacPolicy(Policy):
    """
    Policy that checks if the user has the required permission to
    execute a command through the role(s) they have been assigned.
    """

    _CRUD_PERMISSION_TYPE_MAP = Domain.CRUD_PERMISSION_TYPE_MAP

    def __init__(
        self,
        get_permission_for_command: Callable[[Command], Permission],
        get_permission_has_rbac: Callable[[Permission], bool],
        get_roles_by_permission: Callable[[Permission], set[Hashable]],
        retrieve_user_roles: Callable[[User], set[Hashable]],
        retrieve_user_is_non_rbac_authorized: Callable[[Command], bool] | None = None,
        retrieve_user_is_root: Callable[[User], bool] | None = None,
    ):
        self._get_permission_for_command = get_permission_for_command
        self._get_permission_has_rbac = get_permission_has_rbac
        self._get_roles_by_permission = get_roles_by_permission
        self._retrieve_user_roles = retrieve_user_roles
        self._retrieve_user_is_non_rbac_authorized = (
            retrieve_user_is_non_rbac_authorized
        )
        self._retrieve_user_is_root = retrieve_user_is_root

    def is_allowed(self, cmd: Command) -> bool:
        user = cmd.user
        permission = self._get_permission_for_command(cmd)

        # Special cases
        if not self._get_permission_has_rbac(permission):
            # Permission is not subject to RBAC, this should normally only occur for
            # commands that have only some of their permissions subject to RBAC.
            return True
        if user is None:
            # No user provided and permission is required
            return False

        # Check if user has the required RBAC permission by determining if they have
        # any of the roles that have the permission
        user_roles = self._retrieve_user_roles(user)
        permission_roles = self._get_roles_by_permission(permission)
        has_permission = len(user_roles.intersection(permission_roles)) > 0
        if not has_permission:
            if self._retrieve_user_is_root:
                # Root users, if the concept is implemented, are always allowed
                return self._retrieve_user_is_root(user)
            return False

        # Check if user has other required permissions
        if self._retrieve_user_is_non_rbac_authorized:
            has_permission = self._retrieve_user_is_non_rbac_authorized(cmd)
            if has_permission:
                return True
            # Check if user is root user
            if self._retrieve_user_is_root:
                # Root users are always allowed
                return self._retrieve_user_is_root(user)
        return True

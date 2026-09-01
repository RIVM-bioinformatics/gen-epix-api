"""Implement commondb role-based access-control services and policy registration."""

from __future__ import annotations

from collections.abc import Hashable
from enum import Enum
from typing import Any

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.domain.policy.permission import NO_RBAC_PERMISSIONS
from gen_epix.commondb.domain.service import BaseRbacService
from gen_epix.fastapp import Command, Permission
from gen_epix.fastapp.app import App


class RbacService(BaseRbacService):
    """Resolve commondb roles and permissions for command authorization."""

    def __init__(self, app: App, **kwargs: Any) -> None:
        """Initialize configured role mappings and permissions exempt from RBAC.

        Args:
            app: Application that owns this service.
            **kwargs: Additional base-service configuration.
        """
        super().__init__(app, **kwargs)
        app_impl: AppImplDetails = app.impl
        self.role_map: dict[enum.Role | Enum, str] = app_impl.role_map
        self.role_set_map: dict[enum.RoleSet | Enum, frozenset[str]] = (
            app_impl.role_set_map
        )
        self.root_role = self.role_map[enum.Role.ROOT]
        self.guest_role = self.role_map[enum.Role.GUEST]

        # Register permissions without RBAC
        for command_class, permission_type in NO_RBAC_PERMISSIONS:
            permission = self.app.domain.get_permission(command_class, permission_type)
            self.register_permission_without_rbac(permission)

    def register_policies(self) -> None:
        """Register FastApp's RBAC policies for commondb commands."""
        self.register_rbac_policies()

    def retrieve_user_roles(self, user: model.User) -> set[Hashable]:  # type: ignore[override]
        """Retrieve the roles assigned directly to a commondb user.

        Args:
            user: User whose assigned roles are requested.

        Returns:
            Assigned role values.
        """
        return user.roles  # type: ignore[return-value]

    def retrieve_user_is_non_rbac_authorized(self, cmd: Command) -> bool:
        """Check authorization requirements that apply in addition to RBAC.

        The user must be active unless they have the root role.

        Args:
            cmd: Command whose authenticated user is evaluated.

        Returns:
            True for an active user or root user; otherwise False.

        The additional check permits a root user to operate regardless of active state.
        A root user is always authorized, any other user must have is_active=True.
        """
        user: model.User | None = cmd.user  # type: ignore[assignment]
        if user is None:
            return False
        return user.is_active or self.root_role in user.roles

    def retrieve_user_is_root(self, user: model.User) -> bool:  # type: ignore[override]
        """Determine whether a user has the configured root role.

        Args:
            user: User whose assigned roles are evaluated.

        Returns:
            True when the user has the root role; otherwise False.
        """
        return self.root_role in user.roles

    def retrieve_own_permissions(
        self, cmd: command.RetrieveOwnPermissionsCommand
    ) -> set[Permission]:
        """Retrieve effective permissions for the command's authenticated user.

        Args:
            cmd: Command carrying the user whose permissions are requested.

        Returns:
            Effective permissions, or an empty set for an unauthenticated user.
        """
        user: model.User | None = cmd.user
        if not user or not user.id:
            return set()
        return self.retrieve_user_permissions(user)

    def retrieve_sub_roles(self, cmd: command.RetrieveSubRolesCommand) -> set[str]:
        """Retrieve all roles inherited by the command's authenticated user.

        Args:
            cmd: Command carrying the user whose inherited roles are requested.

        Returns:
            Inherited roles, including root for a root user, or an empty set.
        """
        user: model.User | None = cmd.user
        if not user or not user.id or not user.roles:
            return set()
        sub_roles: set[str] = set.union(*[self.get_sub_roles(x) for x in user.roles])  # type: ignore[arg-type]
        # Special case: ROOT is included as its own sub-role
        if self.root_role in user.roles:
            sub_roles.add(self.root_role)
        return sub_roles

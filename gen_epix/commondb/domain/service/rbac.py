"""Define the commondb role-based access-control service contract."""

import abc
from enum import Enum
from typing import Any

from gen_epix.commondb.domain import command, enum
from gen_epix.fastapp.app import App
from gen_epix.fastapp.model import Permission
from gen_epix.fastapp.services.rbac import BaseRbacService as ServiceBaseRbacService


class BaseRbacService(ServiceBaseRbacService):
    """Provide role maps and command handlers for commondb RBAC operations."""

    SERVICE_TYPE = enum.ServiceType.RBAC

    def __init__(self, app: App, **kwargs: Any) -> None:
        """Initialize role maps and configured root and guest role values.

        Args:
            app: Application that owns this service.
            **kwargs: Service-specific configuration properties.
        """
        super().__init__(app, **kwargs)
        self.role_map: dict[enum.Role | Enum, str]
        self.role_set_map: dict[enum.RoleSet | Enum, frozenset[str]]
        self.root_role: str
        self.guest_role: str

    def register_handlers(self) -> None:
        """Register handlers that retrieve permissions and inherited sub-roles."""
        self.register_default_crud_handlers()
        f = self.app.register_handler
        f(
            command.RetrieveOwnPermissionsCommand,
            self.retrieve_own_permissions,
        )
        f(
            command.RetrieveSubRolesCommand,
            self.retrieve_sub_roles,
        )

    @abc.abstractmethod
    def retrieve_own_permissions(
        self, cmd: command.RetrieveOwnPermissionsCommand
    ) -> set[Permission]:
        """Retrieve effective permissions for the command's current user.

        Args:
            cmd: Command whose user's permissions are requested.

        Returns:
            Effective permissions for the current user.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_sub_roles(self, cmd: command.RetrieveSubRolesCommand) -> set[str]:
        """Retrieve roles inherited below the command's current user roles.

        Args:
            cmd: Command whose user's inherited roles are requested.

        Returns:
            Roles subordinate to the current user's roles.

        Raises:
            NotImplementedError: Always; concrete services implement retrieval.
        """
        raise NotImplementedError()

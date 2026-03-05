import abc
from enum import Enum
from typing import Any

from gen_epix.commondb.domain import command, enum
from gen_epix.fastapp.app import App
from gen_epix.fastapp.model import Permission
from gen_epix.fastapp.services.rbac import \
    BaseRbacService as ServiceBaseRbacService


class BaseRbacService(ServiceBaseRbacService):
    SERVICE_TYPE = enum.ServiceType.RBAC

    def __init__(self, app: App, **kwargs: Any) -> None:
        super().__init__(app, **kwargs)
        self.role_map: dict[enum.Role | Enum, str]
        self.role_set_map: dict[enum.RoleSet | Enum, frozenset[str]]
        self.root_role: str
        self.guest_role: str

    def register_handlers(self) -> None:
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
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_sub_roles(self, cmd: command.RetrieveSubRolesCommand) -> set[str]:
        raise NotImplementedError

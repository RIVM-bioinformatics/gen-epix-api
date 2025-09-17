import abc
from enum import Enum

from gen_epix.commondb.domain import command, enum
from gen_epix.fastapp.model import Permission
from gen_epix.fastapp.services.rbac import BaseRbacService as ServiceBaseRbacService


class BaseRbacService(ServiceBaseRbacService):
    SERVICE_TYPE = enum.ServiceType.RBAC

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
    def retrieve_sub_roles(self, cmd: command.RetrieveSubRolesCommand) -> set[Enum]:
        raise NotImplementedError

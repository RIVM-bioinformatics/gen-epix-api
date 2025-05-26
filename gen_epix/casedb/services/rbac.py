from __future__ import annotations

import logging
import uuid
from typing import Callable, Hashable
from uuid import UUID

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.service import BaseRbacService
from gen_epix.fastapp import App, Command, Permission


class RbacService(BaseRbacService):

    def __init__(
        self,
        app: App,
        logger: logging.Logger | None = None,
        **kwargs: dict,
    ):
        kwargs["id_factory"] = kwargs.get("id_factory", uuid.uuid4)  # type: ignore[arg-type]
        kwargs["service_type"] = kwargs.get(
            "service_type", BaseRbacService.SERVICE_TYPE  # type: ignore[arg-type]
        )
        super().__init__(app, logger=logger, **kwargs)  # type: ignore[arg-type]
        self._id_factory: Callable[[], UUID]
        # Register permissions without RBAC
        for (
            command_class,
            permission_type,
        ) in BaseRbacService.NO_RBAC_PERMISSIONS:
            permission = self.app.domain.get_permission(command_class, permission_type)
            self.register_permission_without_rbac(permission)

    def register_handlers(self) -> None:
        f = self.app.register_handler
        for command_class in self.app.domain.get_crud_commands_for_service_type(
            self.service_type
        ):
            f(command_class, self.crud)
        f(command.GetOwnPermissionsCommand, self.retrieve_user_permissions)

    def register_policies(self) -> None:
        self.register_rbac_policies()

    def retrieve_user_roles(self, user: model.User) -> set[Hashable]:  # type: ignore[override]
        return user.roles  # type: ignore[return-value]

    def retrieve_user_is_non_rbac_authorized(self, cmd: Command) -> bool:
        """
        Check if the user is authorized to perform the command in addition to RBAC.
        A root user is always authorized, any other user must have is_active=True.
        """
        user: model.User | None = cmd.user  # type: ignore[assignment]
        if user is None:
            return False
        return user.is_active or enum.Role.ROOT in user.roles

    def retrieve_user_is_root(self, user: model.User) -> bool:  # type: ignore[override]
        return enum.Role.ROOT in user.roles

    def get_own_permissions(
        self, cmd: command.GetOwnPermissionsCommand
    ) -> set[Permission]:
        user: model.User | None = cmd.user
        if not user or not user.id:
            return set()
        return self.retrieve_user_permissions(user)  # type: ignore[arg-type]

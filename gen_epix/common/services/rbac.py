from __future__ import annotations

import logging
import uuid
from enum import Enum
from typing import Any, Callable, Hashable, Type
from uuid import UUID

from gen_epix.common.domain import command, model
from gen_epix.common.domain.policy import NO_RBAC_PERMISSIONS
from gen_epix.common.domain.service import BaseRbacService
from gen_epix.fastapp import App, Command, Permission


class RbacService(BaseRbacService):

    def __init__(
        self,
        app: App,
        logger: logging.Logger | None = None,
        role_enum: Type[Enum] = Enum,
        **kwargs: Any,
    ):
        kwargs["id_factory"] = kwargs.get("id_factory", uuid.uuid4)
        super().__init__(app, logger=logger, **kwargs)  # type: ignore[arg-type]
        self._role_enum = role_enum
        self._root_role = role_enum["ROOT"]
        self._id_factory: Callable[[], UUID]
        # Register permissions without RBAC
        for (
            command_class,
            permission_type,
        ) in NO_RBAC_PERMISSIONS:
            permission = self.app.domain.get_permission(command_class, permission_type)
            self.register_permission_without_rbac(permission)

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(command.RetrieveOwnPermissionsCommand, self.retrieve_own_permissions)

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
        return user.is_active or self._root_role in user.roles

    def retrieve_user_is_root(self, user: model.User) -> bool:  # type: ignore[override]
        return self._root_role in user.roles

    def retrieve_own_permissions(
        self, cmd: command.RetrieveOwnPermissionsCommand
    ) -> set[Permission]:
        user: model.User | None = cmd.user
        if not user or not user.id:
            return set()
        return self.retrieve_user_permissions(user)

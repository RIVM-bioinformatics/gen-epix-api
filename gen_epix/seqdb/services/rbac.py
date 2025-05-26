from __future__ import annotations

import logging
import uuid
from typing import Callable, Hashable
from uuid import UUID

from gen_epix.fastapp import App, Command
from gen_epix.seqdb.domain import enum, model
from gen_epix.seqdb.domain.service import BaseRbacService


class RbacService(BaseRbacService):

    def __init__(
        self,
        app: App,
        logger: logging.Logger | None = None,
        **kwargs: dict,
    ):
        kwargs["id_factory"] = kwargs.get("id_factory", uuid.uuid4)
        kwargs["service_type"] = kwargs.get(
            "service_type", BaseRbacService.SERVICE_TYPE
        )
        super().__init__(app, logger=logger, **kwargs)
        self._id_factory: Callable[[], UUID]
        # Register permissions without RBAC
        for (
            command_class,
            permission_type,
        ) in BaseRbacService.NO_RBAC_PERMISSIONS:
            permission = self.app.domain.get_permission(command_class, permission_type)
            self.register_permission_without_rbac(permission)

    def register_policies(self) -> None:
        self.register_rbac_policies()

    def retrieve_user_roles(self, user: model.User) -> set[Hashable]:
        return user.roles

    def retrieve_user_is_non_rbac_authorized(self, cmd: Command) -> bool:
        """
        Check if the user is authorized to perform the command in addition to RBAC.
        A root user is always authorized, any other user must have is_active=True.
        """
        if cmd.user is None:
            return False
        return cmd.user.is_active or enum.Role.ROOT in cmd.user.roles

    def retrieve_user_is_root(self, user: model.User) -> bool:
        return enum.Role.ROOT in user.roles

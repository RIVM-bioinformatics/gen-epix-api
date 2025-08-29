from enum import Enum
from typing import Any, Callable, Type
from uuid import UUID

from gen_epix.common.domain import command, model
from gen_epix.common.domain.policy import BaseIsOrganizationAdminPolicy
from gen_epix.common.domain.service import BaseAbacService
from gen_epix.fastapp import CrudOperation, CrudOperationSet, exc


class IsOrganizationAdminPolicy(BaseIsOrganizationAdminPolicy):

    def __init__(
        self,
        abac_service: BaseAbacService,
        user_class: Type[model.User] = model.User,
        no_abac_org_admin_roles: set[Enum] | None = None,
        **kwargs: Any,
    ):
        super().__init__(
            abac_service,
            user_class=user_class,
            no_abac_org_admin_roles=no_abac_org_admin_roles,
            **kwargs,
        )
        self._get_organization_ids_handler_map: dict[
            Type[command.Command],
            Callable[[command.Command], set[UUID]],
        ] = {}
        f = self.register_retrieve_organization_ids_handler
        f(command.SiteCrudCommand, self._get_organization_ids_for_site)
        f(command.ContactCrudCommand, self._get_organization_ids_for_contact)

    def is_allowed(self, cmd: command.Command) -> bool:  # type: ignore[arg-type]
        if cmd.user is None:
            return False
        user: model.User = cmd.user  # type: ignore[assignment]

        # Role is org admin without further ABAC restrictions
        if user.roles.intersection(self.no_abac_org_admin_roles):
            return True

        # Policy only applies to write operations for crud commands
        if (
            isinstance(cmd, command.CrudCommand)
            and cmd.operation not in CrudOperationSet.WRITE.value
        ):
            return True

        organization_ids = self.retrieve_organization_ids(cmd)
        # Check if user is an admin for all of the affected organizations
        user_admin_organization_ids = self.abac_service.get_organizations_under_admin(
            user
        )
        has_permission = organization_ids.issubset(user_admin_organization_ids)
        return has_permission

    def register_retrieve_organization_ids_handler(
        self,
        cmd_class: Type[command.Command],
        handler: Callable[[command.Command], set[UUID]],
    ) -> None:
        self._get_organization_ids_handler_map[cmd_class] = handler

    def retrieve_organization_ids(self, cmd: command.Command) -> set[UUID]:
        cmd_class = type(cmd)
        handler = self._get_organization_ids_handler_map.get(cmd_class)
        if handler is None:
            # Check if handler registered for parent class
            for (
                handler_cmd_class,
                handler,
            ) in self._get_organization_ids_handler_map.items():
                if issubclass(cmd_class, handler_cmd_class):
                    # Parent class handler found -> register it for the child class as well for next time
                    self._get_organization_ids_handler_map[cmd_class] = handler
                    return handler(cmd)
            raise exc.InitializationServiceError(
                f"No handler registered for command: {cmd_class}"
            )
        return handler(cmd)

    def _get_organization_ids_for_site(self, cmd: command.SiteCrudCommand) -> set[UUID]:
        sites: list[model.Site] = cmd.get_objs()  # type: ignore[assignment]
        return {x.organization_id for x in sites}

    def _get_organization_ids_for_contact(
        self, cmd: command.ContactCrudCommand
    ) -> set[UUID]:
        contacts: list[model.Contact] = cmd.get_objs()  # type: ignore[assignment]
        sites: list[model.Site] = self.abac_service.app.handle(
            command.ContactCrudCommand(
                user=cmd.user,
                objs=None,
                obj_ids=list(set(x.site_id for x in contacts if x.site_id)),
                operation=CrudOperation.READ_SOME,
            )
        )
        return {x.organization_id for x in sites}

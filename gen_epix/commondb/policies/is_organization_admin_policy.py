"""Authorize organization administrators to manage scoped commondb resources."""

from collections.abc import Callable
from typing import Any
from uuid import UUID

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.domain.policy import BaseIsOrganizationAdminPolicy
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.fastapp import CrudOperation, exc


class IsOrganizationAdminPolicy(BaseIsOrganizationAdminPolicy):
    """Encapsulates organization-administrator ABAC checks before command execution."""

    def __init__(self, abac_service: BaseAbacService, **kwargs: Any):
        """Initialize role mappings and organization-ID resolvers.

        Args:
            abac_service: Service that resolves organization administration rights.
            **kwargs: Additional base-policy configuration.
        """
        super().__init__(abac_service, **kwargs)

        app_impl: AppImplDetails = abac_service.app.impl
        self.user_class: type[model.User] = app_impl.get_mapped_class(model.User)
        self.role_map = app_impl.role_map
        self.role_set_map = app_impl.role_set_map

        self._get_organization_ids_handler_map: dict[
            type[command.Command],
            Callable[[command.Command], set[UUID]],
        ] = {}
        f = self.register_retrieve_organization_ids_handler
        f(command.SiteCrudCommand, self._get_organization_ids_for_site)
        f(command.ContactCrudCommand, self._get_organization_ids_for_contact)

    def is_allowed(self, cmd: command.Command) -> bool:  # type: ignore[override]
        """Determine whether a user may manage every organization affected by a command.

        Application administrators bypass organization-specific checks. CRUD read
        operations are also allowed because this policy only restricts writes.

        Args:
            cmd: Command evaluated during the policy's BEFORE lifecycle phase.

        Returns:
            True when the command is allowed for the current user's roles and scope.

        Raises:
            InitializationServiceError: If no organization-ID resolver is registered
                for the command type.
        """
        if cmd.user is None:
            return False
        user: model.User = cmd.user

        # Role is org admin without further ABAC restrictions
        if user.roles.intersection(self.role_set_map[enum.RoleSet.GE_ORG_ADMIN]):
            return True

        # Policy only applies to write operations for crud commands
        if isinstance(cmd, command.CrudCommand) and not cmd.is_write():
            return True

        organization_ids = self.retrieve_organization_ids(cmd)
        # Check if user is an admin for all of the affected organizations
        user_admin_organization_ids = (
            self.abac_service.retrieve_organizations_under_admin(
                command.RetrieveOrganizationsUnderAdminCommand(user=user)
            )
        )
        has_permission = organization_ids.issubset(user_admin_organization_ids)
        return has_permission

    def register_retrieve_organization_ids_handler(
        self,
        command_class: type[command.Command],
        handler: Callable[[command.Command], set[UUID]],
    ) -> None:
        """Register a resolver for organizations affected by a command type.

        Args:
            command_class: Command class for which to resolve organization IDs.
            handler: Function that extracts the affected organization IDs.
        """
        self._get_organization_ids_handler_map[command_class] = handler

    def retrieve_organization_ids(self, cmd: command.Command) -> set[UUID]:
        """Resolve organizations affected by a command, caching inherited resolvers.

        Args:
            cmd: Command whose organization scope is required.

        Returns:
            IDs of organizations affected by the command.

        Raises:
            InitializationServiceError: If neither the command type nor a parent type
                has a registered organization-ID resolver.
        """
        command_class = type(cmd)
        handler = self._get_organization_ids_handler_map.get(command_class)
        if handler is None:
            # Check if handler registered for parent class
            for (
                handler_command_class,
                handler,
            ) in self._get_organization_ids_handler_map.items():
                if issubclass(command_class, handler_command_class):
                    # Parent class handler found -> register it for the child class as well for next time
                    self._get_organization_ids_handler_map[command_class] = handler
                    return handler(cmd)
            raise exc.InitializationServiceError(
                "0f786c67", f"No handler registered for command: {command_class}"
            )
        return handler(cmd)

    def _get_organization_ids_for_site(self, cmd: command.SiteCrudCommand) -> set[UUID]:
        """Extract affected organization IDs from site CRUD command objects."""
        sites: list[model.Site] = cmd.get_objs()  # type: ignore[assignment]
        return {x.organization_id for x in sites}

    def _get_organization_ids_for_contact(
        self, cmd: command.ContactCrudCommand
    ) -> set[UUID]:
        """Retrieve organizations affected by site-linked contact command objects."""
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

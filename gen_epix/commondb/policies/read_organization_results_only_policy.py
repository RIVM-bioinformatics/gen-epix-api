"""Filter commondb read results to organizations visible to the current user."""

from typing import Any
from uuid import UUID

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.domain.policy import BaseReadOrganizationResultsOnlyPolicy
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.fastapp import CrudOperation, exc


class ReadOrganizationResultsOnlyPolicy(BaseReadOrganizationResultsOnlyPolicy):
    """Encapsulates AFTER-phase organization-scope filtering to supported read commands."""

    def __init__(self, abac_service: BaseAbacService, **kwargs: Any):
        """Initialize role mappings and the command types supported by each filter.

        Args:
            abac_service: Service that resolves organization administration rights.
            **kwargs: Additional base-policy configuration.
        """
        super().__init__(abac_service, **kwargs)

        app_impl: AppImplDetails = abac_service.app.impl
        self.user_crud_command_class: type[command.UserCrudCommand] = (
            app_impl.get_mapped_class(command.UserCrudCommand)
        )
        self.role_map = app_impl.role_map
        self.role_set_map = app_impl.role_set_map

        self.has_organization_id_attr_command_classes: set[type[command.Command]] = {
            command.UserCrudCommand,
            command.OrganizationAdminPolicyCrudCommand,
            command.UserInvitationCrudCommand,
            command.OrganizationIdentifierIssuerLinkCrudCommand,
            command.OrganizationSetOrganizationUpdateAssociationCommand,
            command.OrganizationIdentifierIssuerUpdateAssociationCommand,
        }
        self.has_user_id_attr_command_classes: set[type[command.Command]] = set()

    def filter(self, cmd: command.Command, retval: Any) -> Any:  # type: ignore[override]
        """Filter or reject read results outside the user's visible organizations.

        Args:
            cmd: Completed command evaluated during the AFTER lifecycle phase.
            retval: Result produced by the command handler.

        Returns:
            The filtered result, or the original result when the policy is inapplicable.

        Raises:
            ServiceException: If the command has no authenticated user.
            UnauthorizedAuthError: If a targeted result is outside the allowed scope.
            NotImplementedError: If the command or result shape is unsupported.
        """
        if not cmd.user or not cmd.user.id:
            raise exc.ServiceException("d3d0bec8", "Command has no user")
        # TODO: replace filter for AFTER with injecting a filter DURING for efficiency
        if isinstance(cmd, command.RetrieveInviteUserConstraintsCommand):
            # Already handled DURING
            return retval
        if not isinstance(cmd, command.CrudCommand):
            raise NotImplementedError
        if not cmd.is_read():
            # Policy only applies to read or exists operations
            return retval

        # Roles exempt from this policy
        is_exempt = (
            len(
                cmd.user.roles.intersection(
                    self.role_set_map[enum.RoleSet.GE_APP_ADMIN]
                )
            )
            > 0
        )
        if is_exempt:
            return retval

        # Get organizations to filter on: user's own organization plus any
        # organizations they are admin for
        organization_ids = self.abac_service.retrieve_organizations_under_admin(
            command.RetrieveOrganizationsUnderAdminCommand(user=cmd.user)
        )
        if organization_ids:
            organization_ids.add(cmd.user.organization_id)
        else:
            organization_ids = {cmd.user.organization_id}
        # Filter results based on organizations
        msg1 = "User is not an admin for the organization and/or does not belong to it"
        msg2 = "User is not an admin for some of the organizations and/or does not belong to them"
        for command_class in self.has_organization_id_attr_command_classes:
            if isinstance(cmd, command_class):
                return self._filter_on_organization_id(
                    retval, cmd.operation, organization_ids, msg1, msg2
                )
        for command_class in self.has_user_id_attr_command_classes:
            if isinstance(cmd, command_class):
                return self._filter_on_user_id(
                    retval, cmd, cmd.operation, organization_ids, msg1, msg2
                )
        raise NotImplementedError(
            "ReadOrganizationResultsOnlyPolicy cannot filter this command type"
        )

    def _filter_on_organization_id(
        self,
        retval: Any,
        operation: CrudOperation,
        organization_ids: set[UUID],
        msg1: str,
        msg2: str,
    ) -> Any:
        """Filter or reject results according to their direct organization IDs.

        Args:
            retval: Command result to filter or validate.
            operation: CRUD operation being performed (READ_ALL, READ_ONE, etc.).
            organization_ids: Organizations visible to the requesting user.
            msg1: Error message for an unauthorized single result.
            msg2: Error message for unauthorized multiple results.

        Returns:
            Permitted result or filtered result list.

        Raises:
            UnauthorizedAuthError: If a requested result is outside the visible scope.
        """
        if operation == CrudOperation.READ_ALL:
            # Filter results
            return [x for x in retval if x.organization_id in organization_ids]
        if operation == CrudOperation.READ_SOME:
            if any(x.organization_id not in organization_ids for x in retval):
                raise exc.UnauthorizedAuthError("12ee166c", msg2)
        elif operation == CrudOperation.READ_ONE:
            if retval.organization_id not in organization_ids:
                raise exc.UnauthorizedAuthError("73bcbbeb", msg1)
        return retval

    def _filter_on_user_id(
        self,
        retval: Any,
        cmd: command.Command,
        operation: CrudOperation,
        organization_ids: set[UUID],
        msg1: str,
        msg2: str,
    ) -> Any:
        """Filter or reject results associated with users in visible organizations.

        Args:
            cmd: Command whose referenced users are resolved.
            retval: Command result to filter or validate.
            organization_ids: Organizations visible to the requesting user.
            is_read_all: Whether the command retrieves all results.
            is_read_one: Whether the command retrieves one result.
            msg1: Error message for an unauthorized single result.
            msg2: Error message for unauthorized multiple results.

        Returns:
            Filtered all-results list when applicable.

        Raises:
            UnauthorizedAuthError: If a requested result is outside the visible scope.
            NotImplementedError: For a supported non-read result shape.
        """
        users = self._get_users(cmd, operation == CrudOperation.READ_ALL)
        valid_user_ids = {x.id for x in users if x.organization_id in organization_ids}
        if operation == CrudOperation.READ_ALL:
            return [x for x in retval if x.user_id in valid_user_ids]
        if operation == CrudOperation.READ_SOME:
            if any(x.user_id not in valid_user_ids for x in retval):
                raise exc.UnauthorizedAuthError("f84db495", msg2)
        elif operation == CrudOperation.READ_ONE:
            if retval.user_id not in valid_user_ids:
                raise exc.UnauthorizedAuthError("35d7e912", msg1)
        return retval

    def _get_users(self, cmd: command.Command, is_read_all: bool) -> list[model.User]:
        """Retrieve users needed to constrain organization-scoped command results.

        Args:
            cmd: Command whose result users need to be resolved.
            is_read_all: Whether the command requests all users.

        Returns:
            Users returned by the corresponding user CRUD command.
        """
        objs: list = cmd.get_objs() if not is_read_all else []  # type: ignore[attr-defined]
        users: list[model.User] = self.abac_service.app.handle(
            self.user_crud_command_class(
                user=cmd.user,
                objs=None,
                obj_ids=(None if is_read_all else list({x.user_id for x in objs})),
                operation=(
                    CrudOperation.READ_ALL if is_read_all else CrudOperation.READ_SOME
                ),
            )
        )

        return users

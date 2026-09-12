"""Filter commondb read results to records owned by the current user."""

from typing import Any

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, enum, exc
from gen_epix.commondb.domain.policy import BaseReadSelfResultsOnlyPolicy
from gen_epix.commondb.domain.service.abac import BaseAbacService
from gen_epix.fastapp import Command, CrudOperation


class ReadSelfResultsOnlyPolicy(BaseReadSelfResultsOnlyPolicy):
    """Encapsulates AFTER-phase self-only filtering for non-administrative users."""

    def __init__(self, abac_service: BaseAbacService, **kwargs: Any):
        """Initialize role mappings and command attributes that identify ownership.

        Args:
            abac_service: Service that provides application implementation details.
            **kwargs: Additional base-policy configuration.
        """
        super().__init__(abac_service, **kwargs)

        app_impl: AppImplDetails = abac_service.app.impl
        self.role_map = app_impl.role_map
        self.role_set_map = app_impl.role_set_map

        self.id_attr_by_command_class = {
            command.UserCrudCommand: "id",
            command.UserInvitationCrudCommand: "invited_by_user_id",
        }

    def filter(self, cmd: Command, retval: Any) -> Any:
        """Filter or reject read results that are not owned by the current user.

        Organization administrators are exempt from this self-only restriction.

        Args:
            cmd: Completed command evaluated during the AFTER lifecycle phase.
            retval: Result produced by the command handler.

        Returns:
            Filtered result, or the original result when the policy is inapplicable.

        Raises:
            ServiceException: If the command has no authenticated user.
            UnauthorizedAuthError: If a targeted result is not owned by the user.
            NotImplementedError: If the command type has no ownership attribute mapping.
        """
        if not cmd.user or not cmd.user.id:
            raise exc.ServiceException("84aa512b", "Command has no user")
        # TODO: replace filter for AFTER with injecting a filter DURING for efficiency
        if not isinstance(cmd, command.CrudCommand):
            raise NotImplementedError
        if not cmd.is_read():
            # Policy only applies to read or exists operations
            return retval

        # Roles exempt from this policy
        is_exempt = (
            len(
                cmd.user.roles.intersection(
                    self.role_set_map[enum.RoleSet.GE_ORG_ADMIN]
                )
            )
            > 0
        )
        if is_exempt:
            return retval

        # Filter results based on own user
        is_read_all = cmd.operation == CrudOperation.READ_ALL
        is_read_one = cmd.operation == CrudOperation.READ_ONE
        msg = "No data for user"
        user_id = cmd.user.id
        id_attr: str | None = self.id_attr_by_command_class.get(type(cmd))
        if not id_attr:
            raise NotImplementedError
        if is_read_all:
            retval = [x for x in retval if getattr(x, id_attr) == user_id]
        if is_read_one and getattr(retval, id_attr) != user_id:
            raise exc.UnauthorizedAuthError("bcba2f7d", msg)
        if not is_read_one and any(getattr(x, id_attr) != user_id for x in retval):
            raise exc.UnauthorizedAuthError("49f667f6", msg)
        return retval

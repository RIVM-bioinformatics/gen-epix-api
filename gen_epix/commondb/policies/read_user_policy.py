"""Restrict commondb user reads according to ABAC organization visibility."""

from typing import Any
from uuid import UUID

from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, exc, model
from gen_epix.commondb.domain.policy import BaseReadUserPolicy
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.fastapp import Command
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_boolean import EqualsBooleanFilter
from gen_epix.filter.equals_uuid import EqualsUuidFilter


class ReadUserPolicy(BaseReadUserPolicy):
    """Apply AFTER-phase filtering to user records visible to the command user."""

    # TODO: replace by get_content implementation for more efficient application DURING execution

    def __init__(self, abac_service: BaseAbacService, **kwargs: Any):
        """Initialize organization-admin query support and configured role mappings.

        Args:
            abac_service: Service used to dispatch organization-admin policy queries.
            **kwargs: Additional base-policy configuration.
        """
        super().__init__(abac_service, **kwargs)

        app_impl: AppImplDetails = abac_service.app.impl
        self.organization_admin_policy_crud_command_class: type[
            command.OrganizationAdminPolicyCrudCommand
        ] = app_impl.get_mapped_class(command.OrganizationAdminPolicyCrudCommand)
        self.role_map = app_impl.role_map
        self.role_set_map = app_impl.role_set_map

    def filter(
        self, cmd: Command, retval: model.User | list[model.User]
    ) -> model.User | list[model.User]:
        """Filter requested users to records visible under the current user's ABAC scope.

        Args:
            cmd: Completed user CRUD command evaluated in the AFTER phase.
            retval: User or users returned by the command handler.

        Returns:
            The filtered result, or the original result when the policy is inapplicable.

        Raises:
            AssertionError: If the command has no authenticated user.
            UnauthorizedAuthError: If a targeted user is outside the visible scope.
            NotImplementedError: If the command operation or type is unsupported.
        """
        if self._check_invalid_filter_input(cmd):
            return retval
        user: model.User = cmd.user  # type: ignore[assignment]
        if self._is_no_abac_user(user):
            return retval
        organization_ids, is_org_admin, user_ids = self._get_org_and_user_ids(user)
        # Filter or check results
        result_list: list[model.User]
        if cmd.operation == CrudOperation.READ_ALL:  # type: ignore[attr-defined]
            # Open-ended results: filter
            result_list = retval  # type: ignore[assignment]
            return [
                x
                for x in result_list
                if (x.id in user_ids or x.organization_id in organization_ids)
                and (x.is_active or is_org_admin)
            ]
        if cmd.operation == CrudOperation.READ_SOME:  # type: ignore[attr-defined]
            # Specific users requested: check results
            result_list = retval  # type: ignore[assignment]
            return self._filter_read_some(
                result_list,
                organization_ids,
                retval,
                is_org_admin,
                user_ids,
            )
        if cmd.operation == CrudOperation.READ_ONE:  # type: ignore[attr-defined]
            # Specific user requested: check results
            result: model.User = retval  # type: ignore[assignment]
            return self._filter_read_one(
                result,
                organization_ids,
                is_org_admin,
                user_ids,
            )
        raise NotImplementedError("Unsupported operation: {cmd.operation.value}")

    def _is_no_abac_user(self, user: model.User) -> bool:
        """Determine whether a user is exempt from user-read ABAC filtering."""
        return (
            len(
                user.roles.intersection(
                    self.role_set_map[model.enum.RoleSet.GE_APP_ADMIN]
                )
            )
            > 0
        )

    def _check_invalid_filter_input(self, cmd: Command) -> bool:
        """Validate a user-read command and identify non-read operations.

        Args:
            cmd: Command being evaluated by the user-read policy.

        Returns:
            True when the command is not a read operation and needs no filtering.

        Raises:
            NotImplementedError: If the command is not a user CRUD command.
            AssertionError: If the command has no authenticated user ID.
        """
        early_return: bool = False
        user: model.User | None = cmd.user
        if not isinstance(cmd, command.UserCrudCommand):
            raise NotImplementedError(
                "Unsupported command type: {cmd.__class__.__name__}"
            )
        if not cmd.is_read():
            # Not applicable
            early_return = True
        if user is None or user.id is None:
            raise AssertionError("User must be authenticated")

        return early_return

    def _get_org_and_user_ids(
        self,
        user: model.User,
    ) -> tuple[set[UUID], bool, set[UUID]]:
        """Build the organizations and users visible to a requesting user.

        Args:
            user: Authenticated user whose roles define the read scope.

        Returns:
            Administered organization IDs, admin status, and visible user IDs.
        """
        organization_ids: set[UUID]
        is_org_admin = (
            len(
                user.roles.intersection(
                    self.role_set_map[model.enum.RoleSet.GE_ORG_ADMIN]
                )
            )
            > 0
        )
        if is_org_admin:
            # User is organization admin: can read all users (active or not) of all
            # organizations they are admin of, plus all organization admins of those
            org_admin_user_ids, organization_ids = self._get_admin_user_ids(user)
        else:
            # Regular user: can read only self and active organization admins of own organization
            org_admin_user_ids = self.get_admin_user_ids_own_organization(user)
            organization_ids = set()
        user_ids: set[UUID] = {user.id} | org_admin_user_ids  # type: ignore

        return organization_ids, is_org_admin, user_ids

    def _filter_read_one(
        self,
        result: model.User,
        organization_ids: set[UUID],
        is_org_admin: bool,
        user_ids: set[UUID],
    ) -> model.User | list[model.User]:
        """Allow or deny a single returned user according to the read scope.

        Args:
            result: User returned by the command.
            organization_ids: Organizations administered by the requester.
            is_org_admin: Whether the requester is an organization administrator.
            user_ids: Explicit user IDs visible to the requester.

        Returns:
            The permitted user result.

        Raises:
            UnauthorizedAuthError: If the result is outside the requester's scope.
        """
        if (
            result.organization_id not in organization_ids and result.id not in user_ids
        ) or not (result.is_active or is_org_admin):
            # User cannot read users outside their admin organizations
            raise exc.UnauthorizedAuthError(
                "9acec44a", "Cannot read users outside your admin organizations"
            )
        return result

    def _filter_read_some(
        self,
        result_list: list[model.User],
        organization_ids: set[UUID],
        results: model.User | list[model.User],
        is_org_admin: bool,
        user_ids: set[UUID],
    ) -> model.User | list[model.User]:
        """Allow or deny multiple returned users according to the read scope.

        Args:
            result_list: Returned users used for permission validation.
            organization_ids: Organizations administered by the requester.
            results: Original command result to return when permitted.
            is_org_admin: Whether the requester is an organization administrator.
            user_ids: Explicit user IDs visible to the requester.

        Returns:
            The original permitted command result.

        Raises:
            UnauthorizedAuthError: If any result is outside the requester's scope.
        """
        if not all(
            (x.organization_id in organization_ids or x.id in user_ids)
            and (x.is_active or is_org_admin)
            for x in result_list
        ):
            # User cannot read users outside their admin organizations
            raise exc.UnauthorizedAuthError(
                "5710ba8d", "Cannot read users outside your admin organizations"
            )
        return results

    def get_admin_user_ids_own_organization(self, user: model.User) -> set[UUID]:
        """Retrieve active organization administrator IDs for a user's organization.

        Args:
            user: User whose organization defines the administrator scope.

        Returns:
            IDs of active administrators for the user's organization.
        """
        org_admin_policies = self.abac_service.app.handle(
            self.organization_admin_policy_crud_command_class(
                user=user,
                operation=CrudOperation.READ_ALL,
                query_filter=CompositeFilter(
                    filters=[
                        EqualsUuidFilter(
                            key="organization_id", value=user.organization_id
                        ),
                        EqualsBooleanFilter(key="is_active", value=True),
                    ],
                    operator=LogicalOperator.AND,
                ),
            )
        )
        org_admin_user_ids = {x.user_id for x in org_admin_policies}
        return org_admin_user_ids

    def _get_admin_user_ids(
        self,
        user: model.User,
    ) -> tuple[set[UUID], set[UUID]]:
        """Retrieve active administrators and organizations administered by a user.

        Args:
            user: Organization administrator whose scope is resolved.

        Returns:
            Administrator user IDs and organization IDs under the user's administration.
        """
        org_admin_policies = self.abac_service.app.handle(
            self.organization_admin_policy_crud_command_class(
                user=user,
                operation=CrudOperation.READ_ALL,
                query_filter=EqualsBooleanFilter(key="is_active", value=True),
            )
        )
        organization_ids = {
            x.organization_id for x in org_admin_policies if x.user_id == user.id
        }
        admin_user_ids = {
            x.user_id
            for x in org_admin_policies
            if x.organization_id in organization_ids
        }
        return admin_user_ids, organization_ids

"""Provide an RBAC policy contract for role creation and updates."""

from typing import Any

from gen_epix.commondb.domain.service.rbac import BaseRbacService
from gen_epix.fastapp import Policy


class BaseIsPermissionSubsetNewRolePolicy(Policy):
    """Encapsulates prevention of creation or updates that would elevate a role's permissions.

    The policy checks whether the user has the required permissions to create or update a
    role.

    The user must have all the permissions that the new role has to avoid elevation of
    privileges.

    Does not apply to read or delete operations.
    """

    def __init__(self, rbac_service: BaseRbacService, **kwargs: Any):
        """Initialize the policy with its RBAC service and configuration properties.

        Args:
            rbac_service: Service that evaluates assigned role permissions.
            **kwargs: Policy-specific configuration properties.
        """
        self.rbac_service = rbac_service
        self.props = kwargs

"""Provide an RBAC policy contract for role creation and updates."""

from typing import Any

from gen_epix.commondb.domain.service.rbac import BaseRbacService
from gen_epix.fastapp import Policy


# TODO: LSP-3893 When a caller evaluates a role create/update command containing
# permissions the acting user does not hold, the documented contract requires
# denying privilege elevation; this class inherits Policy.is_allowed(), which
# raises NotImplementedError instead. Confirm whether this is intentionally an
# incomplete base for a concrete subclass or should implement the check here.
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

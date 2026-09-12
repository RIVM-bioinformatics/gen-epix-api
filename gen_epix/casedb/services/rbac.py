"""Configure role-based authorization for the casedb role hierarchy."""

from gen_epix.casedb.domain import enum
from gen_epix.commondb.services import RbacService as CommonRbacService


class RbacService(CommonRbacService):
    """Encapsulates casedb RBAC using the domain's role enumeration."""

    def __init__(self, app, logger=None, **kwargs):
        """Initialize inherited RBAC policy handling with casedb roles.

        Args:
            app: Application whose commands are authorized.
            logger: Optional logger used by the common RBAC service.
            **kwargs: Additional common RBAC service configuration.
        """
        super().__init__(app, logger=logger, role_enum=enum.Role, **kwargs)

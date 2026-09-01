"""Implement seqdb application service behavior for services.rbac."""

from gen_epix.commondb.services import RbacService as CommonRbacService
from gen_epix.seqdb.domain import enum


class RbacService(CommonRbacService):
    """Encapsulates seqdb RBAC service behavior."""

    def __init__(self, app, logger=None, **kwargs):
        """Initialize RBAC operations using the seqdb role enumeration.

        Args:
            app: Application that dispatches authorization commands.
            logger: Optional logger for authorization events.
            **kwargs: Additional commondb RBAC service configuration.
        """
        super().__init__(app, logger=logger, role_enum=enum.Role, **kwargs)

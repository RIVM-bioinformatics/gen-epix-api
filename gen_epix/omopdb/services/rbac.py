"""OmopDB specialization of shared role-based access command handling."""

from gen_epix.commondb.services import RbacService as CommonRbacService
from gen_epix.omopdb.domain import enum


class RbacService(CommonRbacService):
    """Encapsulates handling of RBAC commands using the OmopDB role enumeration."""

    def __init__(self, app, logger=None, **kwargs):
        """Initialize the shared RBAC service with OmopDB roles."""
        super().__init__(app, logger=logger, role_enum=enum.Role, **kwargs)

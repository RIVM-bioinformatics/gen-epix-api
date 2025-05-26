from gen_epix.casedb.domain.service.rbac import BaseRbacService
from gen_epix.fastapp import Policy


class BaseIsPermissionSubsetNewRolePolicy(Policy):
    """
    Policy that checks if the user has the required permissions to create or update a
    role.

    The user must have all the permissions that the new role has to avoid elevation of
    privileges.

    Does not apply to read or delete operations.
    """

    def __init__(self, rbac_service: BaseRbacService, **kwargs: dict):
        self.rbac_service = rbac_service
        self.props = kwargs

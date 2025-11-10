from gen_epix.casedb.domain import enum
from gen_epix.commondb.services import RbacService as CommonRbacService


class RbacService(CommonRbacService):
    def __init__(self, app, logger=None, **kwargs):
        super().__init__(app, logger=logger, role_enum=enum.Role, **kwargs)

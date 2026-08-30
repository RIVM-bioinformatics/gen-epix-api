"""Implement SeqDB application service behavior for services.rbac."""

from gen_epix.commondb.services import RbacService as CommonRbacService
from gen_epix.seqdb.domain import enum


class RbacService(CommonRbacService):
    def __init__(self, app, logger=None, **kwargs):
        super().__init__(app, logger=logger, role_enum=enum.Role, **kwargs)

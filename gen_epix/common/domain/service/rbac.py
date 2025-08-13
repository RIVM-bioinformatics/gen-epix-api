from gen_epix.common.domain import enum
from gen_epix.fastapp.services.rbac import BaseRbacService as ServiceBaseRbacService


class BaseRbacService(ServiceBaseRbacService):
    SERVICE_TYPE = enum.ServiceType.RBAC

    def register_handlers(self) -> None:
        self.register_default_crud_handlers()

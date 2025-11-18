from gen_epix.fastapp.service import BaseService
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.enum import ServiceType


class BaseFileService(BaseService):
    SERVICE_TYPE = ServiceType.FILE

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(command.FileCrudCommand, self.crud)

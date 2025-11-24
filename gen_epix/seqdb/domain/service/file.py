from abc import abstractmethod
from uuid import UUID

from gen_epix.fastapp.service import BaseService
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.enum import ServiceType


class BaseFileService(BaseService):
    SERVICE_TYPE = ServiceType.FILE

    def register_handlers(self) -> None:
        self.register_default_crud_handlers()
        f = self.app.register_handler
        f(
            command.CreateFileCommand,
            self.create_file,
        )

    @abstractmethod
    def create_file(
        self,
        cmd: command.CreateFileCommand,
    ) -> UUID:
        raise NotImplementedError()

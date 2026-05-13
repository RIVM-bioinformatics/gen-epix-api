from abc import abstractmethod
from uuid import UUID

from gen_epix.fastapp.service import BaseService
from gen_epix.seqdb.domain import command, model
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
        f(
            command.FileCrudCommand,
            self.crud_file,
        )

    @abstractmethod
    def create_file(
        self,
        cmd: command.CreateFileCommand,
    ) -> UUID:
        """Create a new file and return its unique identifier."""
        raise NotImplementedError()

    @abstractmethod
    def crud_file(
        self,
        cmd: command.FileCrudCommand,
    ) -> model.File | list[model.File] | UUID | list[UUID] | bool | list[bool] | None:
        """Perform CRUD operations on files based on the command."""
        raise NotImplementedError()

"""Define SeqDB domain interfaces and policies for domain.service.file."""

from abc import abstractmethod
from uuid import UUID

from gen_epix.fastapp.service import BaseService
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.enum import ServiceType


class BaseFileService(BaseService):
    """Define the file-service command handlers for SeqDB implementations."""

    SERVICE_TYPE = ServiceType.FILE

    def register_handlers(self) -> None:
        """Register default CRUD and SeqDB-specific file command handlers."""
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
        """Create a file and return its identifier.

        Args:
            cmd: File-creation command to execute.

        Returns:
            The identifier of the created file.

        Raises:
            NotImplementedError: Always, until a concrete file service implements it.
        """
        raise NotImplementedError()

    @abstractmethod
    def crud_file(
        self,
        cmd: command.FileCrudCommand,
    ) -> model.File | list[model.File] | UUID | list[UUID] | bool | list[bool] | None:
        """Execute a file CRUD command.

        Args:
            cmd: File CRUD command to execute.

        Returns:
            The command-specific file result.

        Raises:
            NotImplementedError: Always, until a concrete file service implements it.
        """
        raise NotImplementedError()

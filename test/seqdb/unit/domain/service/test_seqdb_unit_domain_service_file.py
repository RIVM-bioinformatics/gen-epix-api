"""Verify the abstract seqdb file-service handler contract."""

import inspect
from test.util.mock_compat import MagicMock, call
from uuid import UUID

from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.enum import ServiceType
from gen_epix.seqdb.domain.service.file import BaseFileService


class ConcreteFileService(BaseFileService):
    """Provide concrete file handlers for base-service tests."""

    def create_file(self, cmd: command.CreateFileCommand) -> UUID:
        """Return the test file identifier."""
        return cmd.file.id

    def crud_file(
        self,
        cmd: command.FileCrudCommand,
    ) -> model.File | list[model.File] | UUID | list[UUID] | bool | list[bool] | None:
        """Return a placeholder result for the test CRUD handler."""
        return None


def test_register_handlers_binds_default_and_file_specific_handlers():
    """Register generic CRUD first, then override file CRUD specifically."""
    app = MagicMock()
    app.domain.get_crud_commands_for_service_type.return_value = {
        command.FileCrudCommand
    }
    service = ConcreteFileService(
        app,
        service_type=ServiceType.FILE,
        register_handlers=False,
    )

    service.register_handlers()

    assert service.service_type == ServiceType.FILE
    assert app.register_handler.call_args_list == [
        call(command.FileCrudCommand, service.crud),
        call(command.CreateFileCommand, service.create_file),
        call(command.FileCrudCommand, service.crud_file),
    ]


def test_base_file_service_remains_abstract():
    """Keep create and CRUD operations abstract on the base service."""
    assert inspect.isabstract(BaseFileService)

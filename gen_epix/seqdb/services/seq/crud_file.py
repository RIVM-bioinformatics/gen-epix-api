"""Implement seqdb CRUD service operations for services.seq.crud_file."""

from uuid import UUID

from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service.file import BaseFileService


def file_service_crud_file(
    self: BaseFileService, cmd: command.FileCrudCommand
) -> list[model.File] | model.File | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for file entities.

    Args:
        self: File service executing the command.
        cmd: Typed file CRUD command.

    Returns:
        The action-specific file result.

    Raises:
        AssertionError: The command operation is unsupported.
    """
    user_id = cmd.user.id if cmd.user else None
    files: list[model.File] = cmd.get_objs()  # type: ignore[assignment]
    if cmd.is_create():
        # TODO: Specific logic for create operation to be added
        pass

    elif cmd.is_read():
        # TODO: Specific logic for read operation to be added
        pass

    elif cmd.is_update():
        # TODO: Specific logic for update operation to be added
        pass

    elif cmd.is_delete():
        # TODO: Specific logic for delete operation to be added, e.g. check for foreign key constraints before deletion
        pass

    else:
        raise AssertionError(f"Unsupported operation type: {cmd.operation.value}")

    return self.crud(cmd)  # type: ignore[return-value]

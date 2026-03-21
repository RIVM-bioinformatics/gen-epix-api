from uuid import UUID

from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_crud_seq_alignment(
    self: BaseSeqService, cmd: command.SeqAlignmentCrudCommand
) -> (
    list[model.SeqAlignment]
    | model.SeqAlignment
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for SeqAlignment entities."""
    user_id = cmd.user.id if cmd.user else None
    seq_alignments: list[model.SeqAlignment] = cmd.get_objs()  # type: ignore[assignment]
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
        raise NotImplementedError(f"Unsupported operation type: {cmd.operation.value}")

    return self.crud(cmd)  # type: ignore[return-value]

"""Implement seqdb CRUD service operations for services.seq.crud_seq_taxonomy."""

from uuid import UUID

from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_crud_seq_taxonomy(
    self: BaseSeqService, cmd: command.SeqTaxonomyCrudCommand
) -> (
    list[model.SeqTaxonomy]
    | model.SeqTaxonomy
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for sequence-taxonomy entities.

    Args:
        self: Sequence service executing the command.
        cmd: Typed sequence-taxonomy CRUD command.

    Returns:
        The action-specific sequence-taxonomy result.

    Raises:
        AssertionError: The command operation is unsupported.
    """
    user_id = cmd.user.id if cmd.user else None
    seq_taxonomies: list[model.SeqTaxonomy] = cmd.get_objs()  # type: ignore[assignment]
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

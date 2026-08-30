"""Implement SeqDB CRUD service operations for services.seq.crud_sample_data_collection_link."""

from uuid import UUID

from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_crud_sample_data_collection_link(
    self: BaseSeqService, cmd: command.SampleDataCollectionLinkCrudCommand
) -> (
    list[model.SampleDataCollectionLink]
    | model.SampleDataCollectionLink
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for SampleDataCollectionLink entities."""
    user_id = cmd.user.id if cmd.user else None
    sample_data_collection_links: list[model.SampleDataCollectionLink] = cmd.get_objs()  # type: ignore[assignment]
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

from uuid import UUID

from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_crud_allele(
    self: BaseSeqService, cmd: command.AlleleCrudCommand
) -> list[model.Allele] | model.Allele | list[UUID] | UUID | list[bool] | bool | None:
    """Handle CRUD operations for Allele entities."""
    user_id = cmd.user.id if cmd.user else None
    alleles: list[model.Allele] = cmd.get_objs()  # type: ignore[assignment]
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

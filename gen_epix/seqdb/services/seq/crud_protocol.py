from uuid import UUID

from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_crud_protocol(
    self: BaseSeqService, cmd: command.ProtocolCrudCommand
) -> (
    list[model.Protocol] | model.Protocol | list[UUID] | UUID | list[bool] | bool | None
):
    """Handle CRUD operations for Protocol entities"""
    if cmd.is_create():
        # if git commit hash is given, it may not already exists for the same protocol_type
        
        pass
    elif cmd.is_update():
        # protocol_type is read once (not allowed to update)
        pass
    elif cmd.is_delete():
        # verify if foreign key constraint would be violated (enforced by SQL, not by DICT)
        pass

    return self.crud(cmd)

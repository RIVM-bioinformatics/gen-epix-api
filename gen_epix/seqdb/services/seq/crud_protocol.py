from uuid import UUID

from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.enum import ProtocolType
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_crud_protocol(
    self: BaseSeqService, cmd: command.ProtocolCrudCommand
) -> (
    list[model.Protocol] | model.Protocol | list[UUID] | UUID | list[bool] | bool | None
):
    """Handle CRUD operations for Protocol entities"""
    user_id = cmd.user.id if cmd.user else None
    protocols: list[model.Protocol] = cmd.get_objs()  # type: ignore[assignment]
    if cmd.is_create():
        # if git commit hash is given, it may not already exists for the same protocol_type
        with self.repository.uow() as uow:
            all_protocols: list[model.Protocol] = self.repository.crud(  # type: ignore[assignment]
                uow, user_id, model.Protocol, None, None, CrudOperation.READ_ALL
            )
            all_protocols_type: set[ProtocolType] = {
                x.protocol_type for x in all_protocols
            }
            for protocol in protocols:
                if (
                    protocol.protocol_type in all_protocols_type
                    and protocol.git_commit_hash is not None
                ):
                    raise ValueError(
                        f"Protocol with protocol_type {protocol.protocol_type} already exists, cannot create another with git_commit_hash {protocol.git_commit_hash}"
                    )

    elif cmd.is_update():
        # protocol_type is read-only (not allowed to update)
        protocols_ids: set[UUID] = {x.id for x in protocols if x.id is not None}
        with self.repository.uow() as uow:
            existing_protocols: list[model.Protocol] = self.repository.crud(  # type: ignore[assignment]
                uow,
                user_id,
                model.Protocol,
                None,
                protocols_ids,
                CrudOperation.READ_SOME,
            )
            existing_protocols_by_id: dict[UUID, model.Protocol] = {
                x.id: x for x in existing_protocols if x.id is not None
            }
            for protocol in protocols:
                protocol_id = protocol.id
                if protocol_id is not None and protocol_id in existing_protocols_by_id:
                    if (
                        protocol.protocol_type
                        != existing_protocols_by_id[protocol_id].protocol_type
                    ):
                        raise ValueError(
                            f"Cannot update protocol_type for Protocol {protocol_id}: immutable field"
                        )

    elif cmd.is_delete():
        # verify if foreign key constraint would be violated (enforced by SQL, not by DICT)
        # TODO: Does this require a specific check? SARepository already has UniqueConstraintViolationError handling??
        pass

    return self.crud(cmd)  # type: ignore[return-value]

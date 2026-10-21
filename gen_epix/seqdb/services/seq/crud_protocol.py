"""Implement seqdb CRUD service operations for services.seq.crud_protocol."""

from uuid import UUID

from gen_epix.fastapp import CrudOperation
from gen_epix.filter.string_set import StringSetFilter
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.enum import ProtocolType
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_crud_protocol(
    self: BaseSeqService, cmd: command.ProtocolCrudCommand
) -> (
    list[model.Protocol] | model.Protocol | list[UUID] | UUID | list[bool] | bool | None
):
    """Handle CRUD operations for protocol entities.

    Args:
        self: Sequence service executing the command.
        cmd: Typed protocol CRUD command.

    Returns:
        The action-specific protocol result.

    Raises:
        ValueError: A create duplicates a protocol identity or an update changes type.
    """
    user_id = cmd.user.id if cmd.user else None
    protocols: list[model.Protocol] = cmd.get_objs()  # type: ignore[assignment]
    if cmd.is_create():
        _validate_protocol_creation(self, user_id, protocols)
    elif cmd.is_update():
        _validate_protocol_updates(self, user_id, protocols)
    elif cmd.is_delete():
        # verify if foreign key constraint would be violated (enforced by SQL, not by DICT)
        # TODO: Does this require a specific check? SARepository already has UniqueConstraintViolationError handling??
        pass

    return self.crud(cmd)  # type: ignore[return-value]


def _validate_protocol_creation(
    service: BaseSeqService, user_id: UUID | None, protocols: list[model.Protocol]
) -> None:
    """Reject duplicate protocol type and commit-hash pairs."""
    commit_hashes = {
        protocol.git_commit_hash
        for protocol in protocols
        if protocol.git_commit_hash is not None
    }
    with service.repository.uow() as uow:
        existing_protocols: list[model.Protocol] = service.repository.crud(
            uow,
            user_id,
            model.Protocol,
            CrudOperation.READ_ALL,
            filter=StringSetFilter(
                key="git_commit_hash", members=frozenset(commit_hashes)
            ),
        )
    seen: set[tuple[ProtocolType, str]] = set()
    for protocol in existing_protocols + protocols:
        if protocol.git_commit_hash is None:
            continue
        identifier = (protocol.protocol_type, protocol.git_commit_hash)
        if identifier in seen:
            raise ValueError(
                f"Protocol with protocol_type {protocol.protocol_type} and git_commit_hash {protocol.git_commit_hash} already exists, cannot create another"
            )
        seen.add(identifier)


def _validate_protocol_updates(
    service: BaseSeqService, user_id: UUID | None, protocols: list[model.Protocol]
) -> None:
    """Reject updates that change an existing protocol's immutable type."""
    protocol_ids: set[UUID] = {protocol.id for protocol in protocols if protocol.id}
    with service.repository.uow() as uow:
        existing_protocols: list[model.Protocol] = service.repository.crud(
            uow,
            user_id,
            model.Protocol,
            CrudOperation.READ_SOME,
            obj_ids=protocol_ids,
        )
    existing_protocol_map: dict[UUID, model.Protocol] = {
        protocol.id: protocol
        for protocol in existing_protocols
        if protocol.id is not None
    }
    for protocol in protocols:
        protocol_id = protocol.id
        if protocol_id is None or protocol_id not in existing_protocol_map:
            continue
        if protocol.protocol_type != existing_protocol_map[protocol_id].protocol_type:
            raise ValueError(
                f"Cannot update protocol_type for Protocol {protocol_id}: immutable field"
            )

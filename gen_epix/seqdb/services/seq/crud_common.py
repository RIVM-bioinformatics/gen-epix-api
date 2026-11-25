"""Implement seqdb CRUD service operations for services.seq.crud_common."""

from uuid import UUID

from gen_epix.commondb.domain.command import CrudCommand
from gen_epix.filter.base import Filter
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.uuid_set import UuidSetFilter


def _get_not_implemented_message(cmd: CrudCommand) -> str:
    """Format an unsupported CRUD-operation message including the caller's roles."""
    user = cmd.user
    message = f"Command {cmd.__class__.__name__} operation {cmd.operation.value} not implemented"
    if user is None:
        return message
    return message + " for user with role(s) " + ", ".join(map(str, user.roles))


def _compose_id_filter(*key_and_ids: tuple[str, set[UUID]]) -> Filter:
    """Combine field-specific UUID membership filters with logical AND."""
    return CompositeFilter(
        filters=[
            UuidSetFilter(key=key, members=frozenset(ids)) for key, ids in key_and_ids
        ],
        operator=LogicalOperator.AND,
    )

"""Test CRUD dispatch for tree-algorithm service operations."""

from types import SimpleNamespace
from typing import cast

import pytest

from gen_epix.seqdb.domain.command import TreeAlgorithmCrudCommand
from gen_epix.seqdb.domain.service import BaseSeqService
from gen_epix.seqdb.services.seq.crud_tree_algorithm import (
    seq_service_crud_tree_algorithm,
)


def _create_command(operation: str) -> SimpleNamespace:
    """Create a CRUD command-shaped object for one operation."""
    return SimpleNamespace(
        operation=SimpleNamespace(value=operation),
        user=None,
        get_objs=list,
        is_create=lambda: operation == "create",
        is_read=lambda: operation == "read",
        is_update=lambda: operation == "update",
        is_delete=lambda: operation == "delete",
    )


@pytest.mark.parametrize(
    "operation",
    ["create", "read", "update", "delete"],
    ids=["create", "read", "update", "delete"],
)
def test_crud_operations_delegate_command_and_return_result(operation: str) -> None:
    """Pass supported tree-algorithm commands to the base CRUD handler."""
    command = _create_command(operation)
    result = object()
    received_commands = []

    def crud(cmd: SimpleNamespace) -> object:
        received_commands.append(cmd)
        return result

    service = SimpleNamespace(crud=crud)

    actual = seq_service_crud_tree_algorithm(
        cast(BaseSeqService, service), cast(TreeAlgorithmCrudCommand, command)
    )

    assert received_commands == [command]
    assert actual is result


def test_unsupported_operation_raises_assertion() -> None:
    """Reject operations outside the CRUD command contract."""
    command = _create_command("unsupported")

    with pytest.raises(AssertionError, match="Unsupported operation type: unsupported"):
        seq_service_crud_tree_algorithm(
            cast(BaseSeqService, SimpleNamespace()),
            cast(TreeAlgorithmCrudCommand, command),
        )

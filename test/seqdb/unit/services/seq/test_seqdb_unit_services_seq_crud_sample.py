"""Unit tests for the SeqDB sample CRUD service handler."""

from types import SimpleNamespace

import pytest

from gen_epix.seqdb.services.seq.crud_sample import seq_service_crud_sample


def _create_command(operation: str) -> SimpleNamespace:
    """Create a CRUD command-shaped object for one operation."""
    return SimpleNamespace(
        operation=SimpleNamespace(value=operation),
        user=None,
        get_objs=lambda: [],
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
    """Delegate supported sample operations and preserve the handler result."""
    command = _create_command(operation)
    result = object()
    received_commands = []

    def crud(cmd: SimpleNamespace) -> object:
        received_commands.append(cmd)
        return result

    service = SimpleNamespace(crud=crud)

    actual = seq_service_crud_sample(service, command)

    assert received_commands == [command]
    assert actual is result


def test_unsupported_operation_raises_assertion() -> None:
    """Reject operations outside the CRUD command contract."""
    command = _create_command("unsupported")

    with pytest.raises(AssertionError, match="Unsupported operation type: unsupported"):
        seq_service_crud_sample(SimpleNamespace(), command)

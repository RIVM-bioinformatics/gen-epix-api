"""Verify locus-code-map CRUD service delegation."""

from test.util.mock_compat import Mock
from types import SimpleNamespace

import pytest

from gen_epix.seqdb.services.seq.crud_locus_code_map import (
    seq_service_crud_locus_code_map,
)


def _create_command(operation: str) -> SimpleNamespace:
    """Create a CRUD command-shaped object for one operation."""
    return SimpleNamespace(
        operation=SimpleNamespace(value=operation),
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
    """Pass supported locus-code-map commands through unchanged."""
    cmd = _create_command(operation)
    expected_result = object()
    service = SimpleNamespace(crud=Mock(return_value=expected_result))

    result = seq_service_crud_locus_code_map(service, cmd)

    service.crud.assert_called_once_with(cmd)
    assert result is expected_result


def test_unsupported_operation_raises_assertion() -> None:
    """Reject operation values outside the CRUD command contract."""
    cmd = _create_command("unsupported")

    with pytest.raises(AssertionError, match="Unsupported operation type: unsupported"):
        seq_service_crud_locus_code_map(SimpleNamespace(), cmd)

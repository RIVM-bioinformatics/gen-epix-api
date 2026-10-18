"""Test generic CRUD delegation for allele entities."""

# ruff: noqa: I001

from test.util.mock_compat import Mock
from types import SimpleNamespace

import pytest

from gen_epix.seqdb.services.seq.crud_allele import seq_service_crud_allele


@pytest.mark.parametrize(
    "operation_method", ["is_create", "is_read", "is_update", "is_delete"]
)
def test_crud_operation_delegates_to_generic_crud(operation_method: str) -> None:
    """Delegate every supported CRUD operation and return its result."""
    command = Mock()
    command.user = None
    command.get_objs.return_value = []
    for method_name in ("is_create", "is_read", "is_update", "is_delete"):
        getattr(command, method_name).return_value = method_name == operation_method
    result = object()
    service = SimpleNamespace(crud=Mock(return_value=result))

    actual = seq_service_crud_allele(service, command)  # type: ignore[arg-type]

    assert actual is result
    service.crud.assert_called_once_with(command)


def test_crud_rejects_unsupported_operation() -> None:
    """Raise an assertion containing the unsupported operation value."""
    command = Mock()
    command.user = None
    command.get_objs.return_value = []
    for method_name in ("is_create", "is_read", "is_update", "is_delete"):
        getattr(command, method_name).return_value = False
    command.operation = SimpleNamespace(value="UNKNOWN")
    service = SimpleNamespace(crud=Mock())

    with pytest.raises(AssertionError, match="UNKNOWN"):
        seq_service_crud_allele(service, command)  # type: ignore[arg-type]

    service.crud.assert_not_called()

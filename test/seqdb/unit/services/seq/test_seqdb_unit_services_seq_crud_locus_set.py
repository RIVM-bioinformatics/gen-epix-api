"""Test generic CRUD dispatch for SeqDB locus sets."""

from types import SimpleNamespace

import pytest

from gen_epix.seqdb.services.seq.crud_locus_set import seq_service_crud_locus_set


def make_command(operation):
    """Build a minimal command exposing the target service's CRUD contract."""
    selected = {operation: True}
    return SimpleNamespace(
        get_objs=list,
        is_create=lambda: selected.get("create", False),
        is_read=lambda: selected.get("read", False),
        is_update=lambda: selected.get("update", False),
        is_delete=lambda: selected.get("delete", False),
        operation=SimpleNamespace(value=operation),
        user=None,
    )


@pytest.mark.parametrize("operation", ["create", "read", "update", "delete"])
def test_supported_operations_delegate_the_original_command(operation):
    """Delegate each supported CRUD operation without replacing its command."""
    command = make_command(operation)
    result = object()
    calls = []
    service = SimpleNamespace(crud=lambda cmd: calls.append(cmd) or result)

    assert seq_service_crud_locus_set(service, command) is result
    assert calls == [command]


def test_unsupported_operation_raises_before_crud_delegation():
    """Reject an unsupported operation without invoking generic CRUD."""
    command = make_command("unsupported")
    calls = []
    service = SimpleNamespace(crud=calls.append)

    with pytest.raises(AssertionError, match="Unsupported operation type: unsupported"):
        seq_service_crud_locus_set(service, command)

    assert not calls

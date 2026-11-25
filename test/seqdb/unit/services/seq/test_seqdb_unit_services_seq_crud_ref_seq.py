"""Verify reference-sequence CRUD operations."""

from types import SimpleNamespace

import pytest

from gen_epix.fastapp.enum import CrudOperation, CrudOperationSet
from gen_epix.seqdb.services.seq.crud_ref_seq import seq_service_crud_ref_seq


def _create_command(operation: CrudOperation) -> SimpleNamespace:
    """Create a CRUD command-shaped object for one operation."""
    return SimpleNamespace(
        operation=operation,
        user=None,
        get_objs=lambda: [],
        is_create=lambda: operation in CrudOperationSet.CREATE.value,
        is_read=lambda: operation in CrudOperationSet.READ_OR_EXISTS.value,
        is_update=lambda: operation in CrudOperationSet.UPDATE.value,
        is_delete=lambda: operation in CrudOperationSet.DELETE.value,
    )


@pytest.mark.parametrize(
    "operation", [CrudOperation.UPSERT_ONE, CrudOperation.UPSERT_SOME]
)
def test_ref_seq_rejects_upsert_operations(operation: CrudOperation) -> None:
    """Reject upsert operations, which have no explicit RBAC permission type."""
    with pytest.raises(ValueError, match="Reference sequences do not support upsert"):
        seq_service_crud_ref_seq(SimpleNamespace(), _create_command(operation))


@pytest.mark.parametrize(
    "operation",
    [
        CrudOperation.UPDATE_ONE,
        CrudOperation.UPDATE_SOME,
        CrudOperation.DELETE_ONE,
        CrudOperation.DELETE_SOME,
        CrudOperation.DELETE_ALL,
    ],
)
def test_ref_seq_update_and_delete_delegate_to_generic_crud(
    operation: CrudOperation,
) -> None:
    """Allow authorized updates and deletes to reach the generic CRUD service."""
    command = _create_command(operation)
    result = object()
    received_commands = []

    def crud(cmd: SimpleNamespace) -> object:
        received_commands.append(cmd)
        return result

    assert seq_service_crud_ref_seq(SimpleNamespace(crud=crud), command) is result
    assert received_commands == [command]


@pytest.mark.parametrize(
    "operation", [CrudOperation.CREATE_ONE, CrudOperation.READ_ONE]
)
def test_ref_seq_create_and_read_delegate_to_generic_crud(
    operation: CrudOperation,
) -> None:
    """Continue delegating permitted create and read operations."""
    command = _create_command(operation)
    result = object()
    received_commands = []

    def crud(cmd: SimpleNamespace) -> object:
        received_commands.append(cmd)
        return result

    assert seq_service_crud_ref_seq(SimpleNamespace(crud=crud), command) is result
    assert received_commands == [command]

"""Verify read-set identifier CRUD operation delegation."""

import pytest

from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain.command import ReadSetIdentifierCrudCommand
from gen_epix.seqdb.services.seq.crud_read_set_identifier import (
    seq_service_crud_read_set_identifier,
)


@pytest.mark.parametrize(
    "operation", [CrudOperation.UPSERT_ONE, CrudOperation.UPSERT_SOME]
)
def test_upsert_operations_delegate_to_generic_crud(operation: CrudOperation) -> None:
    """Pass supported upsert writes to the shared CRUD implementation."""
    cmd = ReadSetIdentifierCrudCommand.model_construct(operation=operation)
    calls: list[ReadSetIdentifierCrudCommand] = []

    class CrudRecorder:
        def crud(self, received_cmd: ReadSetIdentifierCrudCommand) -> str:
            calls.append(received_cmd)
            return "result"

    assert (
        seq_service_crud_read_set_identifier(CrudRecorder(), cmd) == "result"
    )  # type: ignore[arg-type]
    assert calls == [cmd]

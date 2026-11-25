"""Verify sequence CRUD operation delegation."""

from uuid import uuid4

import pytest

from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain.command import SeqCrudCommand
from gen_epix.seqdb.services.seq.crud_seq import seq_service_crud_seq


@pytest.mark.parametrize(
    "operation", [CrudOperation.UPSERT_ONE, CrudOperation.UPSERT_SOME]
)
def test_upsert_operations_delegate_to_generic_crud(operation: CrudOperation) -> None:
    """Pass supported upsert writes to the shared CRUD implementation."""
    cmd = SeqCrudCommand.model_construct(operation=operation)
    result = uuid4()
    calls: list[SeqCrudCommand] = []

    class CrudRecorder:
        def crud(self, received_cmd: SeqCrudCommand) -> object:
            calls.append(received_cmd)
            return result

    assert seq_service_crud_seq(CrudRecorder(), cmd) == result  # type: ignore[arg-type]
    assert calls == [cmd]

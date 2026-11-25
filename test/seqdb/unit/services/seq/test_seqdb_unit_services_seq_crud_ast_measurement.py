"""Verify AST measurement CRUD operation delegation."""

import pytest

from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain.command import AstMeasurementCrudCommand
from gen_epix.seqdb.services.seq.crud_ast_measurement import (
    seq_service_crud_ast_measurement,
)


@pytest.mark.parametrize(
    "operation", [CrudOperation.UPSERT_ONE, CrudOperation.UPSERT_SOME]
)
def test_upsert_operations_delegate_to_generic_crud(operation: CrudOperation) -> None:
    """Pass supported upsert writes to the shared CRUD implementation."""
    cmd = AstMeasurementCrudCommand.model_construct(operation=operation)
    calls: list[AstMeasurementCrudCommand] = []

    class CrudRecorder:
        def crud(self, received_cmd: AstMeasurementCrudCommand) -> str:
            calls.append(received_cmd)
            return "result"

    assert (
        seq_service_crud_ast_measurement(CrudRecorder(), cmd) == "result"
    )  # type: ignore[arg-type]
    assert calls == [cmd]

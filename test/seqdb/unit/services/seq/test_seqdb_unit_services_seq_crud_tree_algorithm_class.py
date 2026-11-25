"""Verify tree-algorithm-class CRUD operation delegation."""

import pytest

from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain.command import TreeAlgorithmClassCrudCommand
from gen_epix.seqdb.services.seq.crud_tree_algorithm_class import (
    seq_service_crud_tree_algorithm_class,
)


@pytest.mark.parametrize(
    "operation", [CrudOperation.UPSERT_ONE, CrudOperation.UPSERT_SOME]
)
def test_upsert_operations_delegate_to_generic_crud(operation: CrudOperation) -> None:
    """Pass supported upsert writes to the shared CRUD implementation."""
    cmd = TreeAlgorithmClassCrudCommand.model_construct(operation=operation)
    calls: list[TreeAlgorithmClassCrudCommand] = []

    class CrudRecorder:
        def crud(self, received_cmd: TreeAlgorithmClassCrudCommand) -> str:
            calls.append(received_cmd)
            return "result"

    assert (
        seq_service_crud_tree_algorithm_class(CrudRecorder(), cmd) == "result"
    )  # type: ignore[arg-type]
    assert calls == [cmd]

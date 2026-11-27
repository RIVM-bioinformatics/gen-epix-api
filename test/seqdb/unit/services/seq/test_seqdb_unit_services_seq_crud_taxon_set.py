"""Verify taxon-set CRUD operation delegation."""

import pytest

from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain.command import TaxonSetCrudCommand
from gen_epix.seqdb.services.seq.crud_taxon_set import seq_service_crud_taxon_set


@pytest.mark.parametrize(
    "operation", [CrudOperation.UPSERT_ONE, CrudOperation.UPSERT_SOME]
)
def test_upsert_operations_delegate_to_generic_crud(operation: CrudOperation) -> None:
    """Pass supported upsert writes to the shared CRUD implementation."""
    cmd = TaxonSetCrudCommand.model_construct(operation=operation)
    calls: list[TaxonSetCrudCommand] = []

    class CrudRecorder:
        def crud(self, received_cmd: TaxonSetCrudCommand) -> str:
            calls.append(received_cmd)
            return "result"

    assert seq_service_crud_taxon_set(CrudRecorder(), cmd) == "result"  # type: ignore[arg-type]
    assert calls == [cmd]

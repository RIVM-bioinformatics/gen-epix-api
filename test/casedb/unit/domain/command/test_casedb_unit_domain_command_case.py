"""Validate CaseType descriptions in generated CASEDB command schemas."""

import pytest

from gen_epix.casedb.domain.command.case import (
    RetrieveGeneticSequenceFastaByCaseCommand,
    RetrieveIsOwnCasesCommand,
    RetrievePhylogeneticTreeByCasesCommand,
    RetrieveSimilarCasesCommand,
)

CASE_TYPE_ID_DESCRIPTION = "The CaseType ID that all the cases must belong to."


@pytest.mark.parametrize(
    "command_class",
    [
        RetrieveGeneticSequenceFastaByCaseCommand,
        RetrieveIsOwnCasesCommand,
        RetrievePhylogeneticTreeByCasesCommand,
        RetrieveSimilarCasesCommand,
    ],
)
def test_case_type_id_schema_description(command_class: type) -> None:
    """Keep the CaseType constraint visible in generated command schemas."""
    assert (
        command_class.model_fields["case_type_id"].description
        == CASE_TYPE_ID_DESCRIPTION
    )

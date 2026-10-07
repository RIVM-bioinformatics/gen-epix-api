"""Validate CaseType descriptions in generated CASEDB command schemas."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.casedb.domain import model
from gen_epix.casedb.domain.command.case import (
    DimCrudCommand,
    RetrieveGeneticSequenceFastaByCaseCommand,
    RetrieveIsOwnCasesCommand,
    RetrievePhylogeneticTreeByCasesCommand,
    RetrieveSimilarCasesCommand,
)
from gen_epix.fastapp.enum import CrudOperation

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


def _make_dim(is_case_date_dim: bool) -> model.Dim:
    return model.Dim(
        case_type_id=uuid4(),
        ref_dim_id=uuid4(),
        code="dimension",
        rank=1,
        is_case_date_dim=is_case_date_dim,
    )


def test_dim_create_some_rejects_multiple_case_date_dimensions() -> None:
    with pytest.raises(ValidationError, match="At most one case-date dimension"):
        DimCrudCommand(
            operation=CrudOperation.CREATE_SOME,
            objs=[_make_dim(True), _make_dim(False), _make_dim(True)],
        )


@pytest.mark.parametrize("case_date_flags", [[False, False], [True, False]])
def test_dim_create_some_allows_at_most_one_case_date_dimension(
    case_date_flags: list[bool],
) -> None:
    command = DimCrudCommand(
        operation=CrudOperation.CREATE_SOME,
        objs=[_make_dim(flag) for flag in case_date_flags],
    )

    assert command.get_objs() is not None


def test_dim_update_some_does_not_apply_create_batch_rule() -> None:
    command = DimCrudCommand(
        operation=CrudOperation.UPDATE_SOME,
        objs=[_make_dim(True), _make_dim(True)],
    )

    assert command.get_objs() is not None

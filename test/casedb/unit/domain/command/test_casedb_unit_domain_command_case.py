"""Validate CaseType descriptions in generated CASEDB command schemas."""

from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel, ValidationError

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
def test_case_type_id_schema_description(command_class: type[BaseModel]) -> None:
    """Keep the CaseType constraint visible in generated command schemas."""
    assert (
        command_class.model_fields["case_type_id"].description
        == CASE_TYPE_ID_DESCRIPTION
    )


def _make_dim(is_case_date_dim: bool, case_type_id: UUID | None = None) -> model.Dim:
    return model.Dim(
        case_type_id=case_type_id or uuid4(),
        ref_dim_id=uuid4(),
        code="dimension",
        rank=1,
        is_case_date_dim=is_case_date_dim,
    )


def test_dim_create_some_rejects_multiple_case_date_dimensions() -> None:
    """Reject two case-date dimensions for one case type in a batch."""
    case_type_id = uuid4()
    with pytest.raises(ValidationError, match="At most one case-date dimension"):
        DimCrudCommand(
            operation=CrudOperation.CREATE_SOME,
            objs=[
                _make_dim(True, case_type_id),
                _make_dim(False, case_type_id),
                _make_dim(True, case_type_id),
            ],
        )


@pytest.mark.parametrize("case_date_flags", [[False, False], [True, False]])
def test_dim_create_some_allows_at_most_one_case_date_dimension(
    case_date_flags: list[bool],
) -> None:
    """Allow a batch with zero or one case-date dimension per case type."""
    command = DimCrudCommand(
        operation=CrudOperation.CREATE_SOME,
        objs=[_make_dim(flag) for flag in case_date_flags],
    )

    assert command.get_objs() is not None


def test_dim_create_some_allows_case_date_dimensions_for_different_case_types() -> None:
    """Allow one case-date dimension for each of multiple case types."""
    command = DimCrudCommand(
        operation=CrudOperation.CREATE_SOME,
        objs=[_make_dim(True), _make_dim(True)],
    )

    assert command.get_objs() is not None


def test_dim_update_some_does_not_apply_create_batch_rule() -> None:
    """Do not apply the create-batch limit to updates."""
    command = DimCrudCommand(
        operation=CrudOperation.UPDATE_SOME,
        objs=[_make_dim(True), _make_dim(True)],
    )

    assert command.get_objs() is not None

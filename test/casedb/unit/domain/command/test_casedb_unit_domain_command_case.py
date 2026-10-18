"""Validate CaseType descriptions in generated CASEDB command schemas."""

from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel, ValidationError

from gen_epix.casedb.domain import model
from gen_epix.casedb.domain.command.case import (
    CreateCaseSetCommand,
    DimCrudCommand,
    RetrieveCaseRightsCommand,
    RetrieveCasesByIdCommand,
    RetrieveCaseSetRightsCommand,
    RetrieveGeneticSequenceFastaByCaseCommand,
    RetrieveIsOwnCasesCommand,
    RetrievePhylogeneticTreeByCasesCommand,
    RetrieveSeqDistancesByCasesCommand,
    RetrieveSimilarCasesCommand,
    UploadCasesCommand,
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


def _make_case(case_type_id: UUID) -> model.Case:
    return model.Case(
        case_type_id=case_type_id,
        created_in_data_collection_id=uuid4(),
        content={},
    )


def _make_case_batch(case_type_id: UUID) -> model.CaseBatchForUpload:
    return model.CaseBatchForUpload(
        cases=[model.CaseForUpload(case=_make_case(case_type_id))]
    )


def test_create_case_set_excludes_its_created_data_collection() -> None:
    """Keep the creating collection out of additional case-set links."""
    created_in_data_collection_id = uuid4()
    additional_data_collection_id = uuid4()
    case_set = model.CaseSet(
        case_type_id=uuid4(),
        created_in_data_collection_id=created_in_data_collection_id,
        name="Example",
        code="example",
        description="Example case set",
        case_set_category_id=uuid4(),
        case_set_status_id=uuid4(),
    )

    create_command = CreateCaseSetCommand(
        case_set=case_set,
        data_collection_ids={
            created_in_data_collection_id,
            additional_data_collection_id,
        },
    )

    assert create_command.data_collection_ids == {additional_data_collection_id}


def test_upload_cases_accepts_matching_case_type() -> None:
    """Accept a batch whose cases all match the requested case type."""
    case_type_id = uuid4()

    upload_command = UploadCasesCommand(
        case_type_id=case_type_id,
        case_batch=_make_case_batch(case_type_id),
    )

    assert upload_command.case_batch.cases[0].case.case_type_id == case_type_id


def test_upload_cases_rejects_mismatched_case_type() -> None:
    """Reject a batch containing a case of another type."""
    with pytest.raises(ValidationError, match="All cases must belong"):
        UploadCasesCommand(
            case_type_id=uuid4(),
            case_batch=_make_case_batch(uuid4()),
        )


@pytest.mark.parametrize(
    "command_class",
    [RetrieveCasesByIdCommand, RetrieveCaseRightsCommand],
    ids=["retrieve-cases", "retrieve-case-rights"],
)
@pytest.mark.parametrize("case_count", [0, 1, 3], ids=["empty", "single", "multiple"])
def test_case_id_commands_accept_unique_ids(
    command_class: type[BaseModel], case_count: int
) -> None:
    """Accept empty, singleton, and distinct case-ID lists in input order."""
    case_ids = [uuid4() for _ in range(case_count)]

    retrieve_command = command_class(case_type_id=uuid4(), case_ids=case_ids)

    assert retrieve_command.case_ids == case_ids


@pytest.mark.parametrize(
    "command_class",
    [RetrieveCasesByIdCommand, RetrieveCaseRightsCommand],
    ids=["retrieve-cases", "retrieve-case-rights"],
)
def test_case_id_commands_reject_duplicate_ids(
    command_class: type[BaseModel],
) -> None:
    """Reject duplicate case IDs in retrieval and rights commands."""
    duplicate_case_id = uuid4()

    with pytest.raises(ValidationError, match="Duplicate case ids"):
        command_class(
            case_type_id=uuid4(), case_ids=[duplicate_case_id, duplicate_case_id]
        )


@pytest.mark.parametrize("case_count", [0, 1, 3], ids=["empty", "single", "multiple"])
def test_case_set_rights_accepts_unique_ids(case_count: int) -> None:
    """Accept empty, singleton, and distinct case-set ID lists."""
    case_set_ids = [uuid4() for _ in range(case_count)]

    retrieve_command = RetrieveCaseSetRightsCommand(case_set_ids=case_set_ids)

    assert retrieve_command.case_set_ids == case_set_ids


def test_case_set_rights_rejects_duplicate_ids() -> None:
    """Reject duplicate case-set IDs before rights lookup."""
    duplicate_case_set_id = uuid4()

    with pytest.raises(ValidationError, match="Duplicate CaseSet IDs"):
        RetrieveCaseSetRightsCommand(
            case_set_ids=[duplicate_case_set_id, duplicate_case_set_id]
        )


def test_retrieve_similar_cases_accepts_zero_distance() -> None:
    """Allow an exact-match-only distance threshold."""
    similar_cases_command = RetrieveSimilarCasesCommand(
        case_type_id=uuid4(),
        max_distance=0,
        genetic_distance_col_id=uuid4(),
        case_ids=[uuid4()],
    )

    assert similar_cases_command.max_distance == 0


def test_retrieve_similar_cases_rejects_negative_distance() -> None:
    """Reject negative genetic-distance thresholds."""
    with pytest.raises(ValidationError):
        RetrieveSimilarCasesCommand(
            case_type_id=uuid4(),
            max_distance=-0.01,
            genetic_distance_col_id=uuid4(),
            case_ids=[uuid4()],
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


@pytest.mark.parametrize("case_count", [0, 1, 3])
def test_retrieve_seq_distances_accepts_unique_case_ids(case_count: int) -> None:
    """Accept empty or unique case IDs and preserve their order."""
    case_ids = [uuid4() for _ in range(case_count)]

    retrieve_command = RetrieveSeqDistancesByCasesCommand(
        case_type_id=uuid4(),
        case_ids=case_ids,
        genetic_distance_col_id=uuid4(),
    )

    assert retrieve_command.case_ids == case_ids


def test_retrieve_seq_distances_rejects_duplicate_case_ids() -> None:
    """Reject repeated case IDs before dispatch."""
    duplicate_case_id = uuid4()

    with pytest.raises(ValidationError, match="case_ids must be unique"):
        RetrieveSeqDistancesByCasesCommand(
            case_type_id=uuid4(),
            case_ids=[duplicate_case_id, duplicate_case_id],
            genetic_distance_col_id=uuid4(),
        )

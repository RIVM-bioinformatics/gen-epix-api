"""Test dictionary-backed case-statistics repository behavior."""

from datetime import datetime
from test.util.mock_compat import Mock
from uuid import UUID, uuid4

from gen_epix.casedb.domain import model
from gen_epix.casedb.repositories.case_dict import CaseDictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def _repository_with_one_case() -> tuple[CaseDictRepository, model.Case, UUID]:
    case_type_id: UUID = uuid4()
    case = model.Case(
        id=uuid4(),
        case_type_id=case_type_id,
        created_in_data_collection_id=uuid4(),
        timed_at=datetime(2024, 1, 2, 12, 34, 56),
        content={},
    )
    repository = CaseDictRepository.__new__(CaseDictRepository)
    repository._db = {  # type: ignore[attr-defined]
        model.Case: {case.id: case},
        model.CaseDataCollectionLink: {},
    }
    return repository, case, case_type_id


def test_unrestricted_statistics_include_all_cases_and_preserve_dates() -> None:
    """A missing access map means unrestricted case and date access."""
    repository, case, case_type_id = _repository_with_one_case()

    result = repository.retrieve_case_stats(Mock(spec=BaseUnitOfWork), case_type_id)

    assert result.n_cases == 1
    assert result.first_case_date == case.timed_at
    assert result.last_case_date == case.timed_at


def test_empty_access_map_excludes_all_cases() -> None:
    """An explicit empty access map means no accessible data collections."""
    repository, _, case_type_id = _repository_with_one_case()

    result = repository.retrieve_case_stats(
        Mock(spec=BaseUnitOfWork), case_type_id, data_collections_by_time_unit={}
    )

    assert result.n_cases == 0
    assert result.first_case_date is None
    assert result.last_case_date is None

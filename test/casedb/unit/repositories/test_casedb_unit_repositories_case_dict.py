"""Test dictionary-backed case-statistics repository behavior."""

from datetime import datetime
from test.util.mock_compat import Mock
from uuid import UUID, uuid4

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.repositories.case_dict import CaseDictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.datetime_range import DatetimeRangeFilter

_TIMED_AT = datetime(2024, 1, 2, 12, 34, 56)


def _repository_with_one_case() -> tuple[CaseDictRepository, model.Case, UUID]:
    case_type_id: UUID = uuid4()
    case = model.Case(
        id=uuid4(),
        case_type_id=case_type_id,
        created_in_data_collection_id=uuid4(),
        timed_at=_TIMED_AT,
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


def test_collection_time_unit_index_map_handles_missing_and_multiple_scopes() -> None:
    year_collection_id = uuid4()
    month_collection_id = uuid4()

    assert CaseDictRepository._get_data_collection_time_unit_index_map(None) == {}
    assert CaseDictRepository._get_data_collection_time_unit_index_map({}) == {}
    result = CaseDictRepository._get_data_collection_time_unit_index_map(
        {
            enum.ColType.TIME_YEAR: {year_collection_id},
            enum.ColType.TIME_MONTH: {month_collection_id},
        }
    )

    assert result == {
        year_collection_id: list(enum.ColTypeOrder.TIME_RESOLUTION_DESC.value).index(
            enum.ColType.TIME_YEAR
        ),
        month_collection_id: list(enum.ColTypeOrder.TIME_RESOLUTION_DESC.value).index(
            enum.ColType.TIME_MONTH
        ),
    }


def test_case_map_filters_by_type_and_optional_ids() -> None:
    repository, case, case_type_id = _repository_with_one_case()
    assert case.id is not None
    other_case = model.Case(
        id=uuid4(),
        case_type_id=uuid4(),
        created_in_data_collection_id=uuid4(),
        timed_at=_TIMED_AT,
        content={},
    )
    assert other_case.id is not None
    repository.db[model.Case][other_case.id] = other_case

    assert repository._get_case_map(case_type_id, None) == {case.id: case}
    assert repository._get_case_map(case_type_id, {case.id}) == {case.id: case}
    assert repository._get_case_map(case_type_id, set()) == {}


def test_build_case_stats_rows_includes_only_accessible_linked_collections() -> None:
    repository, case, _ = _repository_with_one_case()
    assert case.id is not None
    linked_collection_id = uuid4()
    link = model.CaseDataCollectionLink(
        id=uuid4(),
        case_id=case.id,
        data_collection_id=linked_collection_id,
    )
    repository.db[model.CaseDataCollectionLink][link.id] = link
    rows = repository._build_case_stats_rows(
        {case.id: case},
        {linked_collection_id: 1},
        {linked_collection_id},
        has_abac=True,
        has_private_data_collections=True,
    )

    assert rows == [(case.timed_at, case.id, case.count, 1, True)]


def test_aggregate_case_stats_rows_counts_cases_once_and_applies_date_filter() -> None:
    repository, _, case_type_id = _repository_with_one_case()
    excluded_case_id = uuid4()
    included_case_id = uuid4()
    zero_count_case_id = uuid4()
    case_stats = model.CaseStats(case_type_id=case_type_id)
    rows = [
        (datetime(2023, 12, 31), excluded_case_id, 2, 0, True),
        (datetime(2024, 2, 1), included_case_id, 3, 0, True),
        (datetime(2024, 2, 1), included_case_id, 3, 0, False),
        (datetime(2024, 1, 1), zero_count_case_id, 0, 0, True),
    ]

    result = repository._aggregate_case_stats_rows(
        case_stats,
        rows,
        has_abac=False,
        datetime_range_filter=DatetimeRangeFilter(lower_bound=datetime(2024, 1, 1)),
    )

    assert result.n_cases == 3
    assert result.n_own_cases == 3
    assert result.first_case_date == datetime(2024, 2, 1)
    assert result.last_case_date == datetime(2024, 2, 1)

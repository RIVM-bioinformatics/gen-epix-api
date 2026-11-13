"""Test dictionary-backed case-statistics repository behavior."""

from datetime import datetime
from test.util.mock_compat import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.repositories.case_dict import CaseDictRepository
from gen_epix.fastapp.repositories.dict.unit_of_work import DictUnitOfWork
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
    denied_link = model.CaseDataCollectionLink(
        id=uuid4(),
        case_id=case.id,
        data_collection_id=uuid4(),
    )
    orphan_link = model.CaseDataCollectionLink(
        id=uuid4(),
        case_id=uuid4(),
        data_collection_id=linked_collection_id,
    )
    repository.db[model.CaseDataCollectionLink].update(
        {entry.id: entry for entry in (link, denied_link, orphan_link)}
    )
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


def test_retrieve_case_stats_filters_by_case_ids() -> None:
    repository, case, case_type_id = _repository_with_one_case()
    assert case.id is not None
    excluded_case = model.Case(
        id=uuid4(),
        case_type_id=case_type_id,
        created_in_data_collection_id=uuid4(),
        count=5,
        timed_at=datetime(2025, 1, 1),
        content={},
    )
    assert excluded_case.id is not None
    repository.db[model.Case][excluded_case.id] = excluded_case

    result = repository.retrieve_case_stats(
        Mock(spec=BaseUnitOfWork), case_type_id, case_ids={case.id}
    )

    assert result.n_cases == case.count
    assert result.first_case_date == case.timed_at
    assert result.last_case_date == case.timed_at


def _repository_with_case_stats_fixture(
    target_count: int, is_private: bool
) -> tuple[CaseDictRepository, UUID, UUID, UUID]:
    case_type_id = uuid4()
    public_data_collection_id = uuid4()
    private_data_collection_id = uuid4()
    target_case_id = uuid4()
    zero_case = model.Case(
        id=uuid4(),
        case_type_id=case_type_id,
        created_in_data_collection_id=public_data_collection_id,
        count=0,
        timed_at=datetime(2020, 2, 3, 12),
        content={},
    )
    one_case = model.Case(
        id=uuid4(),
        case_type_id=case_type_id,
        created_in_data_collection_id=public_data_collection_id,
        count=1,
        timed_at=datetime(2021, 4, 5, 12),
        content={},
    )
    target_case = model.Case(
        id=target_case_id,
        case_type_id=case_type_id,
        created_in_data_collection_id=public_data_collection_id,
        count=target_count,
        timed_at=datetime(2022, 6, 7, 12),
        content={},
    )
    cases = [zero_case, one_case, target_case]
    links = (
        [
            model.CaseDataCollectionLink(
                id=uuid4(),
                case_id=target_case_id,
                data_collection_id=private_data_collection_id,
            )
        ]
        if is_private
        else []
    )
    repository = CaseDictRepository.__new__(CaseDictRepository)
    repository._db = {  # type: ignore[attr-defined]
        model.Case: {case.id: case for case in cases},
        model.CaseDataCollectionLink: {link.id: link for link in links},
    }
    return (
        repository,
        case_type_id,
        public_data_collection_id,
        private_data_collection_id,
    )


@pytest.mark.parametrize(
    "target_count",
    [0, 1, 3],
    ids=["zero-target-cases", "one-target-case", "multiple-target-cases"],
)
@pytest.mark.parametrize(
    "is_date_restricted",
    [False, True],
    ids=["unrestricted-date-resolution", "year-resolution"],
)
@pytest.mark.parametrize("is_private", [False, True], ids=["public", "private"])
@pytest.mark.parametrize(
    "is_datetime_filtered",
    [False, True],
    ids=["without-date-filter", "with-date-filter"],
)
def test_retrieve_case_stats_count_access_and_private_matrix(
    target_count: int,
    is_date_restricted: bool,
    is_private: bool,
    is_datetime_filtered: bool,
) -> None:
    repository, case_type_id, public_id, private_id = (
        _repository_with_case_stats_fixture(target_count, is_private)
    )
    data_collections_by_time_unit = (
        {
            enum.ColType.TIME_YEAR: {public_id, private_id},
        }
        if is_date_restricted
        else None
    )

    stats = repository.retrieve_case_stats(
        DictUnitOfWork(),
        case_type_id=case_type_id,
        data_collections_by_time_unit=data_collections_by_time_unit,
        private_data_collection_ids={private_id} if is_private else set(),
        datetime_range_filter=(
            DatetimeRangeFilter(lower_bound=datetime(2022, 1, 1))
            if is_datetime_filtered
            else None
        ),
    )

    expected_target_date = (
        datetime(2022, 1, 1) if is_date_restricted else datetime(2022, 6, 7, 12)
    )
    expected_one_date = (
        datetime(2021, 1, 1) if is_date_restricted else datetime(2021, 4, 5, 12)
    )
    expected_count = target_count if is_datetime_filtered else 1 + target_count
    assert stats.n_cases == expected_count
    assert stats.n_own_cases == (target_count if is_private else 0)
    if is_datetime_filtered:
        expected_filtered_date = expected_target_date if target_count > 0 else None
        assert stats.first_case_date == expected_filtered_date
        assert stats.last_case_date == expected_filtered_date
    else:
        assert stats.first_case_date == expected_one_date
        assert stats.last_case_date == (
            expected_target_date if target_count > 0 else expected_one_date
        )

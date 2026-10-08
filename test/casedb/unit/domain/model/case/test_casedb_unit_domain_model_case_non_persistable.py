from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.casedb.domain.model.case.non_persistable import (
    BaseCaseRights,
    CaseCohortLink,
    CaseQuery,
    CaseQueryResult,
    CaseRights,
    CaseSetQuery,
    CaseSetRights,
    CaseStats,
    RefDataAccess,
    SimilarCase,
)
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.filter import CompositeFilter
from gen_epix.filter.datetime_range import DatetimeRangeFilter
from gen_epix.filter.uuid_set import UuidSetFilter

NOW = datetime(2024, 5, 1, 12, 0, 0)

REF_FILTER_METHODS = [
    ("get_case_type_set_filter", "case_type_set_ids"),
    ("get_case_type_filter", "case_type_ids"),
    ("get_col_set_filter", "col_set_ids"),
    ("get_col_filter", "col_ids"),
    ("get_dim_filter", "dim_ids"),
    ("get_ref_dim_filter", "ref_dim_ids"),
    ("get_ref_col_filter", "ref_col_ids"),
]


def _uuid_filter(key: str = "id") -> CompositeFilter:
    return CompositeFilter(filters=[UuidSetFilter(key=key, members={uuid4()})])


def _base_rights_kwargs() -> dict:
    return {
        "created_in_data_collection_id": uuid4(),
        "case_type_id": uuid4(),
        "data_collection_ids": {uuid4()},
        "is_full_access": False,
        "add_data_collection_ids": set(),
        "remove_data_collection_ids": set(),
        "can_delete": False,
        "shared_in_data_collection_ids": set(),
    }


class TestCaseStats:
    def test_defaults_are_empty(self) -> None:
        stats = CaseStats(case_type_id=uuid4())
        assert stats.n_cases == 0
        assert stats.n_own_cases == 0
        assert stats.case_set_id is None
        assert stats.first_case_date is None
        assert stats.last_case_date is None

    @pytest.mark.parametrize(
        "first, last",
        [
            pytest.param(NOW, NOW, id="equal-dates"),
            pytest.param(NOW, NOW + timedelta(days=1), id="ordered-dates"),
        ],
    )
    @pytest.mark.parametrize("n_own_cases", [0, 3], ids=["none-own", "all-own"])
    def test_valid_non_empty(
        self, first: datetime, last: datetime, n_own_cases: int
    ) -> None:
        stats = CaseStats(
            case_type_id=uuid4(),
            n_cases=3,
            n_own_cases=n_own_cases,
            first_case_date=first,
            last_case_date=last,
        )
        assert stats.first_case_date == first
        assert stats.last_case_date == last

    @pytest.mark.parametrize(
        "kwargs, message",
        [
            pytest.param(
                {
                    "n_cases": 1,
                    "n_own_cases": 2,
                    "first_case_date": NOW,
                    "last_case_date": NOW,
                },
                "n_own_cases cannot be greater",
                id="own-exceeds-total",
            ),
            pytest.param(
                {"first_case_date": NOW},
                "must be None",
                id="empty-with-first-date",
            ),
            pytest.param(
                {"last_case_date": NOW},
                "must be None",
                id="empty-with-last-date",
            ),
            pytest.param(
                {"n_cases": 1},
                "must be provided",
                id="non-empty-without-dates",
            ),
            pytest.param(
                {"n_cases": 1, "first_case_date": NOW},
                "must be provided",
                id="non-empty-without-last",
            ),
            pytest.param(
                {"n_cases": 1, "last_case_date": NOW},
                "must be provided",
                id="non-empty-without-first",
            ),
            pytest.param(
                {
                    "n_cases": 2,
                    "first_case_date": NOW + timedelta(seconds=1),
                    "last_case_date": NOW,
                },
                "must be before or equal",
                id="dates-reversed",
            ),
            pytest.param({"n_cases": -1}, "greater than or equal", id="negative-total"),
            pytest.param(
                {"n_own_cases": -1}, "greater than or equal", id="negative-own"
            ),
        ],
    )
    def test_invalid_combinations(self, kwargs: dict, message: str) -> None:
        with pytest.raises(ValidationError, match=message):
            CaseStats(case_type_id=uuid4(), **kwargs)

    def test_entity_is_not_persistable(self) -> None:
        assert CaseStats.ENTITY.persistable is False
        assert CaseStats.ENTITY.snake_case_plural_name == "case_set_stats"


class TestCaseQuery:
    def test_defaults(self) -> None:
        case_type_id = uuid4()
        query = CaseQuery(case_type_id=case_type_id)
        assert query.case_type_id == case_type_id
        assert query.label is None
        assert query.case_set_ids is None
        assert query.datetime_range_filter is None
        assert query.filter is None
        assert query.id is None

    def test_all_fields(self) -> None:
        case_set_ids = {uuid4(), uuid4()}
        range_filter = DatetimeRangeFilter(key="date", lower_bound=NOW)
        composite = _uuid_filter()
        query = CaseQuery(
            label="q",
            case_type_id=uuid4(),
            case_set_ids=case_set_ids,
            datetime_range_filter=range_filter,
            filter=composite,
        )
        assert query.case_set_ids == case_set_ids
        assert query.datetime_range_filter == range_filter
        assert query.filter == composite

    def test_requires_case_type_id(self) -> None:
        with pytest.raises(ValidationError):
            CaseQuery()  # type: ignore[call-arg]


class TestCaseSetQuery:
    def test_valid(self) -> None:
        composite = _uuid_filter()
        query = CaseSetQuery(label="x", filter=composite)
        assert query.label == "x"
        assert query.filter == composite

    @pytest.mark.parametrize(
        "label, with_filter",
        [
            pytest.param("x", False, id="missing-filter"),
            pytest.param(None, True, id="none-label"),
        ],
    )
    def test_invalid(self, label: str | None, with_filter: bool) -> None:
        kwargs: dict = {"label": label}
        if with_filter:
            kwargs["filter"] = _uuid_filter()
        with pytest.raises(ValidationError):
            CaseSetQuery(**kwargs)


class TestCaseRights:
    def test_base_rights_requires_all_fields(self) -> None:
        kwargs = _base_rights_kwargs()
        assert BaseCaseRights(**kwargs).can_delete is False
        for key in kwargs:
            incomplete = {k: v for k, v in kwargs.items() if k != key}
            with pytest.raises(ValidationError):
                BaseCaseRights(**incomplete)

    def test_case_rights(self) -> None:
        case_id = uuid4()
        col_id = uuid4()
        rights = CaseRights(
            **_base_rights_kwargs(),
            case_id=case_id,
            read_col_ids={col_id},
            write_col_ids=set(),
        )
        assert rights.case_id == case_id
        assert rights.read_col_ids == {col_id}
        assert rights.write_col_ids == set()
        assert CaseRights.NAME == "CaseRights"
        assert CaseRights.ENTITY.persistable is False

    def test_case_rights_requires_col_ids(self) -> None:
        with pytest.raises(ValidationError):
            CaseRights(**_base_rights_kwargs(), case_id=uuid4())  # type: ignore

    def test_case_set_rights(self) -> None:
        case_set_id = uuid4()
        rights = CaseSetRights(
            **_base_rights_kwargs(),
            case_set_id=case_set_id,
            read_case_set=True,
            write_case_set=False,
        )
        assert rights.case_set_id == case_set_id
        assert rights.read_case_set is True
        assert rights.write_case_set is False
        assert CaseSetRights.NAME == "CaseSetRights"
        assert CaseSetRights.ENTITY.persistable is False

    def test_case_set_rights_requires_flags(self) -> None:
        with pytest.raises(ValidationError):
            CaseSetRights(**_base_rights_kwargs(), case_set_id=uuid4())  # type: ignore


class TestCaseQueryResult:
    @pytest.mark.parametrize(
        "case_ids", [[], [uuid4()], [uuid4(), uuid4()]], ids=["empty", "one", "many"]
    )
    def test_valid(self, case_ids: list) -> None:
        query = CaseQuery(case_type_id=uuid4())
        result = CaseQueryResult(
            case_query=query, case_ids=case_ids, is_max_results_exceeded=False
        )
        assert result.case_query == query
        assert result.case_ids == case_ids
        assert result.is_max_results_exceeded is False

    def test_missing_flag_is_invalid(self) -> None:
        with pytest.raises(ValidationError):
            CaseQueryResult(
                case_query=CaseQuery(case_type_id=uuid4()), case_ids=[]
            )  # type: ignore[call-arg]


class TestCaseCohortLink:
    @pytest.mark.parametrize(
        "cohort_id, cohort_definition_id, expected",
        [
            pytest.param(NULL_ID, NULL_ID, True, id="both-null"),
            pytest.param(uuid4(), NULL_ID, False, id="only-definition-null"),
            pytest.param(NULL_ID, uuid4(), False, id="only-cohort-null"),
            pytest.param(uuid4(), uuid4(), False, id="neither-null"),
        ],
    )
    def test_is_null(self, cohort_id, cohort_definition_id, expected: bool) -> None:
        link = CaseCohortLink(
            case_id=uuid4(),
            cohort_id=cohort_id,
            cohort_definition_id=cohort_definition_id,
        )
        assert link.is_null() is expected

    def test_requires_ids(self) -> None:
        with pytest.raises(ValidationError):
            CaseCohortLink(case_id=uuid4())  # type: ignore[call-arg]


class TestRefDataAccess:
    def test_defaults_are_independent_empty_sets(self) -> None:
        first = RefDataAccess(user_id=None, is_full_access=False)
        second = RefDataAccess(user_id=uuid4(), is_full_access=False)
        for _, attr in REF_FILTER_METHODS:
            assert getattr(first, attr) == set()
        first.case_type_ids.add(uuid4())
        assert second.case_type_ids == set()

    def test_requires_user_id_and_full_access(self) -> None:
        with pytest.raises(ValidationError):
            RefDataAccess(is_full_access=False)  # type: ignore[call-arg]
        with pytest.raises(ValidationError):
            RefDataAccess(user_id=None)  # type: ignore[call-arg]

    @pytest.mark.parametrize("method, attr", REF_FILTER_METHODS)
    def test_full_access_returns_none(self, method: str, attr: str) -> None:
        access = RefDataAccess(
            user_id=uuid4(), is_full_access=True, **{attr: {uuid4()}}
        )
        assert getattr(access, method)("field") is None

    @pytest.mark.parametrize("method, attr", REF_FILTER_METHODS)
    def test_restricted_returns_member_filter(self, method: str, attr: str) -> None:
        members = {uuid4(), uuid4()}
        access = RefDataAccess(user_id=uuid4(), is_full_access=False, **{attr: members})
        result = getattr(access, method)("field")
        assert isinstance(result, UuidSetFilter)
        assert result.key == "field"
        assert result.members == members

    @pytest.mark.parametrize("method", [m for m, _ in REF_FILTER_METHODS])
    def test_restricted_empty_members_matches_nothing(self, method: str) -> None:
        access = RefDataAccess(user_id=None, is_full_access=False)
        result = getattr(access, method)("field")
        assert isinstance(result, UuidSetFilter)
        assert result.members == frozenset()

    def test_each_method_uses_its_own_member_set(self) -> None:
        values = {attr: {uuid4()} for _, attr in REF_FILTER_METHODS}
        access = RefDataAccess(user_id=None, is_full_access=False, **values)
        for method, attr in REF_FILTER_METHODS:
            assert getattr(access, method)("f").members == values[attr]


class TestSimilarCase:
    def test_valid(self) -> None:
        case_id = uuid4()
        similar = SimilarCase(id=case_id, timed_at=NOW)
        assert similar.id == case_id
        assert similar.timed_at == NOW

    @pytest.mark.parametrize(
        "kwargs",
        [
            pytest.param({"id": uuid4()}, id="missing-timed-at"),
            pytest.param({"timed_at": NOW}, id="missing-id"),
            pytest.param({"id": uuid4(), "timed_at": None}, id="none-timed-at"),
            pytest.param({"id": "not-a-uuid", "timed_at": NOW}, id="bad-id"),
        ],
    )
    def test_invalid(self, kwargs: dict) -> None:
        with pytest.raises(ValidationError):
            SimilarCase(**kwargs)

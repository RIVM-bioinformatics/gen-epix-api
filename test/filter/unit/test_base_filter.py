from typing import Any, Iterable, Iterator, List, Set, Tuple
from unittest import TestCase

import pytest
from pydantic import BaseModel

from gen_epix.filter.base import Filter, TypedFilter
from gen_epix.filter.enum import FilterType


class EqualsFilter(Filter):
    """Concrete filter for testing equality matching."""

    expected: Any | None = None

    def _match(self, value: Any) -> bool:  # type: ignore[override]
        return value == self.expected


class AlwaysTrueFilter(Filter):
    """Concrete filter that matches any non-None value."""

    def _match(self, value: Any) -> bool:  # type: ignore[override]
        return True


class CompositeFilter(Filter):
    """Concrete composite filter to validate is_composite property."""

    _is_composite: bool = True

    def _match(self, value: Any) -> bool:  # type: ignore[override]
        return True


class TypedTrueFilter(TypedFilter):
    """Concrete typed filter that matches any non-None value."""

    def _match(self, value: Any) -> bool:  # type: ignore[override]
        return True


class RowModel(BaseModel):
    a: Any | None = None
    b: Any | None = None


class BaseFilterTestCase(TestCase):
    """Base test case with common fixtures and utilities for Filter tests."""

    def setUp(self) -> None:
        self.true_filter = AlwaysTrueFilter()
        self.eq_filter = EqualsFilter(expected="x")
        self.composite_filter = CompositeFilter()
        self.typed_true_filter = TypedTrueFilter(
            type=FilterType.BASE.value,
        )

    def make_rows_dict(
        self, values: List[Tuple[str, Any | None]]
    ) -> List[dict[str, Any | None]]:
        rows: List[dict[str, Any | None]] = [{k: v} for k, v in values]
        return rows

    def make_rows_model(self, values: List[Tuple[str, Any | None]]) -> List[RowModel]:
        rows: List[RowModel] = [RowModel(**{k: v}) for k, v in values]
        return rows

    def collect(self, it: Iterable[Any]) -> List[Any]:
        return list(it)


@pytest.mark.scenario_ids("TC-SEC-28-07")
class TestValueMatching(BaseFilterTestCase):
    """Test scenarios related to value matching with match_value."""

    def test_match_value_basic_invert(self) -> None:
        # 1. Input
        value: Any = "x"
        invert: bool = True

        # 2. Mocks/config
        self.eq_filter.invert = True

        # 3. Execute
        result: bool = self.eq_filter.match_value(value)

        # 4. Verify
        assert result is (not invert)

    def test_match_value_basic(self) -> None:
        # 1. Input
        value: Any = "x"
        invert: bool = False

        # 2. Mocks/config
        self.eq_filter.invert = invert

        # 3. Execute
        result: bool = self.eq_filter.match_value(value)

        # 4. Verify
        assert result is (not invert)

    def test_match_value_with_map_fn(self) -> None:
        # 1. Input
        value: Any = "X"

        # 2. Mocks/config
        map_fn = lambda v: str(v).lower()

        # 3. Execute
        result: bool = self.eq_filter.match_value(value, map_fn=map_fn)

        # 4. Verify
        assert result is True

    def test_match_value_with_na_values(self) -> None:
        # 1. Input
        value: Any = None
        na_values: Set[Any] = {None}

        # 2. Mocks/config
        self.true_filter.invert = False

        # 3. Execute
        result: bool = self.true_filter.match_value(value, na_values=na_values)

        # 4. Verify
        assert result is False


@pytest.mark.scenario_ids("TC-SEC-28-07")
class TestColumnMatching(BaseFilterTestCase):
    """Test scenarios related to column matching and filtering."""

    def test_match_column_without_na_values_invert(self) -> None:
        # 1. Input
        values: List[Any | None] = ["x", "y", None, "x"]
        invert: bool = True

        # 2. Mocks/config
        self.eq_filter.invert = invert

        # 3. Execute
        results: List[bool] = list(self.eq_filter.match_column(values))

        # 4. Verify
        assert results == (
            [True, False, False, True] if not invert else [False, True, True, False]
        )

    def test_match_column_without_na_values(self) -> None:
        # 1. Input
        values: List[Any | None] = ["x", "y", None, "x"]
        invert: bool = False

        # 2. Mocks/config
        self.eq_filter.invert = invert

        # 3. Execute
        results: List[bool] = list(self.eq_filter.match_column(values))

        # 4. Verify
        assert results == (
            [True, False, False, True] if not invert else [False, True, True, False]
        )

    def test_match_column_with_na_values_branch_behavior(self) -> None:
        # 1. Input
        values: List[Any | None] = ["x", None, "y"]
        na_values: Set[Any] = {None}

        # 2. Mocks/config
        # Note: match_column ignores _match when na_values provided
        self.eq_filter.invert = False

        # 3. Execute
        results: List[bool] = list(
            self.eq_filter.match_column(values, na_values=na_values)
        )

        # 4. Verify (True when value not in na_values)
        assert results == [True, False, True]

    def test_filter_column_without_na_values(self) -> None:
        # 1. Input
        values: List[Any | None] = ["x", "y", None, "x", "z"]

        # 2. Mocks/config
        self.eq_filter.invert = False

        # 3. Execute
        matched_values: List[Any | None] = list(self.eq_filter.filter_column(values))

        # 4. Verify
        assert matched_values == ["x", "x"]

    def test_filter_column_with_na_values_branch_behavior(self) -> None:
        # 1. Input
        values: List[Any | None] = ["x", None, "y", None]
        na_values: Set[Any] = {None}

        # 2. Mocks/config
        self.eq_filter.invert = False

        # 3. Execute
        matched_values: List[Any | None] = list(
            self.eq_filter.filter_column(values, na_values=na_values)
        )

        # 4. Verify (returns values not in na_values)
        assert matched_values == ["x", "y"]


@pytest.mark.scenario_ids("TC-SEC-28-07")
class TestRowMatching(BaseFilterTestCase):
    """Test scenarios related to single row matching with match_row."""

    def test_match_row_dict_happy_path(self) -> None:
        # 1. Input
        row: dict[str, Any | None] = {"a": "x", "b": "y"}

        # 2. Mocks/config
        self.eq_filter.set_key("a")

        # 3. Execute
        result: bool = self.eq_filter.match_row(row)

        # 4. Verify
        assert result is True

    def test_match_row_model_happy_path(self) -> None:
        # 1. Input
        row: RowModel = RowModel(a="x", b="y")

        # 2. Mocks/config
        self.eq_filter.set_key("a")

        # 3. Execute
        result: bool = self.eq_filter.match_row(row, is_model=True)

        # 4. Verify
        assert result is True

    def test_match_row_missing_key_or_none_value(self) -> None:
        # 1. Input
        row1: dict[str, Any | None] = {"b": "y"}
        row2: dict[str, Any | None] = {"a": None}

        # 2. Mocks/config
        self.eq_filter.set_key("a")

        # 3. Execute
        result1: bool = self.eq_filter.match_row(row1)
        result2: bool = self.eq_filter.match_row(row2)

        # 4. Verify
        assert result1 is False
        assert result2 is False

    def test_match_row_with_na_values_provided(self) -> None:
        # 1. Input
        row: dict[str, Any | None] = {"a": None}
        na_values: Set[Any] = {None}

        # 2. Mocks/config
        self.true_filter.set_key("a")

        # 3. Execute
        result: bool = self.true_filter.match_row(row, na_values=na_values)

        # 4. Verify
        assert result is False

    def test_match_row_raises_when_key_not_set(self) -> None:
        # 1. Input
        row: dict[str, Any | None] = {"a": "x"}

        # 2. Mocks/config
        self.true_filter.key = None

        # 3. Execute / 4. Verify
        with pytest.raises(ValueError):
            self.true_filter.match_row(row)


@pytest.mark.scenario_ids("TC-SEC-28-07")
class TestRowsMatching(BaseFilterTestCase):
    """Test scenarios related to multiple rows matching with match_rows."""

    def test_match_rows_dict_without_na_values(self) -> None:
        # 1. Input
        rows: List[dict[str, Any | None]] = self.make_rows_dict(
            [
                ("a", "x"),
                ("a", None),
                ("b", "y"),
                ("a", "x"),
            ]
        )

        # 2. Mocks/config
        self.eq_filter.set_key("a")

        # 3. Execute
        results: List[bool] = list(self.eq_filter.match_rows(rows))

        # 4. Verify
        assert results == [True, False, False, True]

    def test_match_rows_dict_with_na_values_branch(self) -> None:
        # 1. Input
        rows: List[dict[str, Any | None]] = self.make_rows_dict(
            [
                ("a", "x"),
                ("a", None),
                ("a", "y"),
            ]
        )
        na_values: Set[Any] = {None}

        # 2. Mocks/config
        self.true_filter.set_key("a")

        # 3. Execute
        results: List[bool] = list(
            self.true_filter.match_rows(rows, na_values=na_values)
        )

        # 4. Verify
        assert results == [True, False, True]

    def test_match_rows_model_without_na_values(self) -> None:
        # 1. Input
        rows: List[RowModel] = self.make_rows_model(
            [
                ("a", "x"),
                ("a", None),
                ("b", "y"),
            ]
        )

        # 2. Mocks/config
        self.eq_filter.set_key("a")

        # 3. Execute
        results: List[bool] = list(self.eq_filter.match_rows(rows, is_model=True))

        # 4. Verify
        assert results == [True, False, False]

    def test_match_rows_raises_when_key_not_set(self) -> None:
        # 1. Input
        rows: List[dict[str, Any | None]] = self.make_rows_dict([("a", "x")])

        # 2. Mocks/config
        self.true_filter.key = None

        # 3. Execute / 4. Verify
        with pytest.raises(ValueError):
            list(self.true_filter.match_rows(rows))


@pytest.mark.scenario_ids("TC-SEC-28-07")
class TestFilterRows(BaseFilterTestCase):
    """Test scenarios related to filtering rows (filter_rows)."""

    def test_filter_rows_dict_without_na_values(self) -> None:
        # 1. Input
        rows: List[dict[str, Any | None]] = self.make_rows_dict(
            [
                ("a", "x"),
                ("a", None),
                ("b", "x"),
                ("a", "x"),
            ]
        )

        # 2. Mocks/config
        self.eq_filter.set_key("a")

        # 3. Execute
        filtered: List[dict[str, Any | None]] = list(self.eq_filter.filter_rows(rows))

        # 4. Verify
        assert filtered == [{"a": "x"}, {"a": "x"}]

    def test_filter_rows_dict_with_na_values_branch(self) -> None:
        # 1. Input
        rows: List[dict[str, Any | None]] = self.make_rows_dict(
            [
                ("a", "x"),
                ("a", None),
                ("a", "y"),
            ]
        )
        na_values: Set[Any] = {None}

        # 2. Mocks/config
        self.true_filter.set_key("a")

        # 3. Execute
        filtered: List[dict[str, Any | None]] = list(
            self.true_filter.filter_rows(rows, na_values=na_values)
        )

        # 4. Verify
        assert filtered == [{"a": "x"}, {"a": "y"}]

    def test_filter_rows_model_without_na_values(self) -> None:
        # 1. Input
        rows: List[RowModel] = self.make_rows_model(
            [
                ("a", "x"),
                ("a", None),
                ("b", "y"),
                ("a", "x"),
            ]
        )

        # 2. Mocks/config
        self.eq_filter.set_key("a")

        # 3. Execute
        filtered: List[RowModel] = list(self.eq_filter.filter_rows(rows, is_model=True))

        # 4. Verify
        assert filtered == [RowModel(a="x"), RowModel(a="x")]

    def test_filter_rows_raises_when_key_not_set(self) -> None:
        # 1. Input
        rows: List[dict[str, Any | None]] = self.make_rows_dict([("a", "x")])

        # 2. Mocks/config
        self.true_filter.key = None

        # 3. Execute / 4. Verify
        with pytest.raises(ValueError):
            list(self.true_filter.filter_rows(rows))


@pytest.mark.scenario_ids("TC-SEC-28-07")
class TestKeyMethods(BaseFilterTestCase):
    """Test scenarios related to key setters and getters."""

    def test_set_key_direct_and_get_key(self) -> None:
        # 1. Input
        key_value: str = "a"

        # 2. Mocks/config
        # none

        # 3. Execute
        self.true_filter.set_key(key_value)
        ret_key: Any = self.true_filter.get_key()

        # 4. Verify
        assert ret_key == key_value

    def test_set_key_callable_mapper(self) -> None:
        # 1. Input
        mapper = lambda k: "b" if k == "a" else "c"

        # 2. Mocks/config
        self.true_filter.set_key("a")

        # 3. Execute
        self.true_filter.set_key(mapper)
        ret_key: Any = self.true_filter.get_key()

        # 4. Verify
        assert ret_key == "b"


@pytest.mark.scenario_ids("TC-SEC-28-07")
class TestCallMethod(BaseFilterTestCase):
    """Test scenarios related to the __call__ method delegation and errors."""

    def test_call_axis_0_filters_rows(self) -> None:
        # 1. Input
        rows: List[dict[str, Any | None]] = self.make_rows_dict(
            [
                ("a", "x"),
                ("a", None),
                ("a", "x"),
            ]
        )

        # 2. Mocks/config
        self.eq_filter.set_key("a")

        # 3. Execute
        result_iter: Iterator[Any] = self.eq_filter(rows, axis=0)
        result: List[Any] = list(result_iter)

        # 4. Verify
        assert result == [{"a": "x"}, {"a": "x"}]

    def test_call_axis_1_filters_column(self) -> None:
        # 1. Input
        values: List[Any | None] = ["x", None, "x", "y"]

        # 2. Mocks/config
        self.eq_filter.invert = False

        # 3. Execute
        result_iter: Iterator[Any] = self.eq_filter(values, axis=1)
        result: List[Any] = list(result_iter)

        # 4. Verify
        assert result == ["x", "x"]

    def test_call_invalid_axis_raises(self) -> None:
        # 1. Input
        values: List[Any | None] = ["x", None]

        # 2. Mocks/config
        # none

        # 3. Execute / 4. Verify
        with pytest.raises(ValueError):
            list(self.eq_filter(values, axis=2))


@pytest.mark.scenario_ids("TC-SEC-28-07")
class TestCompositeAndTypedFilter(BaseFilterTestCase):
    """Test scenarios related to composite filters and typed filters."""

    def test_is_composite_property(self) -> None:
        # 1. Input
        # none

        # 2. Mocks/config
        # none

        # 3. Execute
        default_is_composite: bool = self.true_filter.is_composite
        composite_is_composite: bool = self.composite_filter.is_composite

        # 4. Verify
        assert default_is_composite is False
        assert composite_is_composite is True

    def test_typed_filter_literal_type(self) -> None:
        # 1. Input
        # none

        # 2. Mocks/config
        # none

        # 3. Execute
        literal_type: str = self.typed_true_filter.type

        # 4. Verify
        assert literal_type == FilterType.BASE.value

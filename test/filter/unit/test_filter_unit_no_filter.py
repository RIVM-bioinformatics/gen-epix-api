"""Unit tests for NoFilter."""

from collections.abc import Hashable
from typing import Any

import pytest
from pydantic import BaseModel

from gen_epix.filter import NoFilter


class FilterRow(BaseModel):
    """Represent a simple model row for row-filter checks."""

    value: Any | None = None


@pytest.mark.parametrize(
    ("invert", "expected"),
    [(False, True), (True, False)],
)
def test_no_filter_matches_values_and_columns(invert: bool, expected: bool) -> None:
    """Match every scalar and column value unless the filter is inverted."""
    filter_obj = NoFilter(invert=invert)
    values = [None, "value", 0]

    assert [filter_obj.match_value(value, na_values={None}) for value in values] == [
        expected
    ] * len(values)
    assert list(filter_obj.match_column(values, na_values={None})) == [expected] * len(
        values
    )


@pytest.mark.parametrize(
    ("invert", "expected"),
    [(False, [None, "value", 0]), (True, [])],
)
def test_no_filter_filters_columns(invert: bool, expected: list[Any]) -> None:
    """Retain all column values unless the filter is inverted."""
    values = iter([None, "value", 0])

    assert list(NoFilter(invert=invert).filter_column(values)) == expected


@pytest.mark.parametrize(
    ("invert", "expected"),
    [(False, True), (True, False)],
)
def test_no_filter_matches_mapping_and_model_rows(invert: bool, expected: bool) -> None:
    """Match rows independently of row shape, contents, and NA values."""
    filter_obj = NoFilter(invert=invert)
    mapping_row: dict[Hashable, Any | None] = {"value": None}
    model_row = FilterRow(value="present")

    assert filter_obj.match_row(mapping_row, na_values={None}) is expected
    assert filter_obj.match_row(model_row, is_model=True) is expected
    assert list(filter_obj.match_rows([mapping_row], na_values={None})) == [expected]
    assert list(filter_obj.match_rows([model_row], is_model=True)) == [expected]


@pytest.mark.parametrize(
    ("invert", "expected_length"),
    [(False, 1), (True, 0)],
)
def test_no_filter_filters_mapping_and_model_rows(
    invert: bool, expected_length: int
) -> None:
    """Retain both mapping and model rows unless the filter is inverted."""
    mapping_row: dict[Hashable, Any | None] = {"value": None}
    model_row = FilterRow(value="present")

    filtered_mappings = list(
        NoFilter(invert=invert).filter_rows([mapping_row], na_values={None})
    )
    filtered_models = list(
        NoFilter(invert=invert).filter_rows([model_row], is_model=True)
    )

    assert len(filtered_mappings) == expected_length
    assert len(filtered_models) == expected_length
    if not invert:
        assert filtered_mappings == [mapping_row]
        assert filtered_models == [model_row]


def test_no_filter_empty_inputs_yield_empty_results() -> None:
    """Return empty results for empty inputs, including when inverted."""
    for invert in (False, True):
        filter_obj = NoFilter(invert=invert)

        assert list(filter_obj.match_column([])) == []
        assert list(filter_obj.filter_column([])) == []
        assert list(filter_obj.match_rows([])) == []
        assert list(filter_obj.filter_rows([])) == []

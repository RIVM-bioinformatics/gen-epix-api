"""Tests for EqualsStringFilter matching."""

import pytest
from test.filter.unit import util

from gen_epix.filter.equals_string import EqualsStringFilter


@pytest.mark.parametrize(
    ("filter_value", "values", "expected"),
    [
        pytest.param(
            "alpha",
            ["alpha", "Alpha", "beta", "", None],
            [True, False, False, False, False],
            id="exact-and-case-sensitive",
        ),
        pytest.param(
            "",
            ["", "alpha", None],
            [True, False, False],
            id="empty-string",
        ),
    ],
)
def test_equals_string_filter_matches_exact_values(
    filter_value: str,
    values: list[str | None],
    expected: list[bool],
) -> None:
    """Match only values equal to the configured string."""
    filter_obj = EqualsStringFilter(key="value", value=filter_value)
    rows = [{"value": value} for value in values]

    util.validate_filter_behavior(filter_obj, rows, expected)
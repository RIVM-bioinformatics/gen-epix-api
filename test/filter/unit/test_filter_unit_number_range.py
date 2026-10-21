"""Tests for NumberRangeFilter matching."""

from decimal import Decimal
from test.filter.unit import util

import pytest

from gen_epix.filter.number_range import NumberRangeFilter


@pytest.mark.parametrize(
    ("lower_censor", "upper_censor", "expected"),
    [
        (">=", "<", [False, True, True, False, False]),
        (">", "<", [False, False, True, False, False]),
        (">=", "<=", [False, True, True, True, False]),
        (">", "<=", [False, False, True, True, False]),
    ],
)
def test_number_range_matches_censor_operators(
    lower_censor: str,
    upper_censor: str,
    expected: list[bool],
) -> None:
    """Apply all supported inclusive and exclusive numeric bounds."""
    range_filter = NumberRangeFilter(
        lower_bound=10,
        upper_bound=20,
        lower_bound_censor=lower_censor,
        upper_bound_censor=upper_censor,
        key="a",
    )
    rows = [{"a": value} for value in [5, 10, 15, 20, 25]]

    util.validate_filter_behavior(range_filter, rows, expected)


@pytest.mark.parametrize(
    ("lower_censor", "upper_censor", "expected"),
    [
        (">=", "<", [False, True, True, False, False]),
        (">", "<", [False, False, True, False, False]),
        (">=", "<=", [False, True, True, True, False]),
        (">", "<=", [False, False, True, True, False]),
    ],
)
def test_number_range_map_function_converts_numeric_strings(
    lower_censor: str,
    upper_censor: str,
    expected: list[bool],
) -> None:
    """Convert numeric strings before checking range boundaries."""
    range_filter = NumberRangeFilter(
        lower_bound=10,
        upper_bound=20,
        lower_bound_censor=lower_censor,
        upper_bound_censor=upper_censor,
        key="a",
    )
    rows = [{"a": value} for value in ["5", "10.0", 15.5, "20", Decimal(25)]]
    map_fn = lambda value: float(value) if isinstance(value, str) else value

    util.validate_filter_behavior(range_filter, rows, expected, map_fn=map_fn)


def test_number_range_construction_and_validation() -> None:
    """Coerce supported numeric bounds and reject invalid range settings."""
    range_filter = NumberRangeFilter(lower_bound=10, upper_bound=20)
    assert range_filter.lower_bound == 10
    assert range_filter.lower_bound_censor.value == ">="
    assert range_filter.upper_bound == 20
    assert range_filter.upper_bound_censor.value == "<"

    with pytest.raises(ValueError):
        range_filter.lower_bound = 0
    with pytest.raises(ValueError):
        range_filter.lower_bound_censor = ">"
    with pytest.raises(ValueError):
        range_filter.upper_bound = 30
    with pytest.raises(ValueError):
        range_filter.upper_bound_censor = "<="

    for lower_bound, upper_bound in [
        (10, 20.5),
        (10.5, 20),
        (10.5, 20.5),
        (10, Decimal("20.5")),
        (Decimal("10.5"), 20),
        (Decimal("10.5"), Decimal("20.5")),
    ]:
        NumberRangeFilter(lower_bound=lower_bound, upper_bound=upper_bound)

    equal_bounds = NumberRangeFilter(
        lower_bound=10,
        upper_bound=10,
        upper_bound_censor="<=",
    )
    assert equal_bounds.lower_bound == equal_bounds.upper_bound == 10

    coerced_bounds = NumberRangeFilter(
        lower_bound="10",
        lower_bound_censor=">",
        upper_bound="20",
        upper_bound_censor="<=",
    )
    assert coerced_bounds.lower_bound == 10
    assert coerced_bounds.lower_bound_censor.value == ">"
    assert coerced_bounds.upper_bound == 20
    assert coerced_bounds.upper_bound_censor.value == "<="

    with pytest.raises(ValueError):
        NumberRangeFilter(lower_bound=10, upper_bound=10)
    with pytest.raises(ValueError):
        NumberRangeFilter(lower_bound=20, upper_bound=10)
    with pytest.raises(ValueError):
        NumberRangeFilter(lower_bound=10, lower_bound_censor="=", upper_bound=20)
    with pytest.raises(ValueError):
        NumberRangeFilter(lower_bound=10, upper_bound=20, upper_bound_censor="=")

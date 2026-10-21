"""Tests for scalar range validation and matching."""

import pytest
from pydantic import ValidationError

from gen_epix.filter.range import RangeFilter


@pytest.mark.parametrize(
    ("lower_censor", "upper_censor", "expected"),
    [
        (">=", "<", [False, True, True, False]),
        (">=", "<=", [False, True, True, True]),
        (">", "<", [False, False, True, False]),
        (">", "<=", [False, False, True, True]),
    ],
)
def test_bounded_range_matches_configured_censor_operators(
    lower_censor: str,
    upper_censor: str,
    expected: list[bool],
) -> None:
    """Apply each supported combination of inclusive and exclusive bounds."""
    range_filter = RangeFilter(
        key="value",
        lower_bound=10,
        upper_bound=20,
        lower_bound_censor=lower_censor,
        upper_bound_censor=upper_censor,
    )

    assert [range_filter.match_value(value) for value in (9, 10, 15, 20)] == expected


def test_one_sided_ranges_and_equal_inclusive_bounds() -> None:
    """Support lower-only, upper-only, and equal inclusive bounds."""
    lower = RangeFilter(key="value", lower_bound=10)
    upper = RangeFilter(key="value", upper_bound=20)
    equal = RangeFilter(
        key="value",
        lower_bound=10,
        upper_bound=10,
        upper_bound_censor="<=",
    )

    assert not lower.match_value(9)
    assert lower.match_value(10)
    assert upper.match_value(19)
    assert not upper.match_value(20)
    assert equal.match_value(10)
    assert not equal.match_value(11)


@pytest.mark.parametrize(
    "settings",
    [
        {},
        {"lower_bound": 10, "upper_bound": 10},
        {"lower_bound": 20, "upper_bound": 10},
        {"lower_bound": 10, "lower_bound_censor": "<"},
        {"upper_bound": 10, "upper_bound_censor": ">"},
    ],
)
def test_invalid_range_settings_raise_validation_error(
    settings: dict[str, object],
) -> None:
    """Reject missing, reversed, and incompatible range boundaries."""
    with pytest.raises(ValidationError):
        RangeFilter(key="value", **settings)  # type: ignore[arg-type]

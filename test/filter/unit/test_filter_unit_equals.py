"""Verify EqualsFilter's public scalar matching behavior."""

import pytest

from gen_epix.filter.equals import EqualsFilter


@pytest.mark.parametrize(
    ("configured_value", "candidate", "expected"),
    [
        ("alpha", "alpha", True),
        ("alpha", "beta", False),
        ("", "", True),
        ("", "alpha", False),
        (0, 0, True),
        (-4, -4, True),
        (12, 12, True),
        (12, 13, False),
        (12, "12", False),
        (None, "alpha", False),
        ([1, 2], [1, 2], True),
        ([1, 2], [2, 1], False),
    ],
    ids=[
        "equal-string",
        "unequal-string",
        "equal-empty-string",
        "unequal-empty-string",
        "equal-zero",
        "equal-negative-integer",
        "equal-integer",
        "unequal-integer",
        "different-types",
        "none-configured-value",
        "equal-list",
        "unequal-list",
    ],
)
def test_match_compares_candidate_with_configured_value(
    configured_value, candidate, expected
):
    """Match candidates according to generic Python equality."""
    filter_ = EqualsFilter(value=configured_value)

    assert filter_.match_value(candidate) is expected


def test_match_uses_none_when_value_is_omitted():
    """Default the configured equality value to None."""
    filter_ = EqualsFilter()

    assert filter_.value is None

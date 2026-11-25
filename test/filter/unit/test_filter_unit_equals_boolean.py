"""Verify strict candidate matching for boolean equality filters."""

import pytest

from gen_epix.filter.equals_boolean import EqualsBooleanFilter


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [(True, True), (False, False), (1, False), (0, False), ("True", False)],
)
def test_equals_boolean_matches_only_boolean_candidates(
    candidate: object, expected: bool
) -> None:
    """Do not let integers or strings match a configured boolean."""
    filter_ = EqualsBooleanFilter(value=True)

    assert filter_.match_value(candidate) is expected

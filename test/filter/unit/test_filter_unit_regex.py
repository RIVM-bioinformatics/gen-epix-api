"""Tests for RegexFilter validation and matching."""

import pytest
from pydantic import ValidationError

from gen_epix.filter.regex import RegexFilter


@pytest.mark.parametrize(
    ("pattern", "matching_value", "nonmatching_value"),
    [
        ("^[A-Za-z]+$", "letters", "letters123"),
        ("^[0-9]+$", "12345", "12345x"),
    ],
)
def test_regex_compiles_and_matches_values(
    pattern: str,
    matching_value: str,
    nonmatching_value: str,
) -> None:
    """Compile configured patterns and match complete strings as anchored."""
    regex_filter = RegexFilter(pattern=pattern)

    assert regex_filter.pattern == pattern
    assert regex_filter.match_value(matching_value)
    assert not regex_filter.match_value(nonmatching_value)


def test_regex_rejects_invalid_pattern() -> None:
    """Reject a pattern that Python's regular-expression compiler cannot parse."""
    with pytest.raises(ValidationError, match="Invalid regular expression"):
        RegexFilter(pattern="[")

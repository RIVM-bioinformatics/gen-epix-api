"""Verify complete matching for shared ISO-like date literals."""

import pytest

from gen_epix.commondb.domain.literal import ISODATE_PATTERN


@pytest.mark.parametrize(
    "value", ["2024", "2024-06", "2024-06-15", "2024-Q2", "2024-W23"]
)
def test_isodate_pattern_matches_supported_values(value: str) -> None:
    """Accept supported ISO-like year, month, day, quarter, and week values."""
    assert ISODATE_PATTERN.match(value) is not None


@pytest.mark.parametrize("value", ["2024-06junk", "junk2024", "2024-Q5", "2024-W54"])
def test_isodate_pattern_rejects_values_with_invalid_suffixes(value: str) -> None:
    """Reject invalid values even when a valid date prefix is present."""
    assert ISODATE_PATTERN.match(value) is None

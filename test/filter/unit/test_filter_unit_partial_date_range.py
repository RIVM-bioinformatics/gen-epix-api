"""Tests for partial-date range validation."""

import pytest
from pydantic import ValidationError

from gen_epix.filter.partial_date_range import PartialDateRangeFilter


def test_invalid_quarter_bound_raises_validation_error() -> None:
    """Reject quarter bounds outside Q1 through Q4."""
    with pytest.raises(ValidationError, match="Invalid partial-date quarter: 2022-Q5"):
        PartialDateRangeFilter(key="date", lower_bound="2022-Q5")

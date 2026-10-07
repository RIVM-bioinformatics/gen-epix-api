"""Tests for partial-date range validation."""

from test.filter.unit import util

import pytest
from pydantic import ValidationError

from gen_epix.filter.partial_date_range import PartialDateRangeFilter


def test_invalid_quarter_bound_raises_validation_error() -> None:
    """Reject quarter bounds outside Q1 through Q4."""
    with pytest.raises(ValidationError, match="Invalid partial-date quarter: 2022-Q5"):
        PartialDateRangeFilter(key="date", lower_bound="2022-Q5")


def test_partial_date_range_matches_supported_precisions() -> None:
    """Match partial dates consistently across year through day precision."""
    fixed_args = {
        "lower_bound": "2022-01",
        "upper_bound": "2022-03",
        "key": "a",
    }
    precision_cases = [
        (
            ["2021", "2022", "2023"],
            [[False, False, False]] * 4,
        ),
        (
            ["2021-Q4", "2022-Q1", "2022-Q2"],
            [
                [False, False, False],
                [False, False, False],
                [False, True, False],
                [False, False, False],
            ],
        ),
        (
            ["2021-12", "2022-01", "2022-02", "2022-03", "2022-04"],
            [
                [False, True, True, False, False],
                [False, False, True, False, False],
                [False, True, True, True, False],
                [False, False, True, True, False],
            ],
        ),
        (
            [
                "2021-W52",
                "2022-W01",
                "2022-W05",
                "2022-W06",
                "2022-W09",
                "2022-W12",
                "2022-W13",
            ],
            [
                [False, True, True, True, False, False, False],
                [False, False, False, True, False, False, False],
                [False, True, True, True, True, True, False],
                [False, False, False, True, True, True, False],
            ],
        ),
        (
            [
                "2021-12-31",
                "2022-01-01",
                "2022-01-31",
                "2022-02-01",
                "2022-02-28",
                "2022-03-01",
                "2022-04-01",
            ],
            [
                [False, True, True, True, True, False, False],
                [False, False, False, True, True, False, False],
                [False, True, True, True, True, True, False],
                [False, False, False, True, True, True, False],
            ],
        ),
    ]
    censor_pairs = [
        (None, None),
        (">", None),
        (None, "<="),
        (">", "<="),
    ]

    for values, expected_by_censor in precision_cases:
        rows = [{"a": value} for value in values]
        for (lower_censor, upper_censor), expected in zip(
            censor_pairs, expected_by_censor
        ):
            filter_args = dict(fixed_args)
            if lower_censor is not None:
                filter_args["lower_bound_censor"] = lower_censor
            if upper_censor is not None:
                filter_args["upper_bound_censor"] = upper_censor
            util.validate_filter_behavior(
                PartialDateRangeFilter(**filter_args), rows, expected
            )

"""Tests for partial-date range validation."""

from datetime import datetime
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


@pytest.mark.parametrize(
    ("value", "expected_lower", "expected_upper"),
    [
        ("2022", datetime(2022, 1, 1), datetime(2023, 1, 1)),
        ("2022-Q1", datetime(2022, 1, 1), datetime(2022, 4, 1)),
        ("2022-Q2", datetime(2022, 4, 1), datetime(2022, 7, 1)),
        ("2022-Q3", datetime(2022, 7, 1), datetime(2022, 10, 1)),
        ("2022-Q4", datetime(2022, 10, 1), datetime(2023, 1, 1)),
        ("2022-02", datetime(2022, 2, 1), datetime(2022, 3, 1)),
        ("2022-W01", datetime(2022, 1, 3), datetime(2022, 1, 10)),
        ("20220201", datetime(2022, 2, 1), datetime(2022, 2, 2)),
        ("2022-02-01", datetime(2022, 2, 1), datetime(2022, 2, 2)),
        ("2022-02-01T04", datetime(2022, 2, 1, 4), datetime(2022, 2, 1, 5)),
        (
            "2022-02-01T04:05",
            datetime(2022, 2, 1, 4, 5),
            datetime(2022, 2, 1, 4, 6),
        ),
        (
            "2022-02-01T04:05:06",
            datetime(2022, 2, 1, 4, 5, 6),
            datetime(2022, 2, 1, 4, 5, 7),
        ),
        (
            "2022-02-01T04:05:06.123456",
            datetime(2022, 2, 1, 4, 5, 6, 123456),
            datetime(2022, 2, 1, 4, 5, 7, 123456),
        ),
    ],
)
def test_datetime_bounds_cover_supported_iso_precisions(
    value: str, expected_lower: datetime, expected_upper: datetime
) -> None:
    assert PartialDateRangeFilter._get_datetime_bounds(value) == (
        expected_lower,
        expected_upper,
    )


@pytest.mark.parametrize(
    ("bound_args", "values", "expected"),
    [
        (
            {"lower_bound": "2022-02"},
            ["2022-01-31", "2022-02-01", "2022-02-28", "2022-03-01"],
            [False, True, True, True],
        ),
        (
            {"lower_bound": "2022-02", "lower_bound_censor": ">"},
            ["2022-01-31", "2022-02-01", "2022-02-28", "2022-03-01"],
            [False, False, False, True],
        ),
        (
            {"upper_bound": "2022-02"},
            ["2022-01-31", "2022-02-01", "2022-02-28", "2022-03-01"],
            [True, False, False, False],
        ),
        (
            {"upper_bound": "2022-02", "upper_bound_censor": "<="},
            ["2022-01-31", "2022-02-01", "2022-02-28", "2022-03-01"],
            [True, True, True, False],
        ),
    ],
    ids=["lower-inclusive", "lower-exclusive", "upper-exclusive", "upper-inclusive"],
)
def test_one_sided_partial_date_range_matchers(
    bound_args: dict[str, str], values: list[str], expected: list[bool]
) -> None:
    rows = [{"date": value} for value in values]
    filter_ = PartialDateRangeFilter(key="date", **bound_args)

    util.validate_filter_behavior(filter_, rows, expected)


@pytest.mark.parametrize(
    "bound_args",
    [
        {"lower_bound": "2023-01", "upper_bound": "2022-12"},
        {"lower_bound": "2022-01", "lower_bound_censor": "<"},
        {"upper_bound": "2022-01", "upper_bound_censor": ">"},
        {"lower_bound": "2022-01", "upper_bound": "2022-01"},
        {},
    ],
    ids=[
        "reversed",
        "invalid-lower-censor",
        "invalid-upper-censor",
        "equal-exclusive",
        "missing-bounds",
    ],
)
def test_invalid_partial_date_range_settings_are_rejected(
    bound_args: dict[str, str],
) -> None:
    with pytest.raises(ValidationError):
        PartialDateRangeFilter(key="date", **bound_args)


def test_equal_inclusive_partial_date_bounds_match_the_bound_period() -> None:
    filter_ = PartialDateRangeFilter(
        key="date",
        lower_bound="2022-02",
        upper_bound="2022-02",
        lower_bound_censor=">=",
        upper_bound_censor="<=",
    )

    util.validate_filter_behavior(
        filter_,
        [{"date": "2022-02"}, {"date": "2022-01"}, {"date": "2022-03"}],
        [True, False, False],
    )


def test_matcher_rejects_missing_bounds_when_called_directly() -> None:
    filter_ = PartialDateRangeFilter.model_construct(
        key="date", lower_bound=None, upper_bound=None
    )

    with pytest.raises(AssertionError, match="At least one bound must be set"):
        filter_._build_matcher()

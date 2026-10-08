"""Tests for DateRangeFilter matching."""

import datetime
from test.filter.unit import util

from gen_epix.filter.date_range import DateRangeFilter


def test_date_range_match() -> None:
    """Match dates using inclusive and exclusive range boundaries."""
    fixed_args = {
        "lower_bound": datetime.date.fromisoformat("2021-01-01"),
        "upper_bound": datetime.date.fromisoformat("2021-02-01"),
        "key": "a",
    }
    rows = [
        {"a": datetime.date.fromisoformat(value)}
        for value in [
            "2020-12-31",
            "2021-01-01",
            "2021-01-31",
            "2021-02-01",
            "2021-02-02",
        ]
    ]

    util.validate_filter_behavior(
        DateRangeFilter(**fixed_args), rows, [False, True, True, False, False]
    )
    util.validate_filter_behavior(
        DateRangeFilter(lower_bound_censor=">", **fixed_args),
        rows,
        [False, False, True, False, False],
    )
    util.validate_filter_behavior(
        DateRangeFilter(upper_bound_censor="<=", **fixed_args),
        rows,
        [False, True, True, True, False],
    )
    util.validate_filter_behavior(
        DateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        ),
        rows,
        [False, False, True, True, False],
    )


def test_date_range_map_function() -> None:
    """Convert string dates before applying range matching."""
    fixed_args = {
        "lower_bound": datetime.date.fromisoformat("2021-01-01"),
        "upper_bound": datetime.date.fromisoformat("2021-02-01"),
        "key": "a",
    }
    rows = [
        {"a": value}
        for value in [
            "2020-12-31",
            "2021-01-01",
            "2021-01-31",
            "2021-02-01",
            "2021-02-02",
        ]
    ]
    map_fn = lambda value: (
        datetime.date.fromisoformat(value) if isinstance(value, str) else value
    )

    util.validate_filter_behavior(
        DateRangeFilter(**fixed_args),
        rows,
        [False, True, True, False, False],
        map_fn=map_fn,
    )
    util.validate_filter_behavior(
        DateRangeFilter(lower_bound_censor=">", **fixed_args),
        rows,
        [False, False, True, False, False],
        map_fn=map_fn,
    )
    util.validate_filter_behavior(
        DateRangeFilter(upper_bound_censor="<=", **fixed_args),
        rows,
        [False, True, True, True, False],
        map_fn=map_fn,
    )
    util.validate_filter_behavior(
        DateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        ),
        rows,
        [False, False, True, True, False],
        map_fn=map_fn,
    )


def test_date_range_construction_coerces_iso_strings() -> None:
    """Parse ISO date strings into date-valued range bounds."""
    date_filter = DateRangeFilter(
        lower_bound="2022-01-01",
        upper_bound="2022-01-31",
    )

    assert date_filter.lower_bound == datetime.date(2022, 1, 1)
    assert date_filter.upper_bound == datetime.date(2022, 1, 31)

"""Tests for DatetimeRangeFilter timezone-awareness behavior."""

import datetime

import pytest

from gen_epix.filter.datetime_range import DatetimeRangeFilter


@pytest.mark.parametrize(
    ("lower_bound", "upper_bound"),
    [
        (
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 1, 2, tzinfo=datetime.timezone.utc),
        ),
        (
            datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc),
            datetime.datetime(2024, 1, 2),
        ),
    ],
)
def test_datetime_range_rejects_mixed_bound_awareness(
    lower_bound: datetime.datetime, upper_bound: datetime.datetime
) -> None:
    """Reject naive and aware bounds before comparing their order."""
    with pytest.raises(
        ValueError, match="must both be timezone-aware or both be naive"
    ):
        DatetimeRangeFilter(lower_bound=lower_bound, upper_bound=upper_bound)


@pytest.mark.parametrize(
    ("bound", "candidate"),
    [
        (
            datetime.datetime(2024, 1, 1),
            datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc),
        ),
        (
            datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc),
            datetime.datetime(2024, 1, 1),
        ),
    ],
)
def test_datetime_range_rejects_candidate_with_mixed_awareness(
    bound: datetime.datetime, candidate: datetime.datetime
) -> None:
    """Raise a clear error when the candidate and bound differ in awareness."""
    date_filter = DatetimeRangeFilter(lower_bound=bound)

    with pytest.raises(ValueError, match="must have the same timezone awareness"):
        date_filter.match_value(candidate)


def test_datetime_range_compares_aware_values_across_offsets() -> None:
    """Compare aware values by instant even when their UTC offsets differ."""
    date_filter = DatetimeRangeFilter(
        lower_bound=datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc),
        upper_bound=datetime.datetime(2024, 1, 2, tzinfo=datetime.timezone.utc),
    )

    assert date_filter.match_value(
        datetime.datetime(
            2024, 1, 1, 1, tzinfo=datetime.timezone(datetime.timedelta(hours=1))
        )
    )

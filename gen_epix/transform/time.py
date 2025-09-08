import datetime
from typing import Iterable

from gen_epix.transform.enum import TimeUnit


def convert_iso_time_unit(
    src_values: Iterable[str | None],
    src_unit: TimeUnit,
    tgt_unit: TimeUnit,
    from_week_mode: str = "exact",
) -> list[str | None]:
    """
    Convert iso datetime values to another unit.
    """
    if from_week_mode not in {"exact", "round"}:
        raise ValueError(f"Invalid from_week: {from_week_mode}")
    if src_unit == tgt_unit:
        tgt_values = list(src_values)
    elif src_unit == TimeUnit.YEAR:
        # Lowest resolution, nothing to map
        tgt_values = [None for _ in src_values]
    elif src_unit == TimeUnit.QUARTER:
        if tgt_unit == TimeUnit.YEAR:
            tgt_values = [None if x is None else x[0:4] for x in src_values]
        else:
            tgt_values = [None for x in src_values]
    elif src_unit == TimeUnit.MONTH:
        if tgt_unit == TimeUnit.QUARTER:
            tgt_values = [
                None if x is None else x[0:4] + "-Q" + str((int(x[5:7]) + 2) // 3)
                for x in src_values
            ]
        elif tgt_unit == TimeUnit.YEAR:
            tgt_values = [None if x is None else x[0:4] for x in src_values]
        else:
            tgt_values = [None for x in src_values]
    elif src_unit == TimeUnit.WEEK:
        # Weeks that are only partially in a month, quarter or year
        # cannot be mapped with certainty, the rest can.
        # This requires checking if both the start and exclusive end date
        # of the week yield the same lower resolution value
        # If from_week_mode=='round', approximate mapping is used,
        # choosing the time interval in which at least 4
        # (i.e. over half) days of the week fall
        if tgt_unit in {
            TimeUnit.MONTH,
            TimeUnit.QUARTER,
            TimeUnit.YEAR,
        }:
            week_starts = [
                (
                    None
                    if x is None
                    else datetime.date.fromisocalendar(int(x[0:4]), int(x[6:8]), 1)
                )
                for x in src_values
            ]
            if from_week_mode == "exact":
                # No year if end of week lies in the next year
                week_ends = [
                    (
                        None
                        if x is None
                        else datetime.date.fromisocalendar(int(x[0:4]), int(x[6:8]), 7)
                    )
                    for x in src_values
                ]
                week_years = [
                    None if x is None or x.year != y.year else x.year  # type: ignore[union-attr]
                    for x, y in zip(week_starts, week_ends)
                ]
            elif from_week_mode == "round":
                # Last week always has at least 4 days in that year, always use that year
                week_mids = [
                    (
                        None
                        if x is None
                        else datetime.date.fromisocalendar(int(x[0:4]), int(x[6:8]), 4)
                    )
                    for x in src_values
                ]
                week_years = [None if x is None else x.year for x in week_starts]
            else:
                raise NotImplementedError
            if tgt_unit == TimeUnit.YEAR:
                tgt_values = [None if x is None else str(x) for x in week_years]
            elif tgt_unit == TimeUnit.QUARTER:
                if from_week_mode == "exact":
                    # No quarter if end of week lies in the next quarter
                    week_quarters = [
                        (
                            None
                            if x is None
                            else (
                                (x.month + 2) // 3
                                if x.month == y.month or (y.month not in [1, 4, 7, 10])  # type: ignore[union-attr]
                                else None
                            )
                        )
                        for x, y in zip(week_starts, week_ends)  # type: ignore[unbound]
                    ]
                elif from_week_mode == "round":
                    # Choose month in which at least 4 days of the week lie
                    week_quarters = [
                        (
                            None
                            if x is None
                            else (
                                (x.month + 2) // 3
                                if x.month == y.month or (y.month not in [1, 4, 7, 10])  # type: ignore[union-attr]
                                else (y.month + 2) // 3  # type: ignore[union-attr]
                            )
                        )
                        for x, y in zip(week_starts, week_mids)  # type: ignore[unbound]
                    ]
                else:
                    raise NotImplementedError
                tgt_values = [
                    None if y is None else f"{x}-Q{y}"
                    for x, y in zip(week_years, week_quarters)
                ]
            elif tgt_unit == TimeUnit.MONTH:
                if from_week_mode == "exact":
                    # No month if end of week lies in the next month
                    week_months = [
                        None if x is None or x.month != y.month else x.month  # type: ignore[union-attr]
                        for x, y in zip(week_starts, week_ends)  # type: ignore[unbound]
                    ]
                elif from_week_mode == "round":
                    # Choose month in which at least 4 days of the week lie
                    week_months = [
                        (
                            None
                            if x is None
                            else (x.month if x.month == y.month else y.month)  # type: ignore[union-attr]
                        )
                        for x, y in zip(week_starts, week_mids)  # type: ignore[unbound]
                    ]
                else:
                    raise NotImplementedError
                tgt_values = [
                    None if y is None else f"{x}-{y:02}"
                    for x, y in zip(week_years, week_months)
                ]
        else:
            tgt_values = [None for x in src_values]
    elif src_unit == TimeUnit.DAY:
        if tgt_unit == TimeUnit.YEAR:
            tgt_values = [None if x is None else x[0:4] for x in src_values]
        elif tgt_unit == TimeUnit.QUARTER:
            tgt_values = [
                None if x is None else x[0:4] + "-Q" + str((int(x[5:7]) + 2) // 3)
                for x in src_values
            ]
        elif tgt_unit == TimeUnit.MONTH:
            tgt_values = [None if x is None else x[0:7] for x in src_values]
        elif tgt_unit == TimeUnit.WEEK:
            week_tuples = [
                (
                    (None, None, None)
                    if x is None
                    else datetime.date(
                        int(x[0:4]), int(x[5:7]), int(x[8:10])
                    ).isocalendar()
                )
                for x in src_values
            ]
            tgt_values = [
                None if x is None else f"{x}-W{y:02}" for x, y, _ in week_tuples
            ]
        else:
            tgt_values = [None for x in src_values]
    else:
        tgt_values = [None for x in src_values]
    return tgt_values

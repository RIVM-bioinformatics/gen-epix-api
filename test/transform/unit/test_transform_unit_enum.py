"""Unit tests for transform enums."""

from enum import Enum

import pytest

from gen_epix.transform.enum import (
    IntervalTransformStrategy,
    TimeUnit,
    TimeUnitTransformStrategy,
    TransformResultType,
    TransformType,
)


@pytest.mark.parametrize(
    ("enum_type", "expected_members"),
    [
        (
            TimeUnit,
            [
                ("YEAR", "YEAR"),
                ("QUARTER", "QUARTER"),
                ("MONTH", "MONTH"),
                ("WEEK", "WEEK"),
                ("DAY", "DAY"),
            ],
        ),
        (
            TimeUnitTransformStrategy,
            [("EXACT_ONLY", "EXACT_ONLY"), ("LARGEST_OVERLAP", "LARGEST_OVERLAP")],
        ),
        (
            IntervalTransformStrategy,
            [
                ("CONTAINS_ONLY", "CONTAINS_ONLY"),
                ("LARGEST_OVERLAP", "LARGEST_OVERLAP"),
            ],
        ),
        (TransformType, [("BASE", "BASE")]),
        (
            TransformResultType,
            [("SUCCESS", "SUCCESS"), ("ERROR", "ERROR"), ("SKIPPED", "SKIPPED")],
        ),
    ],
    ids=["time-unit", "time-strategy", "interval-strategy", "type", "result"],
)
def test_enum_members_preserve_names_values_and_order(
    enum_type: type[Enum], expected_members: list[tuple[str, str]]
) -> None:
    """Keep each public enum's string values and declaration order stable."""
    assert [(member.name, member.value) for member in enum_type] == expected_members

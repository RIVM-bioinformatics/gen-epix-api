"""Tests for StringSetFilter matching."""

import uuid
from enum import IntEnum
from test.filter.unit import util

import pytest

from gen_epix.filter.string_set import StringSetFilter


@pytest.mark.parametrize(
    "key", ["a", uuid.UUID("12345678-1234-5678-1234-567812345678")]
)
def test_string_set_match_case_sensitivity(key: object) -> None:
    """Match configured strings according to case-sensitivity settings."""
    rows = [{key: value} for value in ["x", "Y", "z", "", None]]

    case_sensitive_filter = StringSetFilter(
        members={"x", "y"},
        key=key,
        case_sensitive=True,
    )
    util.validate_filter_behavior(
        case_sensitive_filter, rows, [True, False, False, False, False]
    )

    case_insensitive_filter = StringSetFilter(
        members={"x", "y"},
        key=key,
        case_sensitive=False,
    )
    util.validate_filter_behavior(
        case_insensitive_filter, rows, [True, True, False, False, False]
    )


def test_string_set_match_enum_names() -> None:
    """Match enum values by member name in either case mode."""

    class Color(IntEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    case_sensitive_filter = StringSetFilter(
        key="a", members=frozenset({"RED", "GREEN"}), case_sensitive=True
    )
    rows = [{"a": value} for value in [Color.RED, Color.GREEN, Color.BLUE, None]]
    util.validate_filter_behavior(
        case_sensitive_filter, rows, [True, True, False, False]
    )

    case_insensitive_filter = StringSetFilter(
        key="a", members=frozenset({"red"}), case_sensitive=False
    )
    rows = [{"a": value} for value in [Color.RED, Color.GREEN, "RED", None]]
    util.validate_filter_behavior(
        case_insensitive_filter, rows, [True, False, True, False]
    )


def test_string_set_construction_normalizes_members() -> None:
    """Normalize member collections without mutating caller-owned inputs."""
    filter_obj = StringSetFilter(members={"apple", "banana", "cherry"})
    assert filter_obj.members == {"apple", "banana", "cherry"}

    duplicate_members = StringSetFilter(members=["dog", "dog", "cat", "bird"])
    assert duplicate_members.members == {"dog", "cat", "bird"}

    case_sensitive_filter = StringSetFilter(
        members={"APPLE", "banana"}, case_sensitive=True
    )
    assert case_sensitive_filter.members == {"APPLE", "banana"}

    case_insensitive_filter = StringSetFilter(
        members={"APPLE", "banana"}, case_sensitive=False
    )
    assert case_insensitive_filter.members == {"APPLE", "banana"}
    assert case_insensitive_filter._members == {"apple", "banana"}

    source_members = {"APPLE", "banana"}
    copied_filter = StringSetFilter(members=source_members, case_sensitive=False)
    source_members.add("CHERRY")
    assert copied_filter.members == {"APPLE", "banana"}

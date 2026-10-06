"""Unit tests for CompositeFilter."""

from test.filter.unit import util

import pytest
from pydantic import BaseModel

from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.number_range import NumberRangeFilter
from gen_epix.filter.partial_date_range import PartialDateRangeFilter
from gen_epix.filter.string_set import StringSetFilter


def test_not_nested_composite_match() -> None:
    """Evaluate supported logical operators over two child filters."""
    rows = [
        {"a": "2022-04", "b": "", "c": "c", "d": None},
        {"a": "2022-04", "b": "b", "c": "c", "d": None},
        {"a": "2022-01", "b": "", "c": "c", "d": None},
        {"a": "2022-01", "b": "b", "c": "c", "d": None},
    ]
    sub_filter1 = PartialDateRangeFilter(
        lower_bound="2022-01",
        upper_bound="2022-03",
        key="a",
    )
    sub_filter2 = StringSetFilter(members={"a", "b", "c"}, key="b")

    def get_filter(operator: str) -> CompositeFilter:
        return CompositeFilter(filters=[sub_filter1, sub_filter2], operator=operator)

    util.validate_filter_behavior(get_filter("AND"), rows, [False, False, False, True])
    util.validate_filter_behavior(get_filter("OR"), rows, [False, True, True, True])
    util.validate_filter_behavior(get_filter("XOR"), rows, [False, True, True, False])
    util.validate_filter_behavior(get_filter("NAND"), rows, [True, True, True, False])
    util.validate_filter_behavior(get_filter("NOR"), rows, [True, False, False, False])
    util.validate_filter_behavior(get_filter("XNOR"), rows, [True, False, False, True])
    util.validate_filter_behavior(
        get_filter("IMPLIES"), rows, [True, True, False, True]
    )
    util.validate_filter_behavior(
        get_filter("NIMPLIES"), rows, [False, False, True, False]
    )
    util.validate_filter_behavior(
        CompositeFilter(filters=[sub_filter1], operator="NOT"),
        rows,
        [True, True, False, False],
    )

    with pytest.raises(ValueError):
        CompositeFilter(filters=[sub_filter1, sub_filter2], operator="NOT")


def test_nested_composite_match() -> None:
    """Evaluate a composite filter nested inside another composite."""
    sub_filter1 = StringSetFilter(members={"a", "b", "c"}, key="a")
    sub_filter2 = CompositeFilter(
        filters=[
            StringSetFilter(members={"a", "b", "c"}, key="a"),
            StringSetFilter(members={"a", "b", "c"}, key="a"),
        ],
        operator="AND",
    )
    composite_filter = CompositeFilter(
        filters=[sub_filter1, sub_filter2],
        operator="AND",
    )

    util.validate_filter_behavior(composite_filter, [{"a": "a"}], [True])


def test_composite_filter_pydantic_and_plain_python_class() -> None:
    """Filter Pydantic models and ordinary objects without changing row identity."""

    class PydanticXY(BaseModel):
        """Represent filterable coordinates using Pydantic."""

        x: int
        y: str

    # pylint: disable=too-few-public-methods
    class PlainXY:
        """Represent filterable coordinates using a plain Python object."""

        def __init__(self, x: int, y: str):
            self.x = x
            self.y = y

    data: list[tuple[int, str]] = [
        (5, "a"),
        (10, "b"),
        (15, "z"),
        (20, "b"),
        (26, "a"),
    ]
    pydantic_rows = [PydanticXY(x=x, y=y) for x, y in data]
    plain_rows = [PlainXY(x=x, y=y) for x, y in data]
    filter_range = NumberRangeFilter(lower_bound=10, upper_bound=20, key="x")
    filter_set = StringSetFilter(members={"a", "b"}, key="y")

    composite_and = CompositeFilter(
        filters=[filter_range, filter_set],
        operator="AND",
    )
    expected_and = [False, True, False, False, False]
    assert list(composite_and.match_rows(pydantic_rows, is_model=True)) == expected_and
    assert list(composite_and.match_rows(plain_rows, is_model=True)) == expected_and
    pydantic_filtered_and = list(
        composite_and.filter_rows(pydantic_rows, is_model=True)
    )
    plain_filtered_and = list(composite_and.filter_rows(plain_rows, is_model=True))
    assert [(row.x, row.y) for row in pydantic_filtered_and] == [data[1]]
    assert [(row.x, row.y) for row in plain_filtered_and] == [data[1]]
    assert pydantic_filtered_and[0] == pydantic_rows[1]
    assert plain_filtered_and[0] == plain_rows[1]

    composite_or = CompositeFilter(
        filters=[filter_range, filter_set],
        operator="OR",
    )
    expected_or = [True, True, True, True, True]
    assert list(composite_or.match_rows(pydantic_rows, is_model=True)) == expected_or
    assert list(composite_or.match_rows(plain_rows, is_model=True)) == expected_or
    pydantic_filtered_or = list(composite_or.filter_rows(pydantic_rows, is_model=True))
    plain_filtered_or = list(composite_or.filter_rows(plain_rows, is_model=True))
    assert [(row.x, row.y) for row in pydantic_filtered_or] == data
    assert [(row.x, row.y) for row in plain_filtered_or] == data
    assert pydantic_filtered_or == pydantic_rows
    assert plain_filtered_or == plain_rows

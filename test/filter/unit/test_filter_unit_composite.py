"""Unit tests for CompositeFilter."""

import datetime
from collections.abc import Callable, Hashable
from test.filter.unit import util
from typing import Any

import pytest
from pydantic import BaseModel

from gen_epix.filter.base import Filter
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.date_range import DateRangeFilter
from gen_epix.filter.enum import LogicalOperator, LogicalOperatorSet
from gen_epix.filter.exists import ExistsFilter
from gen_epix.filter.number_range import NumberRangeFilter
from gen_epix.filter.partial_date_range import PartialDateRangeFilter
from gen_epix.filter.regex import RegexFilter
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


@pytest.mark.parametrize(
    ("value", "string_set_invert", "exists_invert", "expected"),
    [
        pytest.param("member", False, False, True, id="member-neither-inverted"),
        pytest.param("member", False, True, False, id="member-exists-inverted"),
        pytest.param("member", True, False, False, id="member-set-inverted"),
        pytest.param("member", True, True, False, id="member-both-inverted"),
        pytest.param("other", False, False, False, id="other-neither-inverted"),
        pytest.param("other", False, True, False, id="other-exists-inverted"),
        pytest.param("other", True, False, True, id="other-set-inverted"),
        pytest.param("other", True, True, False, id="other-both-inverted"),
        pytest.param(None, False, False, False, id="none-neither-inverted"),
        pytest.param(None, False, True, False, id="none-exists-inverted"),
        pytest.param(None, True, False, False, id="none-set-inverted"),
        pytest.param(None, True, True, True, id="none-both-inverted"),
    ],
)
def test_string_set_and_exists_composite_respects_subfilter_inversion(
    value: str | None,
    string_set_invert: bool,
    exists_invert: bool,
    expected: bool,
) -> None:
    """Compose StringSetFilter and ExistsFilter using each child's inversion."""
    child_filters: list[Filter] = [
        StringSetFilter(
            members=frozenset({"member"}), key="value", invert=string_set_invert
        ),
        ExistsFilter(key="value", invert=exists_invert),
    ]
    composite_filter = CompositeFilter(
        filters=child_filters,
        operator=LogicalOperator.AND,
    )
    row: dict[Hashable, Any | None] = {"value": value}

    assert composite_filter.match_row(row) is expected
    assert list(composite_filter.match_rows([row])) == [expected]
    assert list(composite_filter.filter_rows([row])) == ([row] if expected else [])


def test_logical_operator_sets_partition_all_operators() -> None:
    """Classify every logical operator into exactly one arity group."""
    unary = LogicalOperatorSet.UNARY.value
    binary = LogicalOperatorSet.BINARY.value
    multary = LogicalOperatorSet.MULTARY.value

    assert unary == {LogicalOperator.NOT}
    assert binary == {
        LogicalOperator.XOR,
        LogicalOperator.NAND,
        LogicalOperator.NOR,
        LogicalOperator.XNOR,
        LogicalOperator.IMPLIES,
        LogicalOperator.NIMPLIES,
    }
    assert multary == {LogicalOperator.AND, LogicalOperator.OR}
    assert unary | binary | multary == set(LogicalOperator)
    assert not (unary & binary or unary & multary or binary & multary)


@pytest.mark.parametrize(
    "operator", sorted(LogicalOperatorSet.UNARY.value, key=lambda item: item.value)
)
@pytest.mark.parametrize("child_count", [0, 2], ids=["too-few", "too-many"])
def test_unary_composite_operators_require_one_child(
    operator: LogicalOperator, child_count: int
) -> None:
    """Reject unary operators with a child count other than one."""
    with pytest.raises(ValueError):
        CompositeFilter(
            filters=[ExistsFilter() for _ in range(child_count)],
            operator=operator,
        )


@pytest.mark.parametrize(
    "operator", sorted(LogicalOperatorSet.BINARY.value, key=lambda item: item.value)
)
@pytest.mark.parametrize("child_count", [1, 3], ids=["too-few", "too-many"])
def test_binary_composite_operators_require_two_children(
    operator: LogicalOperator, child_count: int
) -> None:
    """Reject binary operators with a child count other than two."""
    with pytest.raises(ValueError, match="Exactly two filters"):
        CompositeFilter(
            filters=[ExistsFilter() for _ in range(child_count)],
            operator=operator,
        )


@pytest.mark.parametrize(
    "operator", sorted(LogicalOperatorSet.MULTARY.value, key=lambda item: item.value)
)
@pytest.mark.parametrize("child_count", [1, 2, 3])
def test_multary_composite_operators_accept_one_or_more_children(
    operator: LogicalOperator, child_count: int
) -> None:
    """Accept multary operators with any positive child count."""
    composite_filter = CompositeFilter(
        filters=[ExistsFilter() for _ in range(child_count)],
        operator=operator,
    )

    assert composite_filter.operator is operator
    assert len(composite_filter.filters) == child_count


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


def test_composite_filter_depth() -> None:
    """Return the deepest nested composite level, excluding leaf filters."""
    leaf_filter = ExistsFilter(key="a")
    depth_one_filter = CompositeFilter(filters=[leaf_filter], operator="NOT")
    depth_three_filter = CompositeFilter(
        filters=[
            ExistsFilter(key="a"),
            CompositeFilter(
                filters=[
                    ExistsFilter(key="a"),
                    CompositeFilter(filters=[ExistsFilter(key="a")], operator="NOT"),
                ],
                operator="AND",
            ),
        ],
        operator="OR",
    )

    assert depth_one_filter.get_depth() == 1
    assert depth_three_filter.get_depth() == 3


def test_composite_filter_pydantic_and_plain_python_class() -> None:
    """Filter Pydantic models and ordinary objects without changing row identity."""

    class PydanticXY(BaseModel):
        """Represent filterable coordinates using Pydantic."""

        x: int
        y: str

    class PlainXY:  # pylint: disable=too-few-public-methods
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


def test_composite_map_function() -> None:
    """Apply per-key mapping functions before evaluating child filters."""
    date_value = datetime.date.fromisoformat("2022-02-01")
    rows = [
        {"a": "2022-04-01", "b": "", "c": 10, "d": None},
        {"a": "2022-04-01", "b": "", "c": "20", "d": None},
        {"a": "2022-04-01", "b": "B", "c": 10, "d": None},
        {"a": "2022-04-01", "b": "B", "c": "20", "d": None},
        {"a": date_value, "b": "", "c": 10, "d": None},
        {"a": date_value, "b": "", "c": "20", "d": None},
        {"a": date_value, "b": "B", "c": 10, "d": None},
        {"a": date_value, "b": "B", "c": "20", "d": None},
    ]
    filters = [
        StringSetFilter(members={"a", "b", "c"}, key="b"),
        DateRangeFilter(
            lower_bound=datetime.date.fromisoformat("2022-01-01"),
            upper_bound=datetime.date.fromisoformat("2022-03-01"),
            key="a",
        ),
        NumberRangeFilter(lower_bound=15, upper_bound=25, key="c"),
    ]
    map_fn = {
        "a": lambda value: (
            datetime.date.fromisoformat(value) if isinstance(value, str) else value
        ),
        "b": lambda value: value.lower() if isinstance(value, str) else value,
        "c": lambda value: float(value) if isinstance(value, str) else value,
    }

    and_filter = CompositeFilter(filters=filters, operator="AND")
    util.validate_filter_behavior(
        and_filter,
        rows,
        [False, False, False, False, False, False, False, True],
        map_fn=map_fn,
    )

    or_filter = CompositeFilter(filters=filters, operator="OR")
    util.validate_filter_behavior(
        or_filter,
        rows,
        [False, True, True, True, True, True, True, True],
        map_fn=map_fn,
    )


@pytest.mark.parametrize(
    "mapping_kind",
    ["keyed-dict", "shared-callable", "per-child-list"],
)
def test_nested_composite_map_function_applies_to_row_apis(
    mapping_kind: str,
) -> None:
    """Propagate date mapping through nested row matching and filtering."""
    rows = [
        {"date": "2022-02-01"},
        {"date": "2022-04-01"},
        {"date": None},
    ]
    date_filter = DateRangeFilter(
        lower_bound=datetime.date(2022, 1, 1),
        upper_bound=datetime.date(2022, 3, 1),
        key="date",
    )
    nested_filter = CompositeFilter(filters=[date_filter])
    composite_filter = CompositeFilter(filters=[nested_filter])

    def map_date(value: Any) -> Any:
        return datetime.date.fromisoformat(value) if isinstance(value, str) else value

    if mapping_kind == "keyed-dict":
        map_fn: (
            dict[Hashable, Callable[[Any], Any]]
            | Callable[[Any], Any]
            | list[Callable[[Any], Any]]
        ) = {"date": map_date}
    elif mapping_kind == "shared-callable":
        map_fn = map_date
    else:
        map_fn = [map_date]

    assert composite_filter.match_row(rows[0], map_fn=map_fn)
    assert list(composite_filter.match_rows(rows, map_fn=map_fn)) == [
        True,
        False,
        False,
    ]
    assert list(composite_filter.filter_rows(rows, map_fn=map_fn)) == [rows[0]]


def test_composite_construction_retains_child_filters() -> None:
    """Retain child filters in the order supplied during construction."""
    child_filters = [
        ExistsFilter(),
        NumberRangeFilter(lower_bound=10, upper_bound=20),
        RegexFilter(pattern="^[A-Za-z]+$"),
    ]

    composite_filter = CompositeFilter(filters=child_filters)

    assert composite_filter.filters == child_filters

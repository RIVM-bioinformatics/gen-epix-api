"""Unit tests for CompositeFilter."""

import datetime
from test.filter.unit import util

import pytest
from pydantic import BaseModel

from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.date_range import DateRangeFilter
from gen_epix.filter.enum import LogicalOperator, LogicalOperatorSet
from gen_epix.filter.equals_string import EqualsStringFilter
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
    composite_filter = CompositeFilter(
        filters=[ExistsFilter() for _ in range(child_count)],
        operator=operator,
    )

    assert composite_filter.operator is operator
    assert len(composite_filter.filters) == child_count


def test_is_within_max_depth_counts_composite_levels() -> None:
    leaf_filter = ExistsFilter(key="a")
    nested_filter = CompositeFilter(
        filters=[CompositeFilter(filters=[leaf_filter], operator="OR")],
        operator="AND",
    )

    assert CompositeFilter(filters=[leaf_filter]).is_within_max_depth(1)
    assert not nested_filter.is_within_max_depth(1)
    assert nested_filter.is_within_max_depth(2)
    assert not nested_filter.is_within_max_depth(0)


def test_is_within_max_depth_rejects_negative_limit() -> None:
    composite_filter = CompositeFilter(filters=[ExistsFilter(key="a")])

    with pytest.raises(ValueError, match="cannot be negative"):
        composite_filter.is_within_max_depth(-1)


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


@pytest.mark.parametrize(
    ("operator", "expected"),
    [
        pytest.param(LogicalOperator.NOT, False, id="not"),
        pytest.param(LogicalOperator.AND, True, id="and"),
        pytest.param(LogicalOperator.OR, True, id="or"),
        pytest.param(LogicalOperator.XOR, False, id="xor"),
        pytest.param(LogicalOperator.NAND, False, id="nand"),
        pytest.param(LogicalOperator.NOR, False, id="nor"),
        pytest.param(LogicalOperator.XNOR, True, id="xnor"),
        pytest.param(LogicalOperator.IMPLIES, True, id="implies"),
        pytest.param(LogicalOperator.NIMPLIES, False, id="nimplies"),
    ],
)
def test_composite_scalar_methods_preserve_explicit_na_values(
    operator: LogicalOperator, expected: bool
) -> None:
    """Apply the caller's NA policy consistently to every scalar operator."""
    child_count = 1 if operator in LogicalOperatorSet.UNARY.value else 2
    composite_filter = CompositeFilter(
        filters=[ExistsFilter(key="a") for _ in range(child_count)],
        operator=operator,
    )
    row = {"a": None}

    assert composite_filter.match_value(None, na_values=set()) is expected
    assert list(composite_filter.match_column([None], na_values=set())) == [expected]
    assert list(composite_filter.filter_column([None], na_values=set())) == (
        [None] if expected else []
    )
    assert composite_filter.match_row(row, na_values=set()) is expected
    assert list(composite_filter.match_rows([row], na_values=set())) == [expected]


def test_nested_composite_propagates_shared_mapping_function() -> None:
    """Apply a shared mapping function to nested leaf values, not the row."""
    inner_filter = CompositeFilter(
        filters=[EqualsStringFilter(key="a", value="mixed")],
        operator=LogicalOperator.AND,
    )
    composite_filter = CompositeFilter(
        filters=[inner_filter],
        operator=LogicalOperator.AND,
    )

    assert composite_filter.match_row({"a": "MIXED"}, map_fn=str.lower)


def test_nested_composite_uses_parent_list_mapping_for_nested_row() -> None:
    """Apply a per-child list mapping to the nested row, not inner leaves."""
    inner_filter = CompositeFilter(
        filters=[
            EqualsStringFilter(key="a", value="mixed"),
            EqualsStringFilter(key="b", value="mapped"),
        ],
        operator=LogicalOperator.AND,
    )
    composite_filter = CompositeFilter(
        filters=[
            inner_filter,
            EqualsStringFilter(key="c", value="leaf"),
        ],
        operator=LogicalOperator.AND,
    )

    def map_nested_row(row: dict[str, str]) -> dict[str, str]:
        return {"a": row["a"].lower(), "b": row["b"].lower(), "c": row["c"]}

    assert composite_filter.match_row(
        {"a": "MIXED", "b": "MAPPED", "c": "leaf"},
        map_fn=[map_nested_row, str.lower],
    )


def test_nested_composite_accepts_one_parent_list_mapping() -> None:
    """Do not forward a parent's one-entry mapper list to inner leaves."""
    inner_filter = CompositeFilter(
        filters=[
            EqualsStringFilter(key="a", value="a"),
            EqualsStringFilter(key="b", value="b"),
        ],
        operator=LogicalOperator.AND,
    )
    composite_filter = CompositeFilter(
        filters=[inner_filter],
        operator=LogicalOperator.AND,
    )

    assert composite_filter.match_row(
        {"a": "a", "b": "b"},
        map_fn=[lambda row: row],
    )


def test_inverted_child_matches_null_in_dict_rows() -> None:
    """An inverted child matches missing values consistently in row evaluation."""
    composite_filter = CompositeFilter(
        filters=[
            EqualsStringFilter(key="description", value="x", invert=True),
            ExistsFilter(key="value"),
        ],
        operator=LogicalOperator.AND,
    )
    rows = [
        {"description": None, "value": 1},
        {"description": "x", "value": 1},
        {"description": "other", "value": 1},
    ]

    assert list(composite_filter.match_rows(rows)) == [True, False, True]


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


def test_composite_construction_retains_child_filters() -> None:
    """Retain child filters in the order supplied during construction."""
    child_filters = [
        ExistsFilter(),
        NumberRangeFilter(lower_bound=10, upper_bound=20),
        RegexFilter(pattern="^[A-Za-z]+$"),
    ]

    composite_filter = CompositeFilter(filters=child_filters)

    assert composite_filter.filters == child_filters

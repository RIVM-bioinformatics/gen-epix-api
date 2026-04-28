import datetime
import uuid
from enum import IntEnum
from test.filter.unit import util

import numpy as np
import pytest
from pydantic import BaseModel

from gen_epix.filter import ExistsFilter, NumberRangeFilter
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.date_range import DateRangeFilter
from gen_epix.filter.partial_date_range import PartialDateRangeFilter
from gen_epix.filter.string_set import StringSetFilter


@pytest.mark.scenario_ids("TC-SEC-28-07")
class TestFilterMatch:

    def test_exists_match(self) -> None:
        # Match value
        filter = ExistsFilter(key="a")
        rows = [{"a": x} for x in [None, np.nan, "", "null"]]
        util.validate_filter_behavior(filter, rows, [False, True, True, True])
        util.validate_filter_behavior(
            filter, rows, [True, True, True, True], na_values=set()
        )
        util.validate_filter_behavior(
            filter, rows, [False, True, True, True], na_values={None}
        )
        util.validate_filter_behavior(
            filter, rows, [True, False, True, True], na_values={np.nan}
        )
        util.validate_filter_behavior(
            filter, rows, [True, True, False, True], na_values={""}
        )
        util.validate_filter_behavior(
            filter, rows, [True, True, True, False], na_values={"null"}
        )
        util.validate_filter_behavior(
            filter, rows, [False, False, True, True], na_values={None, np.nan}
        )
        util.validate_filter_behavior(
            filter, rows, [True, False, False, True], na_values={np.nan, ""}
        )
        util.validate_filter_behavior(
            filter, rows, [True, True, False, False], na_values={"", "null"}
        )
        # Key does not exist
        filter = ExistsFilter(key="b")
        rows = [{"a": x} for x in [None, np.nan, "", "null"]]
        util.validate_filter_behavior(filter, rows, [False, False, False, False])

    def test_string_set_match(self) -> None:
        for key in ["a", uuid.uuid4()]:
            fixed_args = {
                "members": {"x", "y"},
                "key": key,
            }
            rows = [{key: x} for x in ["x", "Y", "z", "", None]]
            filter = StringSetFilter(case_sensitive=True, **fixed_args)
            util.validate_filter_behavior(
                filter, rows, [True, False, False, False, False]
            )
            filter = StringSetFilter(case_sensitive=False, **fixed_args)
            util.validate_filter_behavior(
                filter, rows, [True, True, False, False, False]
            )

    def test_string_set_match_with_enum(self) -> None:
        class Color(IntEnum):
            RED = 1
            GREEN = 2
            BLUE = 3

        # case_sensitive=True: enum .name must be in members
        f = StringSetFilter(key="a", members=frozenset({"RED", "GREEN"}), case_sensitive=True)
        rows = [{"a": x} for x in [Color.RED, Color.GREEN, Color.BLUE, None]]
        util.validate_filter_behavior(f, rows, [True, True, False, False])

        # case_sensitive=False: .name compared case-insensitively
        f = StringSetFilter(key="a", members=frozenset({"red"}), case_sensitive=False)
        rows = [{"a": x} for x in [Color.RED, Color.GREEN, "RED", None]]
        util.validate_filter_behavior(f, rows, [True, False, True, False])

        # plain strings still work unchanged
        f = StringSetFilter(key="a", members=frozenset({"x"}), case_sensitive=True)
        rows = [{"a": x} for x in ["x", "y", None]]
        util.validate_filter_behavior(f, rows, [True, False, False])

    def test_number_range_match(self) -> None:
        fixed_args = {
            "lower_bound": 10,
            "upper_bound": 20,
            "key": "a",
        }
        rows = [{"a": x} for x in [5, 10, 15, 20, 25]]
        filter = NumberRangeFilter(**fixed_args)
        util.validate_filter_behavior(filter, rows, [False, True, True, False, False])
        filter = NumberRangeFilter(lower_bound_censor=">", **fixed_args)
        util.validate_filter_behavior(filter, rows, [False, False, True, False, False])
        filter = NumberRangeFilter(upper_bound_censor="<=", **fixed_args)
        util.validate_filter_behavior(filter, rows, [False, True, True, True, False])
        filter = NumberRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util.validate_filter_behavior(filter, rows, [False, False, True, True, False])

    def test_date_range_match(self) -> None:
        fixed_args = {
            "lower_bound": datetime.date.fromisoformat("2021-01-01"),
            "upper_bound": datetime.date.fromisoformat("2021-02-01"),
            "key": "a",
        }
        rows = [
            {"a": datetime.date.fromisoformat(x)}
            for x in [
                "2020-12-31",
                "2021-01-01",
                "2021-01-31",
                "2021-02-01",
                "2021-02-02",
            ]
        ]
        filter = DateRangeFilter(**fixed_args)
        util.validate_filter_behavior(filter, rows, [False, True, True, False, False])
        filter = DateRangeFilter(lower_bound_censor=">", **fixed_args)
        util.validate_filter_behavior(filter, rows, [False, False, True, False, False])
        filter = DateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util.validate_filter_behavior(filter, rows, [False, True, True, True, False])
        filter = DateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util.validate_filter_behavior(filter, rows, [False, False, True, True, False])

    def test_partial_date_range_match(self) -> None:
        # Bounds are months
        fixed_args = {
            "lower_bound": "2022-01",
            "upper_bound": "2022-03",
            "key": "a",
        }
        # Values are years
        rows = [
            {"a": x}
            for x in [
                "2021",
                "2022",
                "2023",
            ]
        ]
        filter = PartialDateRangeFilter(**fixed_args)
        util.validate_filter_behavior(filter, rows, [False, False, False])
        filter = PartialDateRangeFilter(lower_bound_censor=">", **fixed_args)
        util.validate_filter_behavior(filter, rows, [False, False, False])
        filter = PartialDateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util.validate_filter_behavior(filter, rows, [False, False, False])
        filter = PartialDateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util.validate_filter_behavior(filter, rows, [False, False, False])
        # Values are quarters
        rows = [
            {"a": x}
            for x in [
                "2021-Q4",
                "2022-Q1",
                "2022-Q2",
            ]
        ]
        filter = PartialDateRangeFilter(**fixed_args)
        util.validate_filter_behavior(filter, rows, [False, False, False])
        filter = PartialDateRangeFilter(lower_bound_censor=">", **fixed_args)
        util.validate_filter_behavior(filter, rows, [False, False, False])
        filter = PartialDateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util.validate_filter_behavior(filter, rows, [False, True, False])
        filter = PartialDateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util.validate_filter_behavior(filter, rows, [False, False, False])
        # Values are months
        rows = [
            {"a": x}
            for x in [
                "2021-12",
                "2022-01",
                "2022-02",
                "2022-03",
                "2022-04",
            ]
        ]
        filter = PartialDateRangeFilter(**fixed_args)
        util.validate_filter_behavior(filter, rows, [False, True, True, False, False])
        filter = PartialDateRangeFilter(lower_bound_censor=">", **fixed_args)
        util.validate_filter_behavior(filter, rows, [False, False, True, False, False])
        filter = PartialDateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util.validate_filter_behavior(filter, rows, [False, True, True, True, False])
        filter = PartialDateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util.validate_filter_behavior(filter, rows, [False, False, True, True, False])
        # Values are weeks
        rows = [
            {"a": x}
            for x in [
                "2021-W52",
                "2022-W01",
                "2022-W05",
                "2022-W06",
                "2022-W09",
                "2022-W12",
                "2022-W13",
            ]
        ]
        filter = PartialDateRangeFilter(**fixed_args)
        util.validate_filter_behavior(
            filter, rows, [False, True, True, True, False, False, False]
        )
        filter = PartialDateRangeFilter(lower_bound_censor=">", **fixed_args)
        util.validate_filter_behavior(
            filter, rows, [False, False, False, True, False, False, False]
        )
        filter = PartialDateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util.validate_filter_behavior(
            filter, rows, [False, True, True, True, True, True, False]
        )
        filter = PartialDateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util.validate_filter_behavior(
            filter, rows, [False, False, False, True, True, True, False]
        )
        # Values are dates
        rows = [
            {"a": x}
            for x in [
                "2021-12-31",
                "2022-01-01",
                "2022-01-31",
                "2022-02-01",
                "2022-02-28",
                "2022-03-01",
                "2022-04-01",
            ]
        ]
        filter = PartialDateRangeFilter(**fixed_args)
        util.validate_filter_behavior(
            filter, rows, [False, True, True, True, True, False, False]
        )
        filter = PartialDateRangeFilter(lower_bound_censor=">", **fixed_args)
        util.validate_filter_behavior(
            filter, rows, [False, False, False, True, True, False, False]
        )
        filter = PartialDateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util.validate_filter_behavior(
            filter, rows, [False, True, True, True, True, True, False]
        )
        filter = PartialDateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util.validate_filter_behavior(
            filter, rows, [False, False, False, True, True, True, False]
        )

    def test_not_nested_composite_match(self) -> None:
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
        sub_filter2 = StringSetFilter(
            members={"a", "b", "c"},
            key="b",
        )

        def _get_filter(operator: str) -> CompositeFilter:
            return CompositeFilter(
                filters=[sub_filter1, sub_filter2],
                operator=operator,
            )

        # Two filters, AND
        filter = _get_filter("AND")
        util.validate_filter_behavior(filter, rows, [False, False, False, True])
        # Two filters, OR
        filter = _get_filter("OR")
        util.validate_filter_behavior(filter, rows, [False, True, True, True])
        # Two filters, XOR
        filter = _get_filter("XOR")
        util.validate_filter_behavior(filter, rows, [False, True, True, False])
        # Two filters, NAND
        filter = _get_filter("NAND")
        util.validate_filter_behavior(filter, rows, [True, True, True, False])
        # Two filters, NOR
        filter = _get_filter("NOR")
        util.validate_filter_behavior(filter, rows, [True, False, False, False])
        # Two filters, XNOR
        filter = _get_filter("XNOR")
        util.validate_filter_behavior(filter, rows, [True, False, False, True])
        # Two filters, IMPLIES
        filter = _get_filter("IMPLIES")
        util.validate_filter_behavior(filter, rows, [True, True, False, True])
        # Two filters, NIMPLIES
        filter = _get_filter("NIMPLIES")
        util.validate_filter_behavior(filter, rows, [False, False, True, False])
        # One filter, NOT
        filter = CompositeFilter(
            filters=[sub_filter1],
            operator="NOT",
        )
        util.validate_filter_behavior(filter, rows, [True, True, False, False])
        # Two filters, NOT
        with pytest.raises(ValueError):
            filter = CompositeFilter(
                filters=[sub_filter1, sub_filter2],
                operator="NOT",
            )

        # TODO: test >2 filters for AND and OR, error for all others
        # TODO: test nested composite filters

        # TODO: test >2 filters for AND and OR, error for all others
        # TODO: test nested composite filters

    def test_nested_composite_match(self) -> None:
        sub_filter1_1 = StringSetFilter(
            members={"a", "b", "c"},
            key="a",
        )
        sub_filter2_1 = StringSetFilter(
            members={"a", "b", "c"},
            key="a",
        )
        sub_filter2_2 = StringSetFilter(
            members={"a", "b", "c"},
            key="a",
        )
        sub_filter1 = sub_filter1_1
        sub_filter2 = CompositeFilter(
            filters=[sub_filter2_1, sub_filter2_2],
            operator="AND",
        )
        filter = CompositeFilter(
            filters=[sub_filter1, sub_filter2],
            operator="AND",
        )

        rows = [
            {"a": "a"},
        ]
        util.validate_filter_behavior(filter, rows, [True])

    def test_simple_filter_pydantic_and_plain_python_class(self) -> None:

        class _PydanticModel(BaseModel):
            x: int

        class _SimpleClass:
            def __init__(self, x: int):
                self.x = x

        values: list[int] = [5, 10, 15, 20, 26]
        pydantic_rows = [_PydanticModel(x=x) for x in values]
        plain_rows = [_SimpleClass(x=x) for x in values]

        num_range_filter = NumberRangeFilter(lower_bound=1, upper_bound=25, key="x")
        expected_matches: list[bool] = [True, True, True, True, False]

        pydantic_matches = list(
            num_range_filter.match_rows(pydantic_rows, is_model=True)
        )
        pydantic_filtered = list(
            num_range_filter.filter_rows(pydantic_rows, is_model=True)
        )

        assert pydantic_matches == expected_matches
        assert pydantic_filtered == pydantic_rows[:-1]
        assert [row.x for row in pydantic_filtered] == values[:-1]

        # Test with plain Python class
        simple_matches = list(num_range_filter.match_rows(plain_rows, is_model=True))
        simple_filtered = list(num_range_filter.filter_rows(plain_rows, is_model=True))

        assert simple_matches == expected_matches
        assert len(simple_filtered) == len(plain_rows) - 1
        assert [row.x for row in simple_filtered] == values[:-1]

    def test_composite_filter_pydantic_and_plain_python_class(self) -> None:

        class _PydanticXY(BaseModel):
            x: int
            y: str

        class _PlainXY:
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
        pydantic_rows = [_PydanticXY(x=x, y=y) for x, y in data]
        plain_rows = [_PlainXY(x=x, y=y) for x, y in data]

        filter_range = NumberRangeFilter(lower_bound=10, upper_bound=20, key="x")
        filter_set = StringSetFilter(members={"a", "b"}, key="y")

        # AND
        composite_and = CompositeFilter(
            filters=[filter_range, filter_set],
            operator="AND",
        )
        expected_matches = [False, True, False, False, False]
        assert (
            list(composite_and.match_rows(pydantic_rows, is_model=True))
            == expected_matches
        )
        assert (
            list(composite_and.match_rows(plain_rows, is_model=True))
            == expected_matches
        )

        pydantic_filtered_and = list(
            composite_and.filter_rows(pydantic_rows, is_model=True)
        )
        plain_filtered_and = list(composite_and.filter_rows(plain_rows, is_model=True))

        assert [(r.x, r.y) for r in pydantic_filtered_and] == [data[1]]
        assert [(r.x, r.y) for r in plain_filtered_and] == [data[1]]
        assert pydantic_filtered_and[0] == pydantic_rows[1]
        assert plain_filtered_and[0] == plain_rows[1]

        # OR
        composite_or = CompositeFilter(
            filters=[filter_range, filter_set],
            operator="OR",
        )
        expected_matches = [True, True, True, True, True]

        assert (
            list(composite_or.match_rows(pydantic_rows, is_model=True))
            == expected_matches
        )
        assert (
            list(composite_or.match_rows(plain_rows, is_model=True)) == expected_matches
        )

        pydantic_filtered_or = list(
            composite_or.filter_rows(pydantic_rows, is_model=True)
        )
        plain_filtered_or = list(composite_or.filter_rows(plain_rows, is_model=True))
        assert [(r.x, r.y) for r in pydantic_filtered_or] == data
        assert [(r.x, r.y) for r in plain_filtered_or] == data
        assert pydantic_filtered_or == pydantic_rows
        assert plain_filtered_or == plain_rows

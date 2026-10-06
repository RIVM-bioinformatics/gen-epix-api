import datetime
import uuid
from enum import IntEnum
from test.filter.unit import util

import pytest
from pydantic import BaseModel

from gen_epix.filter import NumberRangeFilter
from gen_epix.filter.date_range import DateRangeFilter
from gen_epix.filter.partial_date_range import PartialDateRangeFilter
from gen_epix.filter.string_set import StringSetFilter


@pytest.mark.scenario_ids("TC-SEC-28-07")
class TestFilterMatch:

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
        f = StringSetFilter(
            key="a", members=frozenset({"RED", "GREEN"}), case_sensitive=True
        )
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

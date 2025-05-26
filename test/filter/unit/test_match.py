import datetime
import uuid
from test.filter.unit import util

import numpy as np
import pytest

from gen_epix.filter import ExistsFilter, NumberRangeFilter
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.date_range import DateRangeFilter
from gen_epix.filter.partial_date_range import PartialDateRangeFilter
from gen_epix.filter.string_set import StringSetFilter


class TestFilterMatch:

    def test_exists_match(self) -> None:
        # Match value
        filter = ExistsFilter(key="a")
        rows = [{"a": x} for x in [None, np.nan, "", "null"]]
        util._test_filter(filter, rows, [False, True, True, True])
        util._test_filter(filter, rows, [True, True, True, True], na_values=set())
        util._test_filter(filter, rows, [False, True, True, True], na_values={None})
        util._test_filter(filter, rows, [True, False, True, True], na_values={np.nan})
        util._test_filter(filter, rows, [True, True, False, True], na_values={""})
        util._test_filter(filter, rows, [True, True, True, False], na_values={"null"})
        util._test_filter(
            filter, rows, [False, False, True, True], na_values={None, np.nan}
        )
        util._test_filter(
            filter, rows, [True, False, False, True], na_values={np.nan, ""}
        )
        util._test_filter(
            filter, rows, [True, True, False, False], na_values={"", "null"}
        )
        # Key does not exist
        filter = ExistsFilter(key="b")
        rows = [{"a": x} for x in [None, np.nan, "", "null"]]
        util._test_filter(filter, rows, [False, False, False, False])

    def test_string_set_match(self) -> None:
        for key in ["a", uuid.uuid4()]:
            fixed_args = {
                "members": {"x", "y"},
                "key": key,
            }
            rows = [{key: x} for x in ["x", "Y", "z", "", None]]
            filter = StringSetFilter(case_sensitive=True, **fixed_args)
            util._test_filter(filter, rows, [True, False, False, False, False])
            filter = StringSetFilter(case_sensitive=False, **fixed_args)
            util._test_filter(filter, rows, [True, True, False, False, False])

    def test_number_range_match(self) -> None:
        fixed_args = {
            "lower_bound": 10,
            "upper_bound": 20,
            "key": "a",
        }
        rows = [{"a": x} for x in [5, 10, 15, 20, 25]]
        filter = NumberRangeFilter(**fixed_args)
        util._test_filter(filter, rows, [False, True, True, False, False])
        filter = NumberRangeFilter(lower_bound_censor=">", **fixed_args)
        util._test_filter(filter, rows, [False, False, True, False, False])
        filter = NumberRangeFilter(upper_bound_censor="<=", **fixed_args)
        util._test_filter(filter, rows, [False, True, True, True, False])
        filter = NumberRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util._test_filter(filter, rows, [False, False, True, True, False])

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
        util._test_filter(filter, rows, [False, True, True, False, False])
        filter = DateRangeFilter(lower_bound_censor=">", **fixed_args)
        util._test_filter(filter, rows, [False, False, True, False, False])
        filter = DateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util._test_filter(filter, rows, [False, True, True, True, False])
        filter = DateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util._test_filter(filter, rows, [False, False, True, True, False])

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
        util._test_filter(filter, rows, [False, False, False])
        filter = PartialDateRangeFilter(lower_bound_censor=">", **fixed_args)
        util._test_filter(filter, rows, [False, False, False])
        filter = PartialDateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util._test_filter(filter, rows, [False, False, False])
        filter = PartialDateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util._test_filter(filter, rows, [False, False, False])
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
        util._test_filter(filter, rows, [False, False, False])
        filter = PartialDateRangeFilter(lower_bound_censor=">", **fixed_args)
        util._test_filter(filter, rows, [False, False, False])
        filter = PartialDateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util._test_filter(filter, rows, [False, True, False])
        filter = PartialDateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util._test_filter(filter, rows, [False, False, False])
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
        util._test_filter(filter, rows, [False, True, True, False, False])
        filter = PartialDateRangeFilter(lower_bound_censor=">", **fixed_args)
        util._test_filter(filter, rows, [False, False, True, False, False])
        filter = PartialDateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util._test_filter(filter, rows, [False, True, True, True, False])
        filter = PartialDateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util._test_filter(filter, rows, [False, False, True, True, False])
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
        util._test_filter(filter, rows, [False, True, True, True, False, False, False])
        filter = PartialDateRangeFilter(lower_bound_censor=">", **fixed_args)
        util._test_filter(
            filter, rows, [False, False, False, True, False, False, False]
        )
        filter = PartialDateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util._test_filter(filter, rows, [False, True, True, True, True, True, False])
        filter = PartialDateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util._test_filter(filter, rows, [False, False, False, True, True, True, False])
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
        util._test_filter(filter, rows, [False, True, True, True, True, False, False])
        filter = PartialDateRangeFilter(lower_bound_censor=">", **fixed_args)
        util._test_filter(filter, rows, [False, False, False, True, True, False, False])
        filter = PartialDateRangeFilter(upper_bound_censor="<=", **fixed_args)
        util._test_filter(filter, rows, [False, True, True, True, True, True, False])
        filter = PartialDateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        util._test_filter(filter, rows, [False, False, False, True, True, True, False])

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
        util._test_filter(filter, rows, [False, False, False, True])
        # Two filters, OR
        filter = _get_filter("OR")
        util._test_filter(filter, rows, [False, True, True, True])
        # Two filters, XOR
        filter = _get_filter("XOR")
        util._test_filter(filter, rows, [False, True, True, False])
        # Two filters, NAND
        filter = _get_filter("NAND")
        util._test_filter(filter, rows, [True, True, True, False])
        # Two filters, NOR
        filter = _get_filter("NOR")
        util._test_filter(filter, rows, [True, False, False, False])
        # Two filters, XNOR
        filter = _get_filter("XNOR")
        util._test_filter(filter, rows, [True, False, False, True])
        # Two filters, IMPLIES
        filter = _get_filter("IMPLIES")
        util._test_filter(filter, rows, [True, True, False, True])
        # Two filters, NIMPLIES
        filter = _get_filter("NIMPLIES")
        util._test_filter(filter, rows, [False, False, True, False])
        # One filter, NOT
        filter = CompositeFilter(
            filters=[sub_filter1],
            operator="NOT",
        )
        util._test_filter(filter, rows, [True, True, False, False])
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
        util._test_filter(filter, rows, [True])

import datetime
from decimal import Decimal
from test.filter.unit import util

import numpy as np

from gen_epix.filter import ExistsFilter, NumberRangeFilter
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.date_range import DateRangeFilter
from gen_epix.filter.string_set import StringSetFilter


class TestFilterMapfun:

    def test_exists_map_fun(self) -> None:
        def _test(expected_results: list, na_values=None) -> None:
            util._test_filter(
                filter, rows, expected_results, na_values=na_values, map_fun=map_fun
            )

        # Match value
        filter = ExistsFilter(key="a")
        rows = [{"a": x} for x in [None, np.nan, "", "null"]]

        map_fun = lambda x: x
        _test([False, True, True, True])
        _test([True, True, True, True], na_values=set())
        _test([False, True, True, True], na_values={None})
        _test([True, False, True, True], na_values={np.nan})
        _test([True, True, False, True], na_values={""})
        _test([True, True, True, False], na_values={"null"})

        # map_fun is not applied to check na
        map_fun = lambda x: None if x in {np.nan} else x
        _test([True, True, True, True], na_values=set())
        _test([False, True, True, True], na_values={None})
        _test([True, False, True, True], na_values={np.nan})
        _test([True, True, False, True], na_values={""})
        _test([True, True, True, False], na_values={"null"})

    def test_number_range_map_fun(self) -> None:
        def _test(expected_results: list, na_values=None) -> None:
            util._test_filter(
                filter, rows, expected_results, na_values=na_values, map_fun=map_fun
            )

        fixed_args = {
            "lower_bound": 10,
            "upper_bound": 20,
            "key": "a",
        }
        rows = [{"a": x} for x in ["5", "10.0", 15.5, "20", Decimal(25)]]
        map_fun = lambda x: float(x) if isinstance(x, str) else x
        filter = NumberRangeFilter(**fixed_args)
        _test([False, True, True, False, False])
        filter = NumberRangeFilter(lower_bound_censor=">", **fixed_args)
        _test([False, False, True, False, False])
        filter = NumberRangeFilter(upper_bound_censor="<=", **fixed_args)
        _test([False, True, True, True, False])
        filter = NumberRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        _test([False, False, True, True, False])

    def test_date_range_map_fun(self) -> None:
        def _test(expected_results: list, na_values=None) -> None:
            util._test_filter(
                filter, rows, expected_results, na_values=na_values, map_fun=map_fun
            )

        fixed_args = {
            "lower_bound": datetime.date.fromisoformat("2021-01-01"),
            "upper_bound": datetime.date.fromisoformat("2021-02-01"),
            "key": "a",
        }
        rows = [
            {"a": x}
            for x in [
                "2020-12-31",
                "2021-01-01",
                "2021-01-31",
                "2021-02-01",
                "2021-02-02",
            ]
        ]
        map_fun = lambda x: datetime.date.fromisoformat(x) if isinstance(x, str) else x
        filter = DateRangeFilter(**fixed_args)
        _test([False, True, True, False, False])
        filter = DateRangeFilter(lower_bound_censor=">", **fixed_args)
        _test([False, False, True, False, False])
        filter = DateRangeFilter(upper_bound_censor="<=", **fixed_args)
        _test([False, True, True, True, False])
        filter = DateRangeFilter(
            lower_bound_censor=">",
            upper_bound_censor="<=",
            **fixed_args,
        )
        _test([False, False, True, True, False])

    def test_composite_map_fun(self) -> None:
        date_ = datetime.date.fromisoformat("2022-02-01")
        rows = [
            {"a": "2022-04-01", "b": "", "c": 10, "d": None},
            {"a": "2022-04-01", "b": "", "c": "20", "d": None},
            {"a": "2022-04-01", "b": "B", "c": 10, "d": None},
            {"a": "2022-04-01", "b": "B", "c": "20", "d": None},
            {"a": date_, "b": "", "c": 10, "d": None},
            {"a": date_, "b": "", "c": "20", "d": None},
            {"a": date_, "b": "B", "c": 10, "d": None},
            {"a": date_, "b": "B", "c": "20", "d": None},
        ]
        sub_filter1 = DateRangeFilter(
            lower_bound=datetime.date.fromisoformat("2022-01-01"),
            upper_bound=datetime.date.fromisoformat("2022-03-01"),
            key="a",
        )
        sub_filter2 = StringSetFilter(
            members={"a", "b", "c"},
            key="b",
        )
        sub_filter3 = NumberRangeFilter(
            lower_bound=15,
            upper_bound=25,
            key="c",
        )

        map_fun = {
            "a": lambda x: datetime.date.fromisoformat(x) if isinstance(x, str) else x,
            "b": lambda x: x.lower() if isinstance(x, str) else x,
            "c": lambda x: float(x) if isinstance(x, str) else x,
        }

        # AND
        filter = CompositeFilter(
            filters=[sub_filter2, sub_filter1, sub_filter3],
            operator="AND",
        )
        util._test_filter(
            filter,
            rows,
            [False, False, False, False, False, False, False, True],
            map_fun=map_fun,
        )
        # OR
        filter = CompositeFilter(
            filters=[sub_filter2, sub_filter1, sub_filter3],
            operator="OR",
        )
        util._test_filter(
            filter,
            rows,
            [False, True, True, True, True, True, True, True, True],
            map_fun=map_fun,
        )

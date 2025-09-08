import logging
import test.util as test_util

from etl.etl.lsp_api.etl import Etl
from lsp_api.lsp_api.domain import enum

test_util.set_log_level("lsp", logging.ERROR)


def test_map_time():
    def assert_equal(actual, expected):
        if (
            not isinstance(actual, list)
            or len(actual) != len(expected)
            or sum(x != y for x, y in zip(actual, expected)) > 0
        ):
            raise AssertionError(f"Actual {actual} should be {expected}")

    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_YEAR, ["2024"], enum.ColType.TIME_YEAR, None
        )[0],
        ["2024"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_YEAR, ["2024"], enum.ColType.TIME_QUARTER, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_YEAR, ["2024"], enum.ColType.TIME_MONTH, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_YEAR, ["2024"], enum.ColType.TIME_WEEK, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_YEAR, ["2024"], enum.ColType.TIME_DAY, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_QUARTER, ["2024-Q1"], enum.ColType.TIME_YEAR, None
        )[0],
        ["2024"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_QUARTER, ["2024-Q1"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q1"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_QUARTER, ["2024-Q1"], enum.ColType.TIME_MONTH, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_QUARTER, ["2024-Q1"], enum.ColType.TIME_WEEK, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_QUARTER, ["2024-Q1"], enum.ColType.TIME_DAY, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-01"], enum.ColType.TIME_YEAR, None
        )[0],
        ["2024"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-01"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q1"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-02"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q1"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-03"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q1"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-04"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q2"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-05"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q2"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-06"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q2"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-07"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q3"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-08"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q3"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-09"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q3"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-10"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q4"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-11"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q4"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-12"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2024-Q4"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-01"], enum.ColType.TIME_MONTH, None
        )[0],
        ["2024-01"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-01"], enum.ColType.TIME_WEEK, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_MONTH, ["2024-01"], enum.ColType.TIME_DAY, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2020-W52"], enum.ColType.TIME_YEAR, None
        )[0],
        ["2020"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2020-W52"],
            enum.ColType.TIME_YEAR,
            None,
            from_week="round",
        )[0],
        ["2020"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2020-W53"], enum.ColType.TIME_YEAR, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2020-W53"],
            enum.ColType.TIME_YEAR,
            None,
            from_week="round",
        )[0],
        ["2020"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2022-W52"], enum.ColType.TIME_YEAR, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2022-W52"],
            enum.ColType.TIME_YEAR,
            None,
            from_week="round",
        )[0],
        ["2022"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2023-W52"], enum.ColType.TIME_YEAR, None
        )[0],
        ["2023"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2023-W52"],
            enum.ColType.TIME_YEAR,
            None,
            from_week="round",
        )[0],
        ["2023"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2024-W01"], enum.ColType.TIME_YEAR, None
        )[0],
        ["2024"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2022-W52"], enum.ColType.TIME_QUARTER, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2022-W52"],
            enum.ColType.TIME_QUARTER,
            None,
            from_week="round",
        )[0],
        ["2022-Q4"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2023-W13"], enum.ColType.TIME_QUARTER, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2023-W13"],
            enum.ColType.TIME_QUARTER,
            None,
            from_week="round",
        )[0],
        ["2023-Q1"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2023-W17"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2023-Q2"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2023-W17"],
            enum.ColType.TIME_QUARTER,
            None,
            from_week="round",
        )[0],
        ["2023-Q2"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2023-W26"], enum.ColType.TIME_QUARTER, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2023-W26"],
            enum.ColType.TIME_QUARTER,
            None,
            from_week="round",
        )[0],
        ["2023-Q2"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2023-W39"], enum.ColType.TIME_QUARTER, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2023-W39"],
            enum.ColType.TIME_QUARTER,
            None,
            from_week="round",
        )[0],
        ["2023-Q3"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2023-W52"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2023-Q4"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2023-W52"],
            enum.ColType.TIME_QUARTER,
            None,
            from_week="round",
        )[0],
        ["2023-Q4"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2022-W52"], enum.ColType.TIME_MONTH, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2022-W52"],
            enum.ColType.TIME_MONTH,
            None,
            from_week="round",
        )[0],
        ["2022-12"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2023-W13"], enum.ColType.TIME_MONTH, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2023-W13"],
            enum.ColType.TIME_MONTH,
            None,
            from_week="round",
        )[0],
        ["2023-03"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2023-W17"], enum.ColType.TIME_MONTH, None
        )[0],
        ["2023-04"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2023-W17"],
            enum.ColType.TIME_MONTH,
            None,
            from_week="round",
        )[0],
        ["2023-04"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2023-W26"], enum.ColType.TIME_MONTH, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2023-W26"],
            enum.ColType.TIME_MONTH,
            None,
            from_week="round",
        )[0],
        ["2023-06"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2023-W39"], enum.ColType.TIME_MONTH, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2023-W39"],
            enum.ColType.TIME_MONTH,
            None,
            from_week="round",
        )[0],
        ["2023-09"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2023-W52"], enum.ColType.TIME_MONTH, None
        )[0],
        ["2023-12"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK,
            ["2023-W52"],
            enum.ColType.TIME_MONTH,
            None,
            from_week="round",
        )[0],
        ["2023-12"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2024-W01"], enum.ColType.TIME_WEEK, None
        )[0],
        ["2024-W01"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_WEEK, ["2024-W01"], enum.ColType.TIME_DAY, None
        )[0],
        [None],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2023-01-01"], enum.ColType.TIME_YEAR, None
        )[0],
        ["2023"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2023-01-01"], enum.ColType.TIME_QUARTER, None
        )[0],
        ["2023-Q1"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2023-01-01"], enum.ColType.TIME_MONTH, None
        )[0],
        ["2023-01"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2021-01-01"], enum.ColType.TIME_WEEK, None
        )[0],
        ["2020-W53"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2021-01-02"], enum.ColType.TIME_WEEK, None
        )[0],
        ["2020-W53"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2021-01-03"], enum.ColType.TIME_WEEK, None
        )[0],
        ["2020-W53"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2021-01-04"], enum.ColType.TIME_WEEK, None
        )[0],
        ["2021-W01"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2022-01-01"], enum.ColType.TIME_WEEK, None
        )[0],
        ["2021-W52"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2022-01-02"], enum.ColType.TIME_WEEK, None
        )[0],
        ["2021-W52"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2022-01-03"], enum.ColType.TIME_WEEK, None
        )[0],
        ["2022-W01"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2023-01-01"], enum.ColType.TIME_WEEK, None
        )[0],
        ["2022-W52"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2023-01-02"], enum.ColType.TIME_WEEK, None
        )[0],
        ["2023-W01"],
    )
    assert_equal(
        Etl.tfm_time_resolution(
            enum.ColType.TIME_DAY, ["2023-01-01"], enum.ColType.TIME_DAY, None
        )[0],
        ["2023-01-01"],
    )

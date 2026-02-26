import re
from datetime import datetime, timezone
from typing import Any

import polars as pl
import pytest
import xlsxwriter

# Initialize non-aggregated test data: tests incl. their result, scenarios, and the link between them
tests: list[dict[str, Any]] = []
scenario_ids: set[str] = set()
test_scenario_links: list[dict[str, str]] = []


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> None:
    """custom pytest hook to parse the docstring of the test function."""
    if call.when == "call":
        curr_scenarios = set()
        # Add scenario IDs from parent class
        parent = item.parent
        mark: pytest.Mark | None
        if isinstance(parent, pytest.Class):
            mark = parent.keywords.get("scenario_ids")
            if mark:
                for arg in mark.args:
                    curr_scenarios.update(re.split(r"\s*,\s*", arg))
        # Add scenario IDs from test
        if isinstance(item, pytest.Function):
            mark = item.keywords.get("scenario_ids")
            if mark:
                curr_scenarios.update(re.split(r"\s*,\s*", mark.args[0]))
        else:
            raise AssertionError(f"Unknown item of type {type(item)}")
        # Add test
        tests.append(
            {
                "id": item.nodeid,
                "outcome": "PASS" if call.excinfo is None else "FAIL",
                "doc": item.function.__doc__,
                "datetime": datetime.now(timezone.utc),
                "duration": call.duration,
            }
        )
        # Add scenario
        scenario_ids.update(curr_scenarios)
        # Add scenario-test link
        test_scenario_links.extend(
            [
                {"scenario_id": scenario_id, "test_id": item.nodeid}
                for scenario_id in curr_scenarios
            ]
        )


def generate_excel_report(
    tests: list[dict[str, Any]], file_path: str, verbose: bool = True
) -> None:
    """
    Generate Excel file with two sheets:
    1. Individual test results
    2. Aggregated by scenario ID
    """
    for test in tests:
        _remove_timezone_from_datetime(test)

    test_df = pl.DataFrame(tests)
    scenario_df = pl.DataFrame([{"id": x} for x in sorted(scenario_ids)])
    test_scenario_link_df = pl.DataFrame(test_scenario_links)

    # Outer join test and test_scenario_link
    test_with_scenarios_df = test_df.join(
        test_scenario_link_df, left_on="id", right_on="test_id", how="left"
    ).rename({"id": "test_id"})

    # Aggregate data by scenario:
    # Count n_passed and n_failed separately
    # Add durations
    # Add status PASS if n_failed==0
    result_by_scenario_df = (
        # test_with_scenarios_df.filter(pl.col("scenario_id").is_not_null())
        test_with_scenarios_df.group_by("scenario_id")
        .agg(
            [
                pl.len().alias("n_total"),
                (pl.col("outcome") == "PASS").sum().alias("n_passed"),
                (pl.col("outcome") == "FAIL").sum().alias("n_failed"),
                pl.sum("duration").alias("duration"),
            ]
        )
        .with_columns(
            [
                pl.when(pl.col("n_failed") == 0)
                .then(pl.lit("PASS"))
                .otherwise(pl.lit("FAIL"))
                .alias("status")
            ]
        )
    )

    # Aggregate data by test:
    # Count n_scenarios
    # Add min(durations)
    # Add status PASS if n_failed==0 else FAIL
    result_by_test_df = test_with_scenarios_df.group_by("test_id").agg(
        [
            pl.col("scenario_id").drop_nulls().n_unique().alias("n_scenarios"),
            pl.min("duration").alias("min_duration"),
            pl.first("outcome").alias("status"),
            pl.first("doc").alias("doc"),
            pl.first("datetime").alias("datetime"),
        ]
    )

    # Write out
    with xlsxwriter.Workbook(file_path) as workbook:
        test_df.write_excel(workbook, worksheet="test")
        scenario_df.write_excel(workbook, worksheet="scenario")
        test_scenario_link_df.write_excel(workbook, worksheet="test_scenario_link")
        result_by_scenario_df.write_excel(workbook, worksheet="result_by_scenario")
        result_by_test_df.write_excel(workbook, worksheet="result_by_test")
    if verbose:
        print(f"\nAnalysis complete. Results written to: {file_path}")
    return


def _remove_timezone_from_datetime(test: list[dict[str, Any]]) -> None:
    datetime_obj = test.get("datetime")  # type: ignore[attr-defined]
    if isinstance(datetime_obj, datetime) and datetime_obj.tzinfo is not None:
        test["datetime"] = datetime_obj.replace(tzinfo=None)  # type: ignore[call-overload]


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """custom pytest hook to perform actions at the end of the test session."""
    # only create report if there is data to report
    if tests and scenario_ids and test_scenario_links:
        generate_excel_report(tests, "test/output/test_report.xlsx")

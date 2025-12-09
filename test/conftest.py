import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from openpyxl import Workbook

test_results: list[dict[str, object]] = []


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """custom pytest hook to parse the docstring of the test function."""
    if call.when == "call":
        scenario_ids = []
        if item.function.__doc__:
            matches = re.findall(r"test_scenario_id=([^\r\n]+)", item.function.__doc__)
            scenario_ids = [x.strip() for x in matches]

        outcome = call.excinfo is None  # True if passed, False if failed
        result = "Pass" if outcome else "Fail"

        test_results.append(
            {
                "test_name": item.nodeid,
                "scenario_ids": scenario_ids,
                "result": result,
                "result_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "duration": call.duration,
            }
        )


def generate_excel_report(results: list[dict[str, object]], file_path: str) -> None:
    """
    Generate Excel file with two sheets:
    1. Aggregated by scenario ID
    2. Individual test results
    """
    aggregated_results: dict[str, dict[str, object]] = {}
    detailed_rows: list[tuple[str, str, str, str, float]] = []

    for result in results:
        test_name = str(result.get("test_name", ""))
        result_date = str(result.get("result_date", ""))
        result = str(result.get("result", "Fail"))
        duration = float(result.get("duration", 0.0))
        scenario_ids: list[Any] = result.get("scenario_ids") or []

        # If a test has no scenario_ids, include a blank id in details
        if not scenario_ids:
            detailed_rows.append((test_name, "", result_date, result, duration))

        for scenario_id in scenario_ids:
            # Details row per scenario id
            detailed_rows.append(
                (test_name, scenario_id, result_date, result, duration)
            )

            # Initialize aggregation entry
            if scenario_id not in aggregated_results:
                aggregated_results[scenario_id] = {
                    "id": scenario_id,
                    "result_date": result_date,
                    "all_pass": True,  # start optimistic; flip to False on any Fail
                }
            # Update pass/fail
            if result != "Pass":
                aggregated_results[scenario_id]["all_pass"] = False
            # Update result_date to the most recent
            try:
                current_datetime = datetime.strptime(
                    str(aggregated_results[scenario_id]["result_date"]),
                    "%Y-%m-%d %H:%M:%S",
                )
                new_datetime = datetime.strptime(result_date, "%Y-%m-%d %H:%M:%S")
                if new_datetime > current_datetime:
                    aggregated_results[scenario_id]["result_date"] = result_date
            except Exception:
                # Fallback: overwrite if parsing fails
                aggregated_results[scenario_id]["result_date"] = result_date

    # Prepare workbook
    workbook = Workbook()

    # Aggregated sheet
    aggregated_results_sheet = workbook.active
    aggregated_results_sheet.title = "Aggregated"
    aggregated_results_sheet.append(["id", "result_date", "result"])
    for scenario_id, data in aggregated_results.items():
        aggregated_results_sheet.append(
            [data["id"], data["result_date"], "Pass" if data["all_pass"] else "Fail"]
        )

    # Details sheet
    detailed_results_sheet = workbook.create_sheet("Details")
    detailed_results_sheet.append(
        ["test_name", "scenario_id", "result_date", "result", "duration"]
    )
    for row in detailed_rows:
        detailed_results_sheet.append(list(row))

    # Ensure directory exists and save
    out_path = Path(file_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(out_path)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """custom pytest hook to perform actions at the end of the test session."""
    if test_results:
        generate_excel_report(test_results, "test/output/test_report.xlsx")

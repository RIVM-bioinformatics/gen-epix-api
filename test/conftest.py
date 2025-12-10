import re
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import pytest
from openpyxl import Workbook

test_results: list[dict[str, str | list[str] | Literal["Pass", "Fail"] | float]] = []


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> None:
    """custom pytest hook to parse the docstring of the test function."""
    if call.when == "call":
        scenario_ids: list[str] = []
        if item.function.__doc__:  # type: ignore[attr-defined]
            matches = re.findall(r"test_scenario_id=([^\r\n]+)", item.function.__doc__)  # type: ignore[attr-defined]
            scenario_ids = [x.strip() for x in matches]

        outcome = call.excinfo is None
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


def generate_excel_report(
    results: list[dict[str, str | list[str] | Literal["Pass", "Fail"] | float]],
    file_path: str,
) -> None:
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
        test_result = str(result.get("result", "Fail"))
        duration = float(result.get("duration", 0.0))  # type: ignore[arg-type]
        scenario_ids: list[str] = result.get("scenario_ids") or []  # type: ignore[assignment]

        if not scenario_ids:
            detailed_rows.append((test_name, "", result_date, test_result, duration))

        for scenario_id in scenario_ids:
            detailed_rows.append(
                (test_name, scenario_id, result_date, test_result, duration)
            )
            # Initialize aggregation entry
            if scenario_id not in aggregated_results:
                aggregated_results[scenario_id] = {
                    "id": scenario_id,
                    "result_date": result_date,
                    "all_pass": True,  # flip to False on any Fail
                }
            if test_result != "Pass":
                aggregated_results[scenario_id]["all_pass"] = False
            try:
                current_datetime = datetime.strptime(
                    str(aggregated_results[scenario_id]["result_date"]),
                    "%Y-%m-%d %H:%M:%S",
                )
                new_datetime = datetime.strptime(result_date, "%Y-%m-%d %H:%M:%S")
                if new_datetime > current_datetime:
                    aggregated_results[scenario_id]["result_date"] = result_date
            except ValueError:
                # Fallback: overwrite if parsing fails
                aggregated_results[scenario_id]["result_date"] = result_date

    save_excel_report(file_path, aggregated_results, detailed_rows)


def save_excel_report(
    file_path: str,
    aggregated_results: dict[str, dict[str, object]],
    detailed_rows: list[tuple[str, str, str, str, float]],
) -> None:
    workbook = Workbook()
    # Aggregated sheet
    aggregated_results_sheet = workbook.active
    assert aggregated_results_sheet is not None

    aggregated_results_sheet.title = "Aggregated"
    aggregated_results_sheet.append(["id", "result_date", "result"])
    for _, data in aggregated_results.items():
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

    out_path = Path(file_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(out_path)

    print(
        f"\n\nExcel report with linked test scenarios saved to: {out_path.resolve()}\n"
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """custom pytest hook to perform actions at the end of the test session."""
    if test_results:
        generate_excel_report(test_results, "test/output/test_report.xlsx")

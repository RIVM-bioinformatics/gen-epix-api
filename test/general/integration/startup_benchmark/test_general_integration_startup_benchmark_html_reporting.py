"""Exercise offline controls with optional Playwright and a Chromium browser.

Set STARTUP_DASHBOARD_BROWSER to use an existing browser executable instead of
Playwright's installed Chromium. No application services or network are used.
"""

import copy
import dataclasses
import os

import pytest

from scripts.startup_benchmark.diagnostics import parse_imports
from scripts.startup_benchmark.html_reporting import generate_html
from scripts.startup_benchmark.models import RunRecord

pytestmark = pytest.mark.integration


@pytest.fixture
def dashboard(tmp_path):
    data = {
        "schema_version": 1,
        "application": "casedb",
        "command": "benchmark",
        "options": {"idp_mode": "NONE", "repository_mode": "DICT_EMPTY"},
        "metadata": {"commit": "abc"},
        "configuration_valid": True,
        "series_completed": True,
        "configuration_fingerprint": "same",
        "records": [
            dataclasses.asdict(
                RunRecord(
                    i + 1,
                    "measured",
                    status="success",
                    seconds=2 + i / 100,
                    cleanup="ok",
                )
            )
            for i in range(30)
        ]
        + [
            dataclasses.asdict(
                RunRecord(31, "measured", status="timeout", error="Timed out")
            ),
            dataclasses.asdict(RunRecord(32, "measured")),
            dataclasses.asdict(
                RunRecord(33, "warmup", status="success", seconds=90, cleanup="ok")
            ),
        ],
    }
    diagnostics = copy.deepcopy(data)
    diagnostics["command"] = "diagnose"
    unsafe = "</script><script>window.dashboardInjected=true</script>"
    lines = [
        f"import time: {i + 1} | {(66 - i) * 10} | {unsafe if i == 0 else 'repeated'}"
        for i in range(65)
    ]
    diagnostics["diagnostics"] = [
        {"kind": "imports", "run": 1, "analysis": parse_imports("\n".join(lines))},
        {
            "kind": "imports",
            "run": 2,
            "analysis": parse_imports("import time: 100 | 100 | second_run"),
        },
    ]
    output = tmp_path / "report.html"
    generate_html(data, output, diagnostics)
    return output, data


@pytest.fixture
def browser_page():
    api = pytest.importorskip("playwright.sync_api")
    with api.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(
                executable_path=os.environ.get("STARTUP_DASHBOARD_BROWSER"),
                headless=True,
            )
        except api.Error as error:
            if "Executable doesn't exist" in str(error):
                pytest.skip(
                    "Install Chromium with python -m playwright install chromium"
                )
            raise
        context = browser.new_context(
            offline=True, viewport={"width": 1280, "height": 900}
        )
        page = context.new_page()
        errors, network = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on(
            "console",
            lambda message: (
                errors.append(message.text) if message.type == "error" else None
            ),
        )
        page.on(
            "request",
            lambda request: (
                network.append(request.url)
                if request.url.startswith(("http:", "https:"))
                else None
            ),
        )
        try:
            yield page
            assert not errors
            assert not network
        finally:
            context.close()
            browser.close()


def load_dashboard(page, path):
    page.goto(path.as_uri())
    page.wait_for_function("document.getElementById('import-chart').data !== undefined")


def test_offline_run_filters_sorting_trend_and_histogram(dashboard, browser_page):
    path, _ = dashboard
    page = browser_page
    load_dashboard(page, path)
    summary = page.locator("#summary-title").locator("..").inner_text()
    assert page.locator("#attempts tr").count() == 33
    assert "30 of 30" in page.locator("#selected-count").inner_text()
    assert page.evaluate(
        "document.getElementById('startup-chart').data[0].y.slice(-2)"
    ) == [None, None]
    assert (
        page.evaluate("document.getElementById('startup-chart').data[2].yaxis") == "y2"
    )
    averages = page.evaluate(
        "document.getElementById('startup-chart').data[1].y.slice(0, 5)"
    )
    assert averages[:4] == [None] * 4
    assert averages[4] == pytest.approx(2.02)
    page.locator("#run-min").fill("5")
    page.locator("#run-max").fill("10")
    assert "6 of 30" in page.locator("#selected-count").inner_text()
    assert page.locator("#attempts tr").count() == 6
    assert page.locator("#summary-title").locator("..").inner_text() == summary
    page.locator("#trend").uncheck()
    assert page.evaluate("document.getElementById('startup-chart').data.length") == 1
    page.locator("#bins").fill("3")
    assert page.evaluate("document.getElementById('histogram').data[0].nbinsx") == 3
    page.locator("#reset").click()
    page.locator("#kind").select_option("warmup")
    assert page.locator("#attempts tr").count() == 1
    assert "90.000" in page.locator("#attempts").inner_text()
    page.locator("#reset").click()
    page.locator("#status").select_option("success")
    page.locator("#attempt-sort").select_option("seconds")
    page.locator("#attempt-order").select_option("desc")
    assert page.locator("#attempts tr").first.locator("td").first.inner_text() == "33"
    page.locator("#reset").click()
    screenshot = os.environ.get("STARTUP_DASHBOARD_SCREENSHOT")
    if screenshot:
        page.screenshot(path=screenshot, full_page=True)
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_function("document.documentElement.scrollWidth <= window.innerWidth")


def test_offline_import_sort_search_pagination_and_selection(dashboard, browser_page):
    path, _ = dashboard
    page = browser_page
    load_dashboard(page, path)
    assert page.locator("#import-rows tr").count() == 50
    assert (
        page.locator("#import-rows tr").first.locator("td").first.inner_text() == "64"
    )
    page.locator("#next").click()
    assert page.locator("#import-rows tr").count() == 15
    assert "Page 2 of 2" in page.locator("#page").inner_text()
    page.locator("#previous").click()
    page.locator("#import-sort").select_option("cumulative_us")
    assert page.locator("#import-rows tr").first.locator("td").first.inner_text() == "0"
    page.locator("#module-search").fill("script")
    assert page.locator("#import-rows tr").count() == 1
    assert page.evaluate("window.dashboardInjected === undefined")
    page.locator("#module-search").fill("no_matches")
    assert page.locator("#import-rows tr").count() == 0
    assert "0 of 65" in page.locator("#import-count").inner_text()
    page.locator("#module-search").fill("")
    page.locator("#import-run").select_option("1")
    assert page.locator("#import-rows tr").count() == 1
    assert "second_run" in page.locator("#import-rows").inner_text()
    page.locator("#reset").click()
    assert page.locator("#import-rows tr").count() == 50


@pytest.mark.parametrize("command", ["benchmark", "diagnose"])
def test_offline_empty_states(dashboard, browser_page, command):
    path, data = dashboard
    data["command"] = command
    data["records"] = []
    generate_html(data, path)
    page = browser_page
    page.goto(path.as_uri())
    page.wait_for_function("document.getElementById('histogram').data !== undefined")
    assert page.locator("#startup-empty").is_visible()
    assert page.locator("#imports-empty").is_visible()
    assert page.locator("#attempts tr").count() == 0
    assert "Unavailable" in page.locator(".metrics").inner_text()

import json

import pytest

from scripts.startup_benchmark import __main__ as cli
from scripts.startup_benchmark.models import RunRecord


@pytest.fixture
def series(tmp_path, monkeypatch):
    monkeypatch.setattr(
        cli,
        "capture",
        lambda options, env: {"files": {}, "environment": {}, "commit": "abc"},
    )
    monkeypatch.setattr(cli, "file_fingerprints", dict)
    monkeypatch.setattr(cli, "tls_context", lambda options: None)
    monkeypatch.setattr(
        cli, "configuration_snapshot", lambda *args: {"debug": False, "application": {}}
    )
    monkeypatch.setattr(cli.time, "sleep", lambda seconds: None)
    for key in (
        "PYTHONPROFILEIMPORTTIME",
        "COVERAGE_PROCESS_START",
        "COV_CORE_SOURCE",
        "COV_CORE_CONFIG",
        "COV_CORE_DATAFILE",
    ):
        monkeypatch.delenv(key, raising=False)

    def run(options, directory, index, kind, env):
        return RunRecord(index, kind, status="success", seconds=2, cleanup="ok")

    monkeypatch.setattr(cli, "run_once", run)
    args = cli.parser().parse_args(
        [
            "benchmark",
            "seqdb",
            "--idp-mode",
            "NONE",
            "--repository-mode",
            "DICT_EMPTY",
            "--runs",
            "30",
            "--output",
            str(tmp_path),
        ]
    )
    return args, tmp_path


def test_gate_and_incremental_persistence(series, monkeypatch):
    args, output = series
    args.check_target = True
    run = cli.run_once

    def checked(options, directory, index, kind, env):
        saved = json.loads((directory / "results.json").read_text())
        assert len(saved["records"]) == 30
        assert sum(r["status"] == "success" for r in saved["records"]) == index - 1
        return run(options, directory, index, kind, env)

    monkeypatch.setattr(cli, "run_once", checked)
    assert cli.execute(args) == 0
    assert json.loads((output / "results.json").read_text())["statistics"][
        "target_pass"
    ]


@pytest.mark.parametrize(
    "failure,exit_code,attempted",
    [("timeout", 1, 30), ("occupied_port", 1, 1), ("interrupted", 130, 1)],
)
def test_failure_and_partial_reports(
    series, monkeypatch, failure, exit_code, attempted
):
    args, output = series
    monkeypatch.setattr(
        cli,
        "run_once",
        lambda options, directory, index, kind, env: RunRecord(
            index, kind, status=failure, cleanup="ok"
        ),
    )
    assert cli.execute(args) == exit_code
    saved = json.loads((output / "results.json").read_text())
    assert saved["statistics"]["attempted"] == attempted
    assert (output / "report.md").exists()


def test_invalid_debug_retains_unattempted_series(series, monkeypatch):
    args, output = series
    monkeypatch.setattr(cli, "configuration_snapshot", lambda *args: {"debug": True})
    assert cli.execute(args) == 2
    saved = json.loads((output / "results.json").read_text())
    assert saved["statistics"]["unattempted"] == 30
    assert "debug=True" in saved["configuration_error"]


def test_small_sample_gate_and_cleanup_failure(series, monkeypatch):
    args, output = series
    args.runs = 2
    args.check_target = True
    assert cli.execute(args) == 1
    args.output = output / "failed-cleanup"
    monkeypatch.setattr(
        cli,
        "run_once",
        lambda options, directory, index, kind, env: RunRecord(
            index, kind, status="success", seconds=2, cleanup="failed"
        ),
    )
    assert cli.execute(args) == 1
    saved = json.loads((args.output / "results.json").read_text())
    assert not saved["configuration_valid"]
    assert saved["statistics"]["unattempted"] == 1


def test_configuration_changes_abort_series(series, monkeypatch):
    args, output = series
    monkeypatch.setattr(cli, "file_fingerprints", lambda: {"changed": "hash"})
    assert cli.execute(args) == 1
    saved = json.loads((output / "results.json").read_text())
    assert not saved["configuration_valid"]
    assert saved["configuration_changes"]
    assert saved["statistics"]["unattempted"] == 30


@pytest.mark.parametrize("key", ["PYTHONPROFILEIMPORTTIME", "COVERAGE_PROCESS_START"])
def test_normal_run_refuses_instrumentation(series, monkeypatch, key):
    args, _ = series
    monkeypatch.setenv(key, "1")
    with pytest.raises(ValueError, match="profiling or subprocess coverage"):
        cli.execute(args)


def test_interruption_after_final_measurement_invalidates_gate(series, monkeypatch):
    args, output = series
    sleeps = []

    def interrupt_last_settle(seconds):
        sleeps.append(seconds)
        if len(sleeps) == 30:
            raise KeyboardInterrupt

    monkeypatch.setattr(cli.time, "sleep", interrupt_last_settle)
    assert cli.execute(args) == 130
    saved = json.loads((output / "results.json").read_text())
    assert saved["statistics"]["successes"] == 30
    assert not saved["statistics"]["target_pass"]
    assert not saved["series_completed"]

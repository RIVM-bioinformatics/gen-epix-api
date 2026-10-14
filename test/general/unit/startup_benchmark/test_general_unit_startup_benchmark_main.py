import dataclasses
import json
import subprocess
import sys

import pytest

from scripts.startup_benchmark import __main__ as cli
from scripts.startup_benchmark.models import RunRecord


@pytest.fixture
def series(tmp_path, monkeypatch):
    # Process operations are mocked; exercise the supported platform on any host.
    monkeypatch.setattr(cli.sys, "platform", "linux")
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


@pytest.fixture
def report_inputs(tmp_path):
    data = {
        "schema_version": 1,
        "application": "seqdb",
        "command": "benchmark",
        "options": {"idp_mode": "NONE", "repository_mode": "DICT_EMPTY"},
        "metadata": {"commit": "abc"},
        "configuration_valid": True,
        "configuration_fingerprint": "same",
        "records": [
            dataclasses.asdict(
                RunRecord(1, "measured", status="success", seconds=2, cleanup="ok")
            )
        ],
    }
    source = tmp_path / "results.json"
    source.write_text(json.dumps(data))
    diagnostics = tmp_path / "diagnostics.json"
    diagnostics.write_text(json.dumps({**data, "command": "diagnose"}))
    return source, diagnostics


def invoke_report(monkeypatch, *arguments):
    monkeypatch.setattr(
        sys, "argv", ["benchmark_startup", "report", *map(str, arguments)]
    )
    return cli.main()


@pytest.mark.parametrize("attach", [False, True])
def test_html_report_dispatch_without_measurement(
    report_inputs, tmp_path, monkeypatch, capsys, attach
):
    source, diagnostics = report_inputs
    original = (source.read_bytes(), diagnostics.read_bytes())

    def forbidden(*args):
        pytest.fail("Reporting must not collect measurements")

    monkeypatch.setattr(cli, "execute", forbidden)
    output = tmp_path / "report.html"
    arguments = ["--input", source, "--output", output]
    if attach:
        arguments += ["--diagnostics", diagnostics]
    assert invoke_report(monkeypatch, *arguments) == 0
    assert output.read_text().startswith("<!doctype html>")
    assert str(output) in capsys.readouterr().out
    assert (source.read_bytes(), diagnostics.read_bytes()) == original


def test_legacy_directory_report_unchanged(report_inputs, tmp_path, monkeypatch):
    source, diagnostics = report_inputs
    output = tmp_path / "directory"
    assert (
        invoke_report(
            monkeypatch, source, "--diagnostics", diagnostics, "--output", output
        )
        == 0
    )
    assert {p.name for p in output.iterdir()} == {
        "report.md",
        "startup.svg",
        "results.json",
        "diagnostics.json",
    }


@pytest.mark.parametrize("both", [False, True])
def test_report_requires_exactly_one_input(
    report_inputs, tmp_path, monkeypatch, capsys, both
):
    source, _ = report_inputs
    arguments = [source, "--input", source] if both else []
    output = tmp_path / "report.html"
    assert invoke_report(monkeypatch, *arguments, "--output", output) == 2
    assert "exactly one" in capsys.readouterr().err
    assert not output.exists()


@pytest.mark.parametrize("overwrite", ["results", "diagnostics", "symlink", "hardlink"])
def test_report_rejects_input_overwrite(
    report_inputs, tmp_path, monkeypatch, capsys, overwrite
):
    source, diagnostics = report_inputs
    original = (source.read_bytes(), diagnostics.read_bytes())
    output = source if overwrite == "results" else diagnostics
    if overwrite in ("symlink", "hardlink"):
        output = tmp_path / "alias.html"
        if overwrite == "symlink":
            output.symlink_to(source)
        else:
            output.hardlink_to(source)
    assert (
        invoke_report(
            monkeypatch,
            "--input",
            source,
            "--diagnostics",
            diagnostics,
            "--output",
            output,
        )
        == 2
    )
    assert "overwrite" in capsys.readouterr().err
    assert (source.read_bytes(), diagnostics.read_bytes()) == original


@pytest.mark.parametrize("contents", ["[]", "null", "{", '{"schema_version": 90}'])
def test_html_report_invalid_json_exits_two(
    report_inputs, tmp_path, monkeypatch, contents
):
    source, _ = report_inputs
    source.write_text(contents)
    output = tmp_path / "report.html"
    assert invoke_report(monkeypatch, "--input", source, "--output", output) == 2
    assert not output.exists()


@pytest.mark.parametrize("failure", ["suffix", "missing", "write", "incompatible"])
def test_html_report_errors_exit_two(report_inputs, tmp_path, monkeypatch, failure):
    source, diagnostics = report_inputs
    output = tmp_path / "report.html"
    arguments = []
    if failure == "suffix":
        output = tmp_path / "directory"
    elif failure == "missing":
        source = tmp_path / "missing.json"
    elif failure == "write":
        parent = tmp_path / "file"
        parent.write_text("blocking file")
        output = parent / "report.html"
    else:
        data = json.loads(diagnostics.read_text())
        data["configuration_fingerprint"] = "different"
        diagnostics.write_text(json.dumps(data))
        arguments = ["--diagnostics", diagnostics]
    assert (
        invoke_report(monkeypatch, "--input", source, *arguments, "--output", output)
        == 2
    )
    assert not output.exists()


def test_dashboard_dependencies_not_loaded_by_entrypoint():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; import scripts.startup_benchmark.__main__; "
                'assert not any(k.split(".")[0] in ("jinja2", "plotly", "gen_epix") '
                "for k in sys.modules)"
            ),
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

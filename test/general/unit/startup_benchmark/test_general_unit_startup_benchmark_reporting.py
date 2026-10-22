import dataclasses
import json
import xml.etree.ElementTree as ET

import pytest

from scripts.startup_benchmark.metadata import redact
from scripts.startup_benchmark.models import RunRecord
from scripts.startup_benchmark.reporting import (
    compatible,
    generate,
    load_json,
    save_json,
)


def artifact():
    return {
        "schema_version": 1,
        "application": "seqdb",
        "command": "benchmark",
        "options": {"idp_mode": "NONE", "repository_mode": "DICT_EMPTY"},
        "configuration_valid": True,
        "configuration_fingerprint": "a",
        "metadata": {"commit": "abc"},
        "records": [
            dataclasses.asdict(RunRecord(1, "measured", status="timeout")),
            dataclasses.asdict(RunRecord(2, "measured")),
        ],
    }


def test_roundtrip_partial_report_and_svg(tmp_path):
    data = artifact()
    data["records"][0]["stderr"] = "a|b<script>&\n"
    summary = generate(data, tmp_path)
    assert "0/2" in summary
    assert load_json(tmp_path / "results.json") == data
    ET.parse(tmp_path / "startup.svg")
    markdown = (tmp_path / "report.md").read_text()
    assert "&lt;script&gt;" in markdown
    assert "a&#124;b" in markdown
    assert data["statistics"]["p95"] is None


def test_schema_and_compatibility(tmp_path):
    data = artifact()
    assert compatible(data, artifact())
    other = artifact()
    other["configuration_fingerprint"] = "b"
    with pytest.raises(ValueError):
        generate(data, tmp_path, other)
    save_json(tmp_path / "bad.json", {"schema_version": 90})
    with pytest.raises(ValueError):
        load_json(tmp_path / "bad.json")


def test_redaction():
    value = {
        "password": "unsafe",
        "nested": {"token": "unsafe"},
        "url": "sql://user:unsafe@host/db",
        "other": "pwd=unsafe;server=local",
    }
    assert "unsafe" not in json.dumps(redact(value))


def test_diagnostic_charts_and_offline_attachment(tmp_path):
    from scripts.startup_benchmark.diagnostics import analyze_phases, parse_imports

    data = artifact()
    diagnostics = artifact()
    diagnostics["command"] = "diagnose"
    diagnostics["diagnostics"] = [
        {
            "kind": "imports",
            "analysis": parse_imports("import time: 10 | 10 | <root>&"),
        },
        {
            "kind": "phases",
            "analysis": analyze_phases(
                [
                    {
                        "event": "start",
                        "id": 1,
                        "parent": None,
                        "label": "<app>",
                        "name": "span",
                        "async": False,
                        "time_ns": 1,
                    },
                    {"event": "end", "id": 1, "time_ns": 100, "state": "complete"},
                ]
            ),
        },
    ]
    generate(data, tmp_path, diagnostics)
    for path in tmp_path.glob("*.svg"):
        ET.parse(path)
    assert (tmp_path / "diagnostics.json").exists()
    assert "&lt;root&gt;" in (tmp_path / "report.md").read_text()

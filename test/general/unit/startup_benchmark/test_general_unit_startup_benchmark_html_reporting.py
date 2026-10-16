import builtins
import copy
import dataclasses
import json
import re
from html.parser import HTMLParser

import pytest

from scripts.startup_benchmark import html_reporting
from scripts.startup_benchmark.diagnostics import parse_imports
from scripts.startup_benchmark.models import RunRecord
from scripts.startup_benchmark.statistics import summarize


@pytest.fixture
def artifact():
    return {
        "schema_version": 1,
        "application": "seqdb",
        "command": "benchmark",
        "options": {"idp_mode": "NONE", "repository_mode": "DICT_EMPTY"},
        "configuration_valid": True,
        "series_completed": True,
        "configuration_fingerprint": "same-configuration",
        "metadata": {"commit": "abc"},
        "records": [
            dataclasses.asdict(
                RunRecord(i + 1, "measured", status="success", seconds=14, cleanup="ok")
            )
            for i in range(30)
        ],
    }


@pytest.fixture
def diagnostics(artifact):
    result = copy.deepcopy(artifact)
    result["command"] = "diagnose"
    result["records"] = [
        dataclasses.asdict(
            RunRecord(1, "imports", status="success", seconds=100, cleanup="ok")
        )
    ]
    result["diagnostics"] = [
        {
            "kind": "imports",
            "run": 1,
            "analysis": parse_imports(
                "import time: 10 | 10 |   repeated\n"
                "import time: 20 | 20 |   repeated\n"
                "import time: 5 | 35 | root\n"
            ),
        },
        {"kind": "phases", "run": 2, "analysis": {}},
    ]
    return result


def read_payload(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="benchmark-data" type="application/json">(.*?)</script>',
        text,
        flags=re.DOTALL,
    )
    return json.loads(match.group(1))


@pytest.mark.parametrize("application", ["casedb", "seqdb", "omopdb"])
def test_standalone_report_and_input_immutability(artifact, tmp_path, application):
    artifact["application"] = application
    artifact["statistics"] = {"p95": 900}
    artifact["records"][0]["stderr"] = str(tmp_path / "nonexistent.log")
    original = copy.deepcopy(artifact)
    output = tmp_path / "new" / "report.html"
    assert str(output) in html_reporting.generate_html(artifact, output)
    payload = read_payload(output)
    assert payload["statistics"]["p95"] == 14
    assert payload["statistics"]["target_pass"] is True
    assert payload["imports"] == []
    assert "stderr" not in payload["records"][0]
    assert artifact == original
    text = output.read_text()
    assert f"{application} startup benchmark" in text
    assert text.count('<script id="plotly-bundle">') == 1
    assert text.count("plotly.js v") == 1

    class Resources(HTMLParser):
        def handle_starttag(self, tag, attrs):
            attributes = dict(attrs)
            if tag in ("script", "img", "iframe"):
                assert "src" not in attributes
            if tag == "link":
                assert "href" not in attributes

    Resources().feed(text)


@pytest.mark.parametrize(
    "values,complete,failure,expected_p95,expected_pass",
    [
        ([14] * 30, True, None, 14, True),
        ([15] * 30, True, None, 15, False),
        (list(range(1, 31)), True, None, 29, False),
        ([1, 3], True, None, 3, False),
        ([], True, None, None, False),
        ([14] * 30, False, None, 14, False),
        ([14] * 30, True, "timeout", 14, False),
        ([14] * 30, True, "not_attempted", 14, False),
    ],
)
def test_statistics_boundaries(
    artifact, tmp_path, values, complete, failure, expected_p95, expected_pass
):
    artifact["records"] = [
        dataclasses.asdict(
            RunRecord(i + 1, "measured", status="success", seconds=v, cleanup="ok")
        )
        for i, v in enumerate(values)
    ]
    if failure:
        artifact["records"].append(
            dataclasses.asdict(RunRecord(len(values) + 1, "measured", status=failure))
        )
    artifact["series_completed"] = complete
    output = tmp_path / "report.htm"
    html_reporting.generate_html(artifact, output)
    stats = read_payload(output)["statistics"]
    assert stats == summarize(artifact["records"], True, complete)
    assert stats["p95"] == expected_p95
    assert stats["target_pass"] is expected_pass
    if values:
        assert stats["mean"] == pytest.approx(sum(values) / len(values))
        assert stats["minimum"] == min(values)
        assert stats["maximum"] == max(values)


def test_nonmeasured_times_excluded(artifact, tmp_path):
    for i, kind in enumerate(("warmup", "imports", "phases"), 31):
        artifact["records"].append(
            dataclasses.asdict(
                RunRecord(i, kind, status="success", seconds=900, cleanup="ok")
            )
        )
    output = tmp_path / "report.html"
    html_reporting.generate_html(artifact, output)
    stats = read_payload(output)["statistics"]
    assert stats["mean"] == stats["median"] == stats["p95"] == 14
    assert stats["requested"] == 30


def test_full_import_occurrences_and_diagnostic_only(artifact, diagnostics, tmp_path):
    originals = copy.deepcopy((artifact, diagnostics))
    output = tmp_path / "attached.html"
    html_reporting.generate_html(artifact, output, diagnostics)
    imports = read_payload(output)["imports"]
    assert len(imports) == 1
    assert imports[0]["records"] == [
        {k: r[k] for k in ("id", "module", "self_us", "cumulative_us", "chain")}
        for r in diagnostics["diagnostics"][0]["analysis"]["records"]
    ]
    assert [r["module"] for r in imports[0]["records"]].count("repeated") == 2
    assert (artifact, diagnostics) == originals
    html_reporting.generate_html(diagnostics, output)
    payload = read_payload(output)
    assert payload["imports"] == imports
    assert payload["statistics"]["p95"] is None
    assert payload["statistics"]["requested"] == 0


def test_html_safe_data(artifact, diagnostics, tmp_path):
    unsafe = '</script><script>window.injected=true</script>&"<img src=x>'
    artifact["options"]["idp_mode"] = unsafe
    artifact["records"][0]["error"] = unsafe
    diagnostics["diagnostics"][0]["analysis"]["records"][0]["module"] = unsafe
    output = tmp_path / "safe.html"
    html_reporting.generate_html(artifact, output, diagnostics)
    text = output.read_text()
    assert unsafe not in text
    assert "&lt;/script&gt;" in text
    payload = read_payload(output)
    assert payload["records"][0]["error"] == unsafe
    assert payload["imports"][0]["records"][0]["module"] == unsafe


@pytest.mark.parametrize(
    "path,value",
    [
        (("schema_version",), 90),
        (("application",), []),
        (("command",), "other"),
        (("metadata",), {}),
        (("options", "idp_mode"), None),
        (("configuration_valid",), "true"),
        (("series_completed",), None),
        (("records",), {}),
        (("records", 0), None),
        (("records", 0, "index"), True),
        (("records", 0, "status"), None),
        (("records", 0, "seconds"), None),
        (("records", 0, "seconds"), -1),
        (("records", 0, "seconds"), float("nan")),
        (("records", 0, "seconds"), float("inf")),
        (("records", 0, "seconds"), True),
        (("records", 0, "index"), 2),
        (("records", 0, "error"), {}),
    ],
)
def test_malformed_artifacts_rejected(artifact, tmp_path, path, value):
    parent = artifact
    for key in path[:-1]:
        parent = parent[key]
    parent[path[-1]] = value
    output = tmp_path / "report.html"
    with pytest.raises(ValueError, match="Invalid"):
        html_reporting.generate_html(artifact, output)
    assert not output.exists()


@pytest.mark.parametrize("data", [None, [], "invalid"])
def test_nonobject_artifacts_rejected(data, tmp_path):
    with pytest.raises(ValueError, match="Invalid"):
        html_reporting.generate_html(data, tmp_path / "report.html")


@pytest.mark.parametrize(
    "path,value",
    [
        (("run",), "one"),
        (("analysis",), None),
        (("analysis", "records"), None),
        (("analysis", "warnings"), None),
        (("analysis", "interpretation"), None),
        (("analysis", "records", 0, "self_us"), -1),
        (("analysis", "records", 0, "cumulative_us"), True),
        (("analysis", "records", 0, "chain"), "root"),
        (("analysis", "records", 0, "module"), None),
    ],
)
def test_malformed_imports_rejected(diagnostics, tmp_path, path, value):
    parent = diagnostics["diagnostics"][0]
    for key in path[:-1]:
        parent = parent[key]
    parent[path[-1]] = value
    with pytest.raises(ValueError, match="Invalid import"):
        html_reporting.generate_html(diagnostics, tmp_path / "report.html")


@pytest.mark.parametrize(
    "key,value",
    [
        ("application", "casedb"),
        ("configuration_fingerprint", "different"),
        ("configuration_valid", False),
        ("metadata", {"commit": "different"}),
    ],
)
def test_incompatible_diagnostics_rejected(artifact, diagnostics, tmp_path, key, value):
    diagnostics[key] = value
    with pytest.raises(ValueError, match="does not match"):
        html_reporting.generate_html(artifact, tmp_path / "report.html", diagnostics)


@pytest.mark.parametrize("dependency", ["jinja2", "plotly.offline"])
def test_missing_dependencies_explain_installation(
    artifact, tmp_path, monkeypatch, dependency
):
    original_import = builtins.__import__

    def import_without_dependency(name, *args, **kwargs):
        if name == dependency:
            raise ImportError("unavailable")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_dependency)
    with pytest.raises(ValueError, match="pip install -r dev-requirements.txt"):
        html_reporting.generate_html(artifact, tmp_path / "report.html")


def test_atomic_write_failure_preserves_existing_output(
    artifact, tmp_path, monkeypatch
):
    output = tmp_path / "report.html"
    output.write_text("previous report")

    def denied(*args):
        raise PermissionError("denied")

    monkeypatch.setattr(html_reporting.os, "replace", denied)
    with pytest.raises(PermissionError):
        html_reporting.generate_html(artifact, output)
    assert output.read_text() == "previous report"
    assert list(tmp_path.iterdir()) == [output]


def test_output_suffix_required(artifact, tmp_path):
    with pytest.raises(ValueError, match=".html or .htm"):
        html_reporting.generate_html(artifact, tmp_path / "directory")

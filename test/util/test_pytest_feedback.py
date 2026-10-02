import ast
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "util" / "pytest_feedback.py"
RUN_PY = REPO / "run.py"

_spec = importlib.util.spec_from_file_location("pytest_feedback", SCRIPT)
assert _spec and _spec.loader
pf = importlib.util.module_from_spec(_spec)
sys.modules["pytest_feedback"] = pf
_spec.loader.exec_module(pf)

ALL_PASS_XML = """<testsuites><testsuite name="pytest" tests="2" time="1.5">
<testcase classname="test.test_a" name="test_one" file="test/test_a.py" time="0.1"/>
<testcase classname="test.test_a" name="test_two" file="test/test_a.py" time="0.1"/>
</testsuite></testsuites>"""

ASSERT_XML = """<testsuites><testsuite name="pytest" tests="3" time="2.0">
<testcase classname="test.test_a.TestX" name="test_bad" file="test/test_a.py">
<failure message="assert 1 == 2">    def test_bad(self):
&gt;       assert 1 == 2
E       assert 1 == 2

test/test_a.py:7: AssertionError</failure></testcase>
<testcase classname="test.test_a" name="test_ok" file="test/test_a.py"/>
<testcase classname="test.test_a" name="test_skip" file="test/test_a.py">
<skipped type="pytest.skip" message="s"/></testcase>
</testsuite></testsuites>"""

COLLECTION_XML = """<testsuites><testsuite name="pytest" tests="1" errors="1">
<testcase classname="" name="test.test_b" file="">
<error message="collection failure">test/test_b.py:1: in &lt;module&gt;
    import nonexistent
E   ModuleNotFoundError: No module named 'nonexistent'</error></testcase>
</testsuite></testsuites>"""


def _many_failures_xml(n: int, long_trace: bool = False) -> str:
    trace = "\n".join(f"line {i}" for i in range(100)) if long_trace else "x"
    cases = "".join(
        f'<testcase classname="test.t" name="t{i}" file="test/t.py">'
        f'<failure message="assert False">{trace}\ntest/t.py:{i + 1}: AssertionError'
        f"</failure></testcase>"
        for i in range(n)
    )
    return f"<testsuites><testsuite tests='{n}'>{cases}</testsuite></testsuites>"


def _parse(tmp_path: Path, xml: str) -> dict[str, Any]:
    path = tmp_path / "r.xml"
    path.write_text(xml, encoding="utf-8")
    parsed = pf.parse_junit(path, tmp_path)
    assert parsed is not None
    return parsed


def _summary(parsed: Any, returncode: int = 1, **kw: Any) -> dict[str, Any]:
    return pf.build_summary(
        "fast",
        ["pytest"],
        returncode,
        kw.pop("timed_out", False),
        10,
        parsed,
        kw.pop("log_text", ""),
        **kw,
    )


# parsing


def test_pytest_feedback_parse_all_pass(tmp_path: Path) -> None:
    summary = _summary(_parse(tmp_path, ALL_PASS_XML), returncode=0)
    assert summary["status"] == "passed"
    assert (summary["total"], summary["passed"], summary["failed"]) == (2, 2, 0)
    assert summary["failures"] == []
    assert summary["truncated"] == {"truncated": False, "omitted_failures": 0}
    assert "No action required" in pf.render_feedback(summary)


def test_pytest_feedback_parse_assertion_failure(tmp_path: Path) -> None:
    summary = _summary(_parse(tmp_path, ASSERT_XML))
    assert summary["status"] == "failed"
    assert (summary["failed"], summary["skipped"], summary["passed"]) == (1, 1, 1)
    (failure,) = summary["failures"]
    assert failure["rank"] == 1
    assert failure["test"] == "test/test_a.py::TestX::test_bad"
    assert (failure["file"], failure["line"]) == ("test/test_a.py", 7)
    assert failure["kind"] == "assertion"
    assert failure["assertion"] == "E       assert 1 == 2"
    md = pf.render_feedback(summary)
    assert "Location: test/test_a.py:7" in md
    assert "Do not modify tests unless" in md


def test_pytest_feedback_assertion_null_when_absent(tmp_path: Path) -> None:
    xml = (
        '<testsuite tests="1"><testcase classname="a" name="t">'
        '<failure message="boom">no frames here</failure></testcase></testsuite>'
    )
    (failure,) = _summary(_parse(tmp_path, xml))["failures"]
    assert failure["assertion"] is None
    assert failure["file"] is None and failure["line"] is None
    assert failure["kind"] == "error"


def test_pytest_feedback_parse_collection_error(tmp_path: Path) -> None:
    summary = _summary(_parse(tmp_path, COLLECTION_XML), returncode=2)
    assert summary["status"] == "error"
    (failure,) = summary["failures"]
    assert failure["kind"] == "collection"
    assert (failure["file"], failure["line"]) == ("test/test_b.py", 1)
    assert "ModuleNotFoundError" in failure["assertion"]
    assert "Do not touch tests" in pf.render_feedback(summary)


def test_pytest_feedback_truncates_failure_count(tmp_path: Path) -> None:
    summary = _summary(_parse(tmp_path, _many_failures_xml(13)))
    assert len(summary["failures"]) == 10
    assert summary["truncated"] == {"truncated": True, "omitted_failures": 3}
    assert "3 further failure(s) omitted" in pf.render_feedback(summary)


def test_pytest_feedback_truncates_long_traceback(tmp_path: Path) -> None:
    summary = _summary(_parse(tmp_path, _many_failures_xml(1, long_trace=True)))
    (failure,) = summary["failures"]
    assert len(failure["traceback_tail"].splitlines()) == 40
    assert "traceback_tail" in failure["truncated_fields"]
    assert "Truncated fields: traceback_tail" in pf.render_feedback(summary)


def test_pytest_feedback_invalid_xml_returns_none(tmp_path: Path) -> None:
    path = tmp_path / "r.xml"
    path.write_text("<not xml", encoding="utf-8")
    assert pf.parse_junit(path, tmp_path) is None
    assert pf.parse_junit(tmp_path / "missing.xml", tmp_path) is None


# argument validation


def _root(tmp_path: Path) -> Path:
    (tmp_path / "test").mkdir()
    (tmp_path / "test" / "test_ok.py").write_text("def test_ok():\n    pass\n")
    (tmp_path / "other.py").write_text("")
    return tmp_path


@pytest.mark.parametrize(
    "arg",
    ["test/missing.py", "other.py", "test/../other.py", "../x.py", "-k", "/etc/passwd"],
)
def test_pytest_feedback_rejects_bad_paths(tmp_path: Path, arg: str) -> None:
    root = _root(tmp_path)
    with pytest.raises(pf.ArgumentError):
        pf.validate_targets([arg], root)


def test_pytest_feedback_rejects_empty_targets(tmp_path: Path) -> None:
    with pytest.raises(pf.ArgumentError):
        pf.validate_targets([], _root(tmp_path))


def test_pytest_feedback_rejects_symlink_escape(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "test" / "link.py").symlink_to(root / "other.py")
    with pytest.raises(pf.ArgumentError):
        pf.validate_targets(["test/link.py"], root)


def test_pytest_feedback_accepts_node_id_unchanged(tmp_path: Path) -> None:
    root = _root(tmp_path)
    given = ["test/test_ok.py::test_ok", "test"]
    assert pf.validate_targets(given, root) == given


def test_pytest_feedback_cli_rejects_missing_path_without_running(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def boom(*args: Any, **kwargs: Any) -> int:
        raise AssertionError("pytest must not run")

    monkeypatch.setattr(pf, "run_feedback", boom)
    with pytest.raises(SystemExit) as exc:
        pf.PytestFeedback().targeted("test/casedb/test_retrieve_seq_distances.py")
    assert exc.value.code == 2
    assert "does not exist" in capsys.readouterr().err


# command / mode behavior


def test_pytest_feedback_command_flags() -> None:
    args = pf.build_pytest_args(["test/a.py"])
    assert "-s" not in args and "-v" not in args
    assert "--junitxml=.pytest-feedback/results.xml" in args
    assert args[-1] == "test/a.py"


def test_pytest_feedback_full_command_wraps_coverage() -> None:
    cmd = pf.build_command(["test/a"], coverage=True)
    assert cmd[1:6] == ["-m", "coverage", "run", "--source=gen_epix", "-m"]


def test_pytest_feedback_full_e2e_toggle() -> None:
    with_e2e = pf._selected_groups("full", True)
    without = pf._selected_groups("full", False)
    assert "test/end_to_end" in with_e2e
    assert without == [g for g in with_e2e if g != "test/end_to_end"]


def test_pytest_feedback_targeted_runs_exactly_given_paths(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "test" / "test_other.py").write_text(
        "def test_other():\n    assert False\n"
    )
    code = pf.run_feedback("targeted", ["test/test_ok.py"], 120, root=root)
    summary = json.loads((root / ".pytest-feedback" / "summary.json").read_text())
    assert code == 0
    assert summary["total"] == 1 and summary["passed"] == 1
    assert summary["command"].endswith("test/test_ok.py")


# exit codes, artifacts, timeout


def test_pytest_feedback_exit_1_on_failure_with_location(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _root(tmp_path)
    (root / "test" / "test_bad.py").write_text(
        "def test_bad():\n    x = 1\n    assert x == 2\n"
    )
    code = pf.run_feedback("targeted", ["test/test_bad.py"], 120, root=root)
    assert code == 1
    out_dir = root / ".pytest-feedback"
    summary = json.loads((out_dir / "summary.json").read_text())
    (failure,) = summary["failures"]
    assert failure["test"] == "test/test_bad.py::test_bad"
    assert (failure["file"], failure["line"]) == ("test/test_bad.py", 3)
    assert (out_dir / "results.xml").exists()
    printed = capsys.readouterr().out
    assert printed == (out_dir / "feedback.md").read_text()
    assert "test/test_bad.py:3" in printed


def test_pytest_feedback_exit_2_on_collection_error(tmp_path: Path) -> None:
    root = _root(tmp_path)
    (root / "test" / "test_broken.py").write_text("import nonexistent_module_xyz\n")
    code = pf.run_feedback("targeted", ["test/test_broken.py"], 120, root=root)
    summary = json.loads((root / ".pytest-feedback" / "summary.json").read_text())
    assert code == 2
    assert summary["status"] == "error"
    assert summary["failures"][0]["kind"] == "collection"


def test_pytest_feedback_timeout_is_infrastructure_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(tmp_path)
    sleeper = [sys.executable, "-c", "import time; time.sleep(30)"]
    monkeypatch.setattr(pf, "build_command", lambda targets, coverage: sleeper)
    code = pf.run_feedback("targeted", ["test/test_ok.py"], 1, root=root)
    summary = json.loads((root / ".pytest-feedback" / "summary.json").read_text())
    assert code == 2
    assert summary["status"] == "error"
    assert summary["failures"][0]["kind"] == "timeout"


def test_pytest_feedback_no_tests_collected_is_error(tmp_path: Path) -> None:
    summary = _summary(None, returncode=5)
    assert summary["status"] == "error"
    assert "no tests were collected" in summary["failures"][0]["message"]


def test_pytest_feedback_coverage_failure_reported_separately(tmp_path: Path) -> None:
    cov = {"html_exit_code": 1, "xml_exit_code": 0}
    summary = _summary(_parse(tmp_path, ALL_PASS_XML), returncode=0, coverage=cov)
    assert summary["status"] == "error"
    assert summary["coverage"] == cov
    assert summary["failed"] == 0
    assert "html FAILED, xml ok" in pf.render_feedback(summary)


# drift against run.py


def _run_py_function(name: str) -> ast.FunctionDef:
    tree = ast.parse(RUN_PY.read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Run")
    return next(
        n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name
    )


def _test_groups(func: ast.FunctionDef) -> list[str]:
    found = [
        elt
        for node in ast.walk(func)
        if isinstance(node, ast.List)
        for elt in node.elts
        if isinstance(elt, ast.Constant)
        and isinstance(elt.value, str)
        and elt.value.startswith("test/")
        and not elt.value.startswith("test/output/")
    ]
    found.sort(key=lambda e: (e.lineno, e.col_offset))
    return [str(e.value) for e in found]


def test_pytest_feedback_fast_groups_match_run_py() -> None:
    assert pf.FAST_GROUPS == _test_groups(_run_py_function("test_all_unit"))


def test_pytest_feedback_full_groups_match_run_py() -> None:
    assert pf.FULL_GROUPS == _test_groups(_run_py_function("test_all"))


def test_pytest_feedback_pytest_args_match_run_py() -> None:
    tree = ast.parse(RUN_PY.read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Run")
    value = next(
        n.value
        for n in cls.body
        if isinstance(n, ast.Assign)
        and any(
            isinstance(t, ast.Name) and t.id == "DEFAULT_PYTEST_ARGS" for t in n.targets
        )
    )
    expected = [a for a in ast.literal_eval(value) if a not in ("-s", "-v")]
    assert pf.PYTEST_ARGS == expected

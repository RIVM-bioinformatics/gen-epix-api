"""Run pytest once and write structured feedback for a coding-agent repair loop.

Usage:
    uv run python util/pytest_feedback.py fast
    uv run python util/pytest_feedback.py targeted test/casedb/unit/test_x.py
    uv run python util/pytest_feedback.py full [--include_e2e=False]

Artifacts are written to ``.pytest-feedback/``: ``results.xml`` (raw JUnit XML),
``summary.json``, ``feedback.md`` and ``pytest.log`` (raw output, never printed).

Exit codes: 0 = all passed, 1 = test failures, 2 = infrastructure, argument,
collection or timeout error.

The group lists below are copies of those in ``run.py``; a test guards against drift.
"""

import json
import os
import re
import shlex
import signal
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import fire  # type: ignore[import-untyped]

SCHEMA_VERSION = 1
FEEDBACK_DIR = ".pytest-feedback"
RESULTS_FILE = "results.xml"
LOG_FILE = "pytest.log"
RERUN_PREFIX = "uv run python util/pytest_feedback.py"

EXIT_PASSED = 0
EXIT_FAILED = 1
EXIT_ERROR = 2

MAX_FAILURES = 10
MAX_LINES = 40

# Copy of Run.DEFAULT_PYTEST_ARGS in run.py without the noisy "-s" and "-v".
PYTEST_ARGS = [
    "-W",
    "ignore::DeprecationWarning",
    "-W",
    "ignore::pytest.PytestAssertRewriteWarning",
    "-W",
    "ignore::sqlalchemy.exc.SAWarning",
]
# pyproject.toml sets addopts = "-v -s"; clear it. xunit1 adds file/line to testcases.
PYTEST_OVERRIDES = ["-o", "addopts=", "-o", "junit_family=xunit1"]

# Copy of the group list in Run.test_all_unit.
FAST_GROUPS = [
    "test/filter/unit",
    "test/transform/unit",
    "test/fastapp/unit",
    "test/seqdb/unit",
    "test/commondb/unit",
    "test/casedb/unit",
    "test/omopdb/unit",
]
E2E_GROUP = "test/end_to_end"
# Copy of the group list in Run.test_all, in order.
FULL_GROUPS = [
    "test/filter/unit",
    "test/transform/unit",
    "test/fastapp/unit",
    "test/fastapp/integration",
    "test/commondb/unit",
    "test/commondb/integration",
    "test/casedb/unit",
    "test/casedb/integration",
    "test/seqdb/unit",
    "test/seqdb/integration",
    "test/omopdb/unit",
    "test/omopdb/integration",
    "test/general/docs",
    "test/general/migrations",
    E2E_GROUP,
    "test/util",
]

DEFAULT_TIMEOUT = 900
FULL_DEFAULT_TIMEOUT = 3600

_FRAME_RE = re.compile(r"^(?P<file>[^\s:]+\.py):(?P<line>\d+):", re.MULTILINE)
_KIND_ORDER = {"collection": 0, "timeout": 1, "error": 2, "assertion": 3}


class ArgumentError(ValueError):
    """Raised when command-line arguments are invalid."""


def default_root() -> Path:
    """Returns the repository root (parent of ``util/``)."""
    return Path(__file__).resolve().parent.parent


def validate_targets(paths: tuple[str, ...] | list[str], root: Path) -> list[str]:
    """Validates targeted test paths or node IDs.

    Args:
        paths: Test files, directories or node IDs (``path::name``).
        root: Repository root; paths must resolve below ``root/test``.

    Returns:
        The given arguments, unchanged.

    Raises:
        ArgumentError: If nothing is given, or a path is missing, uses ``..``,
            looks like an option, or resolves outside ``root/test``.
    """
    if not paths:
        raise ArgumentError("targeted mode requires at least one test path")
    test_root = (root / "test").resolve()
    for arg in paths:
        path_part = str(arg).split("::", 1)[0]
        if not path_part or path_part.startswith("-") or "\x00" in path_part:
            raise ArgumentError(f"invalid test path: {arg!r}")
        if ".." in Path(path_part).parts:
            raise ArgumentError(f"path traversal ('..') is not allowed: {arg!r}")
        candidate = Path(path_part)
        if not candidate.is_absolute():
            candidate = root / candidate
        if not candidate.exists():
            raise ArgumentError(f"path does not exist: {path_part!r}")
        if not candidate.resolve().is_relative_to(test_root):
            raise ArgumentError(f"path must be under test/: {path_part!r}")
    return [str(p) for p in paths]


def build_pytest_args(targets: list[str]) -> list[str]:
    """Builds the pytest arguments (without interpreter or ``-m pytest``)."""
    junit = f"--junitxml={FEEDBACK_DIR}/{RESULTS_FILE}"
    return [*PYTEST_ARGS, *PYTEST_OVERRIDES, junit, *targets]


def build_command(targets: list[str], coverage: bool) -> list[str]:
    """Builds the full pytest command, wrapped in ``coverage run`` if requested."""
    if coverage:
        prefix = [sys.executable, "-m", "coverage", "run", "--source=gen_epix"]
        return [*prefix, "-m", "pytest", *build_pytest_args(targets)]
    return [sys.executable, "-m", "pytest", *build_pytest_args(targets)]


def run_process(
    command: list[str], log_path: Path, cwd: Path, timeout: float, append: bool = False
) -> tuple[int, bool]:
    """Runs a command with output redirected to a log file.

    Args:
        command: Command to run.
        log_path: File receiving stdout and stderr.
        cwd: Working directory.
        timeout: Seconds before the process group is killed.
        append: Append to the log instead of truncating it.

    Returns:
        Tuple of return code and whether the timeout was hit.
    """
    with open(log_path, "ab" if append else "wb") as log:
        proc = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=log,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            return proc.wait(timeout=timeout), False
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            return proc.returncode, True


def _cap_head(lines: list[str]) -> tuple[list[str], bool]:
    return lines[:MAX_LINES], len(lines) > MAX_LINES


def _cap_tail(lines: list[str]) -> tuple[list[str], bool]:
    return lines[-MAX_LINES:], len(lines) > MAX_LINES


def _relative(file: str, root: Path) -> str:
    path = Path(file)
    if path.is_absolute():
        try:
            return str(path.resolve().relative_to(root.resolve()))
        except ValueError:
            return file
    return file


def _node_id(case: ET.Element) -> str:
    """Builds a node ID from xunit1 ``file`` plus the classname remainder."""
    name = case.get("name", "")
    classname = case.get("classname", "")
    file = case.get("file")
    if not file:
        return f"{classname}::{name}" if classname else name
    module = file.removesuffix(".py").replace("/", ".")
    rest = classname.removeprefix(module).strip(".")
    parts = [file, *([p for p in rest.split(".") if p]), name]
    return "::".join(p for p in parts if p)


def _failure_entry(child: ET.Element, case: ET.Element, root: Path) -> dict[str, Any]:
    text = child.text or ""
    message_attr = child.get("message", "")
    if child.tag == "error" and message_attr.startswith("collection failure"):
        kind = "collection"
    elif child.tag == "failure" and (
        message_attr.startswith("assert") or "AssertionError" in message_attr
    ):
        kind = "assertion"
    else:
        kind = "error"
    text_lines = text.splitlines()
    truncated_fields: list[str] = []
    message_lines, cut = _cap_head((message_attr or text).splitlines())
    if cut:
        truncated_fields.append("message")
    e_lines = [ln for ln in text_lines if re.match(r"^E( |$)", ln)]
    e_lines, cut = _cap_head(e_lines)
    if cut:
        truncated_fields.append("assertion")
    tail, cut = _cap_tail(text_lines)
    if cut:
        truncated_fields.append("traceback_tail")
    frames = list(_FRAME_RE.finditer(text))
    file: str | None = None
    line: int | None = None
    if frames:
        file = _relative(frames[-1].group("file"), root)
        line = int(frames[-1].group("line"))
    return {
        "test": _node_id(case),
        "file": file,
        "line": line,
        "kind": kind,
        "message": "\n".join(message_lines),
        "assertion": "\n".join(e_lines) if e_lines else None,
        "traceback_tail": "\n".join(tail),
        "truncated_fields": truncated_fields,
    }


def parse_junit(path: Path, root: Path) -> dict[str, Any] | None:
    """Parses a JUnit XML file written by pytest.

    Args:
        path: JUnit XML file.
        root: Repository root, used to relativise traceback paths.

    Returns:
        Dict with ``counts``, ``duration`` and ``failures`` (all, ranked, uncapped),
        or None if the file is missing or not valid XML.
    """
    try:
        tree = ET.parse(path)
    except (OSError, ET.ParseError):
        return None
    top = tree.getroot()
    suites = [top] if top.tag == "testsuite" else top.findall("testsuite")
    counts = {"total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    counts["xfailed"] = 0
    failures: list[dict[str, Any]] = []
    for case in top.iter("testcase"):
        counts["total"] += 1
        child = next((c for c in case if c.tag in ("failure", "error")), None)
        if child is not None:
            counts["failed" if child.tag == "failure" else "errors"] += 1
            failures.append(_failure_entry(child, case, root))
            continue
        skipped = case.find("skipped")
        if skipped is None:
            counts["passed"] += 1
        elif "xfail" in (skipped.get("type") or ""):
            counts["xfailed"] += 1
        else:
            counts["skipped"] += 1
    duration = sum(float(s.get("time", 0) or 0) for s in suites)
    failures.sort(key=lambda f: _KIND_ORDER[f["kind"]])
    return {"counts": counts, "duration": round(duration, 3), "failures": failures}


def _synthetic_failure(kind: str, message: str) -> dict[str, Any]:
    lines, cut = _cap_tail(message.splitlines())
    return {
        "test": None,
        "file": None,
        "line": None,
        "kind": kind,
        "message": lines[-1] if lines else message,
        "assertion": None,
        "traceback_tail": "\n".join(lines),
        "truncated_fields": ["traceback_tail"] if cut else [],
    }


def _log_tail(log_path: Path) -> str:
    try:
        return log_path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return ""


def _next_action(status: str, mode: str) -> str:
    if status == "passed":
        return "No action required."
    if status == "error":
        return (
            "Fix the environment, imports or collection problem first, then re-run "
            f"`{RERUN_PREFIX} {mode}`. Do not modify tests."
        )
    return (
        "Fix the implementation behind the first failure, then re-run it with "
        f"`{RERUN_PREFIX} targeted <test>`."
    )


def build_summary(
    mode: str,
    command: list[str],
    returncode: int,
    timed_out: bool,
    timeout: float,
    parsed: dict[str, Any] | None,
    log_text: str,
    coverage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Builds the summary.json content.

    Args:
        mode: ``fast``, ``targeted`` or ``full``.
        command: The pytest command that was run.
        returncode: Pytest's raw return code.
        timed_out: Whether the timeout was hit.
        timeout: Timeout in seconds.
        parsed: Result of ``parse_junit``, or None if unavailable.
        log_text: Raw pytest output, used only for infrastructure error details.
        coverage: Exit codes of the coverage steps (``full`` mode), else None.

    Returns:
        The summary dictionary.
    """
    counts = (
        parsed["counts"]
        if parsed
        else dict.fromkeys(
            ("total", "passed", "failed", "errors", "skipped", "xfailed"), 0
        )
    )
    failures: list[dict[str, Any]] = list(parsed["failures"]) if parsed else []
    infra = False
    if timed_out:
        infra = True
        failures.insert(
            0, _synthetic_failure("timeout", f"pytest exceeded timeout of {timeout}s")
        )
    elif returncode == 0 and parsed is None:
        infra = True
        failures.append(_synthetic_failure("error", "no JUnit XML was produced"))
    elif returncode not in (0, 1):
        infra = True
        if not failures:
            detail = "no tests were collected" if returncode == 5 else log_text
            failures.append(
                _synthetic_failure("error", detail or f"pytest exit {returncode}")
            )
    elif returncode == 1 and not failures:
        infra = True
        failures.append(_synthetic_failure("error", "failures reported but unparsed"))
    elif failures and all(f["kind"] == "collection" for f in failures):
        infra = True
    coverage_failed = bool(
        coverage and (coverage["html_exit_code"] or coverage["xml_exit_code"])
    )
    if infra:
        status = "error"
    elif returncode == 1:
        status = "failed"
    elif coverage_failed:
        status = "error"
        failures.append(
            _synthetic_failure("error", "coverage html/xml report step failed")
        )
    else:
        status = "passed"
    for rank, failure in enumerate(failures, start=1):
        failure["rank"] = rank
    kept = failures[:MAX_FAILURES]
    kept = [{"rank": f.pop("rank"), **f} for f in kept]
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "status": status,
        "command": shlex.join(command),
        "exit_code": returncode,
        **counts,
        "duration": parsed["duration"] if parsed else 0.0,
        "failures": kept,
        "truncated": {
            "truncated": len(failures) > MAX_FAILURES,
            "omitted_failures": max(0, len(failures) - MAX_FAILURES),
        },
        "coverage": coverage,
        "next_action": _next_action(status, mode),
    }


def _fence(text: str) -> str:
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    ticks = "`" * max(3, longest + 1)
    return f"{ticks}text\n{text}\n{ticks}"


_FAILED_STEPS = [
    "Inspect the failing implementation.",
    "Determine the root cause.",
    "Make the smallest appropriate implementation change.",
    "Do not modify tests unless the test is demonstrably incorrect; if you think it "
    "is, stop and report the evidence.",
    "Re-run the failing test in targeted mode.",
    "If it passes, run the relevant module (targeted), then `fast`. Only run `full` "
    "when the change is cross-cutting.",
    "Stop and report after 2 failed repair attempts on the same failure.",
]


def render_feedback(summary: dict[str, Any]) -> str:
    """Renders feedback.md from a summary dictionary only."""
    lines = [
        "# Pytest Feedback",
        "",
        "## Status",
        "",
        f"- Status: {summary['status']}",
        f"- Mode: {summary['mode']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']} (errors: {summary['errors']})",
        f"- Skipped: {summary['skipped']}",
        f"- Duration: {summary['duration']}s",
    ]
    cov = summary.get("coverage")
    if cov:
        html_ok = "ok" if cov["html_exit_code"] == 0 else "FAILED"
        xml_ok = "ok" if cov["xml_exit_code"] == 0 else "FAILED"
        lines.append(f"- Coverage reports: html {html_ok}, xml {xml_ok}")
    lines += ["", "## Failed Tests", ""]
    if not summary["failures"]:
        lines += ["None.", ""]
    for f in summary["failures"]:
        loc = "unknown"
        if f["file"]:
            loc = f"{f['file']}:{f['line']}" if f["line"] else f["file"]
        cut = f.get("truncated_fields") or []
        lines += [
            f"### {f['rank']}. {f['test'] or '(no test id)'}",
            "",
            f"- Location: {loc}",
            f"- Kind: {f['kind']}",
            (
                f"- Failure: {f['message'] or '(no message)'}"
                if "\n" not in f["message"]
                else "- Failure:"
            ),
        ]
        if "\n" in f["message"]:
            lines += ["", _fence(f["message"])]
        if f["assertion"] is not None:
            lines += ["", "Relevant assertion:", "", _fence(f["assertion"])]
        if f["traceback_tail"]:
            lines += ["", "Traceback tail:", "", _fence(f["traceback_tail"])]
        if cut:
            lines += ["", f"Truncated fields: {', '.join(cut)}"]
        lines.append("")
    trunc = summary["truncated"]
    if trunc["truncated"]:
        lines += [
            f"Truncated: {trunc['omitted_failures']} further failure(s) omitted.",
            "",
        ]
    lines += ["## Instructions", ""]
    if summary["status"] == "failed":
        lines += [f"{i}. {step}" for i, step in enumerate(_FAILED_STEPS, start=1)]
    elif summary["status"] == "error":
        lines.append(
            "Fix the environment or imports first (collection, infrastructure or "
            "timeout error). Do not touch tests."
        )
    else:
        lines.append("No action required.")
    lines += ["", f"Next action: {summary['next_action']}", ""]
    return "\n".join(lines)


def _selected_groups(mode: str, include_e2e: bool) -> list[str]:
    if mode == "fast":
        return list(FAST_GROUPS)
    return [g for g in FULL_GROUPS if include_e2e or g != E2E_GROUP]


def run_feedback(
    mode: str,
    targets: list[str],
    timeout: float,
    root: Path | None = None,
    coverage: bool = False,
) -> int:
    """Runs pytest once, writes the artifacts and prints feedback.md.

    Args:
        mode: ``fast``, ``targeted`` or ``full``.
        targets: Pytest targets (already validated).
        timeout: Seconds before pytest is killed.
        root: Repository root; defaults to the repo containing this script.
        coverage: Run under coverage and generate html/xml reports.

    Returns:
        The exit code: 0 passed, 1 test failures, 2 error.
    """
    root = root or default_root()
    out_dir = root / FEEDBACK_DIR
    out_dir.mkdir(exist_ok=True)
    results = out_dir / RESULTS_FILE
    log_path = out_dir / LOG_FILE
    results.unlink(missing_ok=True)
    command = build_command(targets, coverage)
    returncode, timed_out = run_process(command, log_path, root, timeout)
    cov: dict[str, Any] | None = None
    if coverage and not timed_out:
        (root / "test" / "output").mkdir(parents=True, exist_ok=True)
        steps = {
            "html_exit_code": ["html", "-d", "test/output/coverage.html"],
            "xml_exit_code": ["xml", "-o", "test/output/coverage.xml"],
        }
        cov = {}
        for key, args in steps.items():
            cmd = [sys.executable, "-m", "coverage", *args]
            cov[key], _ = run_process(cmd, log_path, root, timeout, append=True)
    summary = build_summary(
        mode,
        command,
        returncode,
        timed_out,
        timeout,
        parse_junit(results, root),
        _tail_text(_log_tail(log_path)),
        cov,
    )
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    feedback = render_feedback(summary)
    (out_dir / "feedback.md").write_text(feedback, encoding="utf-8")
    print(feedback, end="")
    return {"passed": EXIT_PASSED, "failed": EXIT_FAILED}.get(
        summary["status"], EXIT_ERROR
    )


def _tail_text(text: str) -> str:
    return "\n".join(text.splitlines()[-MAX_LINES:])


class PytestFeedback:
    """Fire CLI: run pytest once and write structured feedback."""

    def fast(self, timeout: float = DEFAULT_TIMEOUT) -> None:
        """Runs all unit-test groups without coverage.

        Args:
            timeout: Seconds before pytest is killed.
        """
        sys.exit(run_feedback("fast", _selected_groups("fast", True), timeout))

    def targeted(self, *paths: str, timeout: float = DEFAULT_TIMEOUT) -> None:
        """Runs exactly the given test files or node IDs below ``test/``.

        Args:
            *paths: Test files, directories or node IDs.
            timeout: Seconds before pytest is killed.
        """
        try:
            targets = validate_targets([str(p) for p in paths], default_root())
        except ArgumentError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(EXIT_ERROR)
        sys.exit(run_feedback("targeted", targets, timeout))

    def full(
        self, include_e2e: bool = True, timeout: float = FULL_DEFAULT_TIMEOUT
    ) -> None:
        """Runs the equivalent of ``run.py test_all`` with coverage reports.

        Args:
            include_e2e: Include ``test/end_to_end``.
            timeout: Seconds before pytest is killed.
        """
        groups = _selected_groups("full", include_e2e)
        sys.exit(run_feedback("full", groups, timeout, coverage=True))


if __name__ == "__main__":
    fire.Fire(PytestFeedback)

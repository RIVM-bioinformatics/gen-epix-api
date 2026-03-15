from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

import pytest

_REPO_ROOT = Path(__file__).parents[2]


@pytest.fixture
def run_command_contract_env() -> Iterator[dict[str, Path]]:
    tmp_dir = _REPO_ROOT / ".tmp-test-artifacts" / "run_command_contract" / uuid4().hex
    sitecustomize_dir = tmp_dir / "bootstrap"
    sitecustomize_dir.mkdir(parents=True)
    (sitecustomize_dir / "sitecustomize.py").write_text(
        textwrap.dedent(
            """\
            from __future__ import annotations

            import json
            import os
            import subprocess
            from pathlib import Path

            plan_path = os.environ.get("GEN_EPIX_RUNPY_CONTRACT_PLAN")
            log_path = os.environ.get("GEN_EPIX_RUNPY_CONTRACT_LOG")

            if plan_path and log_path:
                response_plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
                planned_responses = iter(response_plan["responses"])
                log_file = Path(log_path)
                log_file.parent.mkdir(parents=True, exist_ok=True)
                original_run = subprocess.run

                def _is_contract_command(command):
                    return len(command) >= 3 and command[1:3] == ["-m", "coverage"]

                def _fake_run(args, *unused_args, **kwargs):
                    command = list(args) if isinstance(args, (list, tuple)) else [args]
                    if not _is_contract_command(command):
                        return original_run(args, *unused_args, **kwargs)
                    try:
                        response = next(planned_responses)
                    except StopIteration as exc:
                        raise AssertionError(
                            f"Unexpected subprocess.run call: {command!r}"
                        ) from exc

                    log_entry = {
                        "args": command,
                        "check": bool(kwargs.get("check", False)),
                    }
                    with log_file.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(log_entry) + "\\n")

                    returncode = int(response["returncode"])
                    stdout = response.get("stdout")
                    stderr = response.get("stderr")
                    if kwargs.get("check") and returncode != 0:
                        raise subprocess.CalledProcessError(
                            returncode,
                            command,
                            output=stdout,
                            stderr=stderr,
                        )
                    return subprocess.CompletedProcess(
                        command,
                        returncode,
                        stdout=stdout,
                        stderr=stderr,
                    )

                subprocess.run = _fake_run
            """
        ),
        encoding="utf-8",
    )
    try:
        yield {
            "sitecustomize_dir": sitecustomize_dir,
            "plan_path": tmp_dir / "subprocess_plan.json",
            "log_path": tmp_dir / "subprocess_calls.jsonl",
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        shared_tmp_dir = tmp_dir.parent
        if shared_tmp_dir.exists() and not any(shared_tmp_dir.iterdir()):
            shared_tmp_dir.rmdir()


def _run_test_all(
    run_command_contract_env: dict[str, Path],
    responses: list[dict[str, Any]],
) -> tuple[subprocess.CompletedProcess[str], list[dict[str, Any]]]:
    plan_path = run_command_contract_env["plan_path"]
    log_path = run_command_contract_env["log_path"]
    plan_path.write_text(json.dumps({"responses": responses}), encoding="utf-8")

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    bootstrap_dir = str(run_command_contract_env["sitecustomize_dir"])
    env["PYTHONPATH"] = (
        f"{bootstrap_dir}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath
        else bootstrap_dir
    )
    env["GEN_EPIX_RUNPY_CONTRACT_PLAN"] = str(plan_path)
    env["GEN_EPIX_RUNPY_CONTRACT_LOG"] = str(log_path)

    proc = subprocess.run(
        [sys.executable, "run.py", "test_all"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    calls: list[dict[str, Any]] = []
    if log_path.exists():
        calls = [
            json.loads(line)
            for line in log_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    return proc, calls


def _command_kind(call: dict[str, Any]) -> str:
    args = call["args"]
    if args[1:7] == ["-m", "coverage", "run", "--source=gen_epix", "-m", "pytest"]:
        return "pytest"
    if args[1:4] == ["-m", "coverage", "html"]:
        return "html"
    if args[1:4] == ["-m", "coverage", "xml"]:
        return "xml"
    raise AssertionError(f"Unexpected command logged: {args!r}")


def test_test_all_exits_with_pytest_code_when_pytest_fails(
    run_command_contract_env: dict[str, Path],
) -> None:
    proc, _calls = _run_test_all(
        run_command_contract_env,
        responses=[
            {"returncode": 7},
            {"returncode": 0},
            {"returncode": 0},
        ],
    )

    assert proc.returncode == 7, proc.stderr


def test_test_all_still_runs_html_and_xml_after_pytest_failure(
    run_command_contract_env: dict[str, Path],
) -> None:
    _proc, calls = _run_test_all(
        run_command_contract_env,
        responses=[
            {"returncode": 5},
            {"returncode": 0},
            {"returncode": 0},
        ],
    )

    assert [_command_kind(call) for call in calls] == ["pytest", "html", "xml"]


def test_test_all_fails_with_coverage_code_when_pytest_passes_but_report_generation_fails(
    run_command_contract_env: dict[str, Path],
) -> None:
    proc, calls = _run_test_all(
        run_command_contract_env,
        responses=[
            {"returncode": 0},
            {"returncode": 23},
            {"returncode": 0},
        ],
    )

    assert [_command_kind(call) for call in calls] == ["pytest", "html", "xml"]
    assert proc.returncode == 23, proc.stderr


def test_test_all_exits_zero_when_all_subprocesses_succeed(
    run_command_contract_env: dict[str, Path],
) -> None:
    proc, calls = _run_test_all(
        run_command_contract_env,
        responses=[
            {"returncode": 0},
            {"returncode": 0},
            {"returncode": 0},
        ],
    )

    assert [_command_kind(call) for call in calls] == ["pytest", "html", "xml"]
    assert proc.returncode == 0, proc.stderr

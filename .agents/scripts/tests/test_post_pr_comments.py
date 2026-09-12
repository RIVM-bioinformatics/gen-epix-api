"""Test the PR-comment helper without contacting GitHub."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "post-pr-comments.sh"

JQ_STUB = r"""#!/usr/bin/env python
import json
import re
import sys

args = sys.argv[1:]
expression = args[-1]
variables = {}
index = 0
while index < len(args) - 1:
    if args[index] in {"--arg", "--argjson"}:
        kind, name, value = args[index : index + 3]
        variables[name] = json.loads(value) if kind == "--argjson" else value
        index += 3
    else:
        index += 1

if "-n" in args:
    if "$posted" in expression:
        result = {
            "success": variables["success"],
            "posted": variables["posted"],
            "failed": variables["failed"],
            "error": "",
        }
    elif "could not resolve head SHA" in expression:
        result = {
            "success": False,
            "posted": [],
            "failed": [],
            "error": f"could not resolve head SHA for PR #{variables['pr']}",
        }
    else:
        match = re.search(r'error: "([^"]+)"', expression)
        result = {
            "success": False,
            "posted": [],
            "failed": [],
            "error": match.group(1),
        }
    print(json.dumps(result, separators=(",", ":")))
    raise SystemExit(0)

try:
    value = json.loads(sys.stdin.read())
except json.JSONDecodeError:
    raise SystemExit(4)

if expression == ".":
    print(json.dumps(value))
elif expression == ".pr_number // empty":
    if value.get("pr_number") is None:
        raise SystemExit(1)
    print(value["pr_number"])
elif expression == '.comments | select(type == "array")':
    comments = value.get("comments")
    if not isinstance(comments, list):
        raise SystemExit(1)
    print(json.dumps(comments, separators=(",", ":")))
elif expression == "length":
    print(len(value))
elif re.fullmatch(r"\.\[\d+\]", expression):
    print(json.dumps(value[int(expression[2:-1])], separators=(",", ":")))
elif expression.startswith(".") and "//" in expression:
    field = expression[1:].split()[0]
    default = "RIGHT" if '"RIGHT"' in expression else ""
    selected = value.get(field, default)
    print("" if selected is None else selected)
elif expression == ". + [$idx]":
    print(json.dumps(value + [variables["idx"]], separators=(",", ":")))
elif "file, body, and positive integer line" in expression:
    value.append(
        {
            "index": variables["idx"],
            "file": variables["file"],
            "line": variables["line"],
            "error": (
                "file, body, and positive integer line are required; "
                "sides must be LEFT or RIGHT"
            ),
        }
    )
    print(json.dumps(value, separators=(",", ":")))
elif "error: $err" in expression:
    value.append(
        {
            "index": variables["idx"],
            "file": variables["file"],
            "line": variables["line"],
            "error": variables["err"],
        }
    )
    print(json.dumps(value, separators=(",", ":")))
else:
    raise SystemExit(f"unsupported jq expression: {expression}")
"""

GH_STUB = r"""#!/usr/bin/env bash
if [[ "$1" == "pr" && "$2" == "view" ]]; then
  printf '%s\n' '0123456789abcdef'
  exit 0
fi
if [[ "$1" == "api" ]]; then
  if [[ "$*" != *"AI-generated comment"* ]]; then
    printf '%s\n' 'missing attribution' >&2
    exit 2
  fi
  if [[ "$GH_STUB_MODE" == "success" ]]; then
    exit 0
  fi
  printf '%s\n' 'stubbed gh api failure' >&2
  exit 1
fi
printf '%s\n' 'unexpected gh invocation' >&2
exit 2
"""


def write_executable(path: Path, content: str) -> None:
    """Write a temporary executable using Unix line endings."""
    path.write_text(content, encoding="utf-8", newline="\n")
    path.chmod(0o755)


def is_wsl_bash(bash: str) -> bool:
    """Return whether the executable is the Windows WSL launcher."""
    windir = os.environ.get("WINDIR")
    return windir is not None and Path(bash).resolve() == (
        Path(windir) / "System32" / "bash.EXE"
    )


def bash_path(path: Path, bash: str) -> str:
    """Return a path understood by Git Bash or WSL Bash."""
    resolved = path.resolve().as_posix()
    if is_wsl_bash(bash):
        drive, remainder = resolved.split(":/", maxsplit=1)
        return f"/mnt/{drive.lower()}/{remainder}"
    return resolved


def run_helper(
    tmp_path: Path,
    payload: str,
    *,
    include_jq: bool,
    gh_mode: str = "success",
) -> subprocess.CompletedProcess[str]:
    """Run the helper with isolated command stubs."""
    git_bash = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
    git_bash /= "Git/bin/bash.exe"
    bash = str(git_bash) if git_bash.exists() else shutil.which("bash")
    if bash is None:
        pytest.skip("bash is unavailable")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    if include_jq:
        write_executable(bin_dir / "jq", JQ_STUB)
        write_executable(bin_dir / "gh", GH_STUB)

    environment = os.environ.copy()
    stub_path = bash_path(bin_dir, bash)
    if is_wsl_bash(bash):
        environment["PATH"] = stub_path
        if include_jq:
            environment["PATH"] += ":/usr/local/bin:/usr/bin:/bin"
    else:
        environment["PATH"] = str(bin_dir)
        if include_jq:
            environment["PATH"] += os.pathsep + os.environ["PATH"]
    environment["GH_STUB_MODE"] = gh_mode
    return subprocess.run(
        [bash, bash_path(SCRIPT, bash)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
        env=environment,
    )


def test_missing_jq_returns_contract_json(tmp_path: Path) -> None:
    """Return valid JSON and zero when jq is unavailable."""
    result = run_helper(tmp_path, "{}", include_jq=False)

    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "success": False,
        "posted": [],
        "failed": [],
        "error": "jq is required but was not found",
    }


def test_invalid_json_returns_contract_json(tmp_path: Path) -> None:
    """Return the documented invalid-input result."""
    result = run_helper(tmp_path, "not JSON", include_jq=True)

    assert result.returncode == 0
    assert json.loads(result.stdout)["error"] == "invalid JSON input"


def test_successful_stubbed_post_returns_posted_index(tmp_path: Path) -> None:
    """Report a successful stubbed GitHub API call."""
    payload = json.dumps(
        {
            "pr_number": 42,
            "comments": [
                {"file": "gen_epix/example.py", "line": 7, "body": "Review comment"}
            ],
        }
    )
    result = run_helper(tmp_path, payload, include_jq=True)

    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "success": True,
        "posted": [0],
        "failed": [],
        "error": "",
    }


def test_failed_stubbed_post_returns_failure_detail(tmp_path: Path) -> None:
    """Report a failed stubbed GitHub API call without a remote retry."""
    payload = json.dumps(
        {
            "pr_number": 42,
            "comments": [
                {"file": "gen_epix/example.py", "line": 7, "body": "Review comment"}
            ],
        }
    )
    result = run_helper(tmp_path, payload, include_jq=True, gh_mode="failure")
    response = json.loads(result.stdout)

    assert result.returncode == 0
    assert response["success"] is False
    assert response["posted"] == []
    assert response["failed"][0]["index"] == 0
    assert "stubbed gh api failure" in response["failed"][0]["error"]

from __future__ import annotations

import argparse
import configparser
import io
import os
import platform
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
SETUP_CFG = ROOT / "setup.cfg"
BASELINE_CMD = [sys.executable, "run.py", "test_all"]
MAX_TROUBLESHOOT_MUTANTS = 6
PATCH_MUTMUT_TEMPLATE_SCRIPT = ROOT / "tools" / "patch_mutmut_template.py"
SMOKE_TEST_SELECTION_BY_PATH: dict[str, list[str]] = {
    "gen_epix/filter": ["test/filter/unit"],
    "gen_epix/transform": ["test/transform/unit"],
    "gen_epix/fastapp": ["test/fastapp/unit"],
    "gen_epix/commondb": ["test/commondb/unit"],
    "gen_epix/casedb": ["test/casedb/unit"],
    "gen_epix/seqdb": ["test/seqdb/unit"],
    "gen_epix/omopdb": ["test/omopdb/unit"],
}


def run_command(cmd: list[str], env_overrides: dict[str, str] | None = None) -> None:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    subprocess.run(cmd, cwd=ROOT, check=True, env=env)


def run_command_capture(
    cmd: list[str], env_overrides: dict[str, str] | None = None
) -> str:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        check=True,
        env=env,
        text=True,
        capture_output=True,
    )
    return result.stdout


def ensure_mutmut_platform() -> None:
    if platform.system() == "Windows":
        raise SystemExit(
            "mutmut requires fork support. Run this command from WSL/Linux."
        )


def parse_multiline(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def as_multiline(values: list[str]) -> str:
    return "\n" + "\n".join(values)


def normalize_scope_path(path: str) -> str:
    return path.replace("\\", "/").strip().strip("/")


def get_configured_mutation_paths() -> list[str]:
    parser = configparser.ConfigParser()
    parser.read(SETUP_CFG, encoding="utf-8")
    if "mutmut" not in parser:
        raise SystemExit("Missing [mutmut] section in setup.cfg.")
    paths = parse_multiline(parser["mutmut"].get("paths_to_mutate", ""))
    if not paths:
        raise SystemExit("setup.cfg [mutmut] paths_to_mutate is empty.")
    return [normalize_scope_path(path) for path in paths]


@contextmanager
def temporary_mutation_scope(
    paths: list[str], test_selection: list[str] | None = None
) -> Iterator[None]:
    original_text = SETUP_CFG.read_text(encoding="utf-8")
    parser = configparser.ConfigParser()
    parser.read_file(io.StringIO(original_text))

    if "mutmut" not in parser:
        raise SystemExit("Missing [mutmut] section in setup.cfg.")

    mutmut_cfg = parser["mutmut"]
    original_paths = parse_multiline(mutmut_cfg.get("paths_to_mutate", ""))
    if not original_paths:
        raise SystemExit("setup.cfg [mutmut] paths_to_mutate is empty.")

    scoped_paths = [normalize_scope_path(path) for path in paths]
    mutmut_cfg["paths_to_mutate"] = as_multiline(scoped_paths)

    # Keep the original source roots available in mutants/ for imports while mutating a subset.
    existing_also_copy = parse_multiline(mutmut_cfg.get("also_copy", ""))
    merged_also_copy = list(dict.fromkeys(existing_also_copy + original_paths))
    mutmut_cfg["also_copy"] = as_multiline(merged_also_copy)
    if test_selection:
        mutmut_cfg["pytest_add_cli_args_test_selection"] = as_multiline(test_selection)
        # Keep legacy and current mutmut selection keys in sync for smoke runs.
        mutmut_cfg["tests_dir"] = as_multiline(test_selection)

    with SETUP_CFG.open("w", encoding="utf-8", newline="\n") as f:
        parser.write(f)

    try:
        yield
    finally:
        SETUP_CFG.write_text(original_text, encoding="utf-8")


def run_baseline() -> None:
    run_command(BASELINE_CMD)


def maybe_patch_mutmut_template(auto_patch_mutmut: bool) -> None:
    if not PATCH_MUTMUT_TEMPLATE_SCRIPT.exists():
        raise SystemExit(
            "Missing tools/patch_mutmut_template.py. "
            "Sync your repository before running mutation tests."
        )

    check = subprocess.run(
        [sys.executable, str(PATCH_MUTMUT_TEMPLATE_SCRIPT), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if check.returncode == 0:
        return

    if not auto_patch_mutmut:
        raise SystemExit(
            "mutmut template patch check failed. "
            "Run `python tools/patch_mutmut_template.py` or rerun with "
            "`--auto-patch-mutmut`."
        )

    print("Applying mutmut template patch...")
    run_command([sys.executable, str(PATCH_MUTMUT_TEMPLATE_SCRIPT)])


def run_mutmut(args: list[str], auto_patch_mutmut: bool = False) -> None:
    ensure_mutmut_platform()
    mutmut_executable = shutil.which("mutmut")
    if not mutmut_executable:
        raise SystemExit(
            "Could not find `mutmut` on PATH. Activate your virtual environment "
            "and install requirements-mutation.txt."
        )
    maybe_patch_mutmut_template(auto_patch_mutmut)
    run_command(
        [mutmut_executable] + args,
        env_overrides={"GEN_EPIX_DISABLE_PYTEST_XLSX_REPORT": "1"},
    )


def run_mutmut_capture(args: list[str], auto_patch_mutmut: bool = False) -> str:
    ensure_mutmut_platform()
    mutmut_executable = shutil.which("mutmut")
    if not mutmut_executable:
        raise SystemExit(
            "Could not find `mutmut` on PATH. Activate your virtual environment "
            "and install requirements-mutation.txt."
        )
    maybe_patch_mutmut_template(auto_patch_mutmut)
    return run_command_capture(
        [mutmut_executable] + args,
        env_overrides={"GEN_EPIX_DISABLE_PYTEST_XLSX_REPORT": "1"},
    )


def build_mutmut_run_args(max_children: int) -> list[str]:
    if max_children < 1:
        raise SystemExit("--max-children must be >= 1.")
    return ["run", "--max-children", str(max_children)]


def parse_mutmut_results(output: str) -> list[tuple[str, str]]:
    mutants: list[tuple[str, str]] = []
    for line in output.splitlines():
        if ":" not in line:
            continue
        name, status = line.split(":", 1)
        mutant_name = name.strip()
        mutant_status = status.strip().lower()
        if mutant_name and mutant_status:
            mutants.append((mutant_name, mutant_status))
    return mutants


def select_mutants(
    output: str, statuses: list[str], name_contains: str | None, limit: int
) -> list[str]:
    normalized_statuses = {status.lower().strip() for status in statuses}
    selected: list[str] = []
    for mutant_name, mutant_status in parse_mutmut_results(output):
        if mutant_status not in normalized_statuses:
            continue
        if name_contains and name_contains not in mutant_name:
            continue
        selected.append(mutant_name)
        if len(selected) >= limit:
            break
    return selected


def resolve_smoke_tests(path: str) -> list[str]:
    normalized_path = normalize_scope_path(path)
    for prefix, tests in SMOKE_TEST_SELECTION_BY_PATH.items():
        if normalized_path == prefix or normalized_path.startswith(prefix + "/"):
            return tests
    return []


def add_auto_patch_mutmut_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--auto-patch-mutmut",
        action="store_true",
        help=(
            "Automatically run `python tools/patch_mutmut_template.py` when the "
            "mutmut template patch is missing."
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Local mutation testing entrypoint.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    full_parser = subparsers.add_parser("full", help="Run full mutation testing.")
    full_parser.add_argument(
        "--skip-baseline",
        action="store_true",
        help="Skip baseline run of `python run.py test_all`.",
    )
    full_parser.add_argument(
        "--max-children",
        type=int,
        default=1,
        help=(
            "mutmut worker processes (default: 1). "
            "Lower values reduce timeout-only runs on heavy suites."
        ),
    )
    full_parser.add_argument(
        "--tests",
        action="append",
        default=[],
        help=(
            "Optional test path(s) overriding mutmut test selection for this run. "
            "Repeatable."
        ),
    )
    add_auto_patch_mutmut_arg(full_parser)

    smoke_parser = subparsers.add_parser(
        "smoke", help="Run scoped mutation testing for a quick smoke check."
    )
    smoke_parser.add_argument(
        "--path",
        default="gen_epix/filter",
        help="Scoped mutation path relative to repo root (default: gen_epix/filter).",
    )
    smoke_parser.add_argument(
        "--skip-baseline",
        action="store_true",
        help="Skip baseline run of `python run.py test_all`.",
    )
    smoke_parser.add_argument(
        "--tests",
        action="append",
        default=[],
        help=(
            "Optional test path(s) for smoke run. Repeatable. "
            "If omitted, defaults are inferred from --path when possible."
        ),
    )
    smoke_parser.add_argument(
        "--max-children",
        type=int,
        default=1,
        help="mutmut worker processes (default: 1).",
    )
    add_auto_patch_mutmut_arg(smoke_parser)

    results_parser = subparsers.add_parser("results", help="Show mutation results summary.")
    add_auto_patch_mutmut_arg(results_parser)
    browse_parser = subparsers.add_parser("browse", help="Open the mutmut TUI browser.")
    add_auto_patch_mutmut_arg(browse_parser)
    retry_parser = subparsers.add_parser(
        "retry",
        help=(
            "Rerun a small mutant batch from `mutmut results` "
            "(for timeout-focused troubleshooting)."
        ),
    )
    retry_parser.add_argument(
        "--status",
        action="append",
        default=[],
        help=(
            "Mutant status to include (repeatable). "
            "Examples: timeout, survived, no tests, not checked."
        ),
    )
    retry_parser.add_argument(
        "--contains",
        default="",
        help="Only include mutants whose name contains this text.",
    )
    retry_parser.add_argument(
        "--limit",
        type=int,
        default=MAX_TROUBLESHOOT_MUTANTS,
        help=(
            f"Maximum mutants to rerun (default: {MAX_TROUBLESHOOT_MUTANTS}, "
            f"hard cap: {MAX_TROUBLESHOOT_MUTANTS})."
        ),
    )
    retry_parser.add_argument(
        "--path",
        default="gen_epix/filter/range.py",
        help=(
            "Scoped mutation path relative to repo root used while rerunning "
            "(default: gen_epix/filter/range.py)."
        ),
    )
    retry_parser.add_argument(
        "--tests",
        action="append",
        default=[],
        help=(
            "Optional test path(s) during retry run. Repeatable. "
            "If omitted, defaults are inferred from --path when possible."
        ),
    )
    retry_parser.add_argument(
        "--skip-baseline",
        action="store_true",
        help="Skip baseline run of `python run.py test_all`.",
    )
    retry_parser.add_argument(
        "--max-children",
        type=int,
        default=1,
        help="mutmut worker processes (default: 1).",
    )
    add_auto_patch_mutmut_arg(retry_parser)

    args = parser.parse_args()

    if args.command == "full":
        if not args.skip_baseline:
            run_baseline()
        run_args = build_mutmut_run_args(args.max_children)
        if args.tests:
            mutation_paths = get_configured_mutation_paths()
            print("Full run test selection override:", ", ".join(args.tests))
            with temporary_mutation_scope(mutation_paths, args.tests):
                run_mutmut(run_args, auto_patch_mutmut=args.auto_patch_mutmut)
        else:
            run_mutmut(run_args, auto_patch_mutmut=args.auto_patch_mutmut)
        return

    if args.command == "smoke":
        if not args.skip_baseline:
            run_baseline()
        smoke_tests = args.tests or resolve_smoke_tests(args.path)
        if smoke_tests:
            print("Smoke test selection:", ", ".join(smoke_tests))
        with temporary_mutation_scope([args.path], smoke_tests):
            run_mutmut(
                build_mutmut_run_args(args.max_children),
                auto_patch_mutmut=args.auto_patch_mutmut,
            )
        return

    if args.command == "results":
        run_mutmut(["results"], auto_patch_mutmut=args.auto_patch_mutmut)
        return

    if args.command == "browse":
        run_mutmut(["browse"], auto_patch_mutmut=args.auto_patch_mutmut)
        return

    if args.command == "retry":
        if args.limit < 1:
            raise SystemExit("--limit must be >= 1.")
        if args.limit > MAX_TROUBLESHOOT_MUTANTS:
            raise SystemExit(
                f"--limit cannot exceed {MAX_TROUBLESHOOT_MUTANTS} for troubleshooting runs."
            )
        if not args.skip_baseline:
            run_baseline()
        results_output = run_mutmut_capture(
            ["results"], auto_patch_mutmut=args.auto_patch_mutmut
        )
        statuses = args.status or ["timeout"]
        contains_filter = args.contains.strip() or None
        mutants = select_mutants(
            results_output, statuses, contains_filter, limit=args.limit
        )
        if not mutants:
            status_desc = ", ".join(statuses)
            contains_desc = f", contains='{args.contains}'" if contains_filter else ""
            print(f"No mutants found for status={status_desc}{contains_desc}.")
            return
        print("Retrying mutants:")
        for mutant in mutants:
            print(f"  {mutant}")
        retry_tests = args.tests or resolve_smoke_tests(args.path)
        if retry_tests:
            print("Retry test selection:", ", ".join(retry_tests))
        with temporary_mutation_scope([args.path], retry_tests):
            # Run selected mutants in a single mutmut invocation.
            # mutmut regenerates `.meta` on each `run`, so per-mutant calls would
            # overwrite prior statuses back to "not checked".
            run_mutmut(
                build_mutmut_run_args(args.max_children) + mutants,
                auto_patch_mutmut=args.auto_patch_mutmut,
            )
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()

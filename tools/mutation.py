from __future__ import annotations

import argparse
import configparser
import io
import platform
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
SETUP_CFG = ROOT / "setup.cfg"
BASELINE_CMD = [sys.executable, "run.py", "test_all"]


def run_command(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


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


@contextmanager
def temporary_mutation_scope(paths: list[str]) -> Iterator[None]:
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

    with SETUP_CFG.open("w", encoding="utf-8", newline="\n") as f:
        parser.write(f)

    try:
        yield
    finally:
        SETUP_CFG.write_text(original_text, encoding="utf-8")


def run_baseline() -> None:
    run_command(BASELINE_CMD)


def run_mutmut(args: list[str]) -> None:
    ensure_mutmut_platform()
    run_command([sys.executable, "-m", "mutmut"] + args)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local mutation testing entrypoint.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    full_parser = subparsers.add_parser("full", help="Run full mutation testing.")
    full_parser.add_argument(
        "--skip-baseline",
        action="store_true",
        help="Skip baseline run of `python run.py test_all`.",
    )

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

    subparsers.add_parser("results", help="Show mutation results summary.")
    subparsers.add_parser("browse", help="Open the mutmut TUI browser.")

    args = parser.parse_args()

    if args.command == "full":
        if not args.skip_baseline:
            run_baseline()
        run_mutmut(["run"])
        return

    if args.command == "smoke":
        if not args.skip_baseline:
            run_baseline()
        with temporary_mutation_scope([args.path]):
            run_mutmut(["run", "--max-children", "1"])
        return

    if args.command == "results":
        run_mutmut(["results"])
        return

    if args.command == "browse":
        run_mutmut(["browse"])
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()

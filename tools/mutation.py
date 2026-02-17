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


@contextmanager
def temporary_mutation_scope(paths: list[str]) -> Iterator[None]:
    original_text = SETUP_CFG.read_text(encoding="utf-8")
    parser = configparser.ConfigParser()
    parser.read_file(io.StringIO(original_text))

    if "mutmut" not in parser:
        raise SystemExit("Missing [mutmut] section in setup.cfg.")

    parser["mutmut"]["paths_to_mutate"] = "\n" + "\n".join(paths)
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
        help="Scoped path for paths_to_mutate (default: gen_epix/filter).",
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

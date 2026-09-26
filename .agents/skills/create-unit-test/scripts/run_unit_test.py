import argparse
import os
import sys
from pathlib import Path

import pytest

DEFAULT_PYTEST_ARGS = [
    "-s",
    "-v",
    "-W",
    "ignore::DeprecationWarning",
    "-W",
    "ignore::pytest.PytestAssertRewriteWarning",
    "-W",
    "ignore::sqlalchemy.exc.SAWarning",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run one unit-test file with run.py's default pytest arguments."
    )
    parser.add_argument("test_file", type=Path)
    parser.add_argument(
        "-k", dest="expression", help="Select tests by pytest expression"
    )
    parser.add_argument("--collect-only", action="store_true")
    args = parser.parse_args(argv)

    repository_root = Path(__file__).resolve().parents[4]
    test_file = args.test_file.resolve()
    try:
        relative_path = test_file.relative_to(repository_root / "test")
    except ValueError:
        parser.error("The test file must be inside this repository's test directory")
    if (
        not test_file.is_file()
        or "unit" not in relative_path.parts[:-1]
        or not test_file.name.startswith("test_")
        or test_file.suffix != ".py"
    ):
        parser.error("Expected one existing test_*.py file in a unit-test directory")

    sys.path.insert(0, str(repository_root))
    os.chdir(repository_root)

    pytest_args = [*DEFAULT_PYTEST_ARGS, str(test_file)]
    if args.expression is not None:
        pytest_args.extend(["-k", args.expression])
    if args.collect_only:
        pytest_args.append("--collect-only")
    return int(pytest.main(pytest_args))


if __name__ == "__main__":
    raise SystemExit(main())

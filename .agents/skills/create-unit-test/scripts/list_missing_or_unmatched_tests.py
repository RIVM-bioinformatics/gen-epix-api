"""Compare Python source modules with their canonical mirrored unit-test paths.

This filesystem-only checker does not import modules or assess test coverage.
It reports missing tests and unmatched test modules beneath the unit-test trees.
"""

import argparse
from pathlib import Path


def expected_test_path(source_path: Path, root: Path) -> Path:
    """Return the canonical unit-test path for a module beneath gen_epix.

    Args:
        source_path: Source module path beneath the checkout's gen_epix directory.
        root: Checkout root containing gen_epix and test.

    Returns:
        Mirrored path whose filename includes the package and unit components.
    """
    relative = source_path.relative_to(root / "gen_epix")
    if len(relative.parts) == 1:
        test_parent = Path("unit")
    else:
        test_parent = Path(relative.parts[0], "unit", *relative.parts[1:-1])
    filename_prefix = "_".join(test_parent.parts)
    return root / "test" / test_parent / f"test_{filename_prefix}_{relative.stem}.py"


def find_missing_or_unmatched_tests(
    root: Path, include_init: bool = False
) -> tuple[list[Path], list[Path]]:
    """Find modules without canonical tests and tests without matching modules.

    Args:
        root: Checkout root; gen_epix must exist and test may be absent.
        include_init: Whether package initializers require matching tests.

    Returns:
        Sorted source paths missing tests and sorted unmatched unit-test paths.
        Only test_*.py files in test/unit or test/<package>/unit are tests.
        Fixtures, helpers, integration tests, and performance tests are excluded.

    Raises:
        ValueError: If the source directory does not exist.
    """
    root = root.resolve()
    source_root = root / "gen_epix"
    if not source_root.is_dir():
        raise ValueError(f"Source directory does not exist: {source_root}")
    sources = sorted(source_root.rglob("*.py"))
    expected = {
        expected_test_path(source, root): source
        for source in sources
        if include_init or source.name != "__init__.py"
    }
    ignored_initializers = {
        expected_test_path(source, root)
        for source in sources
        if not include_init and source.name == "__init__.py"
    }
    test_root = root / "test"
    unit_roots = [test_root / "unit"]
    if test_root.is_dir():
        unit_roots.extend(
            package / "unit"
            for package in sorted(test_root.iterdir())
            if package.is_dir() and package.name != "unit"
        )
    tests = {
        test_path
        for unit_root in unit_roots
        if unit_root.is_dir()
        for test_path in unit_root.rglob("test_*.py")
    }
    missing = sorted(source for test, source in expected.items() if not test.is_file())
    unmatched = sorted(tests - expected.keys() - ignored_initializers)
    return missing, unmatched


def main() -> int:
    """Print deterministic mapping findings; findings are not execution failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[4],
        help="Checkout root (defaults to the checkout containing this script).",
    )
    parser.add_argument(
        "--include-init", action="store_true", help="Include __init__.py modules."
    )
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        missing, unmatched = find_missing_or_unmatched_tests(root, args.include_init)
    except ValueError as error:
        parser.error(str(error))
    for source in missing:
        print(f"MISSING_TEST: {source.relative_to(root).as_posix()}")
    for test in unmatched:
        print(f"UNMATCHED_TEST: {test.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Test the structural behavior of the docstring audit helper."""

from __future__ import annotations

import ast
import importlib.util
import textwrap
from pathlib import Path
from types import ModuleType


def load_checker() -> ModuleType:
    """Load the checker from its skill-local script path."""
    script = Path(__file__).parents[1] / "scripts" / "check_docstrings.py"
    spec = importlib.util.spec_from_file_location("check_docstrings", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


def parse(source: str) -> ast.Module:
    """Parse a dedented Python source fragment."""
    return ast.parse(textwrap.dedent(source))


def messages(findings: list[tuple[int, str]]) -> set[str]:
    """Return finding messages without their source lines."""
    return {message for _, message in findings}


def test_coverage_requires_public_private_and_nested_class_docstrings() -> None:
    """Require docstrings on every production class structure."""
    tree = parse('''
        """Module documentation."""

        class Public:
            pass

        class _Private:
            pass

        def outer():
            """Contain a nested class."""
            class Nested:
                pass
        ''')

    assert messages(CHECKER.check_coverage(tree)) == {
        "coverage: class 'Public' docstring is missing",
        "coverage: class '_Private' docstring is missing",
        "coverage: class 'Nested' docstring is missing",
    }


def test_coverage_keeps_private_and_nested_function_exemptions() -> None:
    """Check only structurally public functions automatically."""
    tree = parse('''
        """Module documentation."""

        def public():
            pass

        def _private():
            pass

        def outer():
            """Contain a nested function."""
            def nested():
                pass
        ''')

    assert messages(CHECKER.check_coverage(tree)) == {
        "coverage: function 'public' docstring is missing"
    }


def test_coverage_exempts_override_methods() -> None:
    """Allow an explicit override to inherit an unchanged contract."""
    tree = parse('''
        """Module documentation."""

        class Child:
            """Represent a child implementation."""

            @override
            def execute(self):
                pass
        ''')

    assert CHECKER.check_coverage(tree) == []


def test_coverage_exempts_repository_test_modules(tmp_path: Path) -> None:
    """Do not require module or definition docstrings in test modules."""
    test_module = tmp_path / "test_example.py"
    test_module.write_text("class Example:\n    pass\n", encoding="utf-8")

    assert CHECKER.audit_file(test_module, {"coverage"}) == []


def test_raises_reports_only_undocumented_public_direct_raises() -> None:
    """Keep direct-raise findings advisory and caller-surface focused."""
    tree = parse('''
        """Module documentation."""

        def undocumented():
            """Perform an operation."""
            raise ValueError("bad value")

        def documented():
            """Perform another operation.

            Raises:
                ValueError: If the value is invalid.
            """
            raise ValueError("bad value")

        def _private():
            raise ValueError("implementation detail")
        ''')

    assert messages(CHECKER.check_raises(tree)) == {
        "raises: review whether function 'undocumented' needs Raises:"
    }

"""Audit Python docstrings against the write-docstring skill conventions."""

from __future__ import annotations

import argparse
import ast
from collections.abc import Iterable
from pathlib import Path

CHECKS = {"coverage", "exception-class", "pydantic", "package", "raises"}
FIELD_DECORATORS = {"field_validator", "field_serializer"}
MODEL_VALIDATORS = {"model_validator"}
MODEL_SERIALIZERS = {"model_serializer"}
PYDANTIC_DECORATORS = FIELD_DECORATORS | MODEL_VALIDATORS | MODEL_SERIALIZERS
GOOGLE_SECTIONS = ("Args:", "Returns:", "Raises:")


def python_files(target: Path) -> Iterable[Path]:
    """Yield Python files beneath a target file or directory."""
    if target.is_file():
        if target.suffix == ".py":
            yield target
        return
    yield from target.rglob("*.py")


def decorator_name(decorator: ast.expr) -> str | None:
    """Return the referenced decorator name."""
    callable_node = decorator.func if isinstance(decorator, ast.Call) else decorator
    if isinstance(callable_node, ast.Name):
        return callable_node.id
    if isinstance(callable_node, ast.Attribute):
        return callable_node.attr
    return None


def has_decorator(
    node: ast.FunctionDef | ast.AsyncFunctionDef, names: set[str]
) -> bool:
    """Return whether a function has one of the named decorators."""
    return any(decorator_name(decorator) in names for decorator in node.decorator_list)


def is_overload(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a function is an overload stub."""
    return has_decorator(node, {"overload"})


def is_override(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a function explicitly overrides a base method."""
    return has_decorator(node, {"override"})


def is_public_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a function is part of the structural public surface."""
    return not node.name.startswith("_") or node.name == "__init__"


def is_test_module(path: Path) -> bool:
    """Return whether a path belongs to the repository test tree."""
    parts = {part.lower() for part in path.parts}
    return "gen_epix" not in parts and (
        "test" in parts or path.name.startswith("test_")
    )


def is_exception_class(node: ast.ClassDef) -> bool:
    """Return whether a class directly declares an exception base."""
    return any(
        isinstance(base, ast.Name)
        and base.id.endswith(("Error", "Exception"))
        or isinstance(base, ast.Attribute)
        and base.attr.endswith(("Error", "Exception"))
        for base in node.bases
    )


def imported_symbols(tree: ast.Module) -> list[str]:
    """Return symbols re-exported through import aliases."""
    symbols: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            symbols.extend(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            symbols.extend(
                alias.asname or alias.name.split(".")[0] for alias in node.names
            )
    return symbols


def has_direct_raise(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a function body directly raises an exception."""

    class DirectRaiseVisitor(ast.NodeVisitor):
        """Detect raises while excluding nested definition bodies."""

        found = False

        def visit_Raise(self, node: ast.Raise) -> None:
            """Record a direct raise statement."""
            self.found = True

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Skip a nested function definition."""

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            """Skip a nested async function definition."""

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            """Skip a nested class definition."""

    visitor = DirectRaiseVisitor()
    for child in node.body:
        visitor.visit(child)
    return visitor.found


def check_coverage(tree: ast.Module) -> list[tuple[int, str]]:
    """Return missing class and structural public-function docstrings."""
    findings: list[tuple[int, str]] = []
    if ast.get_docstring(tree) is None:
        findings.append((1, "coverage: module docstring is missing"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and ast.get_docstring(node) is None:
            findings.append(
                (
                    node.lineno,
                    f"coverage: class {node.name!r} docstring is missing",
                )
            )
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            for method in node.body:
                if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if (
                    is_public_function(method)
                    and not is_overload(method)
                    and not is_override(method)
                    and ast.get_docstring(method) is None
                ):
                    findings.append(
                        (
                            method.lineno,
                            f"coverage: function {method.name!r} docstring is missing",
                        )
                    )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if (
                is_public_function(node)
                and not is_overload(node)
                and ast.get_docstring(node) is None
            ):
                findings.append(
                    (
                        node.lineno,
                        f"coverage: function {node.name!r} docstring is missing",
                    )
                )
    return findings


def check_exception_classes(tree: ast.Module) -> list[tuple[int, str]]:
    """Return exception classes missing a meaningful docstring."""
    findings: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or not is_exception_class(node):
            continue
        docstring = ast.get_docstring(node)
        if not docstring:
            findings.append(
                (
                    node.lineno,
                    f"exception-class: exception {node.name!r} docstring is missing",
                )
            )
        elif "raise" in docstring.lower():
            findings.append(
                (
                    node.lineno,
                    f"exception-class: exception {node.name!r} describes when it is raised",
                )
            )
    return findings


def check_pydantic(tree: ast.Module) -> list[tuple[int, str]]:
    """Return Pydantic validation and serialization documentation violations."""
    findings: list[tuple[int, str]] = []
    for class_node in ast.walk(tree):
        if not isinstance(class_node, ast.ClassDef):
            continue
        methods = [
            node
            for node in class_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        docstring = ast.get_docstring(class_node) or ""
        if any(has_decorator(node, MODEL_VALIDATORS) for node in methods):
            if "Model validation:" not in docstring:
                findings.append(
                    (
                        class_node.lineno,
                        f"pydantic: model {class_node.name!r} lacks Model validation:",
                    )
                )
        if any(has_decorator(node, MODEL_SERIALIZERS) for node in methods):
            if "Model serialization:" not in docstring:
                findings.append(
                    (
                        class_node.lineno,
                        f"pydantic: model {class_node.name!r} lacks Model serialization:",
                    )
                )
        for method in methods:
            if not has_decorator(method, PYDANTIC_DECORATORS):
                continue
            if any(
                section in (ast.get_docstring(method) or "")
                for section in GOOGLE_SECTIONS
            ):
                findings.append(
                    (
                        method.lineno,
                        f"pydantic: method {method.name!r} has a Google-style contract",
                    )
                )
    return findings


def check_package(tree: ast.Module) -> list[tuple[int, str]]:
    """Return advisory findings for package re-exports absent from the docstring."""
    docstring = ast.get_docstring(tree)
    if not docstring:
        return [(1, "package: package docstring is missing")]
    return [
        (1, f"package: re-export {symbol!r} is not named in package docstring")
        for symbol in imported_symbols(tree)
        if symbol not in docstring
    ]


def check_raises(tree: ast.Module) -> list[tuple[int, str]]:
    """Return advisory findings for undocumented public direct raises."""
    findings: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if (
            not is_public_function(node)
            or is_overload(node)
            or is_override(node)
            or has_decorator(node, PYDANTIC_DECORATORS)
        ):
            continue
        if not has_direct_raise(node):
            continue
        if "Raises:" not in (ast.get_docstring(node) or ""):
            findings.append(
                (
                    node.lineno,
                    f"raises: review whether function {node.name!r} needs Raises:",
                )
            )
    return findings


def audit_file(path: Path, checks: set[str]) -> list[tuple[int, str]]:
    """Parse a file once and run each requested documentation audit."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as error:
        return [(1, f"parse: cannot parse file: {error}")]

    findings: list[tuple[int, str]] = []
    test_module = is_test_module(path)
    if "coverage" in checks and not test_module:
        findings.extend(check_coverage(tree))
    if "exception-class" in checks:
        findings.extend(check_exception_classes(tree))
    if "pydantic" in checks:
        findings.extend(check_pydantic(tree))
    if "package" in checks and path.name == "__init__.py" and not test_module:
        findings.extend(check_package(tree))
    if "raises" in checks:
        findings.extend(check_raises(tree))
    return findings


def main() -> int:
    """Run selected documentation audits for a Python file or directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Python file or directory to check")
    parser.add_argument(
        "--only",
        choices=sorted(CHECKS),
        nargs="+",
        metavar="CHECK",
        help="Run only selected checks; defaults to every check.",
    )
    args = parser.parse_args()
    checks = set(args.only) if args.only else CHECKS

    findings = [
        (path, line, message)
        for path in python_files(args.target)
        for line, message in audit_file(path, checks)
    ]
    blocking_findings = []
    for path, line, message in findings:
        if message.startswith(("package:", "raises:")):
            print(f"warning: {path}:{line}: {message}")
        else:
            blocking_findings.append((path, line, message))
            print(f"{path}:{line}: {message}")
    return int(bool(blocking_findings))


if __name__ == "__main__":
    raise SystemExit(main())

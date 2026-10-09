"""Test that lazily exported names stay consistent with their type-checking imports.

A package that resolves exports lazily declares them twice: as imports under
``if TYPE_CHECKING:`` for static type checkers, and as a mapping used at runtime.
These tests fail when the two get out of sync.
"""

import ast
import importlib
from pathlib import Path

import pytest

from gen_epix.util import get_package_root


def _find_lazy_packages() -> list[str]:
    """Return the names of all gen_epix packages and modules that use lazy exports."""
    root = get_package_root()
    packages = []
    for path in sorted((root / "gen_epix").rglob("*.py")):
        if path.name == "_lazy.py":
            continue
        if "lazy_exports(" in path.read_text(encoding="utf-8"):
            module_path = path.parent if path.name == "__init__.py" else path
            parts = module_path.relative_to(root).with_suffix("").parts
            packages.append(".".join(parts))
    return packages


def _get_type_checking_imports(path: Path) -> dict[str, str | tuple[str, str]]:
    """Return the exports declared as imports under ``if TYPE_CHECKING:``."""
    root = get_package_root()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    exports: dict[str, str | tuple[str, str]] = {}
    for node in tree.body:
        if not (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id == "TYPE_CHECKING"
        ):
            continue
        for import_node in node.body:
            assert isinstance(import_node, ast.ImportFrom), ast.dump(import_node)
            assert import_node.module is not None
            for alias in import_node.names:
                name = alias.asname or alias.name
                module_parts = [*import_node.module.split("."), alias.name]
                module_path = root.joinpath(*module_parts)
                is_module = (
                    module_path.is_dir() or module_path.with_suffix(".py").is_file()
                )
                exports[name] = (
                    ".".join(module_parts)
                    if is_module
                    else (import_node.module, alias.name)
                )
    return exports


LAZY_PACKAGES = _find_lazy_packages()


def test_lazy_packages_found() -> None:
    """Ensure that the packages under test are actually discovered."""
    assert "gen_epix" in LAZY_PACKAGES
    assert "gen_epix.fastapp" in LAZY_PACKAGES
    assert "gen_epix.casedb.services" in LAZY_PACKAGES
    assert "gen_epix.commondb.domain.exc" in LAZY_PACKAGES


@pytest.mark.parametrize("package_name", LAZY_PACKAGES)
def test_lazy_exports_match_type_checking_imports(package_name: str) -> None:
    """Ensure that the runtime mapping equals the type-checking imports."""
    package = importlib.import_module(package_name)
    assert package.__file__ is not None
    declared = _get_type_checking_imports(Path(package.__file__))
    lazy_exports = getattr(package, "_EXPORTS", None) or getattr(
        package, "_LAZY_EXPORTS"
    )
    assert dict(lazy_exports) == declared


@pytest.mark.parametrize("package_name", LAZY_PACKAGES)
def test_lazy_exports_resolve(package_name: str) -> None:
    """Ensure that every lazy export resolves to the object it is declared as."""
    package = importlib.import_module(package_name)
    lazy_exports = getattr(package, "_EXPORTS", None) or getattr(
        package, "_LAZY_EXPORTS"
    )
    for name, export in lazy_exports.items():
        if isinstance(export, str):
            expected = importlib.import_module(export)
        else:
            expected = getattr(importlib.import_module(export[0]), export[1])
        assert getattr(package, name) is expected, name
        assert name in dir(package)


def test_lazy_export_unknown_name_raises() -> None:
    """Ensure that a name that is not exported still raises AttributeError."""
    package = importlib.import_module("gen_epix")
    with pytest.raises(AttributeError, match="has no attribute 'does_not_exist'"):
        getattr(package, "does_not_exist")


def test_facade_all_matches_exports() -> None:
    """Ensure that ``gen_epix.__all__`` lists exactly the exported names."""
    package = importlib.import_module("gen_epix")
    assert sorted(package.__all__) == sorted(package._EXPORTS)

"""Support lazily resolved package exports (PEP 562).

A package ``__init__`` that re-exports names from heavy submodules can defer
those imports until a name is first accessed, so that importing the package, or
any of its submodules, does not load everything it re-exports. The package
declares the same imports under ``if TYPE_CHECKING:`` so that static type
checkers keep seeing the real types.

This module only depends on the standard library, so that it can be used by
every package ``__init__`` without importing anything else.
"""

import importlib
import sys
from collections.abc import Callable, Mapping
from typing import Any

# Either the path of the module that is itself exported, or the path of a module
# and the name of the attribute of that module that is exported.
LazyExport = str | tuple[str, str]


def lazy_exports(
    module_name: str, exports: Mapping[str, LazyExport]
) -> tuple[Callable[[str], Any], Callable[[], list[str]]]:
    """Create module-level ``__getattr__`` and ``__dir__`` for lazy exports.

    Args:
        module_name: ``__name__`` of the package whose exports are resolved lazily.
        exports: Exported name mapped to its source, either a module path for a
            module export or a ``(module path, attribute name)`` pair.

    Returns:
        The ``__getattr__`` and ``__dir__`` functions to assign in the package.
    """

    def __getattr__(name: str) -> Any:
        export = exports.get(name)
        if export is None:
            raise AttributeError(f"module {module_name!r} has no attribute {name!r}")
        if isinstance(export, str):
            value = importlib.import_module(export)
        else:
            value = getattr(importlib.import_module(export[0]), export[1])
        # Cache, so that subsequent access does not go through __getattr__
        setattr(sys.modules[module_name], name, value)
        return value

    def __dir__() -> list[str]:
        return sorted({*vars(sys.modules[module_name]), *exports})

    return __getattr__, __dir__


def lazy_star_exports(
    module_name: str, source_module_name: str
) -> tuple[Callable[[str], Any], Callable[[], list[str]]]:
    """Create ``__getattr__`` and ``__dir__`` that defer a wildcard re-export.

    The lazy counterpart of ``from <source module> import *``: the public names of
    the source module are available as attributes of the exporting module, but the
    source module is only imported once one of them is accessed.

    Args:
        module_name: ``__name__`` of the module that re-exports the names.
        source_module_name: Path of the module whose public names are re-exported.

    Returns:
        The ``__getattr__`` and ``__dir__`` functions to assign in the module.
    """

    def __getattr__(name: str) -> Any:
        message = f"module {module_name!r} has no attribute {name!r}"
        if name.startswith("_"):
            raise AttributeError(message)
        try:
            source_module = importlib.import_module(source_module_name)
        except ImportError as exception:
            # The source module needs a package that is not installed. The name is
            # then reported as absent, as hasattr() and similar probes expect, with
            # the import failure as the cause.
            raise AttributeError(message) from exception
        if not hasattr(source_module, name):
            raise AttributeError(message)
        value = getattr(source_module, name)
        setattr(sys.modules[module_name], name, value)
        return value

    def __dir__() -> list[str]:
        names = set(vars(sys.modules[module_name]))
        try:
            source_module = importlib.import_module(source_module_name)
        except ImportError:
            return sorted(names)
        names.update(x for x in vars(source_module) if not x.startswith("_"))
        return sorted(names)

    return __getattr__, __dir__

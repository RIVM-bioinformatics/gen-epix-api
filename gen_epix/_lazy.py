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

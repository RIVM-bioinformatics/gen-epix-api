"""Guard against route handlers that would block the event loop.

Command handling (``app.handle``) is synchronous: SQLAlchemy over pyodbc, and
synchronous HTTP clients. An ``async def`` route handler that calls it runs it on
the event loop and blocks every other request on the worker, including
``/v1/health``, until it is done. Route handlers are therefore plain ``def``, so
FastAPI runs them in its threadpool. Only handlers that need to ``await``, and
offload their synchronous work themselves, may be ``async def``.
"""

import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[3] / "gen_epix"

# (module path relative to gen_epix, handler name) -> reason it may be async
ALLOWED_ASYNC_HANDLERS = {
    ("commondb/api/system.py", "get__health"): (
        "does no I/O; on the event loop it answers even when the threadpool is busy"
    ),
    ("casedb/api/case.py", "retrieve__genetic_sequence_fasta"): (
        "awaits token authentication and offloads app.handle with run_in_threadpool"
    ),
}


def _async_route_handlers() -> set[tuple[str, str]]:
    """Return (module, name) of every async function defined in an API module."""
    found: set[tuple[str, str]] = set()
    for path in PACKAGE_ROOT.glob("*/api/*.py"):
        module = path.relative_to(PACKAGE_ROOT).as_posix()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.AsyncFunctionDef):
                found.add((module, node.name))
    return found


def test_route_handlers_are_sync_unless_allowed() -> None:
    unexpected = _async_route_handlers() - set(ALLOWED_ASYNC_HANDLERS)

    assert not unexpected, (
        "Route handlers must be 'def', not 'async def', so that FastAPI runs their "
        f"synchronous command handling in the threadpool: {sorted(unexpected)}"
    )


def test_allowed_async_handlers_still_exist() -> None:
    stale = set(ALLOWED_ASYNC_HANDLERS) - _async_route_handlers()

    assert not stale, f"Remove stale entries from ALLOWED_ASYNC_HANDLERS: {stale}"

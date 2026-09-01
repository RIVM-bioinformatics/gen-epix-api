"""Request scope and principal partitioning.

Two distinct concerns share this module. `RequestScope` is a per-request layer
above the shared cache that guarantees read-your-own-writes within one unit of
work. `ScopeProvider` supplies the identity parts, such as a tenant or a
principal, that must enter the cache key of any result whose content depends on
who asked for it; omitting them is the usual cause of cross-principal leakage.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from gen_epix.fastapp.cache.exc import CacheConfigurationError

_SCOPE_PARTS: ContextVar[Mapping[str, str] | None] = ContextVar(
    "gen_epix_cache_scope_parts", default=None
)
_REQUEST_VALUES: ContextVar[dict[str, Any] | None] = ContextVar(
    "gen_epix_cache_request_values", default=None
)


class ScopeProvider(ABC):
    """Supply the identity parts that partition a cache key."""

    @abstractmethod
    def current(self) -> Mapping[str, str]:
        """Return the parts in force for the calling context."""

    def render(self, required: tuple[str, ...]) -> str:
        """Return the key fragment for the required parts.

        Args:
            required: Names of the parts a region declares as mandatory.

        Returns:
            The parts joined in the declared order, or an empty string when no
            part is required.

        Raises:
            CacheConfigurationError: If a required part is absent. Failing
                closed is deliberate: a missing tenant or principal would
                otherwise produce a key shared by every caller.
        """
        if not required:
            return ""
        parts = self.current()
        missing = [name for name in required if not parts.get(name)]
        if missing:
            raise CacheConfigurationError(
                f"Cache scope is missing required parts {missing}"
            )
        return ",".join(f"{name}={parts[name]}" for name in required)


class NullScopeProvider(ScopeProvider):
    """Provide no identity parts.

    This is correct only for regions whose values are identical for every
    caller.
    """

    __slots__ = ()

    def current(self) -> Mapping[str, str]:
        """See base method."""
        return {}


class StaticScopeProvider(ScopeProvider):
    """Provide a fixed set of identity parts.

    Attributes:
        parts: The parts returned for every call.
    """

    __slots__ = ("parts",)

    def __init__(self, **parts: str):
        """Initialize a StaticScopeProvider instance."""
        self.parts: dict[str, str] = dict(parts)

    def current(self) -> Mapping[str, str]:
        """See base method."""
        return self.parts


class ContextVarScopeProvider(ScopeProvider):
    """Read identity parts from a context variable.

    Middleware binds the parts once per request with `bind`, after which every
    cached call made inside that request, including calls on worker threads
    started with a copied context, is partitioned automatically.
    """

    __slots__ = ()

    def current(self) -> Mapping[str, str]:
        """See base method."""
        return _SCOPE_PARTS.get() or {}

    @staticmethod
    @contextmanager
    def bind(**parts: str) -> Iterator[Mapping[str, str]]:
        """Bind identity parts for the duration of the block.

        Nested binds merge into the enclosing parts rather than replacing them,
        so a handler may add a narrower part without losing the tenant bound by
        middleware.

        Args:
            **parts: Identity part names and values.

        Yields:
            The effective parts inside the block.
        """
        merged = dict(_SCOPE_PARTS.get() or {})
        merged.update(parts)
        token = _SCOPE_PARTS.set(merged)
        try:
            yield merged
        finally:
            _SCOPE_PARTS.reset(token)


class RequestScope:
    """Memoize values for the duration of one request.

    The scope sits above the shared cache. Entries written here are visible to
    the rest of the request immediately, which gives read-your-own-writes even
    when the shared cache is still serving an older value, and they are
    discarded when the request ends. Outside an active scope every operation is
    a no-op, so the same code path works in a background job.
    """

    __slots__ = ()

    @staticmethod
    @contextmanager
    def activate() -> Iterator[dict[str, Any]]:
        """Open a fresh scope for the duration of the block.

        Yields:
            The mapping backing the scope, mainly useful for assertions.
        """
        token = _REQUEST_VALUES.set({})
        try:
            yield _REQUEST_VALUES.get() or {}
        finally:
            _REQUEST_VALUES.reset(token)

    @property
    def is_active(self) -> bool:
        """Return whether a scope is currently open."""
        return _REQUEST_VALUES.get() is not None

    def get(self, key: str, default: Any = None) -> Any:
        """Return a value memoized in the current scope.

        Args:
            key: The composed cache key.
            default: Value returned when the key is absent or no scope is open.
        """
        values = _REQUEST_VALUES.get()
        if values is None:
            return default
        return values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Memoize a value in the current scope, if one is open.

        Args:
            key: The composed cache key.
            value: The value to remember for the rest of the request.
        """
        values = _REQUEST_VALUES.get()
        if values is not None:
            values[key] = value

    def discard(self, key: str) -> None:
        """Forget one memoized value in the current scope.

        Args:
            key: The composed cache key.
        """
        values = _REQUEST_VALUES.get()
        if values is not None:
            values.pop(key, None)

    def clear(self) -> None:
        """Forget every value memoized in the current scope."""
        values = _REQUEST_VALUES.get()
        if values is not None:
            values.clear()

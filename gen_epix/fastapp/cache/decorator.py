"""Declarative caching of function results.

`CachedFunction` is what makes invalidation from an unrelated method possible.
The decorated callable keeps its signature but also exposes the inverse of the
cache operation: `invalidate` for one argument combination, `invalidate_all` for
every result of that function, `set` to publish a value without calling it,
`refresh` to recompute one entry, and `original` to bypass the cache entirely.
Every entry additionally carries an implicit tag naming the function, which is
what allows `invalidate_all` to work against a store whose keys cannot be
enumerated.
"""

import functools
import inspect
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any

from gen_epix.fastapp.cache.key import KeySpec, bind_arguments, function_namespace
from gen_epix.fastapp.cache.stats import CacheStatistics
from gen_epix.fastapp.cache.tag import render_tags

if TYPE_CHECKING:
    from gen_epix.fastapp.cache.region import CacheRegion


class CachedFunction:
    """Wrap a function so that its results are cached and can be invalidated.

    An instance behaves like the wrapped function and additionally acts as a
    descriptor, so it can decorate a plain function or a method. The receiver of
    a method is excluded from the key, which means one cache entry is shared by
    every instance; add the discriminating attribute to the key through a
    `KeySpec` template when that is not what you want.

    Attributes:
        region: The region holding the entries.
        function: The wrapped function.
        ttl: Time to live overriding the region default, if any.
        tag_templates: Tag templates rendered against each call.
        function_tag: Implicit tag carried by every entry of this function.
    """

    def __init__(
        self,
        region: "CacheRegion",
        fn: Callable[..., Any],
        key_spec: KeySpec,
        ttl: float | None = None,
        tags: tuple[str, ...] = (),
        should_cache_fn: Callable[[Any], bool] | None = None,
        condition: Callable[..., bool] | None = None,
    ):
        """Initialize a CachedFunction instance.

        Args:
            region: The region holding the entries.
            fn: The function to wrap.
            key_spec: How keys are composed from the call arguments.
            ttl: Time to live overriding the region default.
            tags: Constant tags or templates over parameter names.
            should_cache_fn: Predicate receiving the result, deciding storage.
            condition: Predicate receiving the call arguments. When it returns
                False the call bypasses the cache in both directions.
        """
        self.region = region
        self.function = fn
        self.ttl = ttl
        self.tag_templates = tuple(tags)
        self.function_tag = function_namespace(fn, key_spec.namespace)
        self._key_generator = key_spec.build(fn)
        self._should_cache_fn = should_cache_fn
        self._condition = condition
        functools.update_wrapper(self, fn)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Return the cached result, computing it on a miss.

        Args:
            *args: Positional arguments of the wrapped function.
            **kwargs: Keyword arguments of the wrapped function.

        Returns:
            The cached or freshly computed result.

        Raises:
            Exception: Whatever the wrapped function raised.
        """
        if self._condition is not None and not self._condition(*args, **kwargs):
            return self.function(*args, **kwargs)
        return self.region.get_or_create(
            self.key(*args, **kwargs),
            lambda: self.function(*args, **kwargs),
            ttl=self.ttl,
            tags=self.tags(*args, **kwargs),
            should_cache_fn=self._should_cache_fn,
        )

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        """Bind the wrapper to an instance when used as a method.

        Args:
            instance: The receiver, or None when accessed on the class.
            owner: The class the attribute was looked up on.

        Returns:
            This wrapper when accessed on the class, otherwise a bound view
            that forwards the receiver to every operation.
        """
        if instance is None:
            return self
        return BoundCachedFunction(self, instance)

    def key(self, *args: Any, **kwargs: Any) -> str:
        """Return the logical cache key for one argument combination.

        A writer that wants to invalidate a specific result and prefers not to
        depend on the reader can reproduce the key with this method.

        Args:
            *args: Positional arguments of the wrapped function.
            **kwargs: Keyword arguments of the wrapped function.
        """
        return self._key_generator(*args, **kwargs)

    def tags(self, *args: Any, **kwargs: Any) -> frozenset[str]:
        """Return the tags attached to the entry for one argument combination.

        Args:
            *args: Positional arguments of the wrapped function.
            **kwargs: Keyword arguments of the wrapped function.
        """
        rendered = render_tags(
            self.tag_templates, bind_arguments(self.function, args, kwargs)
        )
        return rendered | {self.function_tag}

    def get(self, *args: Any, **kwargs: Any) -> Any:
        """Return the cached result without computing it.

        Args:
            *args: Positional arguments of the wrapped function.
            **kwargs: Keyword arguments of the wrapped function.

        Returns:
            The cached result, or `NO_VALUE` when nothing usable is cached.
        """
        return self.region.get(self.key(*args, **kwargs))

    def set(self, value: Any, *args: Any, **kwargs: Any) -> None:
        """Publish a result without calling the wrapped function.

        This is the write-update alternative to eviction: a writer that already
        knows the new value can install it and avoid the miss that a deletion
        would cause.

        Args:
            value: The result to store.
            *args: Positional arguments identifying the entry.
            **kwargs: Keyword arguments identifying the entry.
        """
        self.region.set(
            self.key(*args, **kwargs),
            value,
            ttl=self.ttl,
            tags=self.tags(*args, **kwargs),
        )

    def refresh(self, *args: Any, **kwargs: Any) -> Any:
        """Recompute one entry and store the new result.

        Args:
            *args: Positional arguments of the wrapped function.
            **kwargs: Keyword arguments of the wrapped function.

        Returns:
            The freshly computed result.

        Raises:
            Exception: Whatever the wrapped function raised.
        """
        value = self.function(*args, **kwargs)
        self.set(value, *args, **kwargs)
        return value

    def invalidate(self, *args: Any, **kwargs: Any) -> None:
        """Remove the entry for one argument combination.

        Args:
            *args: Positional arguments identifying the entry.
            **kwargs: Keyword arguments identifying the entry.
        """
        self.region.invalidate_keys(self.key(*args, **kwargs))

    def invalidate_all(self) -> None:
        """Remove every entry produced by this function.

        The removal uses the implicit function tag, so it works without
        enumerating keys and without touching entries of other functions that
        share the region.
        """
        self.region.invalidate_tags(self.function_tag)

    def original(self, *args: Any, **kwargs: Any) -> Any:
        """Call the wrapped function, bypassing the cache in both directions.

        Args:
            *args: Positional arguments of the wrapped function.
            **kwargs: Keyword arguments of the wrapped function.

        Returns:
            The freshly computed result.

        Raises:
            Exception: Whatever the wrapped function raised.
        """
        return self.function(*args, **kwargs)

    def cache_info(self) -> CacheStatistics:
        """Return the statistics of the region backing this function."""
        return self.region.statistics()


class AsyncCachedFunction(CachedFunction):
    """Cache the results of a coroutine function.

    Only the call path differs from `CachedFunction`: it awaits the wrapped
    function and coordinates concurrent awaits for the same key. `refresh` and
    `original` are awaitable as well; `invalidate`, `set` and `key` stay
    synchronous because they never touch the origin.
    """

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Return the cached result, awaiting the loader on a miss.

        Args:
            *args: Positional arguments of the wrapped function.
            **kwargs: Keyword arguments of the wrapped function.

        Returns:
            The cached or freshly computed result.

        Raises:
            Exception: Whatever the wrapped coroutine raised.
        """
        if self._condition is not None and not self._condition(*args, **kwargs):
            return await self.function(*args, **kwargs)
        return await self.region.aget_or_create(
            self.key(*args, **kwargs),
            lambda: self.function(*args, **kwargs),
            ttl=self.ttl,
            tags=self.tags(*args, **kwargs),
            should_cache_fn=self._should_cache_fn,
        )

    async def refresh(self, *args: Any, **kwargs: Any) -> Any:
        """Recompute one entry by awaiting the wrapped coroutine.

        Args:
            *args: Positional arguments of the wrapped function.
            **kwargs: Keyword arguments of the wrapped function.

        Returns:
            The freshly computed result.

        Raises:
            Exception: Whatever the wrapped coroutine raised.
        """
        value = await self.function(*args, **kwargs)
        self.set(value, *args, **kwargs)
        return value

    async def original(self, *args: Any, **kwargs: Any) -> Any:
        """Await the wrapped coroutine, bypassing the cache.

        Args:
            *args: Positional arguments of the wrapped function.
            **kwargs: Keyword arguments of the wrapped function.

        Returns:
            The freshly computed result.

        Raises:
            Exception: Whatever the wrapped coroutine raised.
        """
        return await self.function(*args, **kwargs)


class BoundCachedFunction:
    """Forward the receiver of a cached method to every cache operation.

    Accessing a `CachedFunction` on an instance yields one of these, so that
    ``instance.method.invalidate(x)`` reaches the same entry as
    ``instance.method(x)``.

    Attributes:
        cached: The underlying cached function.
        instance: The receiver to forward.
    """

    __slots__ = ("cached", "instance")

    def __init__(self, cached: CachedFunction, instance: Any):
        """Initialize a BoundCachedFunction instance."""
        self.cached = cached
        self.instance = instance

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the cached function with the bound receiver."""
        return self.cached(self.instance, *args, **kwargs)

    def key(self, *args: Any, **kwargs: Any) -> str:
        """Return the logical key for one argument combination."""
        return self.cached.key(self.instance, *args, **kwargs)

    def tags(self, *args: Any, **kwargs: Any) -> frozenset[str]:
        """Return the tags for one argument combination."""
        return self.cached.tags(self.instance, *args, **kwargs)

    def get(self, *args: Any, **kwargs: Any) -> Any:
        """Return the cached result without computing it."""
        return self.cached.get(self.instance, *args, **kwargs)

    def set(self, value: Any, *args: Any, **kwargs: Any) -> None:
        """Publish a result without calling the wrapped method."""
        self.cached.set(value, self.instance, *args, **kwargs)

    def refresh(self, *args: Any, **kwargs: Any) -> Any:
        """Recompute one entry and store the new result."""
        return self.cached.refresh(self.instance, *args, **kwargs)

    def invalidate(self, *args: Any, **kwargs: Any) -> None:
        """Remove the entry for one argument combination."""
        self.cached.invalidate(self.instance, *args, **kwargs)

    def invalidate_all(self) -> None:
        """Remove every entry produced by this method."""
        self.cached.invalidate_all()

    def original(self, *args: Any, **kwargs: Any) -> Any:
        """Call the wrapped method, bypassing the cache."""
        return self.cached.original(self.instance, *args, **kwargs)

    def cache_info(self) -> CacheStatistics:
        """Return the statistics of the region backing this method."""
        return self.cached.cache_info()


def make_cached_function(
    region: "CacheRegion",
    fn: Callable[..., Any],
    key_spec: KeySpec,
    ttl: float | None = None,
    tags: Iterable[str] = (),
    should_cache_fn: Callable[[Any], bool] | None = None,
    condition: Callable[..., bool] | None = None,
) -> CachedFunction:
    """Wrap a function or coroutine function in the matching cached callable.

    Args:
        region: The region holding the entries.
        fn: The function to wrap.
        key_spec: How keys are composed from the call arguments.
        ttl: Time to live overriding the region default.
        tags: Constant tags or templates over parameter names.
        should_cache_fn: Predicate receiving the result, deciding storage.
        condition: Predicate receiving the call arguments, deciding bypass.

    Returns:
        A `CachedFunction`, or an `AsyncCachedFunction` for a coroutine
        function.
    """
    factory = AsyncCachedFunction if inspect.iscoroutinefunction(fn) else CachedFunction
    return factory(
        region=region,
        fn=fn,
        key_spec=key_spec,
        ttl=ttl,
        tags=tuple(tags),
        should_cache_fn=should_cache_fn,
        condition=condition,
    )


__all__ = [
    "AsyncCachedFunction",
    "BoundCachedFunction",
    "CachedFunction",
    "make_cached_function",
]

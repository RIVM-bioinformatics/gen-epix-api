"""Registry and configuration entry point for cache regions.

`CacheManager` owns the regions of an application, builds them from
configuration, aggregates their statistics, and provides the operations that
span more than one region: invalidating a declared dependency, invalidating a
tag everywhere, clearing everything, disabling caching wholesale, and deferring
invalidation until a unit of work commits.

The dependency-based entry point is the one a writer should normally use.
Readers declare what their results depend on; a writer calls
`invalidate_dependents("case", {"case_id": ...})` and never learns which regions,
keys or functions exist.
"""

from collections.abc import Callable, Iterable, Iterator, Mapping
from contextlib import ExitStack, contextmanager
from enum import Enum
from typing import Any

from gen_epix.fastapp.cache.clock import Clock, SystemClock
from gen_epix.fastapp.cache.enum import (
    EvictionPolicyType,
    ExpiryMode,
    FailureMode,
    InvalidationMode,
)
from gen_epix.fastapp.cache.exc import (
    CacheConfigurationError,
    RegionAlreadyConfiguredError,
    RegionNotFoundError,
)
from gen_epix.fastapp.cache.invalidation import (
    DependencyRegistry,
    Invalidation,
    InvalidationBus,
)
from gen_epix.fastapp.cache.model import RegionConfig
from gen_epix.fastapp.cache.region import CacheRegion
from gen_epix.fastapp.cache.stats import CacheListener, CacheStatistics
from gen_epix.fastapp.cache.transaction import (
    InvalidationTransaction,
    enlist,
    invalidation_transaction,
)
from gen_epix.fastapp.cache.version import MemoryVersionStore, VersionStore

_ENUM_FIELDS: dict[str, type[Enum]] = {
    "eviction_policy": EvictionPolicyType,
    "expiry_mode": ExpiryMode,
    "failure_mode": FailureMode,
}


def region_config_from_mapping(
    name: str,
    settings: Mapping[str, Any],
) -> RegionConfig:
    """Build a region configuration from a settings mapping.

    String values are accepted for the enumerated fields so that a region can be
    described entirely in a configuration file.

    Args:
        name: The region name, which overrides any name in `settings`.
        settings: Field names and values of `RegionConfig`.

    Returns:
        The configuration.

    Raises:
        CacheConfigurationError: If a field is unknown or an enumerated value is
            not one of the accepted names.
    """
    known = set(RegionConfig.__dataclass_fields__)
    unknown = set(settings) - known
    if unknown:
        raise CacheConfigurationError(
            f"Unknown cache settings for region {name}: {sorted(unknown)}"
        )
    values: dict[str, Any] = {
        key: value for key, value in settings.items() if key != "name"
    }
    for field, enum_type in _ENUM_FIELDS.items():
        value = values.get(field)
        if isinstance(value, str):
            try:
                values[field] = enum_type[value.upper()]
            except KeyError as exception:
                raise CacheConfigurationError(
                    f"Invalid {field} {value!r} for region {name}"
                ) from exception
    if "scope_parts" in values:
        values["scope_parts"] = _as_scope_parts(name, values["scope_parts"])
    return RegionConfig(name=name, **values)


def _as_scope_parts(region_name: str, value: Any) -> tuple[str, ...]:
    """Return a configured `scope_parts` value as a tuple of part names.

    A bare string is refused rather than iterated, because `tuple("tenant")`
    would silently yield one scope part per character and produce keys that
    look partitioned but are not.

    Args:
        region_name: The region the setting belongs to, used in error messages.
        value: The configured value.

    Returns:
        The scope part names.

    Raises:
        CacheConfigurationError: If the value is a string, is not a list or
            tuple, or contains anything other than non-empty strings.
    """
    if isinstance(value, str):
        raise CacheConfigurationError(
            f"scope_parts for region {region_name} must be a list of names, "
            f"not the string {value!r}"
        )
    if not isinstance(value, (list, tuple)):
        raise CacheConfigurationError(
            f"scope_parts for region {region_name} must be a list of names"
        )
    parts = tuple(value)
    if any(not isinstance(part, str) or not part for part in parts):
        raise CacheConfigurationError(
            f"scope_parts for region {region_name} must contain non-empty names"
        )
    return parts


class CacheManager:
    """Own the regions of an application and the operations that span them.

    The manager is created once during composition and is safe for concurrent
    use. Regions created through it share the clock, the invalidation bus and
    the version store, which is what makes a cross-region invalidation coherent
    and what lets one bump reach every process.

    Attributes:
        clock: Time source shared by every region it creates.
        dependencies: Registry translating a changed thing into invalidations.
    """

    def __init__(
        self,
        clock: Clock | None = None,
        bus: InvalidationBus | None = None,
        version_store: VersionStore | None = None,
        listener: CacheListener | None = None,
        dependencies: DependencyRegistry | None = None,
    ):
        """Initialize a CacheManager instance.

        Args:
            clock: Time source shared by every region.
            bus: Propagates invalidation between processes. Regions created by
                this manager subscribe to it automatically.
            version_store: Holder of the region generations.
            listener: Observer attached to every region created here.
            dependencies: Registry of declared dependencies.
        """
        self.clock = clock if clock is not None else SystemClock()
        self.dependencies = (
            dependencies if dependencies is not None else DependencyRegistry()
        )
        self._bus = bus
        self._versions = (
            version_store if version_store is not None else MemoryVersionStore()
        )
        self._listener = listener
        self._regions: dict[str, CacheRegion] = {}

    def create_region(self, config: RegionConfig, **kwargs: Any) -> CacheRegion:
        """Build a region, register it and return it.

        Args:
            config: The declarative policy of the region.
            **kwargs: Collaborators forwarded to `CacheRegion`, overriding the
                shared clock, bus, version store or listener when given.

        Returns:
            The registered region.

        Raises:
            RegionAlreadyConfiguredError: If a region of that name exists.
        """
        kwargs.setdefault("clock", self.clock)
        kwargs.setdefault("bus", self._bus)
        kwargs.setdefault("version_store", self._versions)
        kwargs.setdefault("listener", self._listener)
        return self.register_region(CacheRegion(config, **kwargs))

    def register_region(self, region: CacheRegion) -> CacheRegion:
        """Register an externally built region.

        Args:
            region: The region to register.

        Returns:
            The registered region.

        Raises:
            RegionAlreadyConfiguredError: If a region of that name exists.
        """
        if region.name in self._regions:
            raise RegionAlreadyConfiguredError(
                f"Cache region {region.name} is already registered"
            )
        self._regions[region.name] = region
        return region

    def configure(
        self,
        settings: Mapping[str, Mapping[str, Any]],
        **kwargs: Any,
    ) -> list[CacheRegion]:
        """Create every region described by a settings mapping.

        Args:
            settings: Region names mapped to their `RegionConfig` fields.
            **kwargs: Collaborators forwarded to every created region.

        Returns:
            The created regions, in the order they were described.

        Raises:
            CacheConfigurationError: If a region description is invalid.
            RegionAlreadyConfiguredError: If a described region already exists.
        """
        return [
            self.create_region(region_config_from_mapping(name, values), **kwargs)
            for name, values in settings.items()
        ]

    def get_region(self, name: str) -> CacheRegion:
        """Return a registered region.

        Args:
            name: The region name.

        Returns:
            The region.

        Raises:
            RegionNotFoundError: If no region of that name is registered.
        """
        try:
            return self._regions[name]
        except KeyError as exception:
            raise RegionNotFoundError(f"Unknown cache region {name}") from exception

    @property
    def region_names(self) -> list[str]:
        """Return the names of the registered regions."""
        return list(self._regions)

    def regions(self) -> Iterator[CacheRegion]:
        """Yield the registered regions."""
        return iter(list(self._regions.values()))

    def declare_dependency(
        self,
        dependency: str,
        tags: Iterable[str] = (),
        namespaces: Iterable[str] = (),
        regions: Iterable[str] = (),
    ) -> None:
        """Declare what a change to `dependency` invalidates.

        Args:
            dependency: Name of the thing that changes, such as a model name.
            tags: Tag templates over the parameters of the change.
            namespaces: Namespaces whose generation must be advanced.
            regions: Regions that must be cleared entirely.
        """
        self.dependencies.declare(
            dependency, tags=tags, namespaces=namespaces, regions=regions
        )

    def invalidate_dependents(
        self,
        dependency: str,
        parameters: Mapping[str, Any] | None = None,
        mode: InvalidationMode = InvalidationMode.HARD,
    ) -> int:
        """Invalidate everything that was declared to depend on `dependency`.

        This is the operation a mutating method should call. It names the thing
        that changed rather than the caches that hold derived results, so adding
        a new cached reader later requires no change at the call site.

        Args:
            dependency: Name of the thing that changed.
            parameters: Values substituted into the declared tag templates.
            mode: Whether readers must wait for fresh data.

        Returns:
            The number of invalidation requests dispatched, which is zero when
            nothing was declared for that dependency.
        """
        invalidations = self.dependencies.resolve(dependency, parameters, mode)
        for invalidation in invalidations:
            self._dispatch(invalidation)
        return len(invalidations)

    def invalidate_tags(
        self,
        *tags: str,
        region: str | None = None,
        mode: InvalidationMode = InvalidationMode.HARD,
    ) -> None:
        """Invalidate tags in one region or in every region.

        Args:
            *tags: The tags to invalidate.
            region: Restrict the request to one region, or None for all.
            mode: Whether readers must wait for fresh data.
        """
        if tags:
            self._dispatch(
                Invalidation.for_tags(frozenset(tags), region=region, mode=mode)
            )

    def invalidate_keys(self, *keys: str, region: str) -> None:
        """Invalidate fully composed keys in one region.

        Keys are region specific, so a region name is required.

        Args:
            *keys: Logical keys as accepted by the region.
            region: The region owning the keys.

        Raises:
            RegionNotFoundError: If the region is not registered.
        """
        self.get_region(region).invalidate_keys(*keys)

    def clear_all(self) -> None:
        """Delete every entry in every region."""
        self._dispatch(Invalidation.for_all())

    def statistics(self) -> dict[str, CacheStatistics]:
        """Return the counters of every region, keyed by region name."""
        return {name: region.statistics() for name, region in self._regions.items()}

    def total_statistics(self) -> CacheStatistics:
        """Return the counters of every region summed together."""
        total = CacheStatistics()
        for region in self._regions.values():
            total = total + region.statistics()
        return total

    def reset_statistics(self) -> None:
        """Set the counters of every region back to zero."""
        for region in self._regions.values():
            region.reset_statistics()

    @contextmanager
    def disabling(self) -> Iterator["CacheManager"]:
        """Bypass every registered region for the duration of the block.

        Running a test both inside and outside this block is the most direct
        check that behavior does not depend on a cache hit.

        Yields:
            This manager, for convenience.
        """
        with ExitStack() as stack:
            for region in self._regions.values():
                stack.enter_context(region.disabling())
            yield self

    @contextmanager
    def transaction(self) -> Iterator[InvalidationTransaction]:
        """Defer every invalidation in the block until it completes.

        Leaving the block normally applies the buffered requests; leaving it
        with an exception discards them. Wrapping a unit of work in this block
        removes the race in which a concurrent reader repopulates the cache from
        uncommitted state, and it stops a rolled-back change from clearing a
        cache that was still correct.

        Yields:
            The transaction, so that a caller can inspect `pending`.
        """
        with invalidation_transaction(self._apply_everywhere) as transaction:
            yield transaction

    def apply(self, invalidation: Invalidation) -> None:
        """Apply an invalidation request received from outside this process.

        A transport adapter calls this for every inbound message.

        Args:
            invalidation: The request to apply.
        """
        self._apply_everywhere(invalidation)

    def close(self) -> None:
        """Close every region and the invalidation bus."""
        for region in self._regions.values():
            region.close()
        if self._bus is not None:
            self._bus.close()

    def _dispatch(self, invalidation: Invalidation) -> None:
        """Route a request to the ambient transaction, the bus or the regions.

        Args:
            invalidation: The request to route.
        """
        if enlist(invalidation):
            return
        if self._bus is not None:
            self._bus.publish(invalidation)
            return
        self._apply_everywhere(invalidation)

    def _apply_everywhere(self, invalidation: Invalidation) -> None:
        """Offer a request to every region, which ignores what is not its own.

        Args:
            invalidation: The request to apply.
        """
        for region in list(self._regions.values()):
            region.apply(invalidation)


def create_default_manager(
    settings: Mapping[str, Mapping[str, Any]] | None = None,
    bus: InvalidationBus | None = None,
    clock: Clock | None = None,
    listener: CacheListener | None = None,
    region_kwargs: Mapping[str, Any] | None = None,
) -> CacheManager:
    """Build a manager and, optionally, the regions described in settings.

    Args:
        settings: Region names mapped to their configuration fields.
        bus: Propagates invalidation between processes.
        clock: Time source shared by every region.
        listener: Observer attached to every region.
        region_kwargs: Collaborators forwarded to every created region.

    Returns:
        The configured manager.

    Raises:
        CacheConfigurationError: If a region description is invalid.
    """
    manager = CacheManager(clock=clock, bus=bus, listener=listener)
    if settings:
        manager.configure(settings, **dict(region_kwargs or {}))
    return manager


CacheManagerFactory = Callable[[], CacheManager]
"""Factory type used where a manager is resolved lazily during composition."""

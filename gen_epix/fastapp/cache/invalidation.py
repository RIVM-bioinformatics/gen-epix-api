"""Invalidation requests, propagation and declared dependencies.

Three mechanisms live here, in increasing order of decoupling. `Invalidation`
describes one concrete request against keys, tags, a namespace or a whole
region. `InvalidationBus` propagates such a request to every process that holds
a local cache tier. `DependencyRegistry` lets readers declare once what their
results depend on, so that a writer can invalidate by naming the changed thing
instead of naming the caches that happen to hold it.

`InvalidationStrategy` implements the timestamp form of region invalidation: it
marks everything written before a moment as stale without touching the store,
and distinguishes a hard invalidation, where readers must wait for fresh data,
from a soft one, where the previous value may still be served while a refresh
runs.
"""

import threading
import uuid
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any

from gen_epix.fastapp.cache.clock import Clock, SystemClock
from gen_epix.fastapp.cache.enum import InvalidationMode, InvalidationScope
from gen_epix.fastapp.cache.tag import render_tags


@dataclass(slots=True, frozen=True)
class Invalidation:
    """Describe one invalidation request.

    A request is a value object so that it can be buffered until a transaction
    commits, published over a bus, and applied idempotently on the far side.

    Attributes:
        scope: What the request targets.
        mode: Whether readers must wait for fresh data or may serve stale data.
        region: Name of the target region, or None to target every region.
        keys: Fully composed keys targeted by a `KEY` request.
        tags: Tags targeted by a `TAG` request.
        namespace: Namespace whose generation a `NAMESPACE` request bumps.
        generation: Generation observed at the origin, so that a receiver can
            adopt it instead of bumping its own counter twice.
        origin: Identifier of the process that created the request, used to
            ignore an echo of one's own message.
        message_id: Stable identifier that makes repeated delivery harmless.
    """

    scope: InvalidationScope
    mode: InvalidationMode = InvalidationMode.HARD
    region: str | None = None
    keys: frozenset[str] = frozenset()
    tags: frozenset[str] = frozenset()
    namespace: str | None = None
    generation: int | None = None
    origin: str | None = None
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @classmethod
    def for_keys(
        cls,
        keys: Iterable[str],
        region: str | None = None,
        **kwargs: Any,
    ) -> "Invalidation":
        """Build a request targeting explicit keys.

        Args:
            keys: Fully composed cache keys.
            region: Target region name, or None for every region.
            **kwargs: Further fields such as `mode` or `origin`.
        """
        return cls(
            scope=InvalidationScope.KEY,
            keys=frozenset(keys),
            region=region,
            **kwargs,
        )

    @classmethod
    def for_tags(
        cls,
        tags: Iterable[str],
        region: str | None = None,
        **kwargs: Any,
    ) -> "Invalidation":
        """Build a request targeting tags.

        Args:
            tags: Tags carried by the entries to remove.
            region: Target region name, or None for every region.
            **kwargs: Further fields such as `mode` or `origin`.
        """
        return cls(
            scope=InvalidationScope.TAG,
            tags=frozenset(tags),
            region=region,
            **kwargs,
        )

    @classmethod
    def for_namespace(
        cls,
        namespace: str,
        generation: int | None = None,
        region: str | None = None,
        **kwargs: Any,
    ) -> "Invalidation":
        """Build a request that advances the generation of a namespace.

        Args:
            namespace: The namespace whose keys become unreachable.
            generation: Generation observed at the origin, when known.
            region: Target region name, or None for every region.
            **kwargs: Further fields such as `origin`.
        """
        return cls(
            scope=InvalidationScope.NAMESPACE,
            namespace=namespace,
            generation=generation,
            region=region,
            **kwargs,
        )

    @classmethod
    def for_region(cls, region: str, **kwargs: Any) -> "Invalidation":
        """Build a request that clears one whole region.

        Args:
            region: The region to clear.
            **kwargs: Further fields such as `mode` or `origin`.
        """
        return cls(scope=InvalidationScope.REGION, region=region, **kwargs)

    @classmethod
    def for_all(cls, **kwargs: Any) -> "Invalidation":
        """Build a request that clears every region.

        Args:
            **kwargs: Further fields such as `mode` or `origin`.
        """
        return cls(scope=InvalidationScope.ALL, **kwargs)


class InvalidationStrategy:
    """Invalidate by timestamp instead of by deletion.

    Recording a cut-off is constant time regardless of how many entries exist
    and works against a store whose keys cannot be enumerated. Entries written
    before the cut-off are ignored on read; they disappear later through expiry
    or eviction.

    A hard cut-off forces every reader to regenerate. A soft cut-off lets
    readers keep serving the previous value while one of them refreshes it,
    which avoids a load spike at the cost of bounded staleness.

    Attributes:
        clock: Time source, injectable for deterministic tests.
    """

    __slots__ = ("clock", "_lock", "_hard_at", "_soft_at")

    def __init__(self, clock: Clock | None = None):
        """Initialize an InvalidationStrategy instance."""
        self.clock = clock if clock is not None else SystemClock()
        self._lock = threading.Lock()
        self._hard_at: float | None = None
        self._soft_at: float | None = None

    def invalidate(self, mode: InvalidationMode = InvalidationMode.HARD) -> float:
        """Record a cut-off at the current time and return it.

        Args:
            mode: Whether stale values may still be served while refreshing.
        """
        now = self.clock.monotonic()
        with self._lock:
            if mode is InvalidationMode.HARD:
                self._hard_at = now
                self._soft_at = None
            else:
                self._soft_at = now
                self._hard_at = None
        return now

    def is_invalidated(self, created_at: float) -> bool:
        """Return whether an entry written at `created_at` is affected."""
        return self.is_hard_invalidated(created_at) or self.is_soft_invalidated(
            created_at
        )

    def is_hard_invalidated(self, created_at: float) -> bool:
        """Return whether an entry must not be served at all."""
        with self._lock:
            return self._hard_at is not None and created_at < self._hard_at

    def is_soft_invalidated(self, created_at: float) -> bool:
        """Return whether an entry may be served while a refresh runs."""
        with self._lock:
            return self._soft_at is not None and created_at < self._soft_at

    def reset(self) -> None:
        """Forget every recorded cut-off."""
        with self._lock:
            self._hard_at = None
            self._soft_at = None


class InvalidationBus(ABC):
    """Propagate invalidation requests to every holder of a local cache tier.

    A process-local first tier only sees a deletion performed by its own
    process. Without a bus, invalidating from one worker leaves the other
    workers serving the old value until it expires, which is a common and
    silent production defect.
    """

    @abstractmethod
    def publish(self, invalidation: Invalidation) -> None:
        """Send a request to every subscriber, including remote ones."""

    @abstractmethod
    def subscribe(self, handler: Callable[[Invalidation], None]) -> None:
        """Register a handler invoked for every received request."""

    @abstractmethod
    def close(self) -> None:
        """Release the resources held by the bus."""


class LocalInvalidationBus(InvalidationBus):
    """Deliver requests to subscribers inside this process.

    Delivery is idempotent: the identifier of every applied request is
    remembered, so a request that arrives twice, as at-least-once transports
    routinely produce, is applied once. A failing handler is isolated so that
    one broken subscriber cannot block the others.

    Attributes:
        origin: Identifier attached to requests published through this bus.
        history_size: Number of recent message identifiers remembered.
    """

    __slots__ = ("origin", "history_size", "_lock", "_handlers", "_seen", "_order")

    def __init__(self, origin: str | None = None, history_size: int = 4096):
        """Initialize a LocalInvalidationBus instance."""
        self.origin = origin or uuid.uuid4().hex
        self.history_size = history_size
        self._lock = threading.Lock()
        self._handlers: list[Callable[[Invalidation], None]] = []
        self._seen: set[str] = set()
        self._order: deque[str] = deque()

    def publish(self, invalidation: Invalidation) -> None:
        """Stamp this bus as the origin and deliver the request.

        A request that already carries an origin keeps it, so re-publishing a
        message received from elsewhere does not disguise where it came from.
        The message identifier is preserved, which is what lets a transport
        recognize its own echo and lets repeated delivery stay harmless.

        Args:
            invalidation: The request to publish.
        """
        stamped = (
            invalidation
            if invalidation.origin is not None
            else replace(invalidation, origin=self.origin)
        )
        self.deliver(stamped)

    def subscribe(self, handler: Callable[[Invalidation], None]) -> None:
        """See base method."""
        with self._lock:
            self._handlers.append(handler)

    def deliver(self, invalidation: Invalidation) -> bool:
        """Apply a request once, whether it was published locally or received.

        A transport adapter calls this for every inbound message.

        Args:
            invalidation: The request to apply.

        Returns:
            Whether the request was new and therefore delivered.
        """
        with self._lock:
            if invalidation.message_id in self._seen:
                return False
            self._seen.add(invalidation.message_id)
            self._order.append(invalidation.message_id)
            while len(self._order) > self.history_size:
                self._seen.discard(self._order.popleft())
            handlers = list(self._handlers)
        for handler in handlers:
            try:
                handler(invalidation)
            except Exception:  # noqa: BLE001 - one subscriber must not block others
                continue
        return True

    def close(self) -> None:
        """See base method."""
        with self._lock:
            self._handlers.clear()
            self._seen.clear()
            self._order.clear()


@dataclass(slots=True, frozen=True)
class DependencyDeclaration:
    """Record what should be invalidated when one dependency changes.

    Attributes:
        tags: Tag templates rendered against the parameters of the change.
        namespaces: Namespaces whose generation is advanced.
        regions: Regions cleared entirely.
    """

    tags: tuple[str, ...] = ()
    namespaces: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()


class DependencyRegistry:
    """Translate a changed thing into the invalidations it implies.

    Readers, or the code that wires them, declare a dependency once. A writer
    then calls `resolve("case", case_id=...)` and receives the requests to
    apply, without importing the readers, knowing their key formulas, or being
    updated when a new reader appears. This keeps the coupling that scattered
    explicit evictions would otherwise create in one place.
    """

    __slots__ = ("_lock", "_declarations")

    def __init__(self) -> None:
        """Initialize a DependencyRegistry instance."""
        self._lock = threading.Lock()
        self._declarations: dict[str, list[DependencyDeclaration]] = {}

    def declare(
        self,
        dependency: str,
        tags: Iterable[str] = (),
        namespaces: Iterable[str] = (),
        regions: Iterable[str] = (),
    ) -> None:
        """Register what a change to `dependency` invalidates.

        Declarations accumulate, so several readers may contribute to the same
        dependency independently.

        Args:
            dependency: Name of the thing that changes, such as a model name.
            tags: Tag templates over the parameters passed to `resolve`.
            namespaces: Namespaces whose generation must be advanced.
            regions: Regions that must be cleared entirely.
        """
        declaration = DependencyDeclaration(
            tags=tuple(tags), namespaces=tuple(namespaces), regions=tuple(regions)
        )
        with self._lock:
            self._declarations.setdefault(dependency, []).append(declaration)

    def resolve(
        self,
        dependency: str,
        parameters: Mapping[str, Any] | None = None,
        mode: InvalidationMode = InvalidationMode.HARD,
    ) -> list[Invalidation]:
        """Return the requests implied by a change to `dependency`.

        Args:
            dependency: Name of the thing that changed.
            parameters: Values substituted into tag templates, such as the
                identifier of the changed object.
            mode: Whether stale values may still be served while refreshing.

        Returns:
            The requests to apply, which is empty when nothing was declared.
        """
        with self._lock:
            declarations = list(self._declarations.get(dependency, ()))
        arguments = dict(parameters or {})
        invalidations: list[Invalidation] = []
        for declaration in declarations:
            if declaration.tags:
                invalidations.append(
                    Invalidation.for_tags(
                        render_tags(declaration.tags, arguments), mode=mode
                    )
                )
            for namespace in declaration.namespaces:
                invalidations.append(Invalidation.for_namespace(namespace))
            for region in declaration.regions:
                invalidations.append(Invalidation.for_region(region, mode=mode))
        return invalidations

    def dependencies(self) -> set[str]:
        """Return the dependency names that have at least one declaration."""
        with self._lock:
            return set(self._declarations)

    def clear(self) -> None:
        """Discard every declaration."""
        with self._lock:
            self._declarations.clear()

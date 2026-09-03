"""Cache instrumentation.

`CacheStatistics` holds the counters a region maintains, `StatsRecorder`
receives the individual events, and `CacheListener` exposes the same events to
metrics exporters, tracers and tests. `RecordingListener` captures events in
memory so that a test can assert that an invalidation actually happened rather
than inspecting private state.
"""

import threading
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, replace
from typing import Any

from gen_epix.fastapp.cache.enum import CacheOperation, RemovalCause


@dataclass(slots=True, frozen=True)
class CacheStatistics:
    """Encapsulates summarizing the observed behavior of one region.

    Attributes:
        hits: Reads served from the cache.
        misses: Reads that had to consult the loader.
        stale_hits: Reads served from a stale entry while a refresh was due.
        loads: Loader invocations that returned a value.
        load_failures: Loader invocations that raised.
        load_seconds: Total wall-clock time spent inside the loader.
        sets: Values written to the backend.
        deletes: Entries removed by an explicit delete.
        evictions: Entries removed because the backend was over budget.
        expirations: Entries removed because they passed their expiry.
        invalidations: Entries or groups removed by an invalidation request.
        errors: Backend failures observed, whether or not they were absorbed.
    """

    hits: int = 0
    misses: int = 0
    stale_hits: int = 0
    loads: int = 0
    load_failures: int = 0
    load_seconds: float = 0.0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    expirations: int = 0
    invalidations: int = 0
    errors: int = 0

    @property
    def requests(self) -> int:
        """Return the number of read attempts."""
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """Return the fraction of reads served from cache, or 0.0 when idle."""
        return self.hits / self.requests if self.requests else 0.0

    @property
    def average_load_seconds(self) -> float:
        """Return the mean loader duration, or 0.0 when nothing was loaded."""
        total = self.loads + self.load_failures
        return self.load_seconds / total if total else 0.0

    def __add__(self, other: "CacheStatistics") -> "CacheStatistics":
        """Return the element-wise sum of two snapshots.

        Args:
            other: The snapshot to add.

        Returns:
            A new snapshot holding the summed counters.

        Raises:
            TypeError: If `other` is not a `CacheStatistics`.
        """
        if not isinstance(other, CacheStatistics):
            raise TypeError("Can only add CacheStatistics to CacheStatistics")
        return CacheStatistics(
            hits=self.hits + other.hits,
            misses=self.misses + other.misses,
            stale_hits=self.stale_hits + other.stale_hits,
            loads=self.loads + other.loads,
            load_failures=self.load_failures + other.load_failures,
            load_seconds=self.load_seconds + other.load_seconds,
            sets=self.sets + other.sets,
            deletes=self.deletes + other.deletes,
            evictions=self.evictions + other.evictions,
            expirations=self.expirations + other.expirations,
            invalidations=self.invalidations + other.invalidations,
            errors=self.errors + other.errors,
        )


class StatsRecorder(ABC):
    """Encapsulates accumulating cache events into a statistics snapshot.

    Implementations must tolerate concurrent calls from request threads and
    from background refreshes.
    """

    @abstractmethod
    def record(self, field: str, amount: float = 1) -> None:
        """Add `amount` to one counter.

        Args:
            field: The name of a `CacheStatistics` field.
            amount: The increment, which may be fractional for durations.
        """

    @abstractmethod
    def snapshot(self) -> CacheStatistics:
        """Return the counters accumulated so far."""

    @abstractmethod
    def reset(self) -> None:
        """Set every counter back to zero."""


class NullStatsRecorder(StatsRecorder):
    """Encapsulates discarding every event.

    Statistics cost a lock on every operation, so a region that is not being
    observed uses this recorder.
    """

    __slots__ = ()

    def record(self, field: str, amount: float = 1) -> None:
        """See base method."""

    def snapshot(self) -> CacheStatistics:
        """See base method."""
        return CacheStatistics()

    def reset(self) -> None:
        """See base method."""


class InMemoryStatsRecorder(StatsRecorder):
    """Encapsulates accumulating counters in process memory under a lock."""

    __slots__ = ("_lock", "_statistics")

    def __init__(self) -> None:
        """Initialize an InMemoryStatsRecorder instance."""
        self._lock = threading.Lock()
        self._statistics = CacheStatistics()

    def record(self, field: str, amount: float = 1) -> None:
        """See base method.

        Raises:
            AttributeError: If `field` is not a `CacheStatistics` field.
        """
        with self._lock:
            current = getattr(self._statistics, field)
            self._statistics = replace(self._statistics, **{field: current + amount})

    def snapshot(self) -> CacheStatistics:
        """See base method."""
        with self._lock:
            return self._statistics

    def reset(self) -> None:
        """See base method."""
        with self._lock:
            self._statistics = CacheStatistics()


@dataclass(slots=True, frozen=True)
class CacheEvent:
    """Encapsulates describing one observable thing that happened in a region.

    Attributes:
        region: Name of the region that produced the event.
        operation: The kind of operation involved.
        key: The composed cache key, when the event concerns one entry.
        cause: Why an entry was removed, for removal events.
        detail: Free-form context such as a tag name or an exception.
    """

    region: str
    operation: CacheOperation
    key: str | None = None
    cause: RemovalCause | None = None
    detail: Any = None


class CacheListener(ABC):
    """Encapsulates observing cache events without influencing them.

    A listener must not raise; a region treats a failing listener as a defect
    in instrumentation and never lets it break a request.
    """

    @abstractmethod
    def on_event(self, event: CacheEvent) -> None:
        """Handle one cache event.

        Args:
            event: The event that just occurred.
        """


class CompositeListener(CacheListener):
    """Encapsulates fanning one event out to several listeners.

    A failing listener is skipped so that one broken exporter cannot suppress
    the others.

    Attributes:
        listeners: The listeners notified in order.
    """

    __slots__ = ("listeners",)

    def __init__(self, listeners: Iterable[CacheListener] = ()):
        """Initialize a CompositeListener instance."""
        self.listeners: list[CacheListener] = list(listeners)

    def add(self, listener: CacheListener) -> None:
        """Append a listener to the notification list."""
        self.listeners.append(listener)

    def on_event(self, event: CacheEvent) -> None:
        """See base method."""
        for listener in self.listeners:
            try:
                listener.on_event(event)
            except Exception:  # noqa: BLE001 - instrumentation must not break reads
                continue


class RecordingListener(CacheListener):
    """Encapsulates keeping every event in memory for later inspection.

    Attributes:
        events: The events observed so far, in order.
    """

    __slots__ = ("events", "_lock")

    def __init__(self) -> None:
        """Initialize a RecordingListener instance."""
        self.events: list[CacheEvent] = []
        self._lock = threading.Lock()

    def on_event(self, event: CacheEvent) -> None:
        """See base method."""
        with self._lock:
            self.events.append(event)

    def clear(self) -> None:
        """Discard the recorded events."""
        with self._lock:
            self.events.clear()

    def of(self, operation: CacheOperation) -> list[CacheEvent]:
        """Return the recorded events of one operation kind.

        Args:
            operation: The operation to filter on.
        """
        with self._lock:
            return [event for event in self.events if event.operation is operation]

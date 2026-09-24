"""Enumerations shared by the cache framework."""

from enum import Enum


class CacheOperation(Enum):
    """Encapsulates identifying the cache operation that produced an event or statistic."""

    GET = "GET"
    SET = "SET"
    DELETE = "DELETE"
    CLEAR = "CLEAR"
    LOAD = "LOAD"
    REFRESH = "REFRESH"
    INVALIDATE = "INVALIDATE"


class RemovalCause(Enum):
    """Encapsulates explaining why an entry left a cache.

    The values mirror the removal causes used by Caffeine so that eviction
    listeners can distinguish capacity pressure from deliberate removal.
    """

    EXPLICIT = "EXPLICIT"
    REPLACED = "REPLACED"
    EXPIRED = "EXPIRED"
    SIZE = "SIZE"
    INVALIDATED = "INVALIDATED"
    CLEARED = "CLEARED"

    @property
    def was_evicted(self) -> bool:
        """Return whether the removal was automatic rather than caller driven."""
        return self in (RemovalCause.EXPIRED, RemovalCause.SIZE)


class EvictionPolicyType(Enum):
    """Encapsulates naming the built-in eviction strategies selectable through configuration."""

    LRU = "LRU"
    LFU = "LFU"
    FIFO = "FIFO"
    RANDOM = "RANDOM"
    TINY_LFU = "TINY_LFU"


class ExpiryMode(Enum):
    """Encapsulates specifying whether an entry expires relative to its write or its last access."""

    AFTER_WRITE = "AFTER_WRITE"
    AFTER_ACCESS = "AFTER_ACCESS"


class InvalidationScope(Enum):
    """Encapsulates identifying the breadth of an invalidation request."""

    KEY = "KEY"
    TAG = "TAG"
    NAMESPACE = "NAMESPACE"
    REGION = "REGION"
    ALL = "ALL"


class InvalidationMode(Enum):
    """Encapsulates specifying whether invalidated values may still be served while refreshing.

    ``HARD`` forces every reader to wait for a regenerated value. ``SOFT`` lets
    readers keep the previous value until a refresh completes, which trades
    staleness for availability.
    """

    HARD = "HARD"
    SOFT = "SOFT"


class FailureMode(Enum):
    """Encapsulates specifying how a region reacts to a failing cache backend.

    ``FAIL_OPEN`` degrades to the origin loader and keeps the request working.
    ``FAIL_CLOSED`` propagates the backend error to the caller.
    """

    FAIL_OPEN = "FAIL_OPEN"
    FAIL_CLOSED = "FAIL_CLOSED"


class CircuitState(Enum):
    """Encapsulates identifying the state of a circuit breaker guarding a cache backend."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

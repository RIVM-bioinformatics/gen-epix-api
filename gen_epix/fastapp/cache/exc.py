"""Exceptions raised by the cache framework."""


class CacheError(Exception):
    """Base error for every failure originating in the cache framework."""


class CacheConfigurationError(CacheError):
    """Error for an invalid or contradictory cache configuration."""


class RegionAlreadyConfiguredError(CacheConfigurationError):
    """Error for configuring a region that already has a backend."""


class RegionNotConfiguredError(CacheConfigurationError):
    """Error for using a region before a backend was attached to it."""


class RegionNotFoundError(CacheConfigurationError):
    """Error for requesting a region name that the manager does not know."""


class CacheBackendError(CacheError):
    """Failure of the underlying cache store."""


class CacheTimeoutError(CacheBackendError):
    """Error for a cache operation that exceeded its configured time budget."""


class CircuitOpenError(CacheBackendError):
    """Error for a cache operation refused because its circuit breaker is open."""


class SerializationError(CacheError):
    """Error for a value that could not be converted to its stored form."""


class CantDeserializeError(SerializationError):
    """Error for a stored value that the current code can no longer read.

    A region treats this as a cache miss so that entries written by an earlier
    payload schema are transparently regenerated instead of failing a request.
    """


class KeyRejectedError(CacheError):
    """Error for a cache key refused by the configured admission policy."""

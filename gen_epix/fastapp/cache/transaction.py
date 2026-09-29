"""Deferral of invalidation until a unit of work commits.

Invalidating while a transaction is still open is a correctness bug in both
directions: a concurrent reader repopulates the cache from the pre-commit state,
and a rollback leaves the cache cleared for data that never changed. An
`InvalidationTransaction` buffers requests and releases them only on commit,
which is the behavior of Spring's transaction-aware cache manager and of an
`after_commit` hook in Rails.
"""

import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from gen_epix.fastapp.cache.invalidation import Invalidation

_CURRENT: ContextVar["InvalidationTransaction | None"] = ContextVar(
    "gen_epix_cache_invalidation_transaction", default=None
)


class InvalidationTransaction:
    """Encapsulates collecting invalidation requests and applying them on commit.

    Requests that are identical apart from their message identifier collapse
    into one, so a loop that touches many objects of the same kind does not
    replay the same broad invalidation repeatedly. Every other field, including
    the observed generation, is part of that identity: dropping a namespace
    bump because an older one is already buffered would make receivers adopt a
    generation that is behind the origin.

    Attributes:
        sink: Callable applied to each request at commit time.
    """

    __slots__ = ("sink", "_lock", "_pending", "_closed")

    def __init__(self, sink: Callable[[Invalidation], None]):
        """Initialize an InvalidationTransaction instance."""
        self.sink = sink
        self._lock = threading.Lock()
        self._pending: dict[tuple, Invalidation] = {}
        self._closed = False

    @property
    def pending(self) -> list[Invalidation]:
        """Return the buffered requests in insertion order."""
        with self._lock:
            return list(self._pending.values())

    @property
    def is_closed(self) -> bool:
        """Return whether the transaction was already committed or rolled back."""
        with self._lock:
            return self._closed

    def add(self, invalidation: Invalidation) -> None:
        """Buffer a request until commit.

        Args:
            invalidation: The request to defer.

        Raises:
            RuntimeError: If the transaction was already closed, which would
                silently drop the request.
        """
        signature = (
            invalidation.scope,
            invalidation.mode,
            invalidation.region,
            invalidation.keys,
            invalidation.tags,
            invalidation.namespace,
            invalidation.generation,
            invalidation.origin,
        )
        with self._lock:
            if self._closed:
                raise RuntimeError("Cannot add to a closed invalidation transaction")
            self._pending.setdefault(signature, invalidation)

    def commit(self) -> list[Invalidation]:
        """Apply every buffered request and close the transaction.

        Requests are applied in insertion order. The transaction is closed even
        when the sink raises, so a failing invalidation cannot be replayed by a
        later commit of the same transaction.

        Returns:
            The requests that were applied.

        Raises:
            Exception: The first error raised by the sink, after every request
                has been attempted.
        """
        with self._lock:
            if self._closed:
                return []
            pending = list(self._pending.values())
            self._pending.clear()
            self._closed = True
        first_error: BaseException | None = None
        for invalidation in pending:
            try:
                self.sink(invalidation)
            except Exception as exception:  # noqa: BLE001 - reported after the loop
                first_error = first_error or exception
        if first_error is not None:
            raise first_error
        return pending

    def rollback(self) -> None:
        """Discard every buffered request and close the transaction."""
        with self._lock:
            self._pending.clear()
            self._closed = True


def current_transaction() -> InvalidationTransaction | None:
    """Return the transaction bound to the calling context, if any."""
    return _CURRENT.get()


def enlist(invalidation: Invalidation) -> bool:
    """Buffer a request in the ambient transaction when one is open.

    Args:
        invalidation: The request to defer.

    Returns:
        Whether a transaction accepted the request. A caller that receives
        False must apply the request immediately.
    """
    transaction = _CURRENT.get()
    if transaction is None or transaction.is_closed:
        return False
    transaction.add(invalidation)
    return True


@contextmanager
def invalidation_transaction(
    sink: Callable[[Invalidation], None],
) -> Iterator[InvalidationTransaction]:
    """Open a transaction for the duration of the block.

    Leaving the block normally commits the buffered requests; leaving it with
    an exception rolls them back, so a failed unit of work leaves the cache
    untouched.

    Args:
        sink: Callable applied to each request at commit time.

    Returns:
        A context manager that owns the transaction.

    Yields:
        The transaction, mainly so that a caller can inspect `pending`.

    Raises:
        BaseException: Whatever the block raised, after the buffered requests
            have been discarded.
    """
    transaction = InvalidationTransaction(sink)
    token = _CURRENT.set(transaction)
    try:
        yield transaction
    except BaseException:
        transaction.rollback()
        raise
    else:
        transaction.commit()
    finally:
        _CURRENT.reset(token)

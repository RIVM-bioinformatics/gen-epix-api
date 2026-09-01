"""Concurrency primitives that keep one loader per key.

Without coordination, the expiry of a popular entry lets every concurrent
caller run the loader at once and stampede the origin. `SingleFlight` and
`AsyncSingleFlight` elect one caller to load while the others wait for its
result. `RefreshRunner` decides where a background refresh of a stale entry
executes.
"""

import asyncio
import threading
from collections.abc import Callable
from concurrent.futures import Executor
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Mutex(Protocol):
    """Describe a lock with explicit acquire and release semantics."""

    def acquire(self, wait: bool = True) -> bool:
        """Acquire the lock.

        Args:
            wait: Whether to block until the lock is available.

        Returns:
            Whether the lock was acquired.
        """
        ...

    def release(self) -> None:
        """Release the lock."""
        ...

    def locked(self) -> bool:
        """Return whether the lock is currently held."""
        ...


class ThreadMutex:
    """Adapt `threading.Lock` to the `Mutex` protocol."""

    __slots__ = ("_lock",)

    def __init__(self) -> None:
        """Initialize a ThreadMutex instance."""
        self._lock = threading.Lock()

    def acquire(self, wait: bool = True) -> bool:
        """See base method."""
        return self._lock.acquire(wait)

    def release(self) -> None:
        """See base method."""
        self._lock.release()

    def locked(self) -> bool:
        """See base method."""
        return self._lock.locked()


class NullMutex:
    """Grant every acquisition immediately.

    Use this to disable coordination in a region that is provably accessed by a
    single thread, or to measure the cost of locking.
    """

    __slots__ = ()

    def acquire(self, wait: bool = True) -> bool:
        """See base method."""
        return True

    def release(self) -> None:
        """See base method."""

    def locked(self) -> bool:
        """See base method."""
        return False


class KeyedMutex:
    """Hand out one mutex per key and discard it when nobody holds it.

    Locking per key lets regeneration of different keys proceed in parallel,
    unlike a single region-wide mutex. Entries are reference counted so that the
    registry does not grow with the key space.
    """

    __slots__ = ("_guard", "_mutexes", "_users")

    def __init__(self) -> None:
        """Initialize a KeyedMutex instance."""
        self._guard = threading.Lock()
        self._mutexes: dict[str, threading.Lock] = {}
        self._users: dict[str, int] = {}

    def acquire(self, key: str, wait: bool = True) -> bool:
        """Acquire the mutex belonging to `key`.

        Args:
            key: The cache key being regenerated.
            wait: Whether to block until the mutex is available.

        Returns:
            Whether the mutex was acquired.
        """
        with self._guard:
            mutex = self._mutexes.get(key)
            if mutex is None:
                mutex = threading.Lock()
                self._mutexes[key] = mutex
            self._users[key] = self._users.get(key, 0) + 1
        acquired = mutex.acquire(wait)
        if not acquired:
            self._drop(key)
        return acquired

    def release(self, key: str) -> None:
        """Release the mutex belonging to `key`.

        Args:
            key: The key whose mutex is held.

        Raises:
            KeyError: If no mutex is registered for `key`.
        """
        with self._guard:
            mutex = self._mutexes[key]
        mutex.release()
        self._drop(key)

    def is_locked(self, key: str) -> bool:
        """Return whether a regeneration is in progress for `key`."""
        with self._guard:
            mutex = self._mutexes.get(key)
        return mutex is not None and mutex.locked()

    def _drop(self, key: str) -> None:
        """Decrement the user count of `key` and forget an unused mutex."""
        with self._guard:
            remaining = self._users.get(key, 0) - 1
            if remaining <= 0:
                self._users.pop(key, None)
                self._mutexes.pop(key, None)
            else:
                self._users[key] = remaining


class _Call:
    """Hold the shared outcome of one in-flight load.

    Attributes:
        event: Signalled by the leader once the outcome is known.
        value: The loaded value when the load succeeded.
        error: The exception raised by the loader, if any.
    """

    __slots__ = ("event", "value", "error")

    def __init__(self) -> None:
        """Initialize a _Call instance."""
        self.event = threading.Event()
        self.value: Any = None
        self.error: BaseException | None = None


class SingleFlight:
    """Collapse concurrent loads of the same key into one execution.

    The first caller for a key runs the loader; later callers block until it
    finishes and then receive the same value or the same exception. Different
    keys never block each other.
    """

    __slots__ = ("_guard", "_calls")

    def __init__(self) -> None:
        """Initialize a SingleFlight instance."""
        self._guard = threading.Lock()
        self._calls: dict[str, _Call] = {}

    def run(self, key: str, loader: Callable[[], Any]) -> Any:
        """Return the result of `loader`, executing it at most once per key.

        Args:
            key: The cache key being loaded.
            loader: Callable producing the value.

        Returns:
            The value produced by the leading call.

        Raises:
            BaseException: Whatever `loader` raised. Followers receive the same
                exception instance as the leader, so a failed load is not
                retried by every waiter.
        """
        with self._guard:
            call = self._calls.get(key)
            is_leader = call is None
            if call is None:
                call = _Call()
                self._calls[key] = call
        if is_leader:
            try:
                call.value = loader()
            except BaseException as exception:
                call.error = exception
            finally:
                with self._guard:
                    self._calls.pop(key, None)
                call.event.set()
        else:
            call.event.wait()
        if call.error is not None:
            raise call.error
        return call.value

    def is_in_flight(self, key: str) -> bool:
        """Return whether a load for `key` is currently running."""
        with self._guard:
            return key in self._calls

    def try_start(self, key: str) -> bool:
        """Claim leadership for `key` without blocking.

        A stale-while-revalidate read uses this to decide whether it should
        launch the background refresh or leave it to the caller that already
        started one.

        Args:
            key: The cache key to refresh.

        Returns:
            Whether the caller became the leader and must call `finish`.
        """
        with self._guard:
            if key in self._calls:
                return False
            self._calls[key] = _Call()
            return True

    def finish(self, key: str) -> None:
        """Release leadership claimed through `try_start`.

        Args:
            key: The cache key whose refresh completed.
        """
        with self._guard:
            call = self._calls.pop(key, None)
        if call is not None:
            call.event.set()


class AsyncSingleFlight:
    """Collapse concurrent awaited loads of the same key into one execution.

    The instance is bound to the running event loop of its callers and is not
    safe to share across loops.
    """

    __slots__ = ("_futures",)

    def __init__(self) -> None:
        """Initialize an AsyncSingleFlight instance."""
        self._futures: dict[str, asyncio.Future[Any]] = {}

    async def run(self, key: str, loader: Callable[[], Any]) -> Any:
        """Return the result of awaiting `loader`, running it once per key.

        Args:
            key: The cache key being loaded.
            loader: Callable returning an awaitable that produces the value.

        Returns:
            The value produced by the leading call.

        Raises:
            BaseException: Whatever the awaited loader raised.
        """
        pending = self._futures.get(key)
        if pending is not None:
            return await asyncio.shield(pending)
        future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        self._futures[key] = future
        try:
            result = await loader()
        except BaseException as exception:
            future.set_exception(exception)
            raise
        else:
            future.set_result(result)
            return result
        finally:
            self._futures.pop(key, None)
            if future.done() and not future.cancelled():
                # Mark a stored exception as retrieved even when nobody waited.
                future.exception()

    def is_in_flight(self, key: str) -> bool:
        """Return whether a load for `key` is currently running."""
        return key in self._futures


@runtime_checkable
class RefreshRunner(Protocol):
    """Decide where the refresh of a stale entry executes."""

    def submit(self, work: Callable[[], None]) -> None:
        """Schedule `work` for execution.

        Args:
            work: A callable that refreshes one cache entry and must not raise.
        """
        ...


class InlineRefreshRunner:
    """Refresh stale entries on the calling thread.

    This makes a stale read as slow as a miss but adds no threads, which suits
    tests and single-threaded deployments.
    """

    __slots__ = ()

    def submit(self, work: Callable[[], None]) -> None:
        """See base method."""
        work()


class ThreadRefreshRunner:
    """Refresh stale entries on a daemon thread or a supplied executor.

    Attributes:
        executor: The executor used when one was supplied, otherwise None and
            each refresh runs on its own short-lived daemon thread.
    """

    __slots__ = ("executor",)

    def __init__(self, executor: Executor | None = None):
        """Initialize a ThreadRefreshRunner instance."""
        self.executor = executor

    def submit(self, work: Callable[[], None]) -> None:
        """See base method."""
        if self.executor is not None:
            self.executor.submit(work)
            return
        threading.Thread(target=work, daemon=True).start()

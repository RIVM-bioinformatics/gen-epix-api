"""Protection against a slow or failing cache backend.

A cache must never be the reason a request fails or becomes slower than the
origin it fronts. `TimeoutGuard` bounds the duration of a backend call,
`CircuitBreaker` stops calling a store that keeps failing, and `FailurePolicy`
combines both with a fail-open or fail-closed decision.
"""

import threading
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import TypeVar

from gen_epix.fastapp.cache.clock import Clock, SystemClock
from gen_epix.fastapp.cache.enum import CircuitState, FailureMode
from gen_epix.fastapp.cache.exc import (
    CacheBackendError,
    CacheTimeoutError,
    CircuitOpenError,
)

_T = TypeVar("_T")


class CircuitBreaker:
    """Encapsulates stopping calling a backend that fails repeatedly.

    After `failure_threshold` consecutive failures the breaker opens and every
    call is refused without touching the backend. Once `reset_timeout` has
    elapsed a single probe is admitted; its outcome closes the breaker or opens
    it again. This bounds the cost of an unreachable store to one probe per
    timeout instead of one timeout per request.

    Attributes:
        failure_threshold: Consecutive failures that open the breaker.
        reset_timeout: Seconds before a probe is admitted.
        clock: Time source, injectable for deterministic tests.
    """

    __slots__ = (
        "failure_threshold",
        "reset_timeout",
        "clock",
        "_lock",
        "_failures",
        "_opened_at",
        "_state",
    )

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 30.0,
        clock: Clock | None = None,
    ):
        """Initialize a CircuitBreaker instance.

        Args:
            failure_threshold: Consecutive failures that open the breaker.
            reset_timeout: Seconds before a probe is admitted.
            clock: Time source, injectable for deterministic tests.

        Raises:
            ValueError: If the threshold or the timeout is not positive.
        """
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if reset_timeout <= 0:
            raise ValueError("reset_timeout must be positive")
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.clock = clock if clock is not None else SystemClock()
        self._lock = threading.Lock()
        self._failures = 0
        self._opened_at = 0.0
        self._state = CircuitState.CLOSED

    @property
    def state(self) -> CircuitState:
        """Return the current breaker state, admitting a probe when due."""
        with self._lock:
            return self._current_state()

    def allow(self) -> bool:
        """Return whether a call may proceed, admitting at most one probe."""
        with self._lock:
            return self._current_state() is not CircuitState.OPEN

    def record_success(self) -> None:
        """Close the breaker and forget accumulated failures."""
        with self._lock:
            self._failures = 0
            self._state = CircuitState.CLOSED

    def record_failure(self) -> None:
        """Count a failure and open the breaker once the threshold is met."""
        with self._lock:
            if self._state is CircuitState.HALF_OPEN:
                self._open()
                return
            self._failures += 1
            if self._failures >= self.failure_threshold:
                self._open()

    def _current_state(self) -> CircuitState:
        """Return the state, moving an expired open breaker to half open."""
        if self._state is CircuitState.OPEN:
            if self.clock.monotonic() - self._opened_at >= self.reset_timeout:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def _open(self) -> None:
        """Open the breaker and start its reset timer."""
        self._state = CircuitState.OPEN
        self._opened_at = self.clock.monotonic()


class TimeoutGuard:
    """Encapsulates bounding the wall-clock duration of a backend call.

    The call runs on a worker thread so that a store that never answers cannot
    block a request thread. A timed-out call is abandoned rather than
    cancelled, because a blocking client library cannot be interrupted; the
    guard only stops the caller from waiting for it.

    Attributes:
        timeout: Seconds allowed for one call, or None to wait indefinitely.
    """

    __slots__ = ("timeout", "_executor", "_lock", "_max_workers")

    def __init__(self, timeout: float | None = None, max_workers: int = 4):
        """Initialize a TimeoutGuard instance.

        Args:
            timeout: Seconds allowed for one call, or None to disable bounding.
            max_workers: Size of the worker pool created on first use.

        Raises:
            ValueError: If `timeout` is not positive.
        """
        if timeout is not None and timeout <= 0:
            raise ValueError("timeout must be positive")
        self.timeout = timeout
        self._executor: ThreadPoolExecutor | None = None
        self._lock = threading.Lock()
        self._max_workers = max_workers

    def call(self, operation: Callable[[], _T]) -> _T:
        """Run `operation`, giving up after the configured timeout.

        Args:
            operation: The backend call to run.

        Returns:
            Whatever `operation` returned.

        Raises:
            CacheTimeoutError: If the call did not finish in time.
            Exception: Whatever `operation` raised.
        """
        if self.timeout is None:
            return operation()
        future: Future[_T] = self._get_executor().submit(operation)
        try:
            return future.result(timeout=self.timeout)
        except FutureTimeoutError as exception:
            raise CacheTimeoutError(
                f"Cache operation exceeded {self.timeout} seconds"
            ) from exception

    def close(self) -> None:
        """Shut down the worker pool if one was created."""
        with self._lock:
            executor, self._executor = self._executor, None
        if executor is not None:
            executor.shutdown(wait=False)

    def _get_executor(self) -> ThreadPoolExecutor:
        """Return the worker pool, creating it on first use."""
        with self._lock:
            if self._executor is None:
                self._executor = ThreadPoolExecutor(
                    max_workers=self._max_workers,
                    thread_name_prefix="cache-timeout",
                )
            return self._executor


class FailurePolicy:
    """Encapsulates deciding what happens when a cache backend call fails.

    The policy wraps every backend interaction of a region. In `FAIL_OPEN` mode
    a failure is absorbed and the region behaves as if the entry were absent,
    so a broken cache degrades throughput instead of availability. In
    `FAIL_CLOSED` mode the error reaches the caller, which suits regions where a
    silent bypass would overload the origin.

    Attributes:
        mode: Whether failures are absorbed or propagated.
        breaker: Optional breaker that short-circuits a failing backend.
        guard: Optional guard bounding the duration of each call.
        on_error: Optional callback invoked with every absorbed exception.
    """

    __slots__ = ("mode", "breaker", "guard", "on_error")

    def __init__(
        self,
        mode: FailureMode = FailureMode.FAIL_OPEN,
        breaker: CircuitBreaker | None = None,
        guard: TimeoutGuard | None = None,
        on_error: Callable[[BaseException], None] | None = None,
    ):
        """Initialize a FailurePolicy instance."""
        self.mode = mode
        self.breaker = breaker
        self.guard = guard
        self.on_error = on_error

    def run(self, operation: Callable[[], _T], fallback: _T) -> _T:
        """Run a backend operation under the configured protections.

        The breaker is consulted first, then the timeout guard, and the outcome
        updates the breaker. A refused or failed call returns `fallback` in
        fail-open mode.

        Args:
            operation: The backend call to run.
            fallback: Value returned when the call is refused or absorbed.

        Returns:
            The result of `operation`, or `fallback`.

        Raises:
            CircuitOpenError: In fail-closed mode when the breaker is open.
            CacheBackendError: In fail-closed mode when the call failed.
        """
        if self.breaker is not None and not self.breaker.allow():
            error = CircuitOpenError("Cache backend circuit is open")
            return self._handle(error, fallback)
        try:
            result = self.guard.call(operation) if self.guard else operation()
        except Exception as exception:  # noqa: BLE001 - classified below
            if self.breaker is not None:
                self.breaker.record_failure()
            return self._handle(exception, fallback)
        if self.breaker is not None:
            self.breaker.record_success()
        return result

    def _handle(self, exception: BaseException, fallback: _T) -> _T:
        """Absorb or re-raise a failure according to the configured mode.

        Args:
            exception: The failure observed.
            fallback: Value returned when the failure is absorbed.

        Returns:
            `fallback`, in fail-open mode.

        Raises:
            CacheBackendError: In fail-closed mode, wrapping unexpected errors
                so that callers see one error type from the cache layer.
        """
        if self.on_error is not None:
            self.on_error(exception)
        if self.mode is FailureMode.FAIL_OPEN:
            return fallback
        if isinstance(exception, CacheBackendError):
            raise exception
        raise CacheBackendError(str(exception)) from exception

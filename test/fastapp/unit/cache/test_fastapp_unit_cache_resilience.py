"""Tests for cache failure handling and timeouts."""

import time

import pytest

from gen_epix.fastapp.cache.clock import ManualClock
from gen_epix.fastapp.cache.enum import CircuitState, FailureMode
from gen_epix.fastapp.cache.exc import CacheBackendError, CacheTimeoutError
from gen_epix.fastapp.cache.resilience import (
    CircuitBreaker,
    FailurePolicy,
    TimeoutGuard,
)


def test_a_breaker_opens_after_repeated_failures() -> None:
    """Repeated backend failures open the circuit."""
    clock = ManualClock()
    breaker = CircuitBreaker(failure_threshold=2, reset_timeout=30.0, clock=clock)

    breaker.record_failure()
    assert breaker.allow() is True
    breaker.record_failure()

    assert breaker.state is CircuitState.OPEN
    assert breaker.allow() is False


def test_an_open_breaker_admits_a_probe_after_its_timeout() -> None:
    """One probe is admitted after the open interval."""
    clock = ManualClock()
    breaker = CircuitBreaker(failure_threshold=1, reset_timeout=30.0, clock=clock)
    breaker.record_failure()

    clock.advance(30)

    assert breaker.allow() is True
    assert breaker.state is CircuitState.HALF_OPEN
    breaker.record_success()
    assert breaker.state is CircuitState.CLOSED


def test_a_failing_probe_reopens_the_breaker() -> None:
    """A failed half-open probe returns the breaker to open."""
    clock = ManualClock()
    breaker = CircuitBreaker(failure_threshold=1, reset_timeout=10.0, clock=clock)
    breaker.record_failure()
    clock.advance(10)
    breaker.allow()

    breaker.record_failure()

    assert breaker.state is CircuitState.OPEN


def test_an_invalid_breaker_configuration_is_rejected() -> None:
    """Failure threshold and reset timeout must be positive."""
    with pytest.raises(ValueError):
        CircuitBreaker(failure_threshold=0)
    with pytest.raises(ValueError):
        CircuitBreaker(reset_timeout=0)


def test_a_slow_backend_call_is_abandoned() -> None:
    """The caller stops waiting when a backend call exceeds its timeout."""
    guard = TimeoutGuard(timeout=0.05)

    with pytest.raises(CacheTimeoutError):
        guard.call(lambda: time.sleep(1))
    guard.close()


def test_a_guard_without_a_timeout_runs_inline() -> None:
    """An unbounded guard adds no worker pool to the call."""
    guard = TimeoutGuard()

    assert guard.call(lambda: "value") == "value"


def test_non_positive_timeout_and_worker_limits_are_rejected() -> None:
    """Timeout and worker limits must both be positive when supplied."""
    with pytest.raises(ValueError):
        TimeoutGuard(timeout=0)
    with pytest.raises(ValueError):
        TimeoutGuard(max_workers=0)
    with pytest.raises(ValueError):
        TimeoutGuard(max_workers=-1)


def test_fail_open_substitutes_the_fallback() -> None:
    """Fail-open mode absorbs backend failures and reports them."""
    observed: list[BaseException] = []
    policy = FailurePolicy(mode=FailureMode.FAIL_OPEN, on_error=observed.append)

    def explode() -> str:
        """Raise the simulated backend failure."""
        raise CacheBackendError("store unavailable")

    assert policy.run(explode, "fallback") == "fallback"
    assert len(observed) == 1


def test_fail_closed_propagates_the_failure() -> None:
    """Fail-closed mode normalizes unexpected errors to CacheBackendError."""
    policy = FailurePolicy(mode=FailureMode.FAIL_CLOSED)

    def explode() -> str:
        """Raise an unexpected backend error."""
        raise RuntimeError("store unavailable")

    with pytest.raises(CacheBackendError):
        policy.run(explode, "fallback")


def test_an_open_breaker_short_circuits_the_backend() -> None:
    """An open circuit prevents another call to a failing backend."""
    clock = ManualClock()
    breaker = CircuitBreaker(failure_threshold=1, reset_timeout=30.0, clock=clock)
    policy = FailurePolicy(mode=FailureMode.FAIL_OPEN, breaker=breaker)
    calls: list[int] = []

    def explode() -> str:
        """Count the attempt and raise a backend error."""
        calls.append(1)
        raise CacheBackendError("store unavailable")

    policy.run(explode, "fallback")
    policy.run(explode, "fallback")

    assert len(calls) == 1

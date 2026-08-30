"""Tests for serialization, concurrency helpers, resilience and HTTP caching."""

import threading
import time

import pytest

from gen_epix.fastapp.cache.clock import ManualClock, SystemClock
from gen_epix.fastapp.cache.enum import CircuitState, FailureMode
from gen_epix.fastapp.cache.exc import (
    CacheBackendError,
    CacheTimeoutError,
    CantDeserializeError,
    SerializationError,
)
from gen_epix.fastapp.cache.http import (
    SURROGATE_KEY_HEADER,
    HttpCachePolicy,
    compute_etag,
    matches_etag,
)
from gen_epix.fastapp.cache.lock import KeyedMutex, SingleFlight
from gen_epix.fastapp.cache.resilience import (
    CircuitBreaker,
    FailurePolicy,
    TimeoutGuard,
)
from gen_epix.fastapp.cache.serializer import (
    CompressingSerializer,
    DeepCopySerializer,
    IdentitySerializer,
    JsonSerializer,
    PickleSerializer,
    SigningSerializer,
)


def test_a_manual_clock_only_moves_forward() -> None:
    """Time going backwards would resurrect expired entries."""
    clock = ManualClock()
    clock.advance(5)

    assert clock.monotonic() == 5
    with pytest.raises(ValueError):
        clock.advance(-1)
    with pytest.raises(ValueError):
        clock.set(1)


def test_the_system_clock_reports_both_readings() -> None:
    """Expiry uses the monotonic reading, timestamps use wall-clock time."""
    clock = SystemClock()

    assert clock.monotonic() > 0
    assert clock.time() > 0


def test_the_identity_serializer_shares_references() -> None:
    """The fastest option deliberately hands out the cached object itself."""
    serializer = IdentitySerializer()
    value = {"items": [1]}

    assert serializer.loads(serializer.dumps(value)) is value


def test_the_copying_serializer_isolates_both_directions() -> None:
    """Neither the writer nor the reader may hold the stored object."""
    serializer = DeepCopySerializer()
    value = {"items": [1]}

    stored = serializer.dumps(value)
    value["items"].append(2)

    assert serializer.loads(stored) == {"items": [1]}


def test_json_and_pickle_round_trip_their_payloads() -> None:
    """A byte-oriented serializer must read back exactly what it wrote."""
    for serializer, value in (
        (JsonSerializer(), {"a": [1, 2]}),
        (PickleSerializer(), {"a": (1, 2)}),
    ):
        assert serializer.loads(serializer.dumps(value)) == value


def test_a_payload_that_cannot_be_encoded_is_reported() -> None:
    """An unencodable payload is a caller error, not a cache miss."""
    with pytest.raises(SerializationError):
        JsonSerializer().dumps(object())


def test_corrupt_bytes_are_reported_as_unreadable() -> None:
    """An unreadable entry must be regenerable rather than fatal."""
    with pytest.raises(CantDeserializeError):
        JsonSerializer().loads(b"not json")


def test_compression_is_applied_only_above_the_threshold() -> None:
    """Small values must not pay for compression."""
    serializer = CompressingSerializer(JsonSerializer(), threshold=32)

    small = serializer.dumps("x")
    large = serializer.dumps("y" * 500)

    assert small[:1] == b"\x00"
    assert large[:1] == b"\x01"
    assert serializer.loads(large) == "y" * 500


def test_a_tampered_entry_is_rejected() -> None:
    """A signed payload is the minimum safeguard for a shared store."""
    serializer = SigningSerializer(JsonSerializer(), secret=b"secret")
    stored = bytearray(serializer.dumps({"role": "user"}))
    stored[-2] ^= 0xFF

    with pytest.raises(CantDeserializeError):
        serializer.loads(bytes(stored))


def test_an_entry_signed_with_another_secret_is_rejected() -> None:
    """A rotated secret must invalidate rather than be trusted."""
    stored = SigningSerializer(JsonSerializer(), secret=b"old").dumps("value")

    with pytest.raises(CantDeserializeError):
        SigningSerializer(JsonSerializer(), secret=b"new").loads(stored)


def test_an_empty_signing_secret_is_refused() -> None:
    """An empty secret would provide no integrity at all."""
    with pytest.raises(SerializationError):
        SigningSerializer(JsonSerializer(), secret=b"")


def test_a_byte_wrapper_refuses_a_non_byte_inner_serializer() -> None:
    """Stacking a wrapper on a live-object serializer cannot work."""
    with pytest.raises(SerializationError):
        CompressingSerializer(IdentitySerializer()).dumps("value")


def test_single_flight_runs_one_loader_per_key() -> None:
    """Different keys must not block each other while one key loads."""
    flight = SingleFlight()
    calls: list[str] = []
    lock = threading.Lock()

    def loader(key: str) -> str:
        """Record one slow invocation."""
        with lock:
            calls.append(key)
        time.sleep(0.05)
        return key

    results: list[str] = []
    threads = [
        threading.Thread(
            target=lambda key=key: results.append(flight.run(key, lambda: loader(key)))
        )
        for key in ["a", "a", "a", "b"]
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert sorted(calls) == ["a", "b"]
    assert sorted(results) == ["a", "a", "a", "b"]


def test_every_waiter_receives_the_failure_of_the_leader() -> None:
    """A failed load must not be retried once per waiting caller."""
    flight = SingleFlight()
    calls: list[int] = []

    def loader() -> str:
        """Count invocations and always fail.

        Returns:
            Never returns.

        Raises:
            RuntimeError: Always.
        """
        calls.append(1)
        raise RuntimeError("origin refused")

    for _ in range(2):
        with pytest.raises(RuntimeError):
            flight.run("k", loader)

    assert len(calls) == 2


def test_a_refresh_leader_is_elected_only_once() -> None:
    """A second stale reader must not start a competing refresh."""
    flight = SingleFlight()

    assert flight.try_start("k") is True
    assert flight.try_start("k") is False
    flight.finish("k")
    assert flight.try_start("k") is True


def test_a_keyed_mutex_is_discarded_when_nobody_holds_it() -> None:
    """A per-key lock registry must not grow with the key space."""
    mutex = KeyedMutex()

    assert mutex.acquire("k") is True
    assert mutex.is_locked("k") is True
    mutex.release("k")

    assert mutex.is_locked("k") is False


def test_a_breaker_opens_after_repeated_failures() -> None:
    """An unreachable store must cost one probe per timeout, not one per call."""
    clock = ManualClock()
    breaker = CircuitBreaker(failure_threshold=2, reset_timeout=30.0, clock=clock)

    breaker.record_failure()
    assert breaker.allow() is True
    breaker.record_failure()

    assert breaker.state is CircuitState.OPEN
    assert breaker.allow() is False


def test_an_open_breaker_admits_a_probe_after_its_timeout() -> None:
    """Recovery must not require a restart."""
    clock = ManualClock()
    breaker = CircuitBreaker(failure_threshold=1, reset_timeout=30.0, clock=clock)
    breaker.record_failure()

    clock.advance(30)

    assert breaker.allow() is True
    assert breaker.state is CircuitState.HALF_OPEN
    breaker.record_success()
    assert breaker.state is CircuitState.CLOSED


def test_a_failing_probe_reopens_the_breaker() -> None:
    """A store that is still broken must not receive full traffic again."""
    clock = ManualClock()
    breaker = CircuitBreaker(failure_threshold=1, reset_timeout=10.0, clock=clock)
    breaker.record_failure()
    clock.advance(10)
    breaker.allow()

    breaker.record_failure()

    assert breaker.state is CircuitState.OPEN


def test_an_invalid_breaker_configuration_is_rejected() -> None:
    """A breaker that opens on zero failures would never allow anything."""
    with pytest.raises(ValueError):
        CircuitBreaker(failure_threshold=0)
    with pytest.raises(ValueError):
        CircuitBreaker(reset_timeout=0)


def test_a_slow_backend_call_is_abandoned() -> None:
    """A cache must never be slower than the origin it fronts."""
    guard = TimeoutGuard(timeout=0.05)

    with pytest.raises(CacheTimeoutError):
        guard.call(lambda: time.sleep(1))
    guard.close()


def test_a_guard_without_a_timeout_runs_inline() -> None:
    """Bounding is optional and must add no threads when disabled."""
    guard = TimeoutGuard()

    assert guard.call(lambda: "value") == "value"


def test_a_non_positive_timeout_is_rejected() -> None:
    """A zero timeout would fail every call."""
    with pytest.raises(ValueError):
        TimeoutGuard(timeout=0)


def test_fail_open_substitutes_the_fallback() -> None:
    """A broken cache degrades throughput, not availability."""
    observed: list[BaseException] = []
    policy = FailurePolicy(mode=FailureMode.FAIL_OPEN, on_error=observed.append)

    def explode() -> str:
        """Backend call that always fails.

        Returns:
            Never returns.

        Raises:
            CacheBackendError: Always.
        """
        raise CacheBackendError("store unavailable")

    assert policy.run(explode, "fallback") == "fallback"
    assert len(observed) == 1


def test_fail_closed_propagates_the_failure() -> None:
    """Some regions must not silently bypass the cache."""
    policy = FailurePolicy(mode=FailureMode.FAIL_CLOSED)

    def explode() -> str:
        """Backend call that always fails.

        Returns:
            Never returns.

        Raises:
            RuntimeError: Always.
        """
        raise RuntimeError("store unavailable")

    with pytest.raises(CacheBackendError):
        policy.run(explode, "fallback")


def test_an_open_breaker_short_circuits_the_backend() -> None:
    """The point of a breaker is to stop calling a failing store."""
    clock = ManualClock()
    breaker = CircuitBreaker(failure_threshold=1, reset_timeout=30.0, clock=clock)
    policy = FailurePolicy(mode=FailureMode.FAIL_OPEN, breaker=breaker)
    calls: list[int] = []

    def explode() -> str:
        """Count invocations and always fail.

        Returns:
            Never returns.

        Raises:
            CacheBackendError: Always.
        """
        calls.append(1)
        raise CacheBackendError("store unavailable")

    policy.run(explode, "fallback")
    policy.run(explode, "fallback")

    assert len(calls) == 1


def test_an_entity_tag_changes_with_the_body() -> None:
    """A validator must distinguish representations."""
    assert compute_etag(b"a") != compute_etag(b"b")
    assert compute_etag(b"a", weak=True).startswith('W/"')


def test_a_weak_validator_matches_its_strong_counterpart() -> None:
    """Revalidation must succeed regardless of validator strength."""
    etag = compute_etag(b"body")

    assert matches_etag(etag, etag)
    assert matches_etag(f"W/{etag}", etag)
    assert matches_etag("*", etag)
    assert not matches_etag(None, etag)
    assert not matches_etag('"other"', etag)


def test_cache_control_reflects_the_policy() -> None:
    """The directive list is what an intermediary actually obeys."""
    policy = HttpCachePolicy(
        max_age=60,
        shared_max_age=300,
        stale_while_revalidate=30,
        stale_if_error=600,
        vary=("Accept", "Authorization"),
    )

    headers = policy.response_headers(etag='"abc"', surrogate_keys=["case:1"])

    assert "max-age=60" in headers["Cache-Control"]
    assert "s-maxage=300" in headers["Cache-Control"]
    assert "stale-while-revalidate=30" in headers["Cache-Control"]
    assert "stale-if-error=600" in headers["Cache-Control"]
    assert headers["Vary"] == "Accept, Authorization"
    assert headers[SURROGATE_KEY_HEADER] == "case:1"


def test_a_private_response_is_never_shared() -> None:
    """Marking a per-principal response public leaks it to other callers."""
    policy = HttpCachePolicy(max_age=60, shared_max_age=300, private=True)

    directives = policy.cache_control()

    assert "private" in directives
    assert "s-maxage" not in directives


def test_no_store_suppresses_every_other_directive() -> None:
    """A response that must not be stored has nothing else to say."""
    policy = HttpCachePolicy(max_age=60, no_store=True)

    assert policy.cache_control() == "no-store"
    assert policy.is_not_modified({"If-None-Match": '"abc"'}, '"abc"') is False


def test_a_matching_validator_allows_a_not_modified_response() -> None:
    """Turning a large response into a 304 is the point of validation."""
    policy = HttpCachePolicy(max_age=60)

    assert policy.is_not_modified({"if-none-match": '"abc"'}, '"abc"') is True
    assert policy.is_not_modified({"If-None-Match": '"other"'}, '"abc"') is False
    assert policy.is_not_modified({}, '"abc"') is False

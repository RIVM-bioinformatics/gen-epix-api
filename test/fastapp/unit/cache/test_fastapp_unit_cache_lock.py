"""Tests for keyed locking and single-flight coordination."""

import threading
import time

import pytest

from gen_epix.fastapp.cache import lock as cache_lock
from gen_epix.fastapp.cache.lock import KeyedMutex, SingleFlight


def _observe_single_flight_waiters(
    monkeypatch: pytest.MonkeyPatch,
    followers_waiting: threading.Event,
    expected_waiters: int,
) -> None:
    """Signal when followers have entered SingleFlight's shared event wait."""
    waiter_count = 0
    waiter_lock = threading.Lock()

    class ObservedEvent(threading.Event):
        """Signal the test when a caller waits on a shared flight."""

        def wait(self, timeout: float | None = None) -> bool:
            nonlocal waiter_count
            with waiter_lock:
                waiter_count += 1
                if waiter_count == expected_waiters:
                    followers_waiting.set()
            return super().wait(timeout)

    monkeypatch.setattr(cache_lock.threading, "Event", ObservedEvent)


def test_single_flight_runs_one_loader_per_key() -> None:
    """Coalesce concurrent loads of the same key while allowing other keys."""
    flight = SingleFlight()
    calls: list[str] = []
    lock = threading.Lock()

    def loader(key: str) -> str:
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

    assert not any(thread.is_alive() for thread in threads)
    assert sorted(calls) == ["a", "b"]
    assert sorted(results) == ["a", "a", "a", "b"]


def test_every_waiter_receives_the_failure_of_the_leader(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Propagate one leader's failure to concurrent waiters and allow retry."""
    flight = SingleFlight()
    loader_calls: list[None] = []
    leader_started = threading.Event()
    release_leader = threading.Event()
    followers_waiting = threading.Event()

    def loader() -> str:
        loader_calls.append(None)
        if len(loader_calls) == 1:
            leader_started.set()
            assert release_leader.wait(timeout=5)
        raise RuntimeError("origin refused")

    failures: list[RuntimeError] = []

    def run_and_capture_failure() -> None:
        try:
            flight.run("k", loader)
        except RuntimeError as exception:
            failures.append(exception)
        else:
            raise AssertionError("loader failure was not propagated")

    threads = [threading.Thread(target=run_and_capture_failure) for _ in range(3)]
    _observe_single_flight_waiters(monkeypatch, followers_waiting, expected_waiters=2)
    started_threads: list[threading.Thread] = []
    try:
        threads[0].start()
        started_threads.append(threads[0])
        assert leader_started.wait(timeout=5)

        for thread in threads[1:]:
            thread.start()
            started_threads.append(thread)

        assert followers_waiting.wait(timeout=5)
    finally:
        release_leader.set()
        for thread in started_threads:
            thread.join(timeout=5)

    assert not any(thread.is_alive() for thread in started_threads)
    assert len(loader_calls) == 1
    assert len(failures) == 3
    assert all(str(exception) == "origin refused" for exception in failures)
    assert all(exception is failures[0] for exception in failures)

    with pytest.raises(RuntimeError, match="origin refused"):
        flight.run("k", loader)

    assert len(loader_calls) == 2


def test_single_flight_propagates_keyboard_interrupt_and_releases_key() -> None:
    """Propagate BaseException subclasses and release the failed key."""
    flight = SingleFlight()

    def loader() -> str:
        raise KeyboardInterrupt

    try:
        flight.run("k", loader)
    except KeyboardInterrupt:
        pass
    else:
        raise AssertionError("KeyboardInterrupt was not propagated")

    assert not flight.is_in_flight("k")
    assert flight.run("k", lambda: "recovered") == "recovered"


def test_single_flight_success_ignores_callers_active_exception() -> None:
    """Return the loader value when the caller has an active exception context."""
    flight = SingleFlight()

    try:
        raise ValueError("outer")
    except ValueError:
        assert flight.run("k", lambda: "loaded") == "loaded"


def test_a_refresh_leader_is_elected_only_once() -> None:
    """Allow only one in-flight refresh per key until it is finished."""
    flight = SingleFlight()

    assert flight.try_start("k") is True
    assert flight.try_start("k") is False
    flight.finish("k")
    assert flight.try_start("k") is True


def test_a_keyed_mutex_is_discarded_when_nobody_holds_it() -> None:
    """Discard a keyed mutex after its last holder releases it."""
    mutex = KeyedMutex()

    assert mutex.acquire("k") is True
    assert mutex.is_locked("k") is True
    mutex.release("k")

    assert mutex.is_locked("k") is False

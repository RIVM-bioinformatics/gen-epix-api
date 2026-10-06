"""Tests for keyed locking and single-flight coordination."""

import threading
import time

from gen_epix.fastapp.cache.lock import KeyedMutex, SingleFlight


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


def test_every_waiter_receives_the_failure_of_the_leader() -> None:
    """Propagate a loader failure and allow a later call to retry the key."""
    flight = SingleFlight()
    calls: list[int] = []

    def loader() -> str:
        calls.append(1)
        raise RuntimeError("origin refused")

    for _ in range(2):
        try:
            flight.run("k", loader)
        except RuntimeError as exception:
            assert str(exception) == "origin refused"
        else:
            raise AssertionError("loader failure was not propagated")

    assert len(calls) == 2


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

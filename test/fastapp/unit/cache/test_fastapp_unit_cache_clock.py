"""Tests for cache time sources."""

import pytest

from gen_epix.fastapp.cache.clock import ManualClock, SystemClock


def test_a_manual_clock_only_moves_forward() -> None:
    """Moving time backwards must not resurrect expired entries."""
    clock = ManualClock()
    clock.advance(5)

    assert clock.monotonic() == 5
    with pytest.raises(ValueError):
        clock.advance(-1)
    with pytest.raises(ValueError):
        clock.set(1)


def test_the_system_clock_reports_both_readings() -> None:
    """Expiry and timestamps use their respective clock readings."""
    clock = SystemClock()

    assert clock.monotonic() > 0
    assert clock.time() > 0

"""Time sources used by the cache framework.

Every expiry decision in this package reads the current time through a `Clock`
so that tests can advance time deterministically with `ManualClock` instead of
sleeping. `SystemClock` is the production implementation.
"""

import time
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """Encapsulates supplying the monotonic and wall-clock readings a cache needs."""

    def monotonic(self) -> float:
        """Return a strictly non-decreasing reading in seconds."""
        ...

    def time(self) -> float:
        """Return the current wall-clock time as a Unix timestamp."""
        ...


class SystemClock:
    """Encapsulates reading time from the operating system.

    Expiry uses `monotonic` so that wall-clock adjustments cannot resurrect or
    prematurely expire entries, while `time` supplies timestamps that remain
    meaningful when written to a shared store.
    """

    __slots__ = ()

    def monotonic(self) -> float:
        """See base method."""
        return time.monotonic()

    def time(self) -> float:
        """See base method."""
        return time.time()


class ManualClock:
    """Encapsulates advancing only when a test tells it to.

    Both readings start at `start` and move together, so an entry written at
    monotonic time `t` also carries a wall-clock timestamp of `t`.

    Attributes:
        start: The initial value of both readings.
    """

    __slots__ = ("start", "_now")

    def __init__(self, start: float = 0.0):
        """Initialize a ManualClock instance."""
        self.start = start
        self._now = start

    def monotonic(self) -> float:
        """See base method."""
        return self._now

    def time(self) -> float:
        """See base method."""
        return self._now

    def advance(self, seconds: float) -> float:
        """Move the clock forward and return the new reading.

        Args:
            seconds: A non-negative number of seconds to add.

        Returns:
            The reading after advancing.

        Raises:
            ValueError: If `seconds` is negative.
        """
        if seconds < 0:
            raise ValueError("Cannot move a ManualClock backwards")
        self._now += seconds
        return self._now

    def set(self, value: float) -> None:
        """Set both readings to an absolute value.

        Args:
            value: The new reading.

        Raises:
            ValueError: If `value` is earlier than the current reading.
        """
        if value < self._now:
            raise ValueError("Cannot move a ManualClock backwards")
        self._now = value

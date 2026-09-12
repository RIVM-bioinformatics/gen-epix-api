"""Generational key versions.

Deleting a large or unenumerable key set is expensive or impossible, especially
against a shared store. Instead, every key embeds the current version of its
namespace. Bumping that version orphans every previously written key in constant
time; the orphans then leave through ordinary expiry or eviction. This is the
mechanism behind cache versioning in Rails and Django.
"""

import threading
from abc import ABC, abstractmethod


class VersionStore(ABC):
    """Encapsulates holding the current generation number of each namespace.

    Implementations must be safe for concurrent use. A store shared by several
    processes makes a bump visible to all of them; a process-local store only
    invalidates the keys written by the bumping process.
    """

    @abstractmethod
    def get(self, namespace: str) -> int:
        """Return the current generation of `namespace`, creating it at zero."""

    @abstractmethod
    def bump(self, namespace: str) -> int:
        """Advance the generation of `namespace` and return the new value."""

    @abstractmethod
    def set(self, namespace: str, version: int) -> None:
        """Adopt a generation observed elsewhere.

        An invalidation bus uses this to apply a bump that another process
        performed. An implementation must never move a generation backwards,
        because that would make orphaned keys addressable again.

        Args:
            namespace: The namespace to update.
            version: The generation observed remotely.
        """

    @abstractmethod
    def reset(self, namespace: str | None = None) -> None:
        """Set generations back to zero.

        Args:
            namespace: The namespace to reset, or None to reset all of them.
        """

    @abstractmethod
    def snapshot(self) -> dict[str, int]:
        """Return the current generation of every known namespace."""


class MemoryVersionStore(VersionStore):
    """Encapsulates keeping generation numbers in process memory.

    This is exact for a process-local cache. With a shared backend, pair it with
    an invalidation bus so that a bump in one worker reaches the others.
    """

    __slots__ = ("_lock", "_versions")

    def __init__(self) -> None:
        """Initialize a MemoryVersionStore instance."""
        self._lock = threading.Lock()
        self._versions: dict[str, int] = {}

    def get(self, namespace: str) -> int:
        """See base method."""
        with self._lock:
            return self._versions.setdefault(namespace, 0)

    def bump(self, namespace: str) -> int:
        """See base method."""
        with self._lock:
            version = self._versions.get(namespace, 0) + 1
            self._versions[namespace] = version
            return version

    def set(self, namespace: str, version: int) -> None:
        """See base method."""
        with self._lock:
            if version > self._versions.get(namespace, 0):
                self._versions[namespace] = version

    def reset(self, namespace: str | None = None) -> None:
        """See base method."""
        with self._lock:
            if namespace is None:
                self._versions.clear()
            else:
                self._versions.pop(namespace, None)

    def snapshot(self) -> dict[str, int]:
        """See base method."""
        with self._lock:
            return dict(self._versions)

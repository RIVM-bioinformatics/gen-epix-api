"""Tag indexing for invalidation that does not need the key.

A writer rarely knows the key formula used by the readers it invalidates.
Tagging inverts the dependency: a cached entry declares labels such as
``case:42``, and any method that changes case 42 calls
`CacheRegion.invalidate_tags("case:42")` without knowing anything about the
readers. `TagTemplate` renders such labels from call arguments.
"""

import threading
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from gen_epix.fastapp.cache.exc import CacheConfigurationError


@dataclass(slots=True, frozen=True)
class TagTemplate:
    """Encapsulates rendering one tag from the arguments of a cached call.

    A template such as ``"case:{case_id}"`` produces a tag per identifier, while
    a constant such as ``"case"`` produces one tag covering every entry of the
    function. Combining both gives writers a choice between narrow and broad
    invalidation.

    Attributes:
        template: A format string over parameter names, or a constant tag.
    """

    template: str

    def render(self, arguments: Mapping[str, Any]) -> str:
        """Return the tag for one call.

        Args:
            arguments: The call arguments by parameter name.

        Returns:
            The rendered tag.

        Raises:
            CacheConfigurationError: If the template references a parameter
                that the call did not supply.
        """
        try:
            return self.template.format(**arguments)
        except (KeyError, IndexError) as exception:
            raise CacheConfigurationError(
                f"Tag template {self.template!r} references unknown parameter "
                f"{exception}"
            ) from exception


def render_tags(
    templates: Iterable[str | TagTemplate],
    arguments: Mapping[str, Any],
) -> frozenset[str]:
    """Render every configured tag template against one call.

    Args:
        templates: Constant tags or templates.
        arguments: The call arguments by parameter name.

    Returns:
        The rendered tags.

    Raises:
        CacheConfigurationError: If a template references a missing parameter.
    """
    rendered: set[str] = set()
    for template in templates:
        if isinstance(template, TagTemplate):
            rendered.add(template.render(arguments))
        elif "{" in template:
            rendered.add(TagTemplate(template).render(arguments))
        else:
            rendered.add(template)
    return frozenset(rendered)


class TagIndex(ABC):
    """Encapsulates mapping tags to the cache keys that carry them.

    A backend without native tag support needs this index to translate a tag
    invalidation into concrete key deletions. Implementations must be safe for
    concurrent use.
    """

    @abstractmethod
    def add(self, key: str, tags: Iterable[str]) -> None:
        """Associate `key` with `tags`, replacing any previous association."""

    @abstractmethod
    def keys_for(self, tag: str) -> set[str]:
        """Return the keys currently associated with `tag`."""

    @abstractmethod
    def discard_key(self, key: str) -> None:
        """Forget `key` and remove it from every tag."""

    @abstractmethod
    def pop_tag(self, tag: str) -> set[str]:
        """Remove `tag` and return the keys that carried it."""

    @abstractmethod
    def clear(self) -> None:
        """Forget every association."""

    @abstractmethod
    def tags(self) -> set[str]:
        """Return the tags currently known to the index."""


class MemoryTagIndex(TagIndex):
    """Encapsulates keeping tag associations in process memory.

    The index holds both directions so that removing a key does not require a
    scan over all tags. It is exact for a process-local backend; for a shared
    backend it only covers the entries this process wrote, and a tag
    invalidation must additionally be broadcast over an invalidation bus.
    """

    __slots__ = ("_lock", "_keys_by_tag", "_tags_by_key")

    def __init__(self) -> None:
        """Initialize a MemoryTagIndex instance."""
        self._lock = threading.Lock()
        self._keys_by_tag: dict[str, set[str]] = {}
        self._tags_by_key: dict[str, set[str]] = {}

    def add(self, key: str, tags: Iterable[str]) -> None:
        """See base method."""
        new_tags = set(tags)
        with self._lock:
            for stale_tag in self._tags_by_key.get(key, set()) - new_tags:
                holders = self._keys_by_tag.get(stale_tag)
                if holders is not None:
                    holders.discard(key)
                    if not holders:
                        self._keys_by_tag.pop(stale_tag, None)
            if not new_tags:
                self._tags_by_key.pop(key, None)
                return
            self._tags_by_key[key] = new_tags
            for tag in new_tags:
                self._keys_by_tag.setdefault(tag, set()).add(key)

    def keys_for(self, tag: str) -> set[str]:
        """See base method."""
        with self._lock:
            return set(self._keys_by_tag.get(tag, ()))

    def discard_key(self, key: str) -> None:
        """See base method."""
        with self._lock:
            for tag in self._tags_by_key.pop(key, set()):
                holders = self._keys_by_tag.get(tag)
                if holders is None:
                    continue
                holders.discard(key)
                if not holders:
                    self._keys_by_tag.pop(tag, None)

    def pop_tag(self, tag: str) -> set[str]:
        """See base method."""
        with self._lock:
            keys = self._keys_by_tag.pop(tag, set())
            for key in keys:
                remaining = self._tags_by_key.get(key)
                if remaining is None:
                    continue
                remaining.discard(tag)
                if not remaining:
                    self._tags_by_key.pop(key, None)
            return keys

    def clear(self) -> None:
        """See base method."""
        with self._lock:
            self._keys_by_tag.clear()
            self._tags_by_key.clear()

    def tags(self) -> set[str]:
        """See base method."""
        with self._lock:
            return set(self._keys_by_tag)

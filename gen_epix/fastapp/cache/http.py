"""HTTP-level caching helpers.

Caching at the transport boundary is a different mechanism from the value cache
in `CacheRegion`: the store is the client or an intermediary, and the policy
travels in headers. The helpers here are framework independent so that a route
adapter can build the response headers and evaluate a conditional request
without importing a web framework, and so that the same surrogate keys used for
edge purging can be reused as region tags.
"""

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

SURROGATE_KEY_HEADER = "Surrogate-Key"
"""Header carrying the tags an edge cache can later purge by."""

SURROGATE_CONTROL_HEADER = "Surrogate-Control"
"""Header carrying cache directives meant for the edge rather than the client."""


def compute_etag(body: bytes, weak: bool = False) -> str:
    """Return an entity tag derived from a response body.

    Args:
        body: The serialized response body.
        weak: Whether to mark the tag as weak, which asserts semantic rather
            than byte-for-byte equivalence.

    Returns:
        The quoted entity tag, prefixed with ``W/`` when weak.
    """
    digest = hashlib.sha256(body).hexdigest()[:32]
    return f'W/"{digest}"' if weak else f'"{digest}"'


def matches_etag(header_value: str | None, etag: str) -> bool:
    """Return whether a conditional request header matches an entity tag.

    Comparison is weak: a weak tag matches its strong counterpart, which is what
    a validation request needs. A header value of ``*`` matches any tag.

    Args:
        header_value: The value of ``If-None-Match``, or None when absent.
        etag: The current entity tag of the resource.
    """
    if not header_value:
        return False
    if header_value.strip() == "*":
        return True
    current = etag.removeprefix("W/")
    return any(
        candidate.strip().removeprefix("W/") == current
        for candidate in header_value.split(",")
    )


@dataclass(slots=True, frozen=True)
class HttpCachePolicy:
    """Describe how a response may be cached by clients and intermediaries.

    Marking a response `private` is the transport-level counterpart of putting
    the principal in a cache key: it forbids a shared cache from serving the
    response to anyone else. `vary` names the request headers that change the
    response, and omitting a header that does change it is the standard cause of
    cache poisoning and of cross-user leakage.

    Attributes:
        max_age: Seconds a client may reuse the response.
        shared_max_age: Seconds a shared cache may reuse it, overriding
            `max_age` for intermediaries.
        private: Whether only the requesting client may store the response.
        no_store: Whether the response must not be stored at all.
        must_revalidate: Whether a stale response must not be served.
        stale_while_revalidate: Seconds a stale response may be served while it
            is refreshed in the background.
        stale_if_error: Seconds a stale response may be served when the origin
            fails.
        vary: Request headers that select between representations.
    """

    max_age: int | None = None
    shared_max_age: int | None = None
    private: bool = False
    no_store: bool = False
    must_revalidate: bool = False
    stale_while_revalidate: int | None = None
    stale_if_error: int | None = None
    vary: tuple[str, ...] = ()

    def cache_control(self) -> str:
        """Return the ``Cache-Control`` value implied by this policy.

        Returns:
            The directive list, which is ``no-store`` alone when storage is
            forbidden.
        """
        if self.no_store:
            return "no-store"
        directives: list[str] = ["private" if self.private else "public"]
        if self.max_age is not None:
            directives.append(f"max-age={self.max_age}")
        if self.shared_max_age is not None and not self.private:
            directives.append(f"s-maxage={self.shared_max_age}")
        if self.must_revalidate:
            directives.append("must-revalidate")
        if self.stale_while_revalidate is not None:
            directives.append(f"stale-while-revalidate={self.stale_while_revalidate}")
        if self.stale_if_error is not None:
            directives.append(f"stale-if-error={self.stale_if_error}")
        return ", ".join(directives)

    def response_headers(
        self,
        etag: str | None = None,
        surrogate_keys: Iterable[str] = (),
    ) -> dict[str, str]:
        """Return the headers a response should carry under this policy.

        Args:
            etag: Entity tag of the representation, when one was computed.
            surrogate_keys: Tags an edge cache can purge by. Reusing the region
                tags here keeps edge and value caches invalidated together.

        Returns:
            The header names and values to apply to the response.
        """
        headers = {"Cache-Control": self.cache_control()}
        if self.vary:
            headers["Vary"] = ", ".join(self.vary)
        if etag is not None:
            headers["ETag"] = etag
        keys = list(surrogate_keys)
        if keys:
            headers[SURROGATE_KEY_HEADER] = " ".join(sorted(keys))
        return headers

    def is_not_modified(
        self,
        request_headers: Mapping[str, str],
        etag: str | None,
    ) -> bool:
        """Return whether the client already holds the current representation.

        A caller that receives True should answer 304 without a body, which
        turns a large response into a few hundred bytes.

        Args:
            request_headers: The request headers, matched case-insensitively.
            etag: The current entity tag, or None when the resource has none.
        """
        if etag is None or self.no_store:
            return False
        lowered = {name.lower(): value for name, value in request_headers.items()}
        return matches_etag(lowered.get("if-none-match"), etag)

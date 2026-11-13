"""Rate-limit configuration for API requests."""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_ipaddr


def limiter_key_func(request: Request) -> str:
    """Key function for the rate limiter."""
    # TODO: LSP-3893 With Authorization: "", all clients share the empty limiter key
    # instead of using their IP; confirm whether empty credentials should fall back
    # to the client IP or intentionally share a bucket.
    if "authorization" in request.headers:
        return request.headers["authorization"]
    return get_ipaddr(request)


limiter = Limiter(key_func=limiter_key_func, default_limits=["10/second"])

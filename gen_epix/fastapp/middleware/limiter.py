"""Rate-limit configuration for API requests."""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_ipaddr


def limiter_key_func(request: Request) -> str:
    """Key function for the rate limiter."""
    authorization = request.headers.get("authorization")
    if authorization:
        return authorization
    return get_ipaddr(request)


LIMITER = Limiter(key_func=limiter_key_func, default_limits=["10/second"])

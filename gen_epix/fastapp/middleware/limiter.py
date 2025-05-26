from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_ipaddr


def limiter_key_func(request: Request) -> str:
    """
    Key function for the rate limiter.
    """
    if "authorization" in request.headers:
        return request.headers["authorization"]
    return get_ipaddr(request)


limiter = Limiter(key_func=limiter_key_func, default_limits=["10/second"])

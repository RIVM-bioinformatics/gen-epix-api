"""Verify rate-limiter key selection for authenticated and anonymous requests."""

import pytest
from starlette.requests import Request

from gen_epix.fastapp.middleware.limiter import limiter_key_func


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        ([(b"authorization", b"Bearer token")], "Bearer token"),
        ([(b"authorization", b"")], "192.0.2.1"),
        ([], "192.0.2.1"),
    ],
    ids=["authorization", "empty-authorization", "no-authorization"],
)
def test_limiter_key_uses_token_or_client_ip(
    headers: list[tuple[bytes, bytes]], expected: str
) -> None:
    """Use a nonempty authorization value or fall back to the client IP."""
    request = Request(
        {"type": "http", "headers": headers, "client": ("192.0.2.1", 1234)}
    )

    assert limiter_key_func(request) == expected

"""Verify default and endpoint-specific response headers."""

import asyncio

from fastapi import FastAPI, Request, Response

import gen_epix.fastapp.middleware.update_response_header as response_headers


def test_missing_exception_headers_still_adds_version_headers(monkeypatch) -> None:
    """Apply general and version headers when no exception list is supplied."""
    monkeypatch.setenv("APP_VERSION", "2026.1")
    monkeypatch.setattr(response_headers, "get_package_version", lambda: "1.2.3")
    middleware = response_headers.UpdateResponseHeaderMiddleware(
        FastAPI(), general_headers={"X-General": "present"}
    )
    request = Request({"type": "http", "path": "/items", "headers": []})

    async def call_next(_: Request) -> Response:
        return Response("ok", media_type="application/json")

    result = asyncio.run(middleware.dispatch(request, call_next))

    assert result.headers["X-General"] == "present"
    assert result.headers["API-Version"] == "1.2.3"
    assert result.headers["content-type"] == "application/json;version=2026.1"

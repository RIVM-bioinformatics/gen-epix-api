"""Unit tests for the remote retry policy of the fastapp Client."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
import pytest

from gen_epix import fastapp
from gen_epix.commondb.domain import DOMAIN
from gen_epix.commondb.services.client import CommondbClient
from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import AuthProtocol, HttpProtocol
from gen_epix.fastapp.model import Command

POLICY = fastapp.RetryPolicy(
    retryable_status_codes=frozenset({404, 429, 500, 502, 503, 504}),
    wait_schedule=(1, 2, 3),
)


class RetryCommand(Command):
    """Command handled by a test-controlled handler."""

    NAME = "RetryCommand"


def _status_error(status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "http://example.org/x")
    response = httpx.Response(status, request=request)
    return httpx.HTTPStatusError("boom", request=request, response=response)


def _make_client(
    handler: Callable[[Command], Any], retry_policy: fastapp.RetryPolicy | None
) -> CommondbClient:
    client = CommondbClient(
        DOMAIN,
        "example.org",
        8000,
        protocol=HttpProtocol.HTTP,
        auth_protocol=AuthProtocol.NONE,
        retry_policy=retry_policy,
    )
    client.register_route(RetryCommand, "/retry")
    client.register_handler(RetryCommand, handler)
    return client


class Flaky:
    """Handler raising the given errors in order, then returning a value."""

    def __init__(self, *errors: BaseException) -> None:
        self.errors = list(errors)
        self.calls = 0

    def __call__(self, cmd: Command) -> str:
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return "ok"


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record tenacity sleeps instead of waiting."""
    recorded: list[float] = []
    monkeypatch.setattr("tenacity.nap.time.sleep", recorded.append)
    return recorded


class TestRemoteRetryPolicy:
    def test_rejects_auth_status_codes(self) -> None:
        for code in (401, 403):
            codes = frozenset({500, code})
            with pytest.raises(ValueError):
                fastapp.RetryPolicy(codes, (1,))

    def test_is_retryable_for_network_and_listed_status(self) -> None:
        assert POLICY.is_retryable(httpx.ConnectError("x"))
        assert POLICY.is_retryable(httpx.ReadTimeout("x"))
        assert not POLICY.is_retryable(ValueError("x"))


class TestStatusHelpers:
    def test_status_from_message(self) -> None:
        e = exc.ServiceException("11111111", "HTTP status 502 error when handling")
        assert fastapp.RetryPolicy.get_remote_http_status(e) == 502

    def test_status_from_cause(self) -> None:
        e = exc.ServiceException("11111111", "no status here")
        e.__cause__ = _status_error(503)
        assert fastapp.RetryPolicy.get_remote_http_status(e) == 503

    def test_status_fallback_and_non_http(self) -> None:
        assert (
            fastapp.RetryPolicy.get_remote_http_status(
                exc.ServiceException("11111111", "x")
            )
            == 500
        )
        assert fastapp.RetryPolicy.get_remote_http_status(_status_error(404)) == 404
        assert fastapp.RetryPolicy.get_remote_http_status(ValueError("x")) is None

    def test_is_network_error_through_wrapper(self) -> None:
        wrapped = exc.ServiceException("11111111", "wrapped")
        wrapped.__cause__ = httpx.ConnectError("x")
        assert fastapp.RetryPolicy.is_network_error(wrapped)
        assert not fastapp.RetryPolicy.is_network_error(
            exc.ServiceException("11111111", "x")
        )

    def test_is_retryable_status_never_auth(self) -> None:
        e = exc.ServiceException("11111111", "HTTP status 401 error")
        assert not fastapp.RetryPolicy.is_retryable_status(e, frozenset({401, 500}))
        assert not fastapp.RetryPolicy.is_retryable_status(
            exc.AuthException("11111111", "x"), {500}
        )


class TestClientHandleRetry:
    def test_no_policy_means_no_retry(self, sleeps: list[float]) -> None:
        handler = Flaky(_status_error(503), _status_error(503))
        client = _make_client(handler, None)
        cmd = RetryCommand()
        with pytest.raises(exc.ServiceException):
            client.handle(cmd)
        assert handler.calls == 1
        assert sleeps == []

    def test_retries_listed_status_then_succeeds(self, sleeps: list[float]) -> None:
        handler = Flaky(_status_error(503), _status_error(404))
        client = _make_client(handler, POLICY)
        assert client.handle(RetryCommand()) == "ok"
        assert handler.calls == 3
        assert sleeps == [1, 2]

    def test_exhausted_attempts_reraise_last_error(self, sleeps: list[float]) -> None:
        handler = Flaky(*[_status_error(502) for _ in range(10)])
        client = _make_client(handler, POLICY)
        cmd = RetryCommand()
        with pytest.raises(exc.ServiceException, match="HTTP status 502"):
            client.handle(cmd)
        assert handler.calls == len(POLICY.wait_schedule) + 1
        assert sleeps == [1, 2, 3]

    def test_unlisted_status_not_retried(self, sleeps: list[float]) -> None:
        handler = Flaky(_status_error(400))
        client = _make_client(handler, POLICY)
        cmd = RetryCommand()
        with pytest.raises(exc.ServiceException):
            client.handle(cmd)
        assert handler.calls == 1

    def test_network_error_always_retried(self, sleeps: list[float]) -> None:
        handler = Flaky(httpx.ReadTimeout("t"), httpx.ConnectError("c"))
        client = _make_client(handler, fastapp.RetryPolicy(frozenset(), (5, 5)))
        assert client.handle(RetryCommand()) == "ok"
        assert handler.calls == 3

    @pytest.mark.parametrize("status", [401, 403])
    def test_auth_status_never_retried(self, status: int, sleeps: list[float]) -> None:
        handler = Flaky(_status_error(status))
        client = _make_client(handler, POLICY)
        cmd = RetryCommand()
        with pytest.raises(exc.ServiceException):
            client.handle(cmd)
        assert handler.calls == 1

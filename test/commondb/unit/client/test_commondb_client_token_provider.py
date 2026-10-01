"""Unit tests for the token_provider hook of CommondbClient."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx
import jwt
import pytest

from gen_epix.commondb.domain import DOMAIN
from gen_epix.commondb.services.client import CommondbClient
from gen_epix.fastapp import exc
from gen_epix.fastapp.client import RemoteRetryPolicy
from gen_epix.fastapp.enum import AuthProtocol, HttpProtocol
from gen_epix.fastapp.model import Command

_SECRET = "token-provider-test-secret-key-32bytes"


class ProviderCommand(Command):
    """Command handled by a test-controlled handler."""

    NAME = "ProviderCommand"


def _token(exp_offset: float | None, sub: str = "u") -> str:
    claims: dict[str, Any] = {"sub": sub}
    if exp_offset is not None:
        claims["exp"] = int(datetime.now(timezone.utc).timestamp() + exp_offset)
    return jwt.encode(claims, _SECRET, algorithm="HS256")


class Provider:
    """Token provider returning the given tokens in order (last one repeats)."""

    def __init__(self, *tokens: str | Exception) -> None:
        self.tokens = list(tokens)
        self.calls = 0

    def __call__(self) -> str:
        self.calls += 1
        item = self.tokens.pop(0) if len(self.tokens) > 1 else self.tokens[0]
        if isinstance(item, Exception):
            raise item
        return item


def _status_error(status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "http://example.org/x")
    return httpx.HTTPStatusError(
        "boom", request=request, response=httpx.Response(status, request=request)
    )


def _make_client(provider: Provider, **kwargs: Any) -> CommondbClient:
    return CommondbClient(
        DOMAIN,
        "example.org",
        8000,
        protocol=HttpProtocol.HTTP,
        auth_protocol=AuthProtocol.NONE,
        token_provider=provider,
        **kwargs,
    )


class TestTokenProviderHeaders:
    def test_provider_called_once_while_token_valid(self) -> None:
        token = _token(3600)
        provider = Provider(token)
        client = _make_client(provider)
        for _ in range(3):
            headers = client.get_headers(ProviderCommand())
        assert headers["Authorization"] == f"Bearer {token}"
        assert provider.calls == 1

    def test_default_headers_are_kept(self) -> None:
        client = _make_client(Provider(_token(3600)))
        assert client.get_headers(ProviderCommand())["Content-Type"] == (
            "application/json"
        )

    def test_provider_recalled_within_refresh_margin(self) -> None:
        first, second = _token(30, "a"), _token(3600, "b")
        provider = Provider(first, second)
        client = _make_client(provider, oauth_token_refresh_margin=60)
        assert client.get_headers(ProviderCommand())["Authorization"].endswith(first)
        assert client.get_headers(ProviderCommand())["Authorization"].endswith(second)
        assert provider.calls == 2

    def test_token_without_exp_cached_indefinitely(self) -> None:
        provider = Provider(_token(None))
        client = _make_client(provider)
        client.get_headers(ProviderCommand())
        client.get_headers(ProviderCommand())
        assert provider.calls == 1

    def test_opaque_token_cached_indefinitely(self) -> None:
        provider = Provider("not-a-jwt")
        client = _make_client(provider)
        assert client.get_headers(ProviderCommand())["Authorization"] == (
            "Bearer not-a-jwt"
        )
        client.get_headers(ProviderCommand())
        assert provider.calls == 1

    def test_get_access_token(self) -> None:
        token = _token(3600)
        assert _make_client(Provider(token)).get_access_token() == token

    def test_get_access_token_without_token_source(self) -> None:
        client = CommondbClient(DOMAIN, "example.org", 8000, protocol=HttpProtocol.HTTP)
        with pytest.raises(exc.InitializationServiceError):
            client.get_access_token()


class TestTokenProviderValidation:
    def test_conflicts_with_oauth2(self) -> None:
        provider = Provider("x")
        with pytest.raises(exc.InitializationServiceError, match="OAUTH2"):
            CommondbClient(
                DOMAIN,
                "example.org",
                8000,
                auth_protocol=AuthProtocol.OAUTH2,
                oauth_discovery_url="https://idp/.well-known",
                oauth_client_id="id",
                oauth_scope="s",
                token_provider=provider,
            )

    def test_conflicts_with_authorization_default_header(self) -> None:
        provider = Provider("x")
        headers = {"authorization": "Bearer abc"}
        with pytest.raises(exc.InitializationServiceError, match="Authorization"):
            _make_client(provider, default_headers=headers)


class TestTokenProviderHandle:
    @staticmethod
    def _register(client: CommondbClient, handler: Any) -> None:
        client.register_route(ProviderCommand, "/provider")
        client.register_handler(ProviderCommand, handler)

    def test_401_refreshes_token_and_retries_once(self) -> None:
        first, second = _token(3600, "a"), _token(3600, "b")
        provider = Provider(first, second)
        client = _make_client(provider)
        seen: list[str] = []

        def handler(cmd: Command) -> str:
            seen.append(client.get_headers(cmd)["Authorization"])
            if len(seen) == 1:
                raise _status_error(401)
            return "ok"

        self._register(client, handler)
        assert client.handle(ProviderCommand()) == "ok"
        assert provider.calls == 2
        assert seen == [f"Bearer {first}", f"Bearer {second}"]

    def test_second_401_propagates(self) -> None:
        provider = Provider(_token(3600, "a"), _token(3600, "b"))
        client = _make_client(provider)
        calls = 0

        def handler(cmd: Command) -> str:
            nonlocal calls
            calls += 1
            client.get_headers(cmd)
            raise _status_error(401)

        self._register(client, handler)
        cmd = ProviderCommand()
        with pytest.raises(exc.ServiceException, match="HTTP status 401"):
            client.handle(cmd)
        assert calls == 2

    def test_other_errors_do_not_refresh(self) -> None:
        provider = Provider(_token(3600))
        client = _make_client(provider)

        def handler(cmd: Command) -> str:
            client.get_headers(cmd)
            raise _status_error(403)

        self._register(client, handler)
        cmd = ProviderCommand()
        with pytest.raises(exc.ServiceException):
            client.handle(cmd)
        assert provider.calls == 1

    def test_provider_failure_is_auth_error_and_not_transient_retried(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        sleeps: list[float] = []
        monkeypatch.setattr("tenacity.nap.time.sleep", sleeps.append)
        provider = Provider(RuntimeError("login failed"))
        client = _make_client(
            provider, retry_policy=RemoteRetryPolicy(frozenset({500}), (1, 1))
        )

        def handler(cmd: Command) -> str:
            client.get_headers(cmd)
            return "ok"

        self._register(client, handler)
        cmd = ProviderCommand()
        with pytest.raises(exc.ServiceException) as info:
            client.handle(cmd)
        assert isinstance(info.value.__cause__, exc.AuthException)
        assert provider.calls == 1
        assert sleeps == []

    def test_401_refresh_does_not_consume_transient_attempt(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("tenacity.nap.time.sleep", lambda _: None)
        provider = Provider(_token(3600, "a"), _token(3600, "b"))
        client = _make_client(
            provider, retry_policy=RemoteRetryPolicy(frozenset({503}), (1,))
        )
        errors = [_status_error(401), _status_error(503)]
        calls = 0

        def handler(cmd: Command) -> str:
            nonlocal calls
            calls += 1
            client.get_headers(cmd)
            if errors:
                raise errors.pop(0)
            return "ok"

        self._register(client, handler)
        # 401 -> refresh+retry (inside attempt 1); 503 -> transient retry (attempt 2)
        assert client.handle(ProviderCommand()) == "ok"
        assert calls == 3

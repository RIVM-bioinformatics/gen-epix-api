from test.fastapp.auth_test_client import AuthTestClient
from typing import Any, Dict, Optional, Type

import httpx
import pytest

from gen_epix.fastapp.services.auth.introspection import TokenIntrospectionManager
from gen_epix.fastapp.services.auth.oauth_idp_client import OauthIdpClient


class DummyResponse:
    def __init__(
        self, introspection_endpoint: str = "https://introspect.local/token"
    ) -> None:
        self._endpoint: str = introspection_endpoint

    def json(self) -> Dict[str, str]:
        return {"introspection_endpoint": self._endpoint}


def make_dummy_client(counter: Dict[str, int], expected_url: str) -> Type[Any]:
    """Return a DummyClient class bound to `counter` and `expected_url`.

    The returned class matches the interface used in tests (context manager
    with a `get(url)` method) and only accepts a single `verify` argument
    so it can replace `httpx.Client` directly.
    """

    class DummyClient:
        def __init__(self, verify: Any) -> None:
            pass

        def __enter__(self) -> "DummyClient":
            return self

        def __exit__(
            self,
            exc_type: Optional[type],
            exc: Optional[BaseException],
            tb: Optional[Any],
        ) -> Optional[bool]:
            return None

        def get(self, url: str) -> DummyResponse:
            counter["n"] += 1
            assert url == expected_url
            return DummyResponse()

    return DummyClient


def _get_oauth_client() -> OauthIdpClient:
    env = AuthTestClient.get_test_client()
    for idp in env.auth_service.idp_clients:
        if isinstance(idp, OauthIdpClient):
            return idp
    pytest.skip("No OidcClient available")


def test_fetch_introspection_endpoint_returns_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    idp = _get_oauth_client()
    discovery_url = (
        idp.server_cfg.discovery_url
        or "https://discovery.local/.well-known/openid-configuration"
    )

    counter = {"n": 0}

    monkeypatch.setattr(httpx, "Client", make_dummy_client(counter, discovery_url))

    manager = TokenIntrospectionManager(
        server_cfg=idp.server_cfg,
        discovery_url=discovery_url,
        ssl_context=True,
        introspect_token_request_headers=None,
    )

    endpoint = manager._fetch_introspection_endpoint()
    assert endpoint == "https://introspect.local/token"
    assert counter["n"] == 1


def test_get_cached_introspection_endpoint_uses_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    idp = _get_oauth_client()
    discovery_url = (
        idp.server_cfg.discovery_url
        or "https://discovery.local/.well-known/openid-configuration"
    )

    counter = {"n": 0}

    monkeypatch.setattr(httpx, "Client", make_dummy_client(counter, discovery_url))

    manager = TokenIntrospectionManager(
        server_cfg=idp.server_cfg,
        discovery_url=discovery_url,
        ssl_context=True,
        introspect_token_request_headers=None,
    )

    # First call should fetch
    ep1 = manager._get_cached_introspection_endpoint()
    # Second call should use cache and not call httpx.Client.get again
    ep2 = manager._get_cached_introspection_endpoint()

    assert ep1 == ep2 == "https://introspect.local/token"
    assert counter["n"] == 1


def test_get_cached_introspection_endpoint_respects_ttl_and_refetches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    idp = _get_oauth_client()
    discovery_url = (
        idp.server_cfg.discovery_url
        or "https://discovery.local/.well-known/openid-configuration"
    )

    counter = {"n": 0}

    monkeypatch.setattr(httpx, "Client", make_dummy_client(counter, discovery_url))

    manager = TokenIntrospectionManager(
        server_cfg=idp.server_cfg,
        discovery_url=discovery_url,
        ssl_context=True,
        introspect_token_request_headers=None,
    )

    # Prime cache with a stale timestamp (older than TTL)
    manager._introspection_endpoint_cache = {
        "endpoint": "https://old.local/token",
        "last_checked": manager._now() - (manager.INTROSPECTION_ENDPOINT_TTL + 1),
    }

    # Should re-fetch because cache is expired
    endpoint = manager._get_cached_introspection_endpoint()
    assert endpoint == "https://introspect.local/token"
    assert counter["n"] == 1

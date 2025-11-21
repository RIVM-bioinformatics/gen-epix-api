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
    """Return a DummyClient class bound to counter and expected_url"""

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


class TestOauthIdpClientIntrospectionEndpoint:

    CLIENT: OauthIdpClient

    @classmethod
    def setup_class(cls) -> None:
        env = AuthTestClient.get_test_client()
        for idp in env.auth_service.idp_clients:
            if isinstance(idp, OauthIdpClient):
                cls.CLIENT = idp
                break
        else:
            pytest.skip("No OidcClient available")

    def test_fetch_introspection_endpoint_returns_endpoint(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        discovery_url = (
            self.CLIENT.server_cfg.discovery_url
            or "https://discovery.local/.well-known/openid-configuration"
        )

        counter = {"n": 0}

        monkeypatch.setattr(httpx, "Client", make_dummy_client(counter, discovery_url))

        manager = TokenIntrospectionManager(
            server_cfg=self.CLIENT.server_cfg,
            discovery_url=discovery_url,
            ssl_context=True,
            introspect_token_request_headers=None,
        )

        endpoint = manager._fetch_introspection_endpoint()  # type: ignore[protected-access]
        assert endpoint == "https://introspect.local/token"
        assert counter["n"] == 1

    def test_get_cached_introspection_endpoint_uses_cache(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        discovery_url = (
            self.CLIENT.server_cfg.discovery_url
            or "https://discovery.local/.well-known/openid-configuration"
        )

        counter = {"n": 0}

        monkeypatch.setattr(httpx, "Client", make_dummy_client(counter, discovery_url))

        manager = TokenIntrospectionManager(
            server_cfg=self.CLIENT.server_cfg,
            discovery_url=discovery_url,
            ssl_context=True,
            introspect_token_request_headers=None,
        )

        # First call should fetch
        ep1 = manager._get_cached_introspection_endpoint()  # type: ignore[protected-access]
        # Second call should use cache and not call httpx.Client.get again
        ep2 = manager._get_cached_introspection_endpoint()  # type: ignore[protected-access]

        assert ep1 == ep2 == "https://introspect.local/token"
        assert counter["n"] == 1

    def test_get_cached_introspection_endpoint_respects_ttl_and_refetches(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        discovery_url = (
            self.CLIENT.server_cfg.discovery_url
            or "https://discovery.local/.well-known/openid-configuration"
        )

        counter = {"n": 0}

        monkeypatch.setattr(httpx, "Client", make_dummy_client(counter, discovery_url))

        manager = TokenIntrospectionManager(
            server_cfg=self.CLIENT.server_cfg,
            discovery_url=discovery_url,
            ssl_context=True,
            introspect_token_request_headers=None,
        )

        # Prime cache with a stale timestamp (older than TTL)
        manager._introspection_endpoint_cache = {  # type: ignore[protected-access]
            "endpoint": "https://old.local/token",
            "last_checked": manager._now() - (manager.INTROSPECTION_ENDPOINT_TTL + 1),  # type: ignore[protected-access]
        }

        # Should re-fetch because cache is expired
        endpoint = manager._get_cached_introspection_endpoint()  # type: ignore[protected-access]
        assert endpoint == "https://introspect.local/token"
        assert counter["n"] == 1

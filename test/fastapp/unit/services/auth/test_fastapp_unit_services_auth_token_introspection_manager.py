from test.util.mock_compat import MagicMock, Mock, patch

import httpx
import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.services.auth.model import OidcServerCfg
from gen_epix.fastapp.services.auth.token_introspection_manager import (
    TokenIntrospectionManager,
)


class TestTokenIntrospectionManager:
    def create_manager(
        self,
        *,
        timeout_seconds: int | None = 2,
        interval_seconds: int | None = 60,
    ) -> TokenIntrospectionManager:
        server_cfg = OidcServerCfg(
            name="TEST",
            label="Test IDP",
            discovery_url="https://issuer.example.com/.well-known/openid-configuration",
            client_id="client-id",
            client_secret="client-secret",
            scope="openid profile email",
            public=False,
            enable_introspection=True,
        )
        return TokenIntrospectionManager(
            server_cfg=server_cfg,
            discovery_url=server_cfg.discovery_url or "",
            ssl_context=True,
            introspection_timeout_seconds=timeout_seconds,
            introspection_interval_seconds=interval_seconds,
        )

    def patch_discovery_client(
        self, monkeypatch: pytest.MonkeyPatch, discovery_url: str
    ) -> dict[str, int]:
        calls = {"n": 0}
        response = Mock()
        response.json.return_value = {
            "introspection_endpoint": "https://introspect.local/token"
        }
        client_context = MagicMock()
        http_client = Mock()

        def get(request_url: str) -> Mock:
            calls["n"] += 1
            assert request_url == discovery_url
            return response

        http_client.get.side_effect = get
        client_context.__enter__.return_value = http_client
        monkeypatch.setattr(httpx, "Client", Mock(return_value=client_context))
        return calls

    def test_introspect_token_skips_when_cached_recent_and_active(self) -> None:
        manager = self.create_manager()
        manager._introspection_cache = {  # type: ignore[attr-defined]
            "tok": {"active": True, "last_checked": 1000, "exp": 1100}
        }

        with (
            patch.object(manager, "_now", return_value=1000),
            patch.object(manager, "_introspect_token_with_server") as introspect,
        ):
            manager.introspect_token("tok", {"exp": 1100})

        introspect.assert_not_called()

    def test_introspect_token_cached_inactive_denies(self) -> None:
        manager = self.create_manager()
        manager._introspection_cache = {  # type: ignore[attr-defined]
            "tok": {"active": False, "last_checked": 0, "exp": 1100}
        }

        with patch.object(manager, "_now", return_value=1000):
            with pytest.raises(exc.CredentialsAuthError):
                manager.introspect_token("tok", {"exp": 1100})

    def test_introspect_token_recheck_paths(self) -> None:
        manager = self.create_manager()
        manager._introspection_cache = {}  # type: ignore[attr-defined]

        with (
            patch.object(manager, "_now", return_value=1000),
            patch.object(
                manager,
                "_introspect_token_with_server",
                side_effect=[None, True, False],
            ),
        ):
            with pytest.raises(exc.CredentialsAuthError):
                manager.introspect_token("A", {"exp": 1100})

            manager.introspect_token("B", {"exp": 1100})

            with pytest.raises(exc.CredentialsAuthError):
                manager.introspect_token("C", {"exp": 1100})

    def test_zero_interval_rechecks_cached_active_token(self) -> None:
        manager = self.create_manager(interval_seconds=0)
        manager._introspection_cache = {  # type: ignore[attr-defined]
            "tok": {"active": True, "last_checked": 1000, "exp": 1100}
        }

        with (
            patch.object(manager, "_now", return_value=1000),
            patch.object(
                manager, "_introspect_token_with_server", return_value=True
            ) as introspect,
        ):
            manager.introspect_token("tok", {"exp": 1100})

        introspect.assert_called_once_with("tok")

    def test_zero_timeout_is_passed_to_http_client(self) -> None:
        manager = self.create_manager(timeout_seconds=0)
        client_context = MagicMock()
        http_client = Mock()
        client_context.__enter__.return_value = http_client
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"active": True}
        http_client.post.return_value = response

        with (
            patch.object(
                manager,
                "_get_cached_introspection_endpoint",
                return_value="https://issuer.example.com/introspect",
            ),
            patch(
                "gen_epix.fastapp.services.auth.token_introspection_manager.httpx.Client",
                return_value=client_context,
            ) as client_constructor,
        ):
            assert manager._introspect_token_with_server("tok") is True

        client_constructor.assert_called_once_with(verify=True, timeout=0)

    def test_fetch_introspection_endpoint_returns_endpoint(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        manager = self.create_manager()
        calls = self.patch_discovery_client(monkeypatch, manager.discovery_url)

        endpoint = manager._fetch_introspection_endpoint()  # type: ignore[protected-access]

        assert endpoint == "https://introspect.local/token"
        assert calls["n"] == 1

    def test_get_cached_introspection_endpoint_uses_cache(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        manager = self.create_manager()
        calls = self.patch_discovery_client(monkeypatch, manager.discovery_url)

        first_endpoint = manager._get_cached_introspection_endpoint()  # type: ignore[protected-access]
        second_endpoint = manager._get_cached_introspection_endpoint()  # type: ignore[protected-access]

        assert first_endpoint == second_endpoint == "https://introspect.local/token"
        assert calls["n"] == 1

    def test_get_cached_introspection_endpoint_respects_ttl_and_refetches(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        manager = self.create_manager()
        calls = self.patch_discovery_client(monkeypatch, manager.discovery_url)
        manager._introspection_endpoint_cache = {  # type: ignore[attr-defined]
            "endpoint": "https://old.local/token",
            "last_checked": manager._now() - manager.INTROSPECTION_ENDPOINT_TTL - 1,
        }

        endpoint = manager._get_cached_introspection_endpoint()  # type: ignore[protected-access]

        assert endpoint == "https://introspect.local/token"
        assert calls["n"] == 1

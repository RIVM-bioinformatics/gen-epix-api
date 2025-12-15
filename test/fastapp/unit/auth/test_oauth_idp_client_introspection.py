import asyncio
from test.fastapp.auth_test_client import AuthTestClient
from typing import Any

import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.services.auth.token_introspection_manager import (
    TokenIntrospectionManager,
)
from gen_epix.fastapp.services.auth.model import OidcServerCfg
from gen_epix.fastapp.services.auth.oauth_idp_client import OauthIdpClient


class TestOauthIdpClientIntrospection:

    CLIENT: OauthIdpClient
    TOKEN: str

    @classmethod
    def setup_class(cls) -> None:
        env = AuthTestClient.get_test_client()
        for idp in env.auth_service.idp_clients:
            if isinstance(idp, OauthIdpClient):
                cls.CLIENT = idp
                break
        else:  # no break
            pytest.skip("No OidcClient available")

        cls.TOKEN = env.MOCK_JWK_TOKEN.token
        cls._enable_introspection()

    @classmethod
    def _enable_introspection(cls) -> None:
        cls.CLIENT.server_cfg.enable_introspection = True
        if not hasattr(cls.CLIENT, "token_introspection_manger") or (
            getattr(cls.CLIENT, "token_introspection_manger") is None
        ):
            cls.CLIENT.token_introspection_manger = TokenIntrospectionManager(
                server_cfg=cls.CLIENT.server_cfg,
                # Provide a non-empty discovery URL so the manager validates.
                discovery_url=(
                    cls.CLIENT.server_cfg.discovery_url
                    or "https://discovery.local/.well-known/openid-configuration"
                ),
                ssl_context=cls.CLIENT.ssl_context,
                introspect_token_request_headers=None,
                introspection_auth_method=cls.CLIENT.server_cfg.introspection_auth_method,
                introspection_timeout_seconds=cls.CLIENT.server_cfg.introspection_timeout_seconds,
                introspection_interval_seconds=cls.CLIENT.server_cfg.introspection_interval_seconds,
                log_item_class=cls.CLIENT._log_item_class,
                logger=cls.CLIENT.logger,
            )
            # Patch retrieval so tests use a deterministic introspection endpoint
            setattr(
                cls.CLIENT.token_introspection_manger,
                "_get_cached_introspection_endpoint",
                lambda: "https://introspect.local/token",
            )

    def _cache(self) -> dict[str, dict[str, Any]]:
        return getattr(self.CLIENT.token_introspection_manger, "_introspection_cache")

    def _now(self) -> int:
        return getattr(self.CLIENT.token_introspection_manger, "_now")()

    def test_introspection_populates_cache(self) -> None:
        counter: dict[str, int] = {"n": 0}

        def fake_introspect(_token: str) -> bool:
            counter["n"] += 1
            return True

        setattr(
            self.CLIENT.token_introspection_manger,
            "_introspect_token_with_server",
            fake_introspect,
        )

        claims = asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))
        assert claims is not None
        assert counter["n"] == 1

        claims2 = asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))
        assert claims2 is not None
        assert counter["n"] == 1

    def test_introspection_inactive_denies(self) -> None:
        now = self._now()
        self._cache()[self.TOKEN] = {
            "active": False,
            "last_checked": now,
            "exp": now + 600,
        }

        with pytest.raises(exc.CredentialsAuthError):
            asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))

    def test_recheck_to_inactive_then_denies(self) -> None:
        now = self._now()
        interval = (
            self.CLIENT.token_introspection_manger._introspection_interval_seconds
        )
        self._cache()[self.TOKEN] = {
            "active": True,
            "last_checked": now - (interval + 1),
            "exp": now + 600,
        }

        setattr(
            self.CLIENT.token_introspection_manger,
            "_introspect_token_with_server",
            lambda _: False,
        )

        with pytest.raises(exc.CredentialsAuthError):
            asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))

    def test_introspection_failure(self) -> None:
        self._cache().pop(self.TOKEN, None)

        counter: dict[str, int] = {"n": 0}

        def fake_introspect(_token: str) -> None:
            counter["n"] += 1
            return None

        setattr(
            self.CLIENT.token_introspection_manger,
            "_introspect_token_with_server",
            fake_introspect,
        )

        with pytest.raises(exc.CredentialsAuthError):
            asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))
        assert counter["n"] == 1

    def test_cache_expiry_prunes_and_triggers_recheck(self) -> None:
        now = self._now()
        self._cache()[self.TOKEN] = {
            "active": True,
            "last_checked": now - 10,
            "exp": now - 1,
        }

        counter: dict[str, int] = {"n": 0}

        def fake_introspect(_token: str) -> bool:
            counter["n"] += 1
            return True

        setattr(
            self.CLIENT.token_introspection_manger,
            "_introspect_token_with_server",
            fake_introspect,
        )

        claims = asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))
        assert claims is not None
        assert counter["n"] == 1

        claims2 = asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))
        assert claims2 is not None
        assert counter["n"] == 1

    def test_cached_active_within_interval_skips_recheck(self) -> None:
        now = self._now()
        self._cache()[self.TOKEN] = {
            "active": True,
            "last_checked": now,
            "exp": now + 600,
        }

        def fail_if_called(_token: str) -> None:
            raise AssertionError("introspection should not be called within interval")

        setattr(
            self.CLIENT.token_introspection_manger,
            "_introspect_token_with_server",
            fail_if_called,
        )

        claims = asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))
        assert claims is not None

    def test_interval_elapsed_triggers_single_recheck(self) -> None:
        now = self._now()
        interval = (
            self.CLIENT.token_introspection_manger._introspection_interval_seconds
        )
        self._cache()[self.TOKEN] = {
            "active": True,
            "last_checked": now - (interval + 1),
            "exp": now + 600,
        }

        counter: dict[str, int] = {"n": 0}

        def fake_introspect(_token: str) -> bool:
            counter["n"] += 1
            return True

        setattr(
            self.CLIENT.token_introspection_manger,
            "_introspect_token_with_server",
            fake_introspect,
        )

        claims = asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))
        assert claims is not None
        assert counter["n"] == 1

        claims2 = asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))
        assert claims2 is not None
        assert counter["n"] == 1

    def test_claim_map_validator_rejects_bad_types(self) -> None:
        with pytest.raises(ValueError):
            OidcServerCfg(
                claim_map="notadict", name="x", label="x", client_id="x", scope="openid"
            )
        with pytest.raises(ValueError):
            OidcServerCfg(
                claim_map={"__key__": 123},
                name="x",
                label="x",
                client_id="x",
                scope="openid",
            )
        with pytest.raises(ValueError):
            OidcServerCfg(
                claim_map={"__key__": ["email", 123]},
                name="x",
                label="x",
                client_id="x",
                scope="openid",
            )

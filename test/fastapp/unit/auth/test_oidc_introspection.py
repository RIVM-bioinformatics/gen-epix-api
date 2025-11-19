import asyncio
from test.fastapp.auth_test_client import AuthTestClient
from typing import Any

import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.services.auth.model import OidcServerCfg
from gen_epix.fastapp.services.auth.oidc_client import OidcClient


class TestOidcIntrospection:

    client: OidcClient
    token: str

    @classmethod
    def setup_class(cls) -> None:
        env = AuthTestClient.get_test_client()
        for idp in env.auth_service.idp_clients:
            if isinstance(idp, OidcClient):
                cls.client = idp
                break
        else:  # no break
            pytest.skip("No OidcClient available")

        cls.token = env.MOCK_JWK_TOKEN.token
        cls._enable_introspection()

    @classmethod
    def _enable_introspection(cls) -> None:
        cls.client.server_cfg.enable_introspection = True
        cls.client.server_cfg.introspection_endpoint = "https://introspect.local/token"

    def _cache(self) -> dict[str, dict[str, Any]]:
        return getattr(self.client, "_introspection_cache")

    def _now(self) -> int:
        return getattr(self.client, "_now")()

    def test_introspection_populates_cache(self) -> None:
        counter: dict[str, int] = {"n": 0}

        def fake_introspect(_token: str) -> bool:
            counter["n"] += 1
            return True

        setattr(self.client, "_introspect_token_with_server", fake_introspect)

        claims = asyncio.run(self.client.get_claims_from_jwt(self.token))
        assert claims is not None
        assert counter["n"] == 1

        claims2 = asyncio.run(self.client.get_claims_from_jwt(self.token))
        assert claims2 is not None
        assert counter["n"] == 1

    def test_introspection_inactive_denies(self) -> None:
        now = self._now()
        self._cache()[self.token] = {
            "active": False,
            "last_checked": now,
            "exp": now + 600,
        }

        with pytest.raises(exc.CredentialsAuthError):
            asyncio.run(self.client.get_claims_from_jwt(self.token))

    def test_recheck_to_inactive_then_denies(self) -> None:
        now = self._now()
        interval = self.client.server_cfg.introspection_interval_seconds
        self._cache()[self.token] = {
            "active": True,
            "last_checked": now - (interval + 1),
            "exp": now + 600,
        }

        setattr(self.client, "_introspect_token_with_server", lambda _: False)

        with pytest.raises(exc.CredentialsAuthError):
            asyncio.run(self.client.get_claims_from_jwt(self.token))

    def test_introspection_failure(self) -> None:
        self._cache().pop(self.token, None)

        counter: dict[str, int] = {"n": 0}

        def fake_introspect(_token: str) -> None:
            counter["n"] += 1
            return None

        setattr(self.client, "_introspect_token_with_server", fake_introspect)

        with pytest.raises(exc.CredentialsAuthError):
            asyncio.run(self.client.get_claims_from_jwt(self.token))
        assert counter["n"] == 1

    def test_cache_expiry_prunes_and_triggers_recheck(self) -> None:
        now = self._now()
        self._cache()[self.token] = {
            "active": True,
            "last_checked": now - 10,
            "exp": now - 1,
        }

        counter: dict[str, int] = {"n": 0}

        def fake_introspect(_token: str) -> bool:
            counter["n"] += 1
            return True

        setattr(self.client, "_introspect_token_with_server", fake_introspect)

        claims = asyncio.run(self.client.get_claims_from_jwt(self.token))
        assert claims is not None
        assert counter["n"] == 1

        claims2 = asyncio.run(self.client.get_claims_from_jwt(self.token))
        assert claims2 is not None
        assert counter["n"] == 1

    def test_cached_active_within_interval_skips_recheck(self) -> None:
        now = self._now()
        self._cache()[self.token] = {
            "active": True,
            "last_checked": now,
            "exp": now + 600,
        }

        def fail_if_called(_token: str) -> None:
            raise AssertionError("introspection should not be called within interval")

        setattr(self.client, "_introspect_token_with_server", fail_if_called)

        claims = asyncio.run(self.client.get_claims_from_jwt(self.token))
        assert claims is not None

    def test_interval_elapsed_triggers_single_recheck(self) -> None:
        now = self._now()
        interval = self.client.server_cfg.introspection_interval_seconds
        self._cache()[self.token] = {
            "active": True,
            "last_checked": now - (interval + 1),
            "exp": now + 600,
        }

        counter: dict[str, int] = {"n": 0}

        def fake_introspect(_token: str) -> bool:
            counter["n"] += 1
            return True

        setattr(
            self.client,
            "_introspect_token_with_server",
            fake_introspect,
        )

        claims = asyncio.run(self.client.get_claims_from_jwt(self.token))
        assert claims is not None
        assert counter["n"] == 1

        claims2 = asyncio.run(self.client.get_claims_from_jwt(self.token))
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

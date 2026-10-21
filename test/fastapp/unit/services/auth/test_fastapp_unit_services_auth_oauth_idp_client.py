import asyncio
import base64
import json
import logging
import time
from test.fastapp.auth_test_client import AuthTestClient
from test.util.mock_compat import MagicMock, Mock, patch
from typing import Any
from uuid import UUID

import httpx
import jwt
import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import AuthProtocol, OAuthFlow
from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider, OidcServerCfg
from gen_epix.fastapp.services.auth.oauth_idp_client import OauthIdpClient
from gen_epix.fastapp.services.auth.token_introspection_manager import (
    TokenIntrospectionManager,
)

VALID_JWT_TOKEN = jwt.encode(
    {"sub": "u"}, "test-secret-key-with-at-least-32-bytes", algorithm="HS256"
)


class BaseOauthIdpClientTestCase:
    """Base test case with common fixtures and utilities for OauthIdpClient."""

    def setup_method(self) -> None:
        # Logger
        self.logger: Mock = Mock(spec=logging.Logger)
        self.logger.level = logging.DEBUG

        # Minimal valid discovery document
        self.discovery_doc: dict[str, Any] = {
            "issuer": "https://issuer.example.com",
            "authorization_endpoint": "https://issuer.example.com/auth",
            "token_endpoint": "https://issuer.example.com/token",
            "jwks_uri": "https://issuer.example.com/jwks",
            "userinfo_endpoint": "https://issuer.example.com/userinfo",
            "response_types_supported": ["code"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
        }

        # Server config factory
        self.server_cfg: OidcServerCfg = OidcServerCfg(
            name="TEST",
            label="Test IDP",
            discovery_url="https://issuer.example.com/.well-known/openid-configuration",
            client_id="client-id",
            client_secret="client-secret",
            scope="openid profile email",
            public=False,
            enable_introspection=False,
            audience=None,
            # Provide reasonable defaults used by public introspection helper
            introspection_interval_seconds=60,
            introspection_timeout_seconds=2,
            introspection_auth_method="client_secret_basic",
        )

    def create_client(
        self,
        *,
        cfg: OidcServerCfg | None = None,
        discovery_doc: dict[str, Any] | None = None,
        discovery_url: str | None = None,
        enable_introspection: bool = False,
        client_credential_flow_max_retries: int | None = None,
        client_credential_flow_base_delay: float | None = None,
    ) -> OauthIdpClient:
        """Create client with provided overrides."""
        cfg_copy: OidcServerCfg = (cfg or self.server_cfg).model_copy()
        cfg_copy.enable_introspection = enable_introspection
        doc_to_apply: dict[str, Any] | None = discovery_doc or self.discovery_doc

        # COMMENTED OUT: SEEMS NO LONGER NEEDED AND OTHERWISE BREAKS TESTS
        # If a discovery document is supplied but no explicit discovery_url override,
        # clear the cfg discovery_url to avoid unintended network calls during tests.
        # if doc_to_apply is not None and discovery_url is None:
        #     cfg_copy.discovery_url = None

        # During client construction, patch update_server_config_from_discovery so
        # __init__ doesn't perform network discovery. After construction, manually
        # apply the discovery doc to the client's config if provided. Explicit
        # calls to update_server_config_from_discovery in tests will use the real method.
        with patch.object(OauthIdpClient, "update_server_config_from_discovery") as upd:
            upd.return_value = None
            client: OauthIdpClient = OauthIdpClient(
                server_cfg=cfg_copy,
                logger=self.logger,
                discovery_doc=doc_to_apply,
                discovery_url=discovery_url,
                client_credential_flow_max_retries=client_credential_flow_max_retries,
                client_credential_flow_base_delay=client_credential_flow_base_delay,
            )
        if doc_to_apply:
            for key, value in doc_to_apply.items():
                setattr(client.server_cfg, key, value)
        return client

    def patch_httpx_client(self) -> tuple[patch, Mock]:  # type: ignore[valid-type]
        """Patch httpx.Client and return the patcher and the instance mock."""
        client_cm_mock: MagicMock = MagicMock()
        client_mock: Mock = Mock()
        client_cm_mock.__enter__.return_value = client_mock
        client_cm_mock.__exit__.return_value = None
        p: patch = patch(  # type: ignore[valid-type]
            "gen_epix.fastapp.services.auth.oauth_idp_client.httpx.Client",
            return_value=client_cm_mock,
        )
        return p, client_mock

    def now(self) -> int:
        return int(time.time())


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestInitAndConfig(BaseOauthIdpClientTestCase):
    """Tests for initialization and discovery configuration updates."""

    def test_init_with_discovery_doc_sets_model_and_properties(self) -> None:
        # 1. Input
        cfg: OidcServerCfg = self.server_cfg.model_copy()

        # 2. Mocks: none

        # 3. Execute
        client: OauthIdpClient = self.create_client(cfg=cfg)

        # 4. Verify
        assert client.issuer == self.discovery_doc["issuer"]
        assert client.scope == cfg.scope
        assert client.audience == cfg.client_id
        assert client.model is not None  # Security model (OAuth2) created

    def test_update_server_config_from_discovery_doc_only(self) -> None:
        # 1. Input
        cfg: OidcServerCfg = self.server_cfg.model_copy()
        cfg.discovery_url = None
        client: OauthIdpClient = self.create_client(
            cfg=cfg, discovery_doc=self.discovery_doc
        )

        # 2. Mocks: none

        # 3. Execute
        client.update_server_config_from_discovery(
            doc={"issuer": "https://x", "token_endpoint": "t"}
        )

        # 4. Verify: values updated from provided doc
        assert client.server_cfg.issuer == "https://x"
        assert client.server_cfg.token_endpoint == "t"

    def test_update_server_config_from_discovery_no_url_no_doc_raises(self) -> None:
        # 1. Input
        cfg: OidcServerCfg = self.server_cfg.model_copy()
        cfg.discovery_url = None
        client: OauthIdpClient = self.create_client(cfg=cfg, discovery_doc=None)

        # 2. Mocks: none

        # 3. Execute / 4. Verify
        with pytest.raises(exc.InitializationServiceError):
            client.update_server_config_from_discovery()

    def test_update_server_config_from_url_success_and_validation(self) -> None:
        # 1. Input
        cfg: OidcServerCfg = self.server_cfg.model_copy()
        client: OauthIdpClient = self.create_client(
            cfg=cfg, discovery_doc=None, discovery_url=cfg.discovery_url
        )

        # 2. Mocks
        p, client_mock = self.patch_httpx_client()
        response_mock: Mock = Mock()
        response_mock.json.return_value = self.discovery_doc
        response_mock.raise_for_status.return_value = None
        client_mock.get.return_value = response_mock

        # 3. Execute
        p.start()  # type: ignore[attr-defined]
        try:
            client.update_server_config_from_discovery(url=cfg.discovery_url)
        finally:
            p.stop()  # type: ignore[attr-defined]

        # 4. Verify
        assert client.server_cfg.issuer == self.discovery_doc["issuer"]
        assert (
            client.server_cfg.authorization_endpoint
            == self.discovery_doc["authorization_endpoint"]
        )
        client_mock.get.assert_called_once()

    def test_update_server_config_from_url_invalid_raises(self) -> None:
        # 1. Input
        bad_doc: dict[str, Any] = {
            # Missing required fields e.g. issuer
            "authorization_endpoint": "https://issuer.example.com/auth",
            "jwks_uri": "https://issuer.example.com/jwks",
            "response_types_supported": ["code"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
        }
        cfg: OidcServerCfg = self.server_cfg.model_copy()

        # 2. Mocks
        p, client_mock = self.patch_httpx_client()
        response_mock: Mock = Mock()
        response_mock.json.return_value = bad_doc
        response_mock.raise_for_status.return_value = None
        client_mock.get.return_value = response_mock

        # 3. Execute / 4. Verify
        # Patch before constructing the client to avoid injecting a valid discovery doc.
        p.start()  # type: ignore[attr-defined]
        try:
            # Construct the client directly (bypass helper) with no discovery_doc so
            # __init__ triggers URL-based discovery using the patched bad doc.
            with pytest.raises(exc.InitializationServiceError):
                OauthIdpClient(
                    server_cfg=cfg,
                    logger=self.logger,
                    discovery_doc=None,
                    discovery_url=cfg.discovery_url,
                )
        finally:
            p.stop()  # type: ignore[attr-defined]

    def test_update_server_config_from_url_http_error_logs_and_raises(self) -> None:
        # 1. Input
        cfg: OidcServerCfg = self.server_cfg.model_copy()
        client: OauthIdpClient = self.create_client(
            cfg=cfg, discovery_doc=None, discovery_url=cfg.discovery_url
        )

        # 2. Mocks
        p, client_mock = self.patch_httpx_client()
        client_mock.get.side_effect = RuntimeError("boom")

        # 3. Execute / 4. Verify
        p.start()  # type: ignore[attr-defined]
        try:
            with pytest.raises(exc.InitializationServiceError):
                client.update_server_config_from_discovery(url=cfg.discovery_url)
        finally:
            p.stop()  # type: ignore[attr-defined]
        assert self.logger.error.called is True


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestProperties(BaseOauthIdpClientTestCase):
    def test_audience_property_prefers_explicit_audience(self) -> None:
        # 1. Input
        cfg: OidcServerCfg = self.server_cfg.model_copy()
        cfg.audience = "api://aud"

        # 2. Execute
        client: OauthIdpClient = self.create_client(cfg=cfg)

        # 3. Verify
        assert client.audience == "api://aud"

    def test_audience_property_falls_back_to_client_id(self) -> None:
        # 1. Input
        cfg: OidcServerCfg = self.server_cfg.model_copy()
        cfg.audience = None

        # 2. Execute
        client: OauthIdpClient = self.create_client(cfg=cfg)

        # 3. Verify
        assert client.audience == cfg.client_id


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestJwkFetching(BaseOauthIdpClientTestCase):

    def test_get_jwk_from_jwt_parsing_error_raises(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()
        jwt_token = "raw.jwt.parsing-error-canary"

        # 2. Mocks
        with patch(
            "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.get_unverified_header"
        ) as get_hdr:
            get_hdr.side_effect = jwt.PyJWTError()

            # 3. Execute / 4. Verify
            with pytest.raises(exc.UnauthorizedAuthError):
                asyncio.run(client.get_jwk_from_jwt(jwt_token))
        warning = json.loads(self.logger.warning.call_args.args[0])
        assert warning["code"] == "4cff1367"
        assert warning["scheme_name"] == client.scheme_name
        assert "jwt" not in warning
        assert jwt_token not in json.dumps(warning)

    def test_get_jwk_from_jwt_missing_kid_raises(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()
        jwt_token = "raw.jwt.missing-kid-canary"

        # 2. Mocks
        with patch(
            "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.get_unverified_header"
        ) as get_hdr:
            get_hdr.return_value = {}

            # 3. Execute / 4. Verify
            with pytest.raises(exc.UnauthorizedAuthError):
                asyncio.run(client.get_jwk_from_jwt(jwt_token))
        warning = json.loads(self.logger.warning.call_args.args[0])
        assert warning["code"] == "0184bc35"
        assert warning["scheme_name"] == client.scheme_name
        assert "jwt" not in warning
        assert jwt_token not in json.dumps(warning)

    def test_get_jwk_from_jwt_loads_keys_and_finds_key(self) -> None:
        # 1. Input
        cfg: OidcServerCfg = self.server_cfg.model_copy()
        client: OauthIdpClient = self.create_client(cfg=cfg)

        # 2. Mocks
        with (
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.get_unverified_header"
            ) as get_hdr,
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.httpx.Client"
            ) as httpx_client,
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.PyJWK.from_dict"
            ) as from_dict,
        ):
            get_hdr.return_value = {"kid": "k1"}
            # Mock JWKS response with both valid and ignored keys
            client_cm: MagicMock = MagicMock()
            http_client: Mock = Mock()
            client_cm.__enter__.return_value = http_client
            httpx_client.return_value = client_cm
            response_mock: Mock = Mock()
            response_mock.json.return_value = {
                "keys": [
                    {"kid": "k1", "use": "sig", "kty": "RSA"},
                    {"kid": "k2", "use": "enc", "kty": "RSA"},
                ]
            }
            response_mock.raise_for_status.return_value = None
            http_client.get.return_value = response_mock
            jwk_obj: object = object()
            from_dict.side_effect = [jwk_obj]

            # 3. Execute
            key = asyncio.run(client.get_jwk_from_jwt("token"))

            # 4. Verify
            assert key is jwk_obj
            http_client.get.assert_called_once_with(self.discovery_doc["jwks_uri"])

    def test_get_jwk_from_jwt_keys_not_found_after_loading_raises(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()

        # 2. Mocks: header kid unknown, JWKS returns empty
        with (
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.get_unverified_header"
            ) as get_hdr,
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.httpx.Client"
            ) as httpx_client,
        ):
            get_hdr.return_value = {"kid": "missing"}
            client_cm: MagicMock = MagicMock()
            http_client: Mock = Mock()
            client_cm.__enter__.return_value = http_client
            httpx_client.return_value = client_cm
            response_mock: Mock = Mock()
            response_mock.json.return_value = {"keys": []}
            response_mock.raise_for_status.return_value = None
            http_client.get.return_value = response_mock

            # 3. Execute / 4. Verify
            with pytest.raises(exc.UnauthorizedAuthError):
                asyncio.run(client.get_jwk_from_jwt("token"))

    def test_get_jwk_from_jwt_load_keys_http_error_propagates(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()

        # 2. Mocks: cause _load_keys to raise
        with (
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.get_unverified_header"
            ) as get_hdr,
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.httpx.Client"
            ) as httpx_client,
        ):
            get_hdr.return_value = {"kid": "k1"}
            client_cm: MagicMock = MagicMock()
            http_client: Mock = Mock()
            client_cm.__enter__.return_value = http_client
            httpx_client.return_value = client_cm
            http_client.get.side_effect = RuntimeError("boom")

            # 3. Execute / 4. Verify
            with pytest.raises(exc.ServiceUnavailableError):
                asyncio.run(client.get_jwk_from_jwt("token"))


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestClaimsFromJwt(BaseOauthIdpClientTestCase):

    def test_get_claims_from_malformed_jwt_raises_credentials(self) -> None:
        client: OauthIdpClient = self.create_client()

        with pytest.raises(exc.CredentialsAuthError):
            asyncio.run(client.get_claims_from_jwt("invalid-token"))

    def test_get_claims_from_jwt_issuer_mismatch_returns_none(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()

        # 2. Mocks: signature verification succeeds, but the issuer differs.
        verified_claims: dict[str, Any] = {
            "iss": "https://other",
            "sub": "u",
            "exp": 9999999999,
            "iat": 1,
        }
        with (
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.decode",
                return_value=verified_claims,
            ),
            patch.object(OauthIdpClient, "get_jwk_from_jwt", return_value=Mock()),
        ):

            # 3. Execute
            result = asyncio.run(client.get_claims_from_jwt(VALID_JWT_TOKEN))

        # 4. Verify
        assert result is None

    def test_get_claims_from_jwt_decode_expired_signature_error_raises_credentials(
        self,
    ) -> None:
        """Test decode raises ExpiredSignatureError and triggers CredentialsAuthError."""
        client: OauthIdpClient = self.create_client()

        with (
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.decode",
                side_effect=__import__("jwt").ExpiredSignatureError("expired"),
            ),
            patch.object(
                OauthIdpClient, "get_jwk_from_jwt", return_value=Mock()
            ) as get_key,
        ):
            with pytest.raises(exc.CredentialsAuthError):
                asyncio.run(client.get_claims_from_jwt(VALID_JWT_TOKEN))
            assert get_key.called is True

    def test_get_claims_from_jwt_decode_pyjwt_error_raises_credentials(
        self,
    ) -> None:
        """Test decode raises PyJWTError and triggers CredentialsAuthError."""
        client: OauthIdpClient = self.create_client()

        with (
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.decode",
                side_effect=__import__("jwt").PyJWTError("invalid"),
            ),
            patch.object(
                OauthIdpClient, "get_jwk_from_jwt", return_value=Mock()
            ) as get_key,
        ):
            with pytest.raises(exc.CredentialsAuthError):
                asyncio.run(client.get_claims_from_jwt(VALID_JWT_TOKEN))
            assert get_key.called is True

    def test_get_claims_from_jwt_decode_runtime_error_raises_credentials(
        self,
    ) -> None:
        """Test decode raises RuntimeError and triggers CredentialsAuthError."""
        client: OauthIdpClient = self.create_client()

        with (
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.decode",
                side_effect=RuntimeError("other"),
            ),
            patch.object(
                OauthIdpClient, "get_jwk_from_jwt", return_value=Mock()
            ) as get_key,
        ):
            with pytest.raises(exc.CredentialsAuthError):
                asyncio.run(client.get_claims_from_jwt(VALID_JWT_TOKEN))
            assert get_key.called is True

    def test_get_claims_from_jwt_missing_required_claims_raise(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()

        # 2. Mocks: signature verification succeeds, but the subject is missing.
        with (
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.decode",
                return_value={
                    "iss": self.discovery_doc["issuer"],
                    "sub": None,
                    "exp": 9999999999,
                    "iat": 1,
                },
            ),
            patch.object(OauthIdpClient, "get_jwk_from_jwt", return_value=Mock()),
        ):
            # 3. Execute / 4. Verify
            with pytest.raises(exc.CredentialsAuthError):
                asyncio.run(client.get_claims_from_jwt(VALID_JWT_TOKEN))

    def test_get_claims_from_jwt_success_with_claim_map_and_introspection(
        self,
    ) -> None:
        # 1. Input
        cfg: OidcServerCfg = self.server_cfg.model_copy()
        cfg.claim_map = {"email": ["email", "upn"]}

        # 2. Mocks
        tim_mock: Mock = Mock()
        with patch(
            "gen_epix.fastapp.services.auth.oauth_idp_client.TokenIntrospectionManager",
            return_value=tim_mock,
        ):
            client: OauthIdpClient = self.create_client(
                cfg=cfg, enable_introspection=True
            )

        claims_verified: dict[str, Any] = {
            "iss": self.discovery_doc["issuer"],
            "sub": "u",
            "upn": "user@example.com",
            "exp": 9999999999,
            "iat": 1,
        }

        with (
            patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.jwt.decode",
                return_value=claims_verified,
            ),
            patch.object(OauthIdpClient, "get_jwk_from_jwt", return_value=Mock()),
        ):
            # 3. Execute
            result = asyncio.run(client.get_claims_from_jwt(VALID_JWT_TOKEN))

        # 4. Verify
        assert result is not None
        assert result["email"] == "user@example.com"
        tim_mock.introspect_token.assert_called_once()


@pytest.mark.scenario_ids(
    "TC-SEC-25-01", "TC-SEC-25-02", "TC-SEC-28-01", "TC-OWA-07-07"
)
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
        else:
            pytest.skip("No OidcClient available")

        cls.TOKEN = env.MOCK_JWK_TOKEN.token
        cls._enable_introspection()

    @classmethod
    def _enable_introspection(cls) -> None:
        cls.CLIENT.server_cfg.enable_introspection = True
        if not hasattr(cls.CLIENT, "token_introspection_manger") or (
            getattr(cls.CLIENT, "token_introspection_manger") is None
        ):
            cls.CLIENT.token_introspection_manager = TokenIntrospectionManager(
                server_cfg=cls.CLIENT.server_cfg,
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
            setattr(
                cls.CLIENT.token_introspection_manager,
                "_get_cached_introspection_endpoint",
                lambda: "https://introspect.local/token",
            )

    def _cache(self) -> dict[str, dict[str, Any]]:
        return getattr(self.CLIENT.token_introspection_manager, "_introspection_cache")

    def _now(self) -> int:
        return getattr(self.CLIENT.token_introspection_manager, "_now")()

    def test_introspection_populates_cache(self) -> None:
        counter: dict[str, int] = {"n": 0}

        def fake_introspect(_token: str) -> bool:
            counter["n"] += 1
            return True

        setattr(
            self.CLIENT.token_introspection_manager,
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
            self.CLIENT.token_introspection_manager._introspection_interval_seconds
        )
        self._cache()[self.TOKEN] = {
            "active": True,
            "last_checked": now - (interval + 1),
            "exp": now + 600,
        }

        setattr(
            self.CLIENT.token_introspection_manager,
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
            self.CLIENT.token_introspection_manager,
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
            self.CLIENT.token_introspection_manager,
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
            self.CLIENT.token_introspection_manager,
            "_introspect_token_with_server",
            fail_if_called,
        )

        claims = asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))
        assert claims is not None

    def test_interval_elapsed_triggers_single_recheck(self) -> None:
        now = self._now()
        interval = (
            self.CLIENT.token_introspection_manager._introspection_interval_seconds
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
            self.CLIENT.token_introspection_manager,
            "_introspect_token_with_server",
            fake_introspect,
        )

        claims = asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))
        assert claims is not None
        assert counter["n"] == 1

        claims2 = asyncio.run(self.CLIENT.get_claims_from_jwt(self.TOKEN))
        assert claims2 is not None
        assert counter["n"] == 1


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestClientCredentialsFlow(BaseOauthIdpClientTestCase):
    def test_client_credentials_success_single_attempt(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()

        # 2. Mocks
        p, http_client = self.patch_httpx_client()
        response_mock: Mock = Mock()
        response_mock.json.return_value = {"access_token": "TKN"}
        response_mock.raise_for_status.return_value = None
        http_client.post.return_value = response_mock

        # 3. Execute
        p.start()  # type: ignore[attr-defined]
        try:
            token: str = client.retrieve_jwt_with_client_credentials_flow("s1 s2")
        finally:
            p.stop()  # type: ignore[attr-defined]

        # 4. Verify
        assert token == "TKN"
        args, kwargs = http_client.post.call_args
        assert "Authorization" in kwargs["headers"]
        assert (
            base64.b64decode(kwargs["headers"]["Authorization"][6:]).decode()
            == "client-id:client-secret"
        )
        assert kwargs["headers"]["Content-Type"] == "application/x-www-form-urlencoded"
        assert kwargs["data"].startswith("grant_type=client_credentials")

    def test_client_credentials_custom_headers_and_scope(self) -> None:
        client: OauthIdpClient = self.create_client()
        p, http_client = self.patch_httpx_client()
        response_mock: Mock = Mock()
        response_mock.json.return_value = {"access_token": "TKN"}
        response_mock.raise_for_status.return_value = None
        http_client.post.return_value = response_mock

        p.start()  # type: ignore[attr-defined]
        try:
            token = client.retrieve_jwt_with_client_credentials_flow(
                "custom_scope",
                headers={"Custom-Header": "test-value"},
                max_retries=5,
                base_delay=2.0,
            )
        finally:
            p.stop()  # type: ignore[attr-defined]

        assert token == "TKN"
        args, kwargs = http_client.post.call_args
        assert kwargs["headers"]["Custom-Header"] == "test-value"
        assert "scope=custom_scope" in kwargs["data"]

    def test_client_credentials_returns_advertised_expiry(self) -> None:
        client: OauthIdpClient = self.create_client()
        p, http_client = self.patch_httpx_client()
        response_mock: Mock = Mock()
        response_mock.json.return_value = {"access_token": "TKN", "expires_in": 3600}
        response_mock.raise_for_status.return_value = None
        http_client.post.return_value = response_mock

        p.start()  # type: ignore[attr-defined]
        try:
            result = client.retrieve_jwt_with_client_credentials_flow_and_expiry(
                "s1 s2"
            )
        finally:
            p.stop()  # type: ignore[attr-defined]

        assert result == ("TKN", 3600.0)

    @pytest.mark.parametrize(
        "expires_in_json",
        ["Infinity", "-Infinity", "NaN"],
        ids=["positive-infinity", "negative-infinity", "nan"],
    )
    def test_client_credentials_does_not_advertise_non_finite_expiry(
        self, expires_in_json: str
    ) -> None:
        client: OauthIdpClient = self.create_client()
        p, http_client = self.patch_httpx_client()
        response_mock: Mock = Mock()
        response_mock.json.return_value = json.loads(
            f'{{"access_token":"TKN","expires_in":{expires_in_json}}}'
        )
        response_mock.raise_for_status.return_value = None
        http_client.post.return_value = response_mock

        p.start()  # type: ignore[attr-defined]
        try:
            result = client.retrieve_jwt_with_client_credentials_flow_and_expiry(
                "s1 s2"
            )
        finally:
            p.stop()  # type: ignore[attr-defined]

        assert result == ("TKN", None)

    def test_client_credentials_missing_endpoint_raises(self) -> None:
        # 1. Input
        cfg: OidcServerCfg = self.server_cfg.model_copy()
        cfg.token_endpoint = None
        client: OauthIdpClient = self.create_client(cfg=cfg)

        # 2. Mocks
        with patch.object(OauthIdpClient, "update_server_config_from_discovery") as upd:
            # No endpoint after update
            client.server_cfg.token_endpoint = None

            # 3. Execute / 4. Verify
            with pytest.raises(
                exc.ServiceUnavailableError, match="Token endpoint URL is not set"
            ):
                client.retrieve_jwt_with_client_credentials_flow("s")
            assert upd.called is True

    def test_client_credentials_retries_then_fails(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()

        # 2. Mocks
        p, http_client = self.patch_httpx_client()
        http_client.post.side_effect = [
            RuntimeError("e1"),
            RuntimeError("e2"),
            RuntimeError("e3"),
        ]

        # 3. Execute / 4. Verify
        p.start()  # type: ignore[attr-defined]
        try:
            with patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.time.sleep"
            ) as sleep_mock:
                with pytest.raises(exc.ServiceUnavailableError):
                    client.retrieve_jwt_with_client_credentials_flow(
                        "scope", max_retries=2, base_delay=0.0
                    )
                assert sleep_mock.call_args_list == [((0.0,),), ((0.0,),)]
        finally:
            p.stop()  # type: ignore[attr-defined]
        assert self.logger.error.called is True

    def test_client_credentials_retries_http_status_errors(self) -> None:
        client: OauthIdpClient = self.create_client()
        p, http_client = self.patch_httpx_client()
        response_mock: Mock = Mock()
        response_mock.status_code = 500
        response_mock.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=response_mock
        )
        http_client.post.return_value = response_mock

        p.start()  # type: ignore[attr-defined]
        try:
            with patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.time.sleep"
            ) as sleep_mock:
                with pytest.raises(exc.ServiceUnavailableError):
                    client.retrieve_jwt_with_client_credentials_flow(
                        "scope", max_retries=2, base_delay=0.0
                    )
                assert http_client.post.call_count == 3
                assert sleep_mock.call_count == 2
        finally:
            p.stop()  # type: ignore[attr-defined]

    def test_client_credentials_retries_network_errors(self) -> None:
        client: OauthIdpClient = self.create_client()
        p, http_client = self.patch_httpx_client()
        http_client.post.side_effect = httpx.ConnectError("Connection failed")

        p.start()  # type: ignore[attr-defined]
        try:
            with patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.time.sleep"
            ) as sleep_mock:
                with pytest.raises(exc.ServiceUnavailableError):
                    client.retrieve_jwt_with_client_credentials_flow(
                        "scope", max_retries=1, base_delay=0.0
                    )
                assert http_client.post.call_count == 2
                assert sleep_mock.call_count == 1
        finally:
            p.stop()  # type: ignore[attr-defined]

    def test_client_credentials_missing_access_token_raises(self) -> None:
        client: OauthIdpClient = self.create_client()
        p, http_client = self.patch_httpx_client()
        response_mock: Mock = Mock()
        response_mock.json.return_value = {"error": "invalid_request"}
        response_mock.raise_for_status.return_value = None
        http_client.post.return_value = response_mock

        p.start()  # type: ignore[attr-defined]
        try:
            with patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.time.sleep"
            ) as sleep_mock:
                with pytest.raises(exc.ServiceUnavailableError):
                    client.retrieve_jwt_with_client_credentials_flow(
                        "scope", max_retries=0, base_delay=0.0
                    )
                assert http_client.post.call_count == 1
                sleep_mock.assert_not_called()
        finally:
            p.stop()  # type: ignore[attr-defined]

    def test_zero_retries_makes_one_attempt_without_backoff(self) -> None:
        client: OauthIdpClient = self.create_client()
        p, http_client = self.patch_httpx_client()
        http_client.post.side_effect = RuntimeError("unavailable")

        p.start()  # type: ignore[attr-defined]
        try:
            with patch(
                "gen_epix.fastapp.services.auth.oauth_idp_client.time.sleep"
            ) as sleep_mock:
                with pytest.raises(exc.ServiceUnavailableError):
                    client.retrieve_jwt_with_client_credentials_flow(
                        "scope", max_retries=0, base_delay=0.0
                    )
                assert http_client.post.call_count == 1
                sleep_mock.assert_not_called()
        finally:
            p.stop()  # type: ignore[attr-defined]

    def test_zero_retry_and_delay_defaults_are_preserved(self) -> None:
        client: OauthIdpClient = self.create_client(
            client_credential_flow_max_retries=0,
            client_credential_flow_base_delay=0.0,
        )

        assert client._client_credential_flow_max_retries == 0
        assert client._client_credential_flow_base_delay == 0.0


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestUserInfo(BaseOauthIdpClientTestCase):
    def test_get_claims_from_userinfo_success(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()

        # 2. Mocks
        p, http_client = self.patch_httpx_client()
        response_mock: Mock = Mock()
        response_mock.content = json.dumps({"x": 1}).encode()
        http_client.get.return_value = response_mock

        # 3. Execute
        p.start()  # type: ignore[attr-defined]
        try:
            claims: dict[str, Any] = client.get_claims_from_userinfo("AT")
        finally:
            p.stop()  # type: ignore[attr-defined]

        # 4. Verify
        assert claims == {"x": 1}
        args, kwargs = http_client.get.call_args
        assert kwargs["headers"]["Authorization"].startswith("Bearer ")

    def test_get_claims_from_userinfo_error_returns_empty(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()

        # 2. Mocks: claims contain error key
        p, http_client = self.patch_httpx_client()
        response_mock: Mock = Mock()
        response_mock.content = json.dumps({"error": "Invalid"}).encode()
        http_client.get.return_value = response_mock

        # 3. Execute
        p.start()  # type: ignore[attr-defined]
        try:
            claims: dict[str, Any] = client.get_claims_from_userinfo("AT")
        finally:
            p.stop()  # type: ignore[attr-defined]

        # 4. Verify
        assert claims == {}

        # 2b. HTTP error
        p2, http_client2 = self.patch_httpx_client()
        http_client2.get.side_effect = RuntimeError("boom")
        p2.start()  # type: ignore[attr-defined]
        try:
            claims2: dict[str, Any] = client.get_claims_from_userinfo("AT")
        finally:
            p2.stop()  # type: ignore[attr-defined]
        assert claims2 == {}


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestIdentityProvider(BaseOauthIdpClientTestCase):
    def test_get_identity_provider_fields(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client(
            discovery_url=self.server_cfg.discovery_url
        )

        # 2. Execute
        idp: IdentityProvider = client.get_identity_provider()

        # 3. Verify
        assert idp.name == self.server_cfg.name
        assert idp.label == self.server_cfg.label
        assert idp.client_id == self.server_cfg.client_id
        assert idp.client_secret == self.server_cfg.client_secret
        assert idp.discovery_url == self.server_cfg.discovery_url
        assert idp.issuer == self.discovery_doc["issuer"]
        assert idp.auth_protocol == AuthProtocol.OIDC
        assert idp.oauth_flow == OAuthFlow.AUTHORIZATION_CODE
        assert idp.scope == self.server_cfg.scope
        assert idp.public is False


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestCall(BaseOauthIdpClientTestCase):
    def test_call_no_authorization_header_returns_none(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()

        request = Mock()
        request.headers = {}

        # 2. Execute
        result = asyncio.run(client(request))

        # 3. Verify
        assert result is None

    def test_call_wrong_scheme_returns_none(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()
        request = Mock()
        request.headers = {"authorization": "Basic abc"}

        # 2. Execute
        result = asyncio.run(client(request))

        # 3. Verify
        assert result is None

    def test_call_bearer_with_valid_claims_returns_claims_model(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()
        token: str = "tok"
        request = Mock()
        request.headers = {"authorization": f"Bearer {token}"}

        # 2. Mocks
        claims_out: dict[str, Any] = {"iss": self.discovery_doc["issuer"], "sub": "u"}
        with patch.object(
            OauthIdpClient, "get_claims_from_jwt", return_value=claims_out
        ):
            # 3. Execute
            result = asyncio.run(client(request))

        # 4. Verify
        assert isinstance(result, Claims)
        assert result.scheme.lower() == "bearer"
        assert result.token == token
        assert isinstance(result.idp_client_id, UUID)

    def test_call_bearer_with_none_claims_returns_none(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()
        request = Mock()
        request.headers = {"authorization": "Bearer x"}

        # 2. Mocks
        with patch.object(OauthIdpClient, "get_claims_from_jwt", return_value=None):
            # 3. Execute
            result = asyncio.run(client(request))

        # 4. Verify
        assert result is None

    def test_call_bearer_with_auth_exception_returns_none(self) -> None:
        # 1. Input
        client: OauthIdpClient = self.create_client()
        request = Mock()
        request.headers = {"authorization": "Bearer x"}

        # 2. Mocks
        with patch.object(
            OauthIdpClient,
            "get_claims_from_jwt",
            side_effect=exc.CredentialsAuthError("code", "message"),
        ):
            # 3. Execute
            result = asyncio.run(client(request))

        # 4. Verify
        assert result is None

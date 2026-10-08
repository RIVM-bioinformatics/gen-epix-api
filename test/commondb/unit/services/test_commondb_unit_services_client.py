"""Unit tests for CommondbClient class.

Tests cover initialization, authentication/authorization handling, header
management, local/remote app creation, and HTTP timeout configuration.
Tests use mock objects to avoid external dependencies and OS integration.

Pattern note: This test module follows the existing remote app test patterns
from test/fastapp/unit/test_client.py, adapted for the CommondbClient
subclass and its domain-specific initialization.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from test.util.mock_compat import MagicMock, Mock, patch
from typing import Any, cast
from uuid import uuid4

import httpx
import jwt
import pytest

import gen_epix.commondb.services.client as commondb_client_module
from gen_epix import fastapp
from gen_epix.commondb.domain import DOMAIN, command, model
from gen_epix.commondb.services.client import CommondbClient
from gen_epix.fastapp import Client, exc
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import AuthProtocol, HttpProtocol, OAuthFlow
from gen_epix.fastapp.model import Command, Permission

_JWT_TEST_HS256_SECRET = "commondb-remote-app-test-secret-key-32b"

# ============================================================================
# Test Helpers and Dummy Classes
# ============================================================================


class DummyCommand(Command):
    """Minimal command for testing."""

    NAME = "DummyCommand"

    def __init__(self) -> None:
        super().__init__()


class DerivedClient(CommondbClient):
    """Minimal subclass of CommondbClient for testing timeout configuration."""

    # Configure timeouts per command type for testing
    DEFAULT_HTTP_TIMEOUTS: dict[type[Command], float] = {
        DummyCommand: 30.0,
    }


# ============================================================================
# Base Test Case with Common Setup
# ============================================================================


class BaseCommondbClientTestCase:
    """Base test case with common fixtures and setup for CommondbClient."""

    def setup_method(self) -> None:
        """Set up test fixtures by mocking dependencies to avoid side effects."""

        # Patch App.__init__ to avoid side-effects and set required attributes
        def _fake_app_init(self: Any, domain: Domain, **kwargs: Any) -> None:
            setattr(self, "_domain", domain)
            setattr(self, "_logger", None)
            setattr(self, "_command_handler_map", {})

        self._app_init_patcher = patch(
            "gen_epix.fastapp.client.App.__init__", _fake_app_init
        )
        self._app_init_patcher.start()

        # Patch create_ssl_context to return predictable value
        self._ssl_patcher = patch(
            "gen_epix.fastapp.client.create_ssl_context", return_value="SSLCTX"
        )
        self._ssl_patcher.start()

        # Domain stub
        self.domain: Domain = cast(Domain, Mock(spec=Domain))
        self.domain.crud_commands = []  # type: ignore[assignment,misc]

    def teardown_method(self) -> None:
        """Clean up patches."""
        self._app_init_patcher.stop()
        self._ssl_patcher.stop()


# ============================================================================
# Initialization and Defaults Tests
# ============================================================================


@pytest.mark.scenario_ids("TC-LSP-3238-01")
class TestInitialization(BaseCommondbClientTestCase):
    """Test CommondbClient initialization with various configurations."""

    def test_init_with_none_auth_protocol_enum(self) -> None:
        """Initialize with NONE auth protocol as enum."""
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
        )
        assert app._auth_protocol == AuthProtocol.NONE
        assert app._oauth_idp_client is None

    def test_init_with_none_auth_protocol_string(self) -> None:
        """Initialize with NONE auth protocol as string."""
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol="NONE",
        )
        assert app._auth_protocol == AuthProtocol.NONE
        assert app._oauth_idp_client is None

    def test_init_with_oauth2_auth_protocol_enum(self) -> None:
        """Initialize with OAUTH2 auth protocol as enum."""
        with patch(
            "gen_epix.commondb.services.client.OauthIdpClient"
        ) as mock_idp_class:
            app = CommondbClient(
                domain=self.domain,
                host="example.org",
                port=8000,
                auth_protocol=AuthProtocol.OAUTH2,
                oauth_discovery_url="https://idp.example.org/.well-known/openid-configuration",
                oauth_client_id="client123",
                oauth_client_secret="secret123",
                oauth_scope="openid profile",
            )
            assert app._auth_protocol == AuthProtocol.OAUTH2
            assert app._oauth_idp_client is not None
            mock_idp_class.assert_called_once()

    def test_init_with_oauth2_auth_protocol_string(self) -> None:
        """Initialize with OAUTH2 auth protocol as string."""
        with patch(
            "gen_epix.commondb.services.client.OauthIdpClient"
        ) as mock_idp_class:
            app = CommondbClient(
                domain=self.domain,
                host="example.org",
                port=8000,
                auth_protocol="OAUTH2",
                oauth_discovery_url="https://idp.example.org/.well-known/openid-configuration",
                oauth_client_id="client123",
                oauth_client_secret="secret123",
                oauth_scope="openid profile",
            )
            assert app._auth_protocol == AuthProtocol.OAUTH2
            mock_idp_class.assert_called_once()

    def test_init_with_oauth_flow_enum(self) -> None:
        """Initialize with OAuthFlow as enum."""
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
            oauth_flow=OAuthFlow.CLIENT_CREDENTIALS,
        )
        assert app._oauth_flow == OAuthFlow.CLIENT_CREDENTIALS

    def test_init_with_oauth_flow_string(self) -> None:
        """Initialize with OAuthFlow as string."""
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
            oauth_flow="CLIENT_CREDENTIALS",
        )
        assert app._oauth_flow == OAuthFlow.CLIENT_CREDENTIALS

    def test_init_default_route_prefix(self) -> None:
        """Verify default route prefix is /v1."""
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
        )
        assert app._default_route_prefix == "/v1"

    def test_init_custom_route_prefix(self) -> None:
        """Use custom route prefix if provided."""
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
            default_route_prefix="/api/v2",
        )
        assert app._default_route_prefix == "/api/v2"

    def test_init_default_oauth_token_refresh_margin(self) -> None:
        """Verify default OAuth token refresh margin is 60 seconds."""
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
        )
        assert app._oauth_token_refresh_margin == 60

    def test_init_custom_oauth_token_refresh_margin(self) -> None:
        """Use custom OAuth token refresh margin if provided."""
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
            oauth_token_refresh_margin=120,
        )
        assert app._oauth_token_refresh_margin == 120

    def test_init_zero_oauth_token_refresh_margin(self) -> None:
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
            oauth_token_refresh_margin=0,
        )
        assert app._oauth_token_refresh_margin == 0


# ============================================================================
# OAuth2 Validation Tests (Missing Configuration)
# ============================================================================


@pytest.mark.scenario_ids("TC-LSP-3238-02")
class TestOAuth2Validation(BaseCommondbClientTestCase):
    """Test OAuth2 configuration validation during initialization."""

    def test_oauth2_missing_discovery_url(self) -> None:
        """Raise error when OAuth2 requires discovery URL."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbClient(
                domain=self.domain,
                host="example.org",
                port=8000,
                auth_protocol=AuthProtocol.OAUTH2,
                oauth_client_id="client123",
                oauth_client_secret="secret123",
                oauth_scope="openid profile",
            )
        assert "OAuth discovery endpoint" in str(exc_info.value)

    def test_oauth2_missing_client_id(self) -> None:
        """Raise error when OAuth2 requires client ID."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbClient(
                domain=self.domain,
                host="example.org",
                port=8000,
                auth_protocol=AuthProtocol.OAUTH2,
                oauth_discovery_url="https://idp.example.org/.well-known/openid-configuration",
                oauth_client_secret="secret123",
                oauth_scope="openid profile",
            )
        assert "OAuth client ID" in str(exc_info.value)

    def test_oauth2_missing_scope(self) -> None:
        """Raise error when OAuth2 requires scope."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbClient(
                domain=self.domain,
                host="example.org",
                port=8000,
                auth_protocol=AuthProtocol.OAUTH2,
                oauth_discovery_url="https://idp.example.org/.well-known/openid-configuration",
                oauth_client_id="client123",
                oauth_client_secret="secret123",
            )
        assert "OAuth scope" in str(exc_info.value)

    def test_unsupported_auth_protocol(self) -> None:
        """Raise error for OIDC auth protocol (not yet supported)."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbClient(
                domain=self.domain,
                host="example.org",
                port=8000,
                auth_protocol=AuthProtocol.OIDC,
            )
        assert "not supported" in str(exc_info.value)


# ============================================================================
# Header Management Tests
# ============================================================================


@pytest.mark.scenario_ids("TC-LSP-3238-03")
class TestGetHeaders(BaseCommondbClientTestCase):
    """Test get_headers method for different auth protocols."""

    def test_get_headers_with_none_auth_protocol(self) -> None:
        """get_headers returns default headers with NONE protocol."""
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
            default_headers={"X-Custom": "value"},
        )
        cmd = DummyCommand()
        headers = app.get_headers(cmd)
        assert headers == {"X-Custom": "value"}

    def test_get_headers_rejects_unsupported_auth_protocol(self) -> None:
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
        )
        app._auth_protocol = AuthProtocol.OIDC

        with pytest.raises(exc.InitializationServiceError, match="not supported"):
            app.get_headers(DummyCommand())

    def test_get_headers_caches_token(self) -> None:
        """get_headers caches token when not expired."""
        # Create mock OauthIdpClient
        mock_idp_client = Mock()

        # Create JWT token that expires in the future
        exp_time = int(datetime.now(timezone.utc).timestamp()) + 3600
        jwt_token = jwt.encode(
            {"exp": exp_time}, _JWT_TEST_HS256_SECRET, algorithm="HS256"
        )

        mock_idp_client.retrieve_jwt_with_client_credentials_flow_and_expiry.return_value = (
            jwt_token,
            3600.0,
        )

        with patch(
            "gen_epix.commondb.services.client.OauthIdpClient"
        ) as mock_idp_class:
            mock_idp_class.return_value = mock_idp_client

            app = CommondbClient(
                domain=self.domain,
                host="example.org",
                port=8000,
                auth_protocol=AuthProtocol.OAUTH2,
                oauth_discovery_url="https://idp.example.org/.well-known/openid-configuration",
                oauth_client_id="client123",
                oauth_client_secret="secret123",
                oauth_scope="openid profile",
            )

            cmd = DummyCommand()

            # First call retrieves token
            headers1 = app.get_headers(cmd)
            assert "Authorization" in headers1
            assert headers1["Authorization"] == f"Bearer {jwt_token}"
            call_count1 = (
                mock_idp_client.retrieve_jwt_with_client_credentials_flow_and_expiry.call_count
            )

            # Second call uses cached token
            headers2 = app.get_headers(cmd)
            assert headers2 == headers1
            # Call count should not increase (token was cached)
            call_count2 = (
                mock_idp_client.retrieve_jwt_with_client_credentials_flow_and_expiry.call_count
            )
            assert call_count2 == call_count1

    def test_get_headers_refreshes_token_within_refresh_margin(self) -> None:
        """Refresh a token whose lifetime is shorter than the refresh margin."""
        mock_idp_client = Mock()
        mock_idp_client.retrieve_jwt_with_client_credentials_flow_and_expiry.side_effect = [
            ("short-lived-token", 10.0),
            ("long-lived-token", 3600.0),
        ]

        with patch(
            "gen_epix.commondb.services.client.OauthIdpClient"
        ) as mock_idp_class:
            mock_idp_class.return_value = mock_idp_client

            app = CommondbClient(
                domain=self.domain,
                host="example.org",
                port=8000,
                auth_protocol=AuthProtocol.OAUTH2,
                oauth_discovery_url="https://idp.example.org/.well-known/openid-configuration",
                oauth_client_id="client123",
                oauth_client_secret="secret123",
                oauth_scope="openid profile",
                oauth_token_refresh_margin=50,  # Margin is 50 seconds
            )

            cmd = DummyCommand()

            # The short-lived token is returned, but is not reusable within
            # the configured refresh margin.
            headers1 = app.get_headers(cmd)
            assert headers1["Authorization"] == "Bearer short-lived-token"

            # The next call refreshes it and the long-lived token is cached.
            headers2 = app.get_headers(cmd)
            assert headers2["Authorization"] == "Bearer long-lived-token"
            assert app.get_headers(cmd) == headers2
            assert (
                mock_idp_client.retrieve_jwt_with_client_credentials_flow_and_expiry.call_count
                == 2
            )

    def test_get_headers_handles_token_without_expiration(self) -> None:
        """get_headers does not cache a token with no reported lifetime."""
        mock_idp_client = Mock()
        jwt_token = "token-without-lifetime"
        mock_idp_client.retrieve_jwt_with_client_credentials_flow_and_expiry.return_value = (
            jwt_token,
            None,
        )

        with patch(
            "gen_epix.commondb.services.client.OauthIdpClient"
        ) as mock_idp_class:
            mock_idp_class.return_value = mock_idp_client

            app = CommondbClient(
                domain=self.domain,
                host="example.org",
                port=8000,
                auth_protocol=AuthProtocol.OAUTH2,
                oauth_discovery_url="https://idp.example.org/.well-known/openid-configuration",
                oauth_client_id="client123",
                oauth_client_secret="secret123",
                oauth_scope="openid profile",
            )

            cmd = DummyCommand()

            # First call should succeed
            headers = app.get_headers(cmd)
            assert "Authorization" in headers
            assert headers["Authorization"] == f"Bearer {jwt_token}"
            call_count_1 = (
                mock_idp_client.retrieve_jwt_with_client_credentials_flow_and_expiry.call_count
            )

            # Unknown lifetime means the client requests a fresh token.
            headers2 = app.get_headers(cmd)
            assert headers2 == headers
            # The token endpoint was called again.
            call_count_2 = (
                mock_idp_client.retrieve_jwt_with_client_credentials_flow_and_expiry.call_count
            )
            assert call_count_2 == call_count_1 + 1


# ============================================================================
# Create Local or Remote App Tests
# ============================================================================


@pytest.mark.scenario_ids("TC-LSP-3238-04")
class TestCreateLocalOrClient(BaseCommondbClientTestCase):
    """Test create_local_or_remote class method."""

    def test_invalid_app_setup_type_rejected(self) -> None:
        """Raise error for invalid app_setup_type."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbClient.create_local_or_remote(
                app_type=Mock(),
                app_setup_type="INVALID",
            )
        assert "Invalid app_setup_type" in str(exc_info.value)

    def test_app_setup_type_case_insensitive(self) -> None:
        """app_setup_type is case-insensitive."""
        with patch.object(
            CommondbClient, "_create_local_client", return_value=(Mock(), Mock())
        ) as mock_local:
            CommondbClient.create_local_or_remote(
                app_type=Mock(),
                app_setup_type="local",  # lowercase
                local_client_props={"user": {}},
                app_composer_class=Mock,
                user_class=Mock,
                service_type_enum=Mock,
                repository_type_enum=Mock,
            )
            mock_local.assert_called_once()

    def test_remote_setup_delegates_to_remote_client_factory(self) -> None:
        app = Mock()
        remote_props = {"module": "example", "class_name": "RemoteClient"}
        with patch.object(
            CommondbClient, "_create_client", return_value=(app, None)
        ) as mock_remote:
            result_app, user = CommondbClient.create_local_or_remote(
                app_type=Mock(),
                app_setup_type="REMOTE",
                remote_client_props=remote_props,
            )

        assert result_app is app
        assert user is None
        mock_remote.assert_called_once_with(remote_props)

    def test_local_setup_builds_config_when_not_supplied(self) -> None:
        app = Mock()
        user = Mock()
        app_type = Mock()
        service_type_enum = Mock()
        repository_type_enum = Mock()
        app_cfg = Mock()
        cfg_factory = Mock(return_value=app_cfg)
        composer_result = Mock(app=app)
        composer_class = Mock(return_value=composer_result)
        user_class = Mock(return_value=user)
        props = {"user": {"key": "test-user"}}
        with patch(
            f"{commondb_client_module.__name__}.util.get_app_cfg_class",
            return_value=cfg_factory,
        ) as mock_get_cfg:
            result_app, result_user = CommondbClient.create_local_or_remote(
                app_type=app_type,
                app_setup_type="LOCAL",
                local_client_props=props,
                app_composer_class=composer_class,
                user_class=user_class,
                service_type_enum=service_type_enum,
                repository_type_enum=repository_type_enum,
                logger=Mock(),
            )

        assert result_app is app
        assert result_user is user
        mock_get_cfg.assert_called_once_with(app_type)
        cfg_factory.assert_called_once_with(
            app_type, service_type_enum, repository_type_enum
        )
        composer_class.assert_called_once_with(app_cfg, log_setup=True)
        user_class.assert_called_once_with(key="test-user")

    def test_local_setup_uses_supplied_config_and_log_setup(self) -> None:
        app = Mock()
        user = Mock()
        app_cfg = Mock()
        composer_result = Mock(app=app)
        composer_class = Mock(return_value=composer_result)
        user_class = Mock(return_value=user)
        props = {"app_cfg": app_cfg, "log_setup": False, "user": {"key": "u"}}

        result_app, result_user = CommondbClient.create_local_or_remote(
            app_type=Mock(),
            app_setup_type="LOCAL",
            local_client_props=props,
            app_composer_class=composer_class,
            user_class=user_class,
            service_type_enum=Mock(),
            repository_type_enum=Mock(),
        )

        assert result_app is app
        assert result_user is user
        composer_class.assert_called_once_with(app_cfg, log_setup=False)
        user_class.assert_called_once_with(key="u")

    def test_local_setup_rejects_missing_user_key(self) -> None:
        with pytest.raises(exc.InitializationServiceError, match="'user' key"):
            CommondbClient.create_local_or_remote(
                app_type=Mock(),
                app_setup_type="LOCAL",
                local_client_props={},
                app_composer_class=Mock(),
                user_class=Mock(),
                service_type_enum=Mock(),
                repository_type_enum=Mock(),
            )

    def test_local_setup_requires_configuration(self) -> None:
        with pytest.raises(exc.InitializationServiceError, match="local_client_props"):
            CommondbClient.create_local_or_remote(
                app_type=Mock(),
                app_setup_type="LOCAL",
            )

    def test_none_app_setup_returns_app_without_user(self) -> None:
        """NONE setup returns the no-client application and no user."""
        app = Mock()
        with patch.object(
            CommondbClient, "_create_no_client", return_value=app
        ) as mock_no_client:
            result_app, user = CommondbClient.create_local_or_remote(
                app_type=Mock(),
                app_setup_type="NONE",
                no_client_props={},
                app_composer_class=Mock,
                user_class=Mock,
                service_type_enum=Mock,
                repository_type_enum=Mock,
            )

        assert result_app is app
        assert user is None
        mock_no_client.assert_called_once()

    def test_none_app_setup_requires_configuration(self) -> None:
        """Raise an initialization error when NONE setup is incomplete."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbClient.create_local_or_remote(
                app_type=Mock(),
                app_setup_type="NONE",
            )

        assert "no_client_props" in str(exc_info.value)

    def test_no_client_setup_builds_config_when_not_supplied(self) -> None:
        app = Mock()
        app_type = Mock()
        service_type_enum = Mock()
        repository_type_enum = Mock()
        app_cfg = Mock()
        cfg_factory = Mock(return_value=app_cfg)
        composer_result = Mock(app=app)
        composer_class = Mock(return_value=composer_result)
        props: dict[str, Any] = {}
        with patch(
            f"{commondb_client_module.__name__}.util.get_app_cfg_class",
            return_value=cfg_factory,
        ) as mock_get_cfg:
            result_app, user = CommondbClient.create_local_or_remote(
                app_type=app_type,
                app_setup_type="NONE",
                no_client_props=props,
                app_composer_class=composer_class,
                user_class=Mock(),
                service_type_enum=service_type_enum,
                repository_type_enum=repository_type_enum,
            )

        assert result_app is app
        assert user is None
        mock_get_cfg.assert_called_once_with(app_type)
        cfg_factory.assert_called_once_with(
            app_type, service_type_enum, repository_type_enum
        )
        composer_class.assert_called_once_with(app_cfg, log_setup=False)

    def test_no_client_setup_uses_supplied_config(self) -> None:
        app = Mock()
        app_cfg = Mock()
        composer_class = Mock(return_value=Mock(app=app))
        props = {"app_cfg": app_cfg, "log_setup": True}

        result = CommondbClient._create_no_client(
            app_type=Mock(),
            no_client_props=props,
            app_composer_class=composer_class,
            user_class=Mock(),
            service_type_enum=Mock(),
            repository_type_enum=Mock(),
        )

        assert result is app
        composer_class.assert_called_once_with(app_cfg, log_setup=True)


# ============================================================================
# HTTP Timeout Configuration Tests
# ============================================================================


@pytest.mark.scenario_ids("TC-LSP-3238-05")
class TestHttpTimeoutConfiguration(BaseCommondbClientTestCase):
    """Test HTTP timeout configuration per command class."""

    def test_derived_client_has_timeout_configuration(self) -> None:
        """DerivedClient has DEFAULT_HTTP_TIMEOUTS configured."""
        assert hasattr(DerivedClient, "DEFAULT_HTTP_TIMEOUTS")
        assert DummyCommand in DerivedClient.DEFAULT_HTTP_TIMEOUTS
        assert DerivedClient.DEFAULT_HTTP_TIMEOUTS[DummyCommand] == 30.0

    def test_derived_client_initialization(self) -> None:
        """DerivedClient can be initialized."""
        app = DerivedClient(
            domain=self.domain,
            host="example.org",
            port=8000,
        )
        assert isinstance(app, DerivedClient)
        assert isinstance(app, CommondbClient)

    def test_create_client_applies_timeouts(self) -> None:
        """_create_client applies DEFAULT_HTTP_TIMEOUTS to remote app."""
        # Create a mock remote app class
        mock_client_instance = Mock(spec=Client)

        # Patch the module and class to return our mock
        with patch("importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_module.MockClient = Mock(return_value=mock_client_instance)
            mock_import.return_value = mock_module

            # Use DerivedClient to have DEFAULT_HTTP_TIMEOUTS set
            app, user = DerivedClient._create_client(
                client_props={
                    "module": "test.mock_module",
                    "class_name": "MockClient",
                }
            )

            # Verify set_timeout was called for each timeout in DEFAULT_HTTP_TIMEOUTS
            mock_client_instance.set_timeout.assert_called_with(DummyCommand, 30.0)
            assert user is None

    def test_base_client_has_empty_timeouts(self) -> None:
        """Base CommondbClient has empty DEFAULT_HTTP_TIMEOUTS."""
        assert CommondbClient.DEFAULT_HTTP_TIMEOUTS == {}

    def test_timeout_configuration_does_not_affect_none_auth(self) -> None:
        """Timeout configuration works independently of auth protocol."""
        app = DerivedClient(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
        )
        assert app._auth_protocol == AuthProtocol.NONE
        assert app.DEFAULT_HTTP_TIMEOUTS[DummyCommand] == 30.0


# ============================================================================
# Create Remote App Error Handling Tests
# ============================================================================


@pytest.mark.scenario_ids("TC-LSP-3238-06")
class TestCreateClientErrors(BaseCommondbClientTestCase):
    """Test error handling in _create_client."""

    def test_client_props_none_raises_error(self) -> None:
        """_create_client raises error when client_props is None."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbClient._create_client(None)
        assert "client_props must be provided" in str(exc_info.value)

    def test_client_missing_module_raises_error(self) -> None:
        """_create_client raises error when module key is missing."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbClient._create_client({"class_name": "MyApp"})
        assert "'module' and 'class_name' keys" in str(exc_info.value)

    def test_client_missing_class_name_raises_error(self) -> None:
        """_create_client raises error when class_name key is missing."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbClient._create_client({"module": "my.module"})
        assert "'module' and 'class_name' keys" in str(exc_info.value)


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.scenario_ids("TC-LSP-3238-07")
class TestIntegration(BaseCommondbClientTestCase):
    """Integration tests combining multiple features."""

    def test_oauth2_app_gets_headers_with_bearer_token(self) -> None:
        """Full flow: OAuth2 app retrieves and returns bearer token in headers."""
        mock_idp_client = Mock()
        exp_time = int(datetime.now(timezone.utc).timestamp()) + 3600
        jwt_token = jwt.encode(
            {"exp": exp_time}, _JWT_TEST_HS256_SECRET, algorithm="HS256"
        )
        mock_idp_client.retrieve_jwt_with_client_credentials_flow_and_expiry.return_value = (
            jwt_token,
            3600.0,
        )

        with patch(
            "gen_epix.commondb.services.client.OauthIdpClient"
        ) as mock_idp_class:
            mock_idp_class.return_value = mock_idp_client

            app = CommondbClient(
                domain=self.domain,
                host="example.org",
                port=8000,
                auth_protocol=AuthProtocol.OAUTH2,
                oauth_discovery_url="https://idp.example.org/.well-known/openid-configuration",
                oauth_client_id="client123",
                oauth_client_secret="secret123",
                oauth_scope="openid profile",
                default_headers={"X-Service": "api"},
            )

            cmd = DummyCommand()
            headers = app.get_headers(cmd)

            assert headers["Authorization"] == f"Bearer {jwt_token}"
            assert headers["X-Service"] == "api"

    def test_none_auth_app_preserves_custom_headers(self) -> None:
        """Full flow: NONE auth app preserves custom default headers."""
        app = CommondbClient(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
            default_headers={
                "X-Custom-1": "value1",
                "X-Custom-2": "value2",
            },
        )

        cmd = DummyCommand()
        headers = app.get_headers(cmd)

        assert headers["X-Custom-1"] == "value1"
        assert headers["X-Custom-2"] == "value2"
        assert "Authorization" not in headers


# ============================================================================
# Non-CRUD handler tests
#
# Each test builds a real CommondbClient, mocks the underlying httpx
# client, invokes the handler directly, and checks the HTTP call it makes
# (method, URL, body) plus that the response is parsed into the right model.
# This guards against route/model drift between the API and the handler.
# ============================================================================


def _mock_response(json_data: Any, status_code: int = 200) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.content = b"1"
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class TestNonCrudHandlers:
    """Test the hand-written (non-CRUD) command handlers."""

    @pytest.fixture
    def app(self) -> CommondbClient:
        return CommondbClient(DOMAIN, host="example.org", port=8000)

    @pytest.fixture
    def mock_client(self) -> Any:
        with patch("gen_epix.fastapp.client.httpx.Client") as mock_client_class:
            client = MagicMock()
            client.__enter__.return_value = client
            client.__exit__.return_value = None
            mock_client_class.return_value = client
            yield client

    def test_get_identity_providers(
        self, app: CommondbClient, mock_client: Any
    ) -> None:
        data = [
            {
                "name": "n",
                "label": "l",
                "issuer": "i",
                "auth_protocol": "OAUTH2",
            }
        ]
        mock_client.request.return_value = _mock_response(data)
        result = app.get_identity_providers(
            command.GetIdentityProvidersCommand(user=None)
        )
        method, url = mock_client.request.call_args.args
        assert method == "GET"
        assert url == app._routes[command.GetIdentityProvidersCommand]
        assert result == [model.IdentityProvider(**data[0])]

    def test_invite_user(self, app: CommondbClient, mock_client: Any) -> None:
        organization_id = uuid4()
        cmd = command.InviteUserCommand(
            user=None,
            key="a@example.org",
            description="desc",
            roles={"ADMIN"},
            organization_id=organization_id,
        )
        data = {
            "token": "tok",
            "expires_at": "2030-01-01T00:00:00Z",
            "roles": ["ADMIN"],
            "invited_by_user_id": str(uuid4()),
            "organization_id": str(organization_id),
        }
        mock_client.request.return_value = _mock_response(data)
        result = app.invite_user(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "POST"
        assert url == app._routes[command.InviteUserCommand]
        assert json_body == {
            "key": "a@example.org",
            "description": "desc",
            "roles": ["ADMIN"],
            "organization_id": str(organization_id),
        }
        assert result == model.UserInvitation(**data)

    def test_retrieve_invite_user_constraints(
        self, app: CommondbClient, mock_client: Any
    ) -> None:
        data = {"roles": ["ADMIN"], "organization_ids": [str(uuid4())]}
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_invite_user_constraints(
            command.RetrieveInviteUserConstraintsCommand(user=None)
        )
        method, url = mock_client.request.call_args.args
        assert method == "GET"
        assert url == app._routes[command.RetrieveInviteUserConstraintsCommand]
        assert result == model.UserInvitationConstraints(**data)

    def test_register_invited_user(self, app: CommondbClient, mock_client: Any) -> None:
        organization_id = uuid4()
        data = {"roles": ["ADMIN"], "organization_id": str(organization_id)}
        mock_client.request.return_value = _mock_response(data)
        result = app.register_invited_user(
            command.RegisterInvitedUserCommand(user=None, token="tok123")
        )
        method, url = mock_client.request.call_args.args
        assert method == "POST"
        assert url == f"{app._routes[command.RegisterInvitedUserCommand]}/tok123"
        assert result == model.User(**data)

    def test_organization_set_organization_update_association(
        self, app: CommondbClient, mock_client: Any
    ) -> None:
        organization_set_id = uuid4()
        member = model.OrganizationSetMember(
            organization_set_id=organization_set_id, organization_id=uuid4()
        )
        cmd = command.OrganizationSetOrganizationUpdateAssociationCommand(
            user=None, obj_id1=organization_set_id, association_objs=[member]
        )
        data = [
            {
                "organization_set_id": str(organization_set_id),
                "organization_id": str(uuid4()),
            }
        ]
        mock_client.request.return_value = _mock_response(data)
        result = app.organization_set_organization_update_association(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "PUT"
        route = app._routes[command.OrganizationSetOrganizationUpdateAssociationCommand]
        assert url == f"{route}/{organization_set_id}/organizations"
        assert json_body == {
            "organization_set_members": [json.loads(member.model_dump_json())]
        }
        assert result == [model.OrganizationSetMember(**data[0])]

    def test_data_collection_set_data_collection_update_association(
        self, app: CommondbClient, mock_client: Any
    ) -> None:
        data_collection_set_id = uuid4()
        member = model.DataCollectionSetMember(
            data_collection_set_id=data_collection_set_id, data_collection_id=uuid4()
        )
        cmd = command.DataCollectionSetDataCollectionUpdateAssociationCommand(
            user=None, obj_id1=data_collection_set_id, association_objs=[member]
        )
        data = [
            {
                "data_collection_set_id": str(data_collection_set_id),
                "data_collection_id": str(uuid4()),
            }
        ]
        mock_client.request.return_value = _mock_response(data)
        result = app.data_collection_set_data_collection_update_association(cmd)
        method, url = mock_client.request.call_args.args
        assert method == "PUT"
        route = app._routes[
            command.DataCollectionSetDataCollectionUpdateAssociationCommand
        ]
        assert url == f"{route}/{data_collection_set_id}/data_collections"
        assert result == [model.DataCollectionSetMember(**data[0])]

    def test_retrieve_own_permissions(
        self, app: CommondbClient, mock_client: Any
    ) -> None:
        data = [{"command_name": "SomeCommand", "permission_type": "CREATE"}]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_own_permissions(
            command.RetrieveOwnPermissionsCommand(user=None)
        )
        method, url = mock_client.request.call_args.args
        assert method == "GET"
        assert url == app._routes[command.RetrieveOwnPermissionsCommand]
        assert result == {Permission(**data[0])}

    def test_anonymize_user(self, app: CommondbClient, mock_client: Any) -> None:
        tgt_user_id = uuid4()
        mock_client.request.return_value = _mock_response(None)
        result = app.anonymize_user(
            command.AnonymizeUserCommand(user=None, tgt_user_id=tgt_user_id)
        )
        method, url = mock_client.request.call_args.args
        assert method == "POST"
        route = app._routes[command.AnonymizeUserCommand]
        assert url == f"{route}/{tgt_user_id}/anonymize"
        assert result is None

    def test_update_user(self, app: CommondbClient, mock_client: Any) -> None:
        tgt_user_id = uuid4()
        organization_id = uuid4()
        cmd = command.UpdateUserCommand(
            user=None,
            tgt_user_id=tgt_user_id,
            is_active=True,
            roles={"ADMIN"},
            organization_id=organization_id,
        )
        data = {"roles": ["ADMIN"], "organization_id": str(organization_id)}
        mock_client.request.return_value = _mock_response(data)
        result = app.update_user(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "PUT"
        assert url == f"{app._routes[command.UpdateUserCommand]}/{tgt_user_id}"
        assert json_body == {
            "is_active": True,
            "roles": ["ADMIN"],
            "organization_id": str(organization_id),
        }
        assert result == model.User(**data)

    def test_update_user_own_organization(
        self, app: CommondbClient, mock_client: Any
    ) -> None:
        organization_id = uuid4()
        data = {"roles": ["ADMIN"], "organization_id": str(organization_id)}
        mock_client.request.return_value = _mock_response(data)
        result = app.update_user_own_organization(
            command.UpdateUserOwnOrganizationCommand(
                user=None, organization_id=organization_id
            )
        )
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "PUT"
        assert url == app._routes[command.UpdateUserOwnOrganizationCommand]
        assert json_body == {"organization_id": str(organization_id)}
        assert result == model.User(**data)

    def test_organization_identifier_issuer_link_update_association(
        self, app: CommondbClient, mock_client: Any
    ) -> None:
        organization_id = uuid4()
        link = model.OrganizationIdentifierIssuerLink(
            organization_id=organization_id, identifier_issuer_id=uuid4()
        )
        cmd = command.OrganizationIdentifierIssuerUpdateAssociationCommand(
            user=None, obj_id1=organization_id, association_objs=[link]
        )
        data = [
            {
                "organization_id": str(organization_id),
                "identifier_issuer_id": str(uuid4()),
            }
        ]
        mock_client.request.return_value = _mock_response(data)
        result = app.organization_identifier_issuer_link_update_association(cmd)
        method, url = mock_client.request.call_args.args
        assert method == "PUT"
        route = app._routes[
            command.OrganizationIdentifierIssuerUpdateAssociationCommand
        ]
        assert url == f"{route}/{organization_id}/identifier_issuers"
        assert result == [model.OrganizationIdentifierIssuerLink(**data[0])]

    def test_retrieve_organization_contacts(
        self, app: CommondbClient, mock_client: Any
    ) -> None:
        organization_id = uuid4()
        organization = model.Organization.model_construct(name="Org", code="ORG1")
        data = {
            "organization": organization.model_dump(mode="json"),
            "sites": [],
            "contacts": [],
        }
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_organization_contacts(
            command.RetrieveOrganizationContactsCommand(
                user=None, organization_id=organization_id
            )
        )
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "POST"
        assert url == app._routes[command.RetrieveOrganizationContactsCommand]
        assert json_body == {"organization_id": str(organization_id)}
        assert result == model.OrganizationContacts(**data)

    def test_retrieve_organization_admin_name_emails(
        self, app: CommondbClient, mock_client: Any
    ) -> None:
        data = [{"email": "a@example.org"}]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_organization_admin_name_emails(
            command.RetrieveOrganizationAdminNameEmailsCommand(user=None)
        )
        method, url = mock_client.request.call_args.args
        assert method == "GET"
        assert url == app._routes[command.RetrieveOrganizationAdminNameEmailsCommand]
        assert result == [model.UserNameEmail(**data[0])]

    def test_retrieve_feature_flags(
        self, app: CommondbClient, mock_client: Any
    ) -> None:
        data = {"feature_flags": {"my_flag": True}}
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_feature_flags(
            command.RetrieveFeatureFlagsCommand(user=None)
        )
        method, url = mock_client.request.call_args.args
        assert method == "GET"
        assert url == app._routes[command.RetrieveFeatureFlagsCommand]
        assert result == {"my_flag": True}

    def test_delete_all_operational_data(
        self, app: CommondbClient, mock_client: Any
    ) -> None:
        """Parse the JSON result returned by the operational-data reset endpoint."""
        data = {"success": True, "details": {"cases": "[]"}}
        mock_client.request.return_value = _mock_response(data)

        result = app.delete_all_operational_data(
            command.DeleteAllOperationalDataCommand(user=None)
        )

        method, url = mock_client.request.call_args.args
        assert method == "DELETE"
        assert url == app._routes[command.DeleteAllOperationalDataCommand]
        assert result == model.DeleteAllOperationalDataResult(**data)

    def test_delete_all_ref_data(self, app: CommondbClient, mock_client: Any) -> None:
        """Parse the JSON result returned by the reference-data reset endpoint."""
        data = {"success": True, "details": {"case_types": "[]"}}
        mock_client.request.return_value = _mock_response(data)

        result = app.delete_all_ref_data(command.DeleteAllRefDataCommand(user=None))

        method, url = mock_client.request.call_args.args
        assert method == "DELETE"
        assert url == app._routes[command.DeleteAllRefDataCommand]
        assert result == model.DeleteAllRefDataResult(**data)

    def test_retrieve_licenses(self, app: CommondbClient, mock_client: Any) -> None:
        data = [{"name": "pkg", "version": "1.0"}]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_licenses(command.RetrieveLicensesCommand(user=None))
        method, url = mock_client.request.call_args.args
        assert method == "POST"
        assert url == app._routes[command.RetrieveLicensesCommand]
        assert result == [model.PackageMetadata(**data[0])]

    def test_retrieve_outages(self, app: CommondbClient, mock_client: Any) -> None:
        data = [{}]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_outages(command.RetrieveOutagesCommand(user=None))
        method, url = mock_client.request.call_args.args
        assert method == "GET"
        assert url == app._routes[command.RetrieveOutagesCommand]
        assert result == [model.Outage(**data[0])]


_TOKEN_PROVIDER_SECRET = "token-provider-test-secret-key-32bytes"


class ProviderCommand(Command):
    NAME = "ProviderCommand"


def _provider_token(exp_offset: float | None, sub: str = "u") -> str:
    claims: dict[str, Any] = {"sub": sub}
    if exp_offset is not None:
        claims["exp"] = int(datetime.now(timezone.utc).timestamp() + exp_offset)
    return jwt.encode(claims, _TOKEN_PROVIDER_SECRET, algorithm="HS256")


class TokenProvider:
    def __init__(self, *tokens: str | Exception) -> None:
        self.tokens = list(tokens)
        self.calls = 0

    def __call__(self) -> str:
        self.calls += 1
        item = self.tokens.pop(0) if len(self.tokens) > 1 else self.tokens[0]
        if isinstance(item, Exception):
            raise item
        return item


def _token_provider_status_error(status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "http://example.org/x")
    return httpx.HTTPStatusError(
        "boom", request=request, response=httpx.Response(status, request=request)
    )


def _make_token_provider_client(
    provider: TokenProvider, **kwargs: Any
) -> CommondbClient:
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
        token = _provider_token(3600)
        provider = TokenProvider(token)
        client = _make_token_provider_client(provider)
        for _ in range(3):
            headers = client.get_headers(ProviderCommand())
        assert headers["Authorization"] == f"Bearer {token}"
        assert provider.calls == 1

    def test_default_headers_are_kept(self) -> None:
        token = _provider_token(3600)
        client = _make_token_provider_client(TokenProvider(token))
        headers = client.get_headers(ProviderCommand())
        assert headers["Authorization"] == f"Bearer {token}"
        assert headers["Content-Type"] == "application/json"

    def test_provider_recalled_within_refresh_margin(self) -> None:
        first, second = _provider_token(30, "a"), _provider_token(3600, "b")
        provider = TokenProvider(first, second)
        client = _make_token_provider_client(provider, oauth_token_refresh_margin=60)
        assert client.get_headers(ProviderCommand())["Authorization"].endswith(first)
        assert client.get_headers(ProviderCommand())["Authorization"].endswith(second)
        assert provider.calls == 2

    def test_token_without_exp_cached_indefinitely(self) -> None:
        provider = TokenProvider(_provider_token(None))
        client = _make_token_provider_client(provider)
        client.get_headers(ProviderCommand())
        client.get_headers(ProviderCommand())
        assert provider.calls == 1

    def test_opaque_token_cached_indefinitely(self) -> None:
        provider = TokenProvider("not-a-jwt")
        client = _make_token_provider_client(provider)
        assert client.get_headers(ProviderCommand())["Authorization"] == (
            "Bearer not-a-jwt"
        )
        client.get_headers(ProviderCommand())
        assert provider.calls == 1

    def test_get_access_token(self) -> None:
        token = _provider_token(3600)
        assert (
            _make_token_provider_client(TokenProvider(token)).get_access_token()
            == token
        )

    def test_get_access_token_without_token_source(self) -> None:
        client = CommondbClient(DOMAIN, "example.org", 8000, protocol=HttpProtocol.HTTP)
        with pytest.raises(exc.InitializationServiceError):
            client.get_access_token()


class TestTokenProviderValidation:
    def test_conflicts_with_oauth2(self) -> None:
        with pytest.raises(exc.InitializationServiceError, match="OAUTH2"):
            CommondbClient(
                DOMAIN,
                "example.org",
                8000,
                auth_protocol=AuthProtocol.OAUTH2,
                oauth_discovery_url="https://idp/.well-known",
                oauth_client_id="id",
                oauth_scope="s",
                token_provider=TokenProvider("x"),
            )

    def test_conflicts_with_authorization_default_header(self) -> None:
        with pytest.raises(exc.InitializationServiceError, match="Authorization"):
            _make_token_provider_client(
                TokenProvider("x"), default_headers={"authorization": "Bearer abc"}
            )


class TestTokenProviderHandle:
    @staticmethod
    def _register(client: CommondbClient, handler: Any) -> None:
        client.register_route(ProviderCommand, "/provider")
        client.register_handler(ProviderCommand, handler)

    def test_handle_without_provider_uses_base_client(self) -> None:
        client = CommondbClient(
            DOMAIN,
            "example.org",
            8000,
            protocol=HttpProtocol.HTTP,
            auth_protocol=AuthProtocol.NONE,
        )
        self._register(client, lambda _cmd: "ok")

        assert client.handle(ProviderCommand()) == "ok"

    def test_401_refreshes_token_and_retries_once(self) -> None:
        first, second = _provider_token(3600, "a"), _provider_token(3600, "b")
        provider = TokenProvider(first, second)
        client = _make_token_provider_client(provider)
        seen: list[str] = []

        def handler(cmd: Command) -> str:
            seen.append(client.get_headers(cmd)["Authorization"])
            if len(seen) == 1:
                raise _token_provider_status_error(401)
            return "ok"

        self._register(client, handler)
        assert client.handle(ProviderCommand()) == "ok"
        assert provider.calls == 2
        assert seen == [f"Bearer {first}", f"Bearer {second}"]

    def test_second_401_propagates(self) -> None:
        provider = TokenProvider(_provider_token(3600, "a"), _provider_token(3600, "b"))
        client = _make_token_provider_client(provider)
        calls = 0

        def handler(cmd: Command) -> str:
            nonlocal calls
            calls += 1
            client.get_headers(cmd)
            raise _token_provider_status_error(401)

        self._register(client, handler)
        with pytest.raises(exc.ServiceException, match="HTTP status 401"):
            client.handle(ProviderCommand())
        assert calls == 2

    def test_other_errors_do_not_refresh(self) -> None:
        provider = TokenProvider(_provider_token(3600))
        client = _make_token_provider_client(provider)

        def handler(cmd: Command) -> str:
            client.get_headers(cmd)
            raise _token_provider_status_error(403)

        self._register(client, handler)
        with pytest.raises(exc.ServiceException):
            client.handle(ProviderCommand())
        assert provider.calls == 1

    def test_provider_failure_is_auth_error_and_not_transient_retried(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        sleeps: list[float] = []
        monkeypatch.setattr("tenacity.nap.time.sleep", sleeps.append)
        provider = TokenProvider(RuntimeError("login failed"))
        client = _make_token_provider_client(
            provider, retry_policy=fastapp.RetryPolicy(frozenset({500}), (1, 1))
        )

        def handler(cmd: Command) -> str:
            client.get_headers(cmd)
            return "ok"

        self._register(client, handler)
        with pytest.raises(exc.ServiceException) as info:
            client.handle(ProviderCommand())
        assert isinstance(info.value.__cause__, exc.AuthException)
        assert provider.calls == 1
        assert sleeps == []

    def test_401_refresh_does_not_consume_transient_attempt(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("tenacity.nap.time.sleep", lambda _: None)
        provider = TokenProvider(_provider_token(3600, "a"), _provider_token(3600, "b"))
        client = _make_token_provider_client(
            provider, retry_policy=fastapp.RetryPolicy(frozenset({503}), (1,))
        )
        errors = [_token_provider_status_error(401), _token_provider_status_error(503)]
        calls = 0

        def handler(cmd: Command) -> str:
            nonlocal calls
            calls += 1
            client.get_headers(cmd)
            if errors:
                raise errors.pop(0)
            return "ok"

        self._register(client, handler)
        assert client.handle(ProviderCommand()) == "ok"
        assert calls == 3

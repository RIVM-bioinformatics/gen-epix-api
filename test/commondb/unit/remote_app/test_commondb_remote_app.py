"""Unit tests for CommondbRemoteApp class.

Tests cover initialization, authentication/authorization handling, header
management, local/remote app creation, and HTTP timeout configuration.
Tests use mock objects to avoid external dependencies and OS integration.

Pattern note: This test module follows the existing remote app test patterns
from test/fastapp/unit/test_remote_app.py, adapted for the CommondbRemoteApp
subclass and its domain-specific initialization.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from test.util.mock_compat import MagicMock, Mock, patch
from typing import Any, cast
from uuid import uuid4

import jwt
import pytest

from gen_epix.commondb.domain import DOMAIN, command, model
from gen_epix.commondb.services.remote_app import CommondbRemoteApp
from gen_epix.fastapp import RemoteApp, exc
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import AuthProtocol, OAuthFlow
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


class DerivedRemoteApp(CommondbRemoteApp):
    """Minimal subclass of CommondbRemoteApp for testing timeout configuration."""

    # Configure timeouts per command type for testing
    DEFAULT_HTTP_TIMEOUTS: dict[type[Command], float] = {
        DummyCommand: 30.0,
    }


# ============================================================================
# Base Test Case with Common Setup
# ============================================================================


class BaseCommondbRemoteAppTestCase:
    """Base test case with common fixtures and setup for CommondbRemoteApp."""

    def setup_method(self) -> None:
        """Set up test fixtures by mocking dependencies to avoid side effects."""

        # Patch App.__init__ to avoid side-effects and set required attributes
        def _fake_app_init(self: Any, domain: Domain, **kwargs: Any) -> None:
            setattr(self, "_domain", domain)
            setattr(self, "_logger", None)
            setattr(self, "_command_handler_map", {})

        self._app_init_patcher = patch(
            "gen_epix.fastapp.remote_app.App.__init__", _fake_app_init
        )
        self._app_init_patcher.start()

        # Patch create_ssl_context to return predictable value
        self._ssl_patcher = patch(
            "gen_epix.fastapp.remote_app.create_ssl_context", return_value="SSLCTX"
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
class TestInitialization(BaseCommondbRemoteAppTestCase):
    """Test CommondbRemoteApp initialization with various configurations."""

    def test_init_with_none_auth_protocol_enum(self) -> None:
        """Initialize with NONE auth protocol as enum."""
        app = CommondbRemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
        )
        assert app._auth_protocol == AuthProtocol.NONE
        assert app._oauth_idp_client is None

    def test_init_with_none_auth_protocol_string(self) -> None:
        """Initialize with NONE auth protocol as string."""
        app = CommondbRemoteApp(
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
            "gen_epix.commondb.services.remote_app.OauthIdpClient"
        ) as mock_idp_class:
            app = CommondbRemoteApp(
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
            "gen_epix.commondb.services.remote_app.OauthIdpClient"
        ) as mock_idp_class:
            app = CommondbRemoteApp(
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
        app = CommondbRemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
            oauth_flow=OAuthFlow.CLIENT_CREDENTIALS,
        )
        assert app._oauth_flow == OAuthFlow.CLIENT_CREDENTIALS

    def test_init_with_oauth_flow_string(self) -> None:
        """Initialize with OAuthFlow as string."""
        app = CommondbRemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
            oauth_flow="CLIENT_CREDENTIALS",
        )
        assert app._oauth_flow == OAuthFlow.CLIENT_CREDENTIALS

    def test_init_default_route_prefix(self) -> None:
        """Verify default route prefix is /v1."""
        app = CommondbRemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
        )
        assert app._default_route_prefix == "/v1"

    def test_init_custom_route_prefix(self) -> None:
        """Use custom route prefix if provided."""
        app = CommondbRemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
            default_route_prefix="/api/v2",
        )
        assert app._default_route_prefix == "/api/v2"

    def test_init_default_oauth_token_refresh_margin(self) -> None:
        """Verify default OAuth token refresh margin is 60 seconds."""
        app = CommondbRemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
        )
        assert app._oauth_token_refresh_margin == 60

    def test_init_custom_oauth_token_refresh_margin(self) -> None:
        """Use custom OAuth token refresh margin if provided."""
        app = CommondbRemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
            oauth_token_refresh_margin=120,
        )
        assert app._oauth_token_refresh_margin == 120


# ============================================================================
# OAuth2 Validation Tests (Missing Configuration)
# ============================================================================


@pytest.mark.scenario_ids("TC-LSP-3238-02")
class TestOAuth2Validation(BaseCommondbRemoteAppTestCase):
    """Test OAuth2 configuration validation during initialization."""

    def test_oauth2_missing_discovery_url(self) -> None:
        """Raise error when OAuth2 requires discovery URL."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbRemoteApp(
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
            CommondbRemoteApp(
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
            CommondbRemoteApp(
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
            CommondbRemoteApp(
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
class TestGetHeaders(BaseCommondbRemoteAppTestCase):
    """Test get_headers method for different auth protocols."""

    def test_get_headers_with_none_auth_protocol(self) -> None:
        """get_headers returns default headers with NONE protocol."""
        app = CommondbRemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
            default_headers={"X-Custom": "value"},
        )
        cmd = DummyCommand()
        headers = app.get_headers(cmd)
        assert headers == {"X-Custom": "value"}

    def test_get_headers_caches_token(self) -> None:
        """get_headers caches token when not expired."""
        # Create mock OauthIdpClient
        mock_idp_client = Mock()

        # Create JWT token that expires in the future
        exp_time = int(datetime.now(timezone.utc).timestamp()) + 3600
        jwt_token = jwt.encode(
            {"exp": exp_time}, _JWT_TEST_HS256_SECRET, algorithm="HS256"
        )

        mock_idp_client.retrieve_jwt_with_client_credentials_flow.return_value = (
            jwt_token
        )

        with patch(
            "gen_epix.commondb.services.remote_app.OauthIdpClient"
        ) as mock_idp_class:
            mock_idp_class.return_value = mock_idp_client

            app = CommondbRemoteApp(
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
                mock_idp_client.retrieve_jwt_with_client_credentials_flow.call_count
            )

            # Second call uses cached token
            headers2 = app.get_headers(cmd)
            assert headers2 == headers1
            # Call count should not increase (token was cached)
            call_count2 = (
                mock_idp_client.retrieve_jwt_with_client_credentials_flow.call_count
            )
            assert call_count2 == call_count1

    def test_get_headers_refreshes_expired_token(self) -> None:
        """get_headers refreshes token past refresh margin."""
        mock_idp_client = Mock()

        # Create JWT token that expired in the recent past (within refresh margin)
        # This token should trigger a refresh
        now_ts = int(datetime.now(timezone.utc).timestamp())
        exp_time1 = now_ts - 100  # Expired 100 seconds ago
        jwt_token1 = jwt.encode(
            {"exp": exp_time1}, _JWT_TEST_HS256_SECRET, algorithm="HS256"
        )

        # Create different JWT token to return after token refresh
        exp_time2 = now_ts + 3600
        jwt_token2 = jwt.encode(
            {"exp": exp_time2}, _JWT_TEST_HS256_SECRET, algorithm="HS256"
        )

        mock_idp_client.retrieve_jwt_with_client_credentials_flow.side_effect = [
            jwt_token1,
            jwt_token2,
        ]

        with patch(
            "gen_epix.commondb.services.remote_app.OauthIdpClient"
        ) as mock_idp_class:
            mock_idp_class.return_value = mock_idp_client

            app = CommondbRemoteApp(
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

            # First call retrieves token (expired 100 seconds ago)
            headers1 = app.get_headers(cmd)
            assert "Authorization" in headers1
            # Margin is 50 seconds, token expired 100 seconds ago, so it was
            # refreshed immediately on first call (not cached)
            call_count_after_first = (
                mock_idp_client.retrieve_jwt_with_client_credentials_flow.call_count
            )

            # Second call should also refresh since first token was expired
            headers2 = app.get_headers(cmd)
            assert "Authorization" in headers2
            assert (
                mock_idp_client.retrieve_jwt_with_client_credentials_flow.call_count
                > call_count_after_first
            )

    def test_get_headers_handles_token_without_expiration(self) -> None:
        """get_headers caches long-lived tokens correctly.

        Note: Tokens without an 'exp' claim use datetime.max which has platform
        limitations (Windows). This test uses a very distant future time instead.
        """
        mock_idp_client = Mock()

        # Create JWT token with very distant expiration (simulates no exp claim)
        # Using a far future date rather than datetime.max to avoid Windows issues
        far_future_ts = int(datetime.now(timezone.utc).timestamp()) + (
            365 * 24 * 60 * 60 * 100
        )  # 100 years
        jwt_token = jwt.encode(
            {"exp": far_future_ts, "sub": "user123"},
            _JWT_TEST_HS256_SECRET,
            algorithm="HS256",
        )

        mock_idp_client.retrieve_jwt_with_client_credentials_flow.return_value = (
            jwt_token
        )

        with patch(
            "gen_epix.commondb.services.remote_app.OauthIdpClient"
        ) as mock_idp_class:
            mock_idp_class.return_value = mock_idp_client

            app = CommondbRemoteApp(
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
                mock_idp_client.retrieve_jwt_with_client_credentials_flow.call_count
            )

            # Second call should use cached token
            headers2 = app.get_headers(cmd)
            assert headers2 == headers
            # Should still only have been called once (token was cached)
            call_count_2 = (
                mock_idp_client.retrieve_jwt_with_client_credentials_flow.call_count
            )
            assert call_count_2 == call_count_1


# ============================================================================
# Create Local or Remote App Tests
# ============================================================================


@pytest.mark.scenario_ids("TC-LSP-3238-04")
class TestCreateLocalOrRemoteApp(BaseCommondbRemoteAppTestCase):
    """Test create_local_or_remote_app class method."""

    def test_invalid_app_setup_type_rejected(self) -> None:
        """Raise error for invalid app_setup_type."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbRemoteApp.create_local_or_remote_app(
                app_type=Mock(),
                app_setup_type="INVALID",
            )
        assert "Invalid app_setup_type" in str(exc_info.value)

    def test_app_setup_type_case_insensitive(self) -> None:
        """app_setup_type is case-insensitive."""
        with patch.object(
            CommondbRemoteApp, "_create_local_app", return_value=(Mock(), Mock())
        ) as mock_local:
            CommondbRemoteApp.create_local_or_remote_app(
                app_type=Mock(),
                app_setup_type="local",  # lowercase
                local_app_props={"user": {}},
                app_composer_class=Mock,
                user_class=Mock,
                service_type_enum=Mock,
                repository_type_enum=Mock,
            )
            mock_local.assert_called_once()


# ============================================================================
# HTTP Timeout Configuration Tests
# ============================================================================


@pytest.mark.scenario_ids("TC-LSP-3238-05")
class TestHttpTimeoutConfiguration(BaseCommondbRemoteAppTestCase):
    """Test HTTP timeout configuration per command class."""

    def test_derived_remote_app_has_timeout_configuration(self) -> None:
        """DerivedRemoteApp has DEFAULT_HTTP_TIMEOUTS configured."""
        assert hasattr(DerivedRemoteApp, "DEFAULT_HTTP_TIMEOUTS")
        assert DummyCommand in DerivedRemoteApp.DEFAULT_HTTP_TIMEOUTS
        assert DerivedRemoteApp.DEFAULT_HTTP_TIMEOUTS[DummyCommand] == 30.0

    def test_derived_remote_app_initialization(self) -> None:
        """DerivedRemoteApp can be initialized."""
        app = DerivedRemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
        )
        assert isinstance(app, DerivedRemoteApp)
        assert isinstance(app, CommondbRemoteApp)

    def test_create_remote_app_applies_timeouts(self) -> None:
        """_create_remote_app applies DEFAULT_HTTP_TIMEOUTS to remote app."""
        # Create a mock remote app class
        mock_remote_app_instance = Mock(spec=RemoteApp)

        # Patch the module and class to return our mock
        with patch("importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_module.MockRemoteApp = Mock(return_value=mock_remote_app_instance)
            mock_import.return_value = mock_module

            # Use DerivedRemoteApp to have DEFAULT_HTTP_TIMEOUTS set
            app, user = DerivedRemoteApp._create_remote_app(
                remote_app_props={
                    "module": "test.mock_module",
                    "class_name": "MockRemoteApp",
                }
            )

            # Verify set_timeout was called for each timeout in DEFAULT_HTTP_TIMEOUTS
            mock_remote_app_instance.set_timeout.assert_called_with(DummyCommand, 30.0)
            assert user is None

    def test_base_remote_app_has_empty_timeouts(self) -> None:
        """Base CommondbRemoteApp has empty DEFAULT_HTTP_TIMEOUTS."""
        assert CommondbRemoteApp.DEFAULT_HTTP_TIMEOUTS == {}

    def test_timeout_configuration_does_not_affect_none_auth(self) -> None:
        """Timeout configuration works independently of auth protocol."""
        app = DerivedRemoteApp(
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
class TestCreateRemoteAppErrors(BaseCommondbRemoteAppTestCase):
    """Test error handling in _create_remote_app."""

    def test_remote_app_props_none_raises_error(self) -> None:
        """_create_remote_app raises error when remote_app_props is None."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbRemoteApp._create_remote_app(None)
        assert "remote_app_props must be provided" in str(exc_info.value)

    def test_remote_app_missing_module_raises_error(self) -> None:
        """_create_remote_app raises error when module key is missing."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbRemoteApp._create_remote_app({"class_name": "MyApp"})
        assert "'module' and 'class_name' keys" in str(exc_info.value)

    def test_remote_app_missing_class_name_raises_error(self) -> None:
        """_create_remote_app raises error when class_name key is missing."""
        with pytest.raises(exc.InitializationServiceError) as exc_info:
            CommondbRemoteApp._create_remote_app({"module": "my.module"})
        assert "'module' and 'class_name' keys" in str(exc_info.value)


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.scenario_ids("TC-LSP-3238-07")
class TestIntegration(BaseCommondbRemoteAppTestCase):
    """Integration tests combining multiple features."""

    def test_oauth2_app_gets_headers_with_bearer_token(self) -> None:
        """Full flow: OAuth2 app retrieves and returns bearer token in headers."""
        mock_idp_client = Mock()
        exp_time = int(datetime.now(timezone.utc).timestamp()) + 3600
        jwt_token = jwt.encode(
            {"exp": exp_time}, _JWT_TEST_HS256_SECRET, algorithm="HS256"
        )
        mock_idp_client.retrieve_jwt_with_client_credentials_flow.return_value = (
            jwt_token
        )

        with patch(
            "gen_epix.commondb.services.remote_app.OauthIdpClient"
        ) as mock_idp_class:
            mock_idp_class.return_value = mock_idp_client

            app = CommondbRemoteApp(
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
        app = CommondbRemoteApp(
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
# Each test builds a real CommondbRemoteApp, mocks the underlying httpx
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
    def app(self) -> CommondbRemoteApp:
        return CommondbRemoteApp(DOMAIN, host="example.org", port=8000)

    @pytest.fixture
    def mock_client(self) -> Any:
        with patch("gen_epix.fastapp.remote_app.httpx.Client") as mock_client_class:
            client = MagicMock()
            client.__enter__.return_value = client
            client.__exit__.return_value = None
            mock_client_class.return_value = client
            yield client

    def test_get_identity_providers(
        self, app: CommondbRemoteApp, mock_client: Any
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

    def test_invite_user(self, app: CommondbRemoteApp, mock_client: Any) -> None:
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
        self, app: CommondbRemoteApp, mock_client: Any
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

    def test_register_invited_user(
        self, app: CommondbRemoteApp, mock_client: Any
    ) -> None:
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
        self, app: CommondbRemoteApp, mock_client: Any
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
        self, app: CommondbRemoteApp, mock_client: Any
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
        self, app: CommondbRemoteApp, mock_client: Any
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

    def test_anonymize_user(self, app: CommondbRemoteApp, mock_client: Any) -> None:
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

    def test_update_user(self, app: CommondbRemoteApp, mock_client: Any) -> None:
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
        self, app: CommondbRemoteApp, mock_client: Any
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
        self, app: CommondbRemoteApp, mock_client: Any
    ) -> None:
        organization_id = uuid4()
        link = model.OrganizationIdentifierIssuerLink(
            organization_id=organization_id, identifier_issuer_id=uuid4()
        )
        cmd = command.OrganizationIdentifierIssuerLinkUpdateAssociationCommand(
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
            command.OrganizationIdentifierIssuerLinkUpdateAssociationCommand
        ]
        assert url == f"{route}/{organization_id}/identifier_issuers"
        assert result == [model.OrganizationIdentifierIssuerLink(**data[0])]

    def test_retrieve_organization_contacts(
        self, app: CommondbRemoteApp, mock_client: Any
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
        self, app: CommondbRemoteApp, mock_client: Any
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
        self, app: CommondbRemoteApp, mock_client: Any
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

    def test_retrieve_licenses(self, app: CommondbRemoteApp, mock_client: Any) -> None:
        data = [{"name": "pkg", "version": "1.0"}]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_licenses(command.RetrieveLicensesCommand(user=None))
        method, url = mock_client.request.call_args.args
        assert method == "POST"
        assert url == app._routes[command.RetrieveLicensesCommand]
        assert result == [model.PackageMetadata(**data[0])]

    def test_retrieve_outages(self, app: CommondbRemoteApp, mock_client: Any) -> None:
        data = [{}]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_outages(command.RetrieveOutagesCommand(user=None))
        method, url = mock_client.request.call_args.args
        assert method == "GET"
        assert url == app._routes[command.RetrieveOutagesCommand]
        assert result == [model.Outage(**data[0])]

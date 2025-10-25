import base64
from datetime import datetime, timedelta
from math import floor
from test.fastapp.auth_test_client import AuthTestClient
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.services.auth import OidcClient


@pytest.fixture(scope="module", name="env")
def get_test_client() -> AuthTestClient:
    return (
        AuthTestClient.get_test_client()
    )  # type:ignore[no-any-return,no-untyped-call]


class TestAuth:
    NON_SECURE_ENDPOINT = "/non_secure"
    CURRENT_USER_ENDPOINT = "/secure/current_user"

    NOW = datetime.now()
    INVALID_CLAIMS: Dict[str, Any] = {
        "aud": "wrong_aud",  # client id
        "iss": "http://localhost:5003",  # authorization server
        "nbf": floor((NOW + timedelta(seconds=1000)).timestamp()),
        "exp": floor((NOW - timedelta(seconds=1000)).timestamp()),
        "iat": floor((NOW + timedelta(seconds=1000)).timestamp()),
    }

    INVALID_JWK: Dict[str, str] = {
        "alg": "RS384",
        "kid": "wrong_key_id",
        #
        # The following jwk fields are not being checked:
        #
        # "issuer": "wrong_issuer",
        # "use": "wrong_use",
        # "x5t": "wrong_x5t",
        # "kty": "wrong_kty",
    }

    def test_non_secure_happy_flow(self, env: AuthTestClient) -> None:
        response = env.test_client.get(TestAuth.NON_SECURE_ENDPOINT)
        assert response.status_code == 200

    def test_valid_jwt_token_happy_flow(self, env: AuthTestClient) -> None:
        response = env.test_client.get(
            TestAuth.CURRENT_USER_ENDPOINT,
            headers=env.mock_create_token_header(env.MOCK_JWK_TOKEN.token),
        )
        assert response.status_code == 200

    def test_secure_no_token(self, env: AuthTestClient) -> None:
        response = env.test_client.get(self.CURRENT_USER_ENDPOINT)
        assert response.status_code == 401

    def test_invalid_jwt_token(self, env: AuthTestClient) -> None:
        response = env.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=env.mock_create_token_header(
                env.MOCK_JWK_TOKEN.token + "invalid_token"
            ),
        )
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "key,value", INVALID_CLAIMS.items(), ids=INVALID_CLAIMS.keys()
    )
    def test_invalid_claims(self, env: AuthTestClient, key: str, value: str) -> None:
        edited_token = env.MOCK_JWK_TOKEN.edit_claim(key, value)
        response = env.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=env.mock_create_token_header(edited_token),
        )
        assert response.status_code in (401, 403)

    @pytest.mark.parametrize("key,value", INVALID_JWK.items(), ids=INVALID_JWK.keys())
    def test_invalid_jwk(self, env: AuthTestClient, key: str, value: str) -> None:
        for idp_client in env.auth_service.idp_clients:
            if isinstance(idp_client, OidcClient):
                idp_client._load_keys = MagicMock(return_value=None)
            else:
                raise NotImplementedError
        edited_token = env.MOCK_JWK_TOKEN.edit_jwk(key, value)
        response = env.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=env.mock_create_token_header(edited_token),
        )
        assert response.status_code in (401, 403)


class TestOidcClientCredentials:
    """Test the OidcClient retrieve_jwt_with_client_credentials_flow method."""

    @pytest.fixture
    def oidc_client(self, env: AuthTestClient) -> OidcClient:
        """Get an OidcClient instance from the test environment."""
        for idp_client in env.auth_service.idp_clients:
            if isinstance(idp_client, OidcClient):
                return idp_client
        raise RuntimeError("No OidcClient found in test environment")

    @patch("httpx.Client")
    def test_successful_token_retrieval(
        self, mock_client_class: Mock, oidc_client: OidcClient
    ) -> None:
        """Test successful JWT token retrieval with client credentials flow."""
        # Setup mock HTTP client
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"access_token": "test_access_token_123"}
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Set up a valid token endpoint
        oidc_client.server_cfg.token_endpoint = "https://idp1.org/token"

        # Call the method (no await needed - method is now synchronous)
        result = oidc_client.retrieve_jwt_with_client_credentials_flow("openid")

        # Verify result
        assert result == "test_access_token_123"

        # Verify the HTTP request was made correctly
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://idp1.org/token"

        # Unpack request data
        # Split request_data string into a dict
        request_data = dict(x.split("=") for x in call_args[1]["data"].split("&"))
        # Extract client_id and client_secret from request_headers using basic auth
        auth_header = call_args[1]["headers"].get("Authorization", "")
        if auth_header.startswith("Basic "):
            auth_payload = base64.b64decode(auth_header[6:]).decode("utf-8")
            request_data["client_id"], request_data["client_secret"] = (
                auth_payload.split(":", 1)
            )

        # Check expected values
        assert request_data["grant_type"] == "client_credentials"
        assert request_data["scope"] == "openid"
        assert "client_id" in request_data
        assert "client_secret" in request_data

        # Verify headers
        request_headers = call_args[1]["headers"]
        assert request_headers["Content-Type"] == "application/x-www-form-urlencoded"

    @patch("httpx.Client")
    def test_http_error_with_retries(
        self, mock_client_class: Mock, oidc_client: OidcClient
    ) -> None:
        """Test that HTTP errors trigger retries and eventually raise ServiceUnavailableError."""
        # Setup mock HTTP client that always fails
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response
        )
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Set up a valid token endpoint
        oidc_client.server_cfg.token_endpoint = "https://idp1.org/token"

        # Mock time.sleep to speed up the test
        with patch("time.sleep") as mock_sleep:
            # Call the method and expect it to raise an exception
            with pytest.raises(exc.ServiceUnavailableError):
                oidc_client.retrieve_jwt_with_client_credentials_flow(
                    "openid", max_retries=2, base_delay=0.1
                )

            # Verify retries occurred (should be max_retries + 1 attempts = 3 total)
            assert mock_client.post.call_count == 3
            # Verify sleep was called between retries (2 times for 3 attempts)
            assert mock_sleep.call_count == 2

    @patch("httpx.Client")
    def test_missing_token_endpoint(
        self, mock_client_class: Mock, oidc_client: OidcClient
    ) -> None:
        """Test that missing token endpoint raises ServiceUnavailableError."""
        # Set token endpoint to None
        oidc_client.server_cfg.token_endpoint = None

        # Mock update_server_config_from_discovery to still have None token_endpoint
        with patch.object(
            oidc_client, "update_server_config_from_discovery"
        ) as mock_update:
            # Call the method and expect it to raise an exception
            with pytest.raises(
                exc.ServiceUnavailableError, match="Token endpoint URL is not set"
            ):
                oidc_client.retrieve_jwt_with_client_credentials_flow("openid")

            # Verify that discovery update was attempted
            mock_update.assert_called_once()

    @patch("httpx.Client")
    def test_invalid_response_format(
        self, mock_client_class: Mock, oidc_client: OidcClient
    ) -> None:
        """Test handling of invalid response format (missing access_token)."""
        # Setup mock HTTP client with invalid response
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "error": "invalid_request"
        }  # Missing access_token
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Set up a valid token endpoint
        oidc_client.server_cfg.token_endpoint = "https://idp1.org/token"

        # Mock time.sleep to speed up the test
        with patch("time.sleep"):
            # Call the method and expect it to raise an exception due to KeyError
            with pytest.raises(exc.ServiceUnavailableError):
                oidc_client.retrieve_jwt_with_client_credentials_flow("openid")

    @patch("httpx.Client")
    def test_network_failure(
        self, mock_client_class: Mock, oidc_client: OidcClient
    ) -> None:
        """Test handling of network failures during token retrieval."""
        # Setup mock HTTP client that raises a connection error
        mock_client = MagicMock()
        mock_client.post.side_effect = httpx.ConnectError("Connection failed")
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Set up a valid token endpoint
        oidc_client.server_cfg.token_endpoint = "https://idp1.org/token"

        # Mock time.sleep to speed up the test
        with patch("time.sleep") as mock_sleep:
            # Call the method and expect it to raise an exception
            with pytest.raises(exc.ServiceUnavailableError):
                oidc_client.retrieve_jwt_with_client_credentials_flow(
                    "openid", max_retries=1, base_delay=0.1
                )

            # Verify retries occurred
            assert mock_client.post.call_count == 2  # max_retries + 1
            assert mock_sleep.call_count == 1

    def test_custom_parameters(self, oidc_client: OidcClient) -> None:
        """Test that custom headers, max_retries, and base_delay are properly used."""
        custom_headers = {"Custom-Header": "test-value"}

        with patch("httpx.Client") as mock_client_class:
            # Setup mock HTTP client
            mock_client = MagicMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"access_token": "test_token"}
            mock_client.post.return_value = mock_response
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client

            # Set up a valid token endpoint
            oidc_client.server_cfg.token_endpoint = "https://idp1.org/token"

            # Call with custom parameters
            result = oidc_client.retrieve_jwt_with_client_credentials_flow(
                "custom_scope",
                headers=custom_headers,
                max_retries=5,
                base_delay=2.0,
            )

            # Verify result
            assert result == "test_token"

            # Verify custom headers were used
            call_args = mock_client.post.call_args
            request_headers = call_args[1]["headers"]
            assert request_headers["Custom-Header"] == "test-value"

            # Verify custom scope was used
            request_data = dict(x.split("=") for x in call_args[1]["data"].split("&"))
            assert request_data["scope"] == "custom_scope"

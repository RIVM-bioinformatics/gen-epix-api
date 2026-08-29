"""
Unit tests for OAuth 2.0 Validators

This module contains comprehensive pytest unit tests for the OAuth2Validator class
in validators.py. It tests all functionality including client authentication,
scope validation, token management, and oauthlib integration.

Run tests with:
    pytest test_validators.py -v
    pytest test_validators.py::TestOAuth2Validator -v
    pytest test_validators.py::TestOAuth2ValidatorIntegration -v
"""

import os
import sys
from test.test_client.oauth.client_store import Client, ClientStore
from test.test_client.oauth.token_store import Token, TokenStore
from test.test_client.oauth.validators import OAuth2Validator
from test.util.mock_compat import MagicMock
from typing import Any

import pytest

# Add the oauth directory to the path for imports
oauth_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, oauth_path)


class MockRequest:
    """Mock request object for testing."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize mock request with attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Allow setting arbitrary attributes."""
        object.__setattr__(self, name, value)

    def __getattr__(self, name: str) -> Any:
        """Allow getting arbitrary attributes, return None if not found."""
        # Avoid recursion by checking if the attribute actually exists
        if name in self.__dict__:
            return self.__dict__[name]
        return None


class TestOAuth2Validator:
    """Test cases for the OAuth2Validator class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.client_store = ClientStore()
        self.token_store = TokenStore()
        self.validator = OAuth2Validator(self.client_store, self.token_store)

        # Create test clients
        self.test_client1 = Client(
            client_id="test-client-1",
            client_secret="test-secret-1",
            client_name="Test Client 1",
            scopes=["read", "write"],
            grant_types=["client_credentials", "authorization_code"],
            redirect_uris=["https://example.com/callback"],
        )

        self.test_client2 = Client(
            client_id="test-client-2",
            client_secret="test-secret-2",
            client_name="Test Client 2",
            scopes=["admin"],
            grant_types=["client_credentials"],
        )

        # Store test clients
        self.client_store.store_client(self.test_client1)
        self.client_store.store_client(self.test_client2)

        # Create test tokens
        self.test_token1 = Token(
            access_token="test-access-token-1",
            token_type="Bearer",
            expires_in=3600,
            scope="read write",
            client_id="test-client-1",
            refresh_token="test-refresh-token-1",
        )

        self.test_token2 = Token(
            access_token="test-access-token-2",
            token_type="Bearer",
            expires_in=3600,
            scope="admin",
            client_id="test-client-2",
        )

        # Store test tokens
        self.token_store.store_token("test-access-token-1", self.test_token1)
        self.token_store.store_token("test-access-token-2", self.test_token2)

    def test_validator_initialization(self) -> None:
        """Test OAuth2Validator initialization."""
        validator = OAuth2Validator(self.client_store, self.token_store)

        assert validator.client_store == self.client_store
        assert validator.token_store == self.token_store

    def test_client_authentication_required_client_credentials(self) -> None:
        """Test client authentication requirement for client credentials flow."""
        request = MockRequest(grant_type="client_credentials")

        result = self.validator.client_authentication_required(request)

        assert result is True

    def test_client_authentication_required_other_grant_types(self) -> None:
        """Test client authentication requirement for other grant types."""
        request = MockRequest(grant_type="authorization_code")

        result = self.validator.client_authentication_required(request)

        assert result is False

    def test_authenticate_client_valid_credentials(self) -> None:
        """Test client authentication with valid credentials."""
        request = MockRequest(client_id="test-client-1", client_secret="test-secret-1")

        result = self.validator.authenticate_client(request)

        assert result is True
        assert hasattr(request, "client")
        assert request.client == self.test_client1

    def test_authenticate_client_invalid_client_id(self) -> None:
        """Test client authentication with invalid client ID."""
        request = MockRequest(
            client_id="nonexistent-client", client_secret="test-secret-1"
        )

        result = self.validator.authenticate_client(request)

        assert result is False

    def test_authenticate_client_invalid_secret(self) -> None:
        """Test client authentication with invalid secret."""
        request = MockRequest(client_id="test-client-1", client_secret="wrong-secret")

        result = self.validator.authenticate_client(request)

        assert result is False

    def test_authenticate_client_missing_credentials(self) -> None:
        """Test client authentication with missing credentials."""
        # Missing client_secret
        request1 = MockRequest(client_id="test-client-1")
        result1 = self.validator.authenticate_client(request1)
        assert result1 is False

        # Missing client_id
        request2 = MockRequest(client_secret="test-secret-1")
        result2 = self.validator.authenticate_client(request2)
        assert result2 is False

        # Missing both
        request3 = MockRequest()
        result3 = self.validator.authenticate_client(request3)
        assert result3 is False

    def test_validate_client_id_existing_client(self) -> None:
        """Test client ID validation for existing client."""
        request = MockRequest()

        result = self.validator.validate_client_id("test-client-1", request)

        assert result is True

    def test_validate_client_id_nonexistent_client(self) -> None:
        """Test client ID validation for non-existent client."""
        request = MockRequest()

        result = self.validator.validate_client_id("nonexistent-client", request)

        assert result is False

    def test_get_default_scopes_client_with_scopes(self) -> None:
        """Test getting default scopes for client with defined scopes."""
        request = MockRequest()

        result = self.validator.get_default_scopes("test-client-1", request)

        assert result == ["read"]  # First scope

    def test_get_default_scopes_client_without_scopes(self) -> None:
        """Test getting default scopes for client without defined scopes."""
        # Create client without scopes
        client_no_scopes = Client(
            client_id="no-scopes-client",
            client_secret="secret",
            client_name="No Scopes Client",
            scopes=[],
        )
        self.client_store.store_client(client_no_scopes)

        request = MockRequest()

        result = self.validator.get_default_scopes("no-scopes-client", request)

        assert result == []

    def test_get_default_scopes_nonexistent_client(self) -> None:
        """Test getting default scopes for non-existent client."""
        request = MockRequest()

        result = self.validator.get_default_scopes("nonexistent-client", request)

        assert result == []

    def test_validate_scopes_all_valid(self) -> None:
        """Test scope validation with all valid scopes."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.validate_scopes(
            "test-client-1", ["read", "write"], client, request
        )

        assert result is True

    def test_validate_scopes_some_invalid(self) -> None:
        """Test scope validation with some invalid scopes."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.validate_scopes(
            "test-client-1", ["read", "admin"], client, request
        )

        assert result is False

    def test_validate_scopes_empty_request(self) -> None:
        """Test scope validation with empty scope request."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.validate_scopes("test-client-1", [], client, request)

        assert result is True

    def test_validate_scopes_nonexistent_client(self) -> None:
        """Test scope validation for non-existent client."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.validate_scopes(
            "nonexistent-client", ["read"], client, request
        )

        assert result is False

    def test_validate_response_type(self) -> None:
        """Test response type validation (always returns True for client credentials)."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.validate_response_type(
            "test-client-1", "code", client, request
        )

        assert result is True

    def test_save_authorization_code(self) -> None:
        """Test saving authorization code (no-op for client credentials)."""
        request = MockRequest()

        # Should not raise exception
        self.validator.save_authorization_code("test-client-1", {}, request)

    def test_validate_code(self) -> None:
        """Test code validation (always False for client credentials)."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.validate_code("test-client-1", "code", client, request)

        assert result is False

    def test_confirm_redirect_uri(self) -> None:
        """Test redirect URI confirmation (always False for client credentials)."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.confirm_redirect_uri(
            "test-client-1", "code", "https://example.com", client, request
        )

        assert result is False

    def test_validate_grant_type_supported(self) -> None:
        """Test grant type validation for supported grant type."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.validate_grant_type(
            "test-client-1", "client_credentials", client, request
        )

        assert result is True

    def test_validate_grant_type_unsupported(self) -> None:
        """Test grant type validation for unsupported grant type."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.validate_grant_type(
            "test-client-2", "authorization_code", client, request
        )

        assert result is False

    def test_validate_grant_type_nonexistent_client(self) -> None:
        """Test grant type validation for non-existent client."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.validate_grant_type(
            "nonexistent-client", "client_credentials", client, request
        )

        assert result is False

    def test_save_bearer_token(self) -> None:
        """Test saving bearer token."""
        request = MockRequest(client_id="test-client-save")

        token_dict = {
            "access_token": "new-access-token",
            "token_type": "Bearer",
            "expires_in": 7200,
            "scope": "read write",
            "refresh_token": "new-refresh-token",
        }

        self.validator.save_bearer_token(token_dict, request)

        # Verify token was stored
        stored_token = self.token_store.get_token("new-access-token")
        assert stored_token is not None
        assert stored_token.access_token == "new-access-token"
        assert stored_token.token_type == "Bearer"
        assert stored_token.expires_in == 7200
        assert stored_token.scope == "read write"
        assert stored_token.client_id == "test-client-save"
        assert stored_token.refresh_token == "new-refresh-token"

    def test_save_bearer_token_minimal(self) -> None:
        """Test saving bearer token with minimal required fields."""
        request = MockRequest()

        token_dict = {"access_token": "minimal-token"}

        self.validator.save_bearer_token(token_dict, request)

        # Verify token was stored with defaults
        stored_token = self.token_store.get_token("minimal-token")
        assert stored_token is not None
        assert stored_token.access_token == "minimal-token"
        assert stored_token.token_type == "Bearer"
        assert stored_token.expires_in == 3600
        assert stored_token.scope == ""
        assert stored_token.client_id == ""  # Should be empty string due to `or ""`
        assert stored_token.refresh_token is None

    def test_revoke_token(self) -> None:
        """Test token revocation."""
        request = MockRequest()

        # Verify token exists
        assert self.token_store.get_token("test-access-token-1") is not None

        self.validator.revoke_token("test-access-token-1", request)

        # Verify token was deleted
        assert self.token_store.get_token("test-access-token-1") is None

    def test_validate_bearer_token_valid_with_scopes(self) -> None:
        """Test bearer token validation with required scopes."""
        request = MockRequest()

        result = self.validator.validate_bearer_token(
            "test-access-token-1", ["read"], request
        )

        assert result is True

    def test_validate_bearer_token_valid_without_scopes(self) -> None:
        """Test bearer token validation without required scopes."""
        request = MockRequest()

        result = self.validator.validate_bearer_token(
            "test-access-token-1", [], request
        )

        assert result is True

    def test_validate_bearer_token_insufficient_scopes(self) -> None:
        """Test bearer token validation with insufficient scopes."""
        request = MockRequest()

        result = self.validator.validate_bearer_token(
            "test-access-token-1", ["admin"], request
        )

        assert result is False

    def test_validate_bearer_token_nonexistent(self) -> None:
        """Test bearer token validation for non-existent token."""
        request = MockRequest()

        result = self.validator.validate_bearer_token(
            "nonexistent-token", ["read"], request
        )

        assert result is False

    def test_get_default_redirect_uri_with_uris(self) -> None:
        """Test getting default redirect URI for client with redirect URIs."""
        request = MockRequest()

        result = self.validator.get_default_redirect_uri("test-client-1", request)

        assert result == "https://example.com/callback"

    def test_get_default_redirect_uri_without_uris(self) -> None:
        """Test getting default redirect URI for client without redirect URIs."""
        request = MockRequest()

        result = self.validator.get_default_redirect_uri("test-client-2", request)

        assert result == ""

    def test_get_default_redirect_uri_nonexistent_client(self) -> None:
        """Test getting default redirect URI for non-existent client."""
        request = MockRequest()

        result = self.validator.get_default_redirect_uri("nonexistent-client", request)

        assert result == ""

    def test_validate_redirect_uri_valid(self) -> None:
        """Test redirect URI validation for valid URI."""
        request = MockRequest()

        result = self.validator.validate_redirect_uri(
            "test-client-1", "https://example.com/callback", request
        )

        assert result is True

    def test_validate_redirect_uri_invalid(self) -> None:
        """Test redirect URI validation for invalid URI."""
        request = MockRequest()

        result = self.validator.validate_redirect_uri(
            "test-client-1", "https://evil.com/callback", request
        )

        assert result is False

    def test_validate_redirect_uri_nonexistent_client(self) -> None:
        """Test redirect URI validation for non-existent client."""
        request = MockRequest()

        result = self.validator.validate_redirect_uri(
            "nonexistent-client", "https://example.com/callback", request
        )

        assert result is False

    def test_is_within_original_scope_valid(self) -> None:
        """Test scope checking within original scope."""
        request = MockRequest()

        result = self.validator.is_within_original_scope(
            ["read"], "test-refresh-token-1", request
        )

        assert result is True

    def test_is_within_original_scope_invalid(self) -> None:
        """Test scope checking outside original scope."""
        request = MockRequest()

        result = self.validator.is_within_original_scope(
            ["admin"], "test-refresh-token-1", request
        )

        assert result is False

    def test_is_within_original_scope_nonexistent_token(self) -> None:
        """Test scope checking for non-existent refresh token."""
        request = MockRequest()

        result = self.validator.is_within_original_scope(
            ["read"], "nonexistent-refresh-token", request
        )

        assert result is False

    def test_validate_refresh_token_valid(self) -> None:
        """Test refresh token validation for valid token."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.validate_refresh_token(
            "test-refresh-token-1", client, request
        )

        assert result is True

    def test_validate_refresh_token_invalid(self) -> None:
        """Test refresh token validation for invalid token."""
        request = MockRequest()
        client = MagicMock()

        result = self.validator.validate_refresh_token(
            "nonexistent-refresh-token", client, request
        )

        assert result is False

    def test_get_default_scopes_for_client_credentials(self) -> None:
        """Test getting default scopes for client credentials flow."""
        request = MockRequest()

        result = self.validator.get_default_scopes_for_client_credentials(
            "test-client-1", request
        )

        assert result == ["read"]  # First scope

    def test_introspect_token_active(self) -> None:
        """Test token introspection for active token."""
        request = MockRequest()

        result = self.validator.introspect_token("test-access-token-1", None, request)

        assert result["active"] is True
        assert result["client_id"] == "test-client-1"
        assert result["scope"] == "read write"
        assert result["token_type"] == "Bearer"
        assert result["sub"] == "test-client-1"
        assert "exp" in result
        assert "iat" in result

    def test_introspect_token_inactive(self) -> None:
        """Test token introspection for non-existent token."""
        request = MockRequest()

        result = self.validator.introspect_token("nonexistent-token", None, request)

        assert result == {"active": False}

    def test_introspect_token_with_hint(self) -> None:
        """Test token introspection with type hint."""
        request = MockRequest()

        result = self.validator.introspect_token(
            "test-access-token-1", "access_token", request
        )

        assert result["active"] is True
        assert result["client_id"] == "test-client-1"


class TestOAuth2ValidatorIntegration:
    """Integration tests for OAuth2Validator with real stores."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client_store = ClientStore()
        self.token_store = TokenStore()
        self.validator = OAuth2Validator(self.client_store, self.token_store)

    def test_full_client_credentials_flow(self) -> None:
        """Test complete client credentials flow validation."""
        # Create and store client
        client = self.client_store.create_client(
            client_name="Integration Test Client",
            scopes=["read", "write", "admin"],
            grant_types=["client_credentials"],
        )

        # Create request for authentication
        request = MockRequest(
            grant_type="client_credentials",
            client_id=client.client_id,
            client_secret="test-secret",  # Use plain secret for testing
        )

        # Override the client's hashed secret with plain text for this test
        original_secret = client.client_secret
        client.client_secret = "test-secret"

        # Test authentication requirement
        assert self.validator.client_authentication_required(request) is True

        # Test client ID validation
        assert self.validator.validate_client_id(client.client_id, request) is True

        # Test client authentication
        assert self.validator.authenticate_client(request) is True

        # Test grant type validation
        assert (
            self.validator.validate_grant_type(
                client.client_id, "client_credentials", None, request
            )
            is True
        )

        # Test scope validation
        assert (
            self.validator.validate_scopes(
                client.client_id, ["read", "write"], None, request
            )
            is True
        )

        # Test token saving
        token_dict = {
            "access_token": "integration-test-token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "read write",
        }

        self.validator.save_bearer_token(token_dict, request)

        # Test token validation
        assert (
            self.validator.validate_bearer_token(
                "integration-test-token", ["read"], request
            )
            is True
        )

        # Test token introspection
        introspection = self.validator.introspect_token(
            "integration-test-token", None, request
        )
        assert introspection["active"] is True
        assert introspection["client_id"] == client.client_id

        # Restore original secret
        client.client_secret = original_secret

    def test_scope_validation_edge_cases(self) -> None:
        """Test scope validation with various edge cases."""
        # Create client with specific scopes
        client = Client(
            client_id="scope-edge-client",
            client_secret="secret",
            client_name="Scope Edge Test",
            scopes=["read", "write", "user:profile"],
        )
        self.client_store.store_client(client)

        request = MockRequest()

        # Test exact scope match
        assert (
            self.validator.validate_scopes(
                "scope-edge-client", ["read", "write"], None, request
            )
            is True
        )

        # Test subset of scopes
        assert (
            self.validator.validate_scopes("scope-edge-client", ["read"], None, request)
            is True
        )

        # Test scope with special characters
        assert (
            self.validator.validate_scopes(
                "scope-edge-client", ["user:profile"], None, request
            )
            is True
        )

        # Test superset of scopes
        assert (
            self.validator.validate_scopes(
                "scope-edge-client", ["read", "write", "admin"], None, request
            )
            is False
        )

        # Test completely different scopes
        assert (
            self.validator.validate_scopes(
                "scope-edge-client", ["admin", "delete"], None, request
            )
            is False
        )

    def test_token_lifecycle_management(self) -> None:
        """Test complete token lifecycle: create, validate, revoke."""
        # Create client
        client = self.client_store.create_client(
            client_name="Token Lifecycle Client", scopes=["read", "write"]
        )

        request = MockRequest(client_id=client.client_id)

        # Create and save token
        token_dict = {
            "access_token": "lifecycle-token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "read write",
            "refresh_token": "lifecycle-refresh-token",
        }

        self.validator.save_bearer_token(token_dict, request)

        # Validate token exists and works
        assert (
            self.validator.validate_bearer_token("lifecycle-token", ["read"], request)
            is True
        )

        # Test refresh token validation
        assert (
            self.validator.validate_refresh_token(
                "lifecycle-refresh-token", None, request
            )
            is True
        )

        # Test scope checking with refresh token
        assert (
            self.validator.is_within_original_scope(
                ["read"], "lifecycle-refresh-token", request
            )
            is True
        )

        # Revoke token
        self.validator.revoke_token("lifecycle-token", request)

        # Verify token is gone
        assert (
            self.validator.validate_bearer_token("lifecycle-token", ["read"], request)
            is False
        )

        # Verify introspection shows inactive
        introspection = self.validator.introspect_token(
            "lifecycle-token", None, request
        )
        assert introspection["active"] is False

    def test_redirect_uri_validation_comprehensive(self) -> None:
        """Test comprehensive redirect URI validation scenarios."""
        # Create client with multiple redirect URIs
        client = Client(
            client_id="redirect-test-client",
            client_secret="secret",
            client_name="Redirect Test Client",
            redirect_uris=[
                "https://app.example.com/callback",
                "https://app.example.com/auth/callback",
                "http://localhost:3000/callback",
            ],
        )
        self.client_store.store_client(client)

        request = MockRequest()

        # Test all valid URIs
        valid_uris = [
            "https://app.example.com/callback",
            "https://app.example.com/auth/callback",
            "http://localhost:3000/callback",
        ]

        for uri in valid_uris:
            assert (
                self.validator.validate_redirect_uri(
                    "redirect-test-client", uri, request
                )
                is True
            )

        # Test invalid URIs
        invalid_uris = [
            "https://evil.com/callback",
            "https://app.example.com/different",
            "http://localhost:8080/callback",
            "",
        ]

        for uri in invalid_uris:
            assert (
                self.validator.validate_redirect_uri(
                    "redirect-test-client", uri, request
                )
                is False
            )

        # Test default redirect URI
        default_uri = self.validator.get_default_redirect_uri(
            "redirect-test-client", request
        )
        assert default_uri == "https://app.example.com/callback"

    def test_error_handling_and_edge_cases(self) -> None:
        """Test error handling and edge cases across all validator methods."""
        request = MockRequest()

        # Test with completely empty stores
        empty_client_store = ClientStore()
        empty_token_store = TokenStore()
        empty_validator = OAuth2Validator(empty_client_store, empty_token_store)

        # All validations should fail gracefully
        assert empty_validator.validate_client_id("any-client", request) is False
        assert empty_validator.get_default_scopes("any-client", request) == []
        assert (
            empty_validator.validate_scopes("any-client", ["read"], None, request)
            is False
        )
        assert (
            empty_validator.validate_grant_type(
                "any-client", "client_credentials", None, request
            )
            is False
        )
        assert (
            empty_validator.validate_bearer_token("any-token", ["read"], request)
            is False
        )
        assert empty_validator.get_default_redirect_uri("any-client", request) == ""
        assert (
            empty_validator.validate_redirect_uri(
                "any-client", "https://example.com", request
            )
            is False
        )
        assert (
            empty_validator.is_within_original_scope(["read"], "any-token", request)
            is False
        )
        assert (
            empty_validator.validate_refresh_token("any-token", None, request) is False
        )

        # Test introspection with empty store
        introspection = empty_validator.introspect_token("any-token", None, request)
        assert introspection == {"active": False}


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])

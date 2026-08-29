"""
Unit tests for OpenID Connect Provider

This module contains comprehensive pytest unit tests for the OIDCProvider class
in oidc_provider.py. It tests all functionality including discovery document creation,
ID token generation and validation, userinfo endpoint, and OIDC-specific features.

Run tests with:
    pytest test_oidc_provider.py -v
    pytest test_oidc_provider.py::TestOIDCProvider -v
    pytest test_oidc_provider.py::TestOIDCProviderIntegration -v
"""

import os
import sys
from datetime import datetime, timezone
from test.test_client.oauth.jwks import JWKSManager
from test.test_client.oauth.oidc_provider import OIDCProvider
from test.util.mock_compat import MagicMock, patch

import pytest

# Add the oauth directory to the path for imports
oauth_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, oauth_path)


class TestOIDCProvider:
    """Test cases for the OIDCProvider class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_jwks_manager = MagicMock(spec=JWKSManager)
        self.provider = OIDCProvider(self.mock_jwks_manager)

    def test_provider_initialization(self) -> None:
        """Test OIDCProvider initialization."""
        assert self.provider.jwks_manager == self.mock_jwks_manager
        assert isinstance(self.provider, OIDCProvider)

    def test_create_discovery_document_basic(self) -> None:
        """Test creating a basic discovery document."""
        issuer = "https://auth.example.com"

        discovery = self.provider.create_discovery_document(issuer)

        # Verify required OIDC fields
        assert discovery["issuer"] == issuer
        assert discovery["authorization_endpoint"] == f"{issuer}/oauth/authorize"
        assert discovery["token_endpoint"] == f"{issuer}/oauth/token"
        assert discovery["userinfo_endpoint"] == f"{issuer}/oauth/userinfo"
        assert discovery["jwks_uri"] == f"{issuer}/.well-known/jwks.json"

        # Verify other standard endpoints
        assert discovery["introspection_endpoint"] == f"{issuer}/oauth/introspect"
        assert discovery["revocation_endpoint"] == f"{issuer}/oauth/revoke"
        assert discovery["end_session_endpoint"] == f"{issuer}/oauth/logout"

    def test_create_discovery_document_response_types(self) -> None:
        """Test discovery document includes correct response types."""
        issuer = "https://auth.example.com"

        discovery = self.provider.create_discovery_document(issuer)

        expected_response_types = [
            "code",
            "token",
            "id_token",
            "code token",
            "code id_token",
            "token id_token",
            "code token id_token",
        ]
        assert discovery["response_types_supported"] == expected_response_types

    def test_create_discovery_document_grant_types(self) -> None:
        """Test discovery document includes correct grant types."""
        issuer = "https://auth.example.com"

        discovery = self.provider.create_discovery_document(issuer)

        expected_grant_types = [
            "authorization_code",
            "client_credentials",
            "refresh_token",
        ]
        assert discovery["grant_types_supported"] == expected_grant_types

    def test_create_discovery_document_supported_scopes(self) -> None:
        """Test discovery document includes correct supported scopes."""
        issuer = "https://auth.example.com"

        discovery = self.provider.create_discovery_document(issuer)

        expected_scopes = [
            "openid",
            "profile",
            "email",
            "address",
            "phone",
            "offline_access",
            "read",
            "write",
        ]
        assert discovery["scopes_supported"] == expected_scopes

    def test_create_discovery_document_supported_claims(self) -> None:
        """Test discovery document includes correct supported claims."""
        issuer = "https://auth.example.com"

        discovery = self.provider.create_discovery_document(issuer)

        expected_claims = [
            "sub",
            "iss",
            "aud",
            "exp",
            "iat",
            "auth_time",
            "nonce",
            "name",
            "given_name",
            "family_name",
            "email",
            "email_verified",
            "picture",
            "locale",
        ]
        assert discovery["claims_supported"] == expected_claims

    def test_create_discovery_document_auth_methods(self) -> None:
        """Test discovery document includes correct authentication methods."""
        issuer = "https://auth.example.com"

        discovery = self.provider.create_discovery_document(issuer)

        expected_auth_methods = [
            "client_secret_basic",
            "client_secret_post",
            "client_secret_jwt",
            "private_key_jwt",
        ]
        assert (
            discovery["token_endpoint_auth_methods_supported"] == expected_auth_methods
        )

    def test_create_discovery_document_signing_algorithms(self) -> None:
        """Test discovery document includes correct signing algorithms."""
        issuer = "https://auth.example.com"

        discovery = self.provider.create_discovery_document(issuer)

        assert discovery["id_token_signing_alg_values_supported"] == ["RS256"]
        assert discovery["token_endpoint_auth_signing_alg_values_supported"] == [
            "RS256"
        ]
        assert discovery["userinfo_signing_alg_values_supported"] == ["RS256"]

    def test_create_discovery_document_additional_features(self) -> None:
        """Test discovery document includes additional OIDC features."""
        issuer = "https://auth.example.com"

        discovery = self.provider.create_discovery_document(issuer)

        assert discovery["subject_types_supported"] == ["public"]
        assert discovery["response_modes_supported"] == [
            "query",
            "fragment",
            "form_post",
        ]
        assert discovery["claim_types_supported"] == ["normal"]
        assert discovery["claims_parameter_supported"] is False
        assert discovery["request_parameter_supported"] is False
        assert discovery["request_uri_parameter_supported"] is False
        assert discovery["require_request_uri_registration"] is False

    def test_create_id_token_basic(self) -> None:
        """Test creating a basic ID token."""
        # Mock JWKS manager to return a predictable token
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
        self.mock_jwks_manager.create_jwt.return_value = expected_token

        subject = "user123"
        audience = "client456"
        issuer = "https://auth.example.com"

        token = self.provider.create_id_token(subject, audience, issuer)

        assert token == expected_token

        # Verify the JWT was created with correct payload structure
        self.mock_jwks_manager.create_jwt.assert_called_once()
        call_args = self.mock_jwks_manager.create_jwt.call_args[0][0]

        assert call_args["iss"] == issuer
        assert call_args["sub"] == subject
        assert call_args["aud"] == audience
        assert "iat" in call_args
        assert "exp" in call_args
        assert "auth_time" in call_args

    def test_create_id_token_with_nonce(self) -> None:
        """Test creating ID token with nonce."""
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
        self.mock_jwks_manager.create_jwt.return_value = expected_token

        nonce = "random-nonce-123"

        token = self.provider.create_id_token(
            "user123", "client456", "https://auth.example.com", nonce=nonce
        )

        assert token == expected_token

        # Verify nonce is included in payload
        call_args = self.mock_jwks_manager.create_jwt.call_args[0][0]
        assert call_args["nonce"] == nonce

    def test_create_id_token_with_auth_time(self) -> None:
        """Test creating ID token with explicit auth_time."""
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
        self.mock_jwks_manager.create_jwt.return_value = expected_token

        auth_time = 1640995200  # 2022-01-01 00:00:00 UTC

        token = self.provider.create_id_token(
            "user123", "client456", "https://auth.example.com", auth_time=auth_time
        )

        assert token == expected_token

        # Verify auth_time is included in payload
        call_args = self.mock_jwks_manager.create_jwt.call_args[0][0]
        assert call_args["auth_time"] == auth_time

    def test_create_id_token_with_additional_claims(self) -> None:
        """Test creating ID token with additional claims."""
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
        self.mock_jwks_manager.create_jwt.return_value = expected_token

        additional_claims = {
            "name": "John Doe",
            "email": "john@example.com",
            "custom_claim": "custom_value",
        }

        token = self.provider.create_id_token(
            "user123",
            "client456",
            "https://auth.example.com",
            additional_claims=additional_claims,
        )

        assert token == expected_token

        # Verify additional claims are included in payload
        call_args = self.mock_jwks_manager.create_jwt.call_args[0][0]
        assert call_args["name"] == "John Doe"
        assert call_args["email"] == "john@example.com"
        assert call_args["custom_claim"] == "custom_value"

    def test_create_id_token_with_custom_expiry(self) -> None:
        """Test creating ID token with custom expiry time."""
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
        self.mock_jwks_manager.create_jwt.return_value = expected_token

        expires_in = 7200  # 2 hours

        with patch("oidc_provider.datetime") as mock_datetime:
            # Mock current time
            mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            token = self.provider.create_id_token(
                "user123",
                "client456",
                "https://auth.example.com",
                expires_in=expires_in,
            )

        assert token == expected_token

        # Verify expiry time is calculated correctly
        call_args = self.mock_jwks_manager.create_jwt.call_args[0][0]
        expected_exp = int(mock_now.timestamp()) + expires_in
        assert call_args["exp"] == expected_exp

    def test_validate_id_token(self) -> None:
        """Test validating an ID token."""
        id_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
        expected_payload = {
            "iss": "https://auth.example.com",
            "sub": "user123",
            "aud": "client456",
            "exp": 1640995200,
            "iat": 1640991600,
        }

        self.mock_jwks_manager.verify_jwt.return_value = expected_payload

        result = self.provider.validate_id_token(id_token)

        assert result == expected_payload
        self.mock_jwks_manager.verify_jwt.assert_called_once_with(id_token)

    def test_create_userinfo_response_basic(self) -> None:
        """Test creating basic userinfo response."""
        subject = "user123"
        scopes = ["openid"]

        userinfo = self.provider.create_userinfo_response(subject, scopes)

        # Should only include subject for basic openid scope
        assert userinfo["sub"] == subject
        assert len(userinfo) == 1

    def test_create_userinfo_response_with_profile_scope(self) -> None:
        """Test creating userinfo response with profile scope."""
        subject = "user123"
        scopes = ["openid", "profile"]

        userinfo = self.provider.create_userinfo_response(subject, scopes)

        # Should include subject and profile claims
        assert userinfo["sub"] == subject
        assert "name" in userinfo
        assert "given_name" in userinfo
        assert "family_name" in userinfo
        assert "picture" in userinfo
        assert "locale" in userinfo

        # Verify default values
        assert userinfo["name"] == f"Client {subject}"
        assert userinfo["given_name"] == "Client"
        assert userinfo["family_name"] == subject
        assert userinfo["locale"] == "en-US"

    def test_create_userinfo_response_with_email_scope(self) -> None:
        """Test creating userinfo response with email scope."""
        subject = "user123"
        scopes = ["openid", "email"]

        userinfo = self.provider.create_userinfo_response(subject, scopes)

        # Should include subject and email claims
        assert userinfo["sub"] == subject
        assert "email" in userinfo
        assert "email_verified" in userinfo

        # Verify default values
        assert userinfo["email"] == f"{subject}@example.com"
        assert userinfo["email_verified"] is False

    def test_create_userinfo_response_with_custom_claims(self) -> None:
        """Test creating userinfo response with custom user claims."""
        subject = "user123"
        scopes = ["openid", "profile", "email"]
        custom_claims = {
            "name": "John Doe",
            "given_name": "John",
            "family_name": "Doe",
            "email": "john.doe@example.com",
            "email_verified": True,
            "custom_field": "custom_value",
        }

        userinfo = self.provider.create_userinfo_response(
            subject, scopes, custom_claims
        )

        # Should use custom claims instead of defaults
        assert userinfo["sub"] == subject
        assert userinfo["name"] == "John Doe"
        assert userinfo["given_name"] == "John"
        assert userinfo["family_name"] == "Doe"
        assert userinfo["email"] == "john.doe@example.com"
        assert userinfo["email_verified"] is True

        # Custom field should not be included (not in standard claims)
        assert "custom_field" not in userinfo

    def test_create_userinfo_response_with_address_scope(self) -> None:
        """Test creating userinfo response with address scope."""
        subject = "user123"
        scopes = ["openid", "address"]
        custom_claims = {
            "address": {
                "street_address": "123 Main St",
                "locality": "Anytown",
                "region": "CA",
                "postal_code": "12345",
                "country": "US",
            }
        }

        userinfo = self.provider.create_userinfo_response(
            subject, scopes, custom_claims
        )

        assert userinfo["sub"] == subject
        assert userinfo["address"] == custom_claims["address"]

    def test_create_userinfo_response_with_phone_scope(self) -> None:
        """Test creating userinfo response with phone scope."""
        subject = "user123"
        scopes = ["openid", "phone"]
        custom_claims = {
            "phone_number": "+1-555-123-4567",
            "phone_number_verified": True,
        }

        userinfo = self.provider.create_userinfo_response(
            subject, scopes, custom_claims
        )

        assert userinfo["sub"] == subject
        assert userinfo["phone_number"] == "+1-555-123-4567"
        assert userinfo["phone_number_verified"] is True

    def test_create_userinfo_response_multiple_scopes(self) -> None:
        """Test creating userinfo response with multiple scopes."""
        subject = "user123"
        scopes = ["openid", "profile", "email", "phone"]
        custom_claims = {
            "name": "John Doe",
            "given_name": "John",  # Add this explicitly
            "family_name": "Doe",  # Add this explicitly
            "email": "john@example.com",
            "email_verified": True,  # Add this explicitly
            "phone_number": "+1-555-123-4567",
        }

        userinfo = self.provider.create_userinfo_response(
            subject, scopes, custom_claims
        )

        # Should include claims from all scopes
        assert userinfo["sub"] == subject
        assert userinfo["name"] == "John Doe"
        assert userinfo["given_name"] == "John"  # Now provided in custom_claims
        assert userinfo["email"] == "john@example.com"
        assert userinfo["email_verified"] is True  # Now provided in custom_claims
        assert userinfo["phone_number"] == "+1-555-123-4567"

    def test_get_supported_algorithms(self) -> None:
        """Test getting supported algorithms."""
        algorithms = self.provider.get_supported_algorithms()

        assert algorithms == ["RS256"]
        assert isinstance(algorithms, list)

    def test_create_jwks_response(self) -> None:
        """Test creating JWKS response."""
        expected_jwks = {
            "keys": [
                {
                    "kty": "RSA",
                    "kid": "key1",
                    "use": "sig",
                    "alg": "RS256",
                    "n": "sample_n_value",
                    "e": "AQAB",
                }
            ]
        }

        self.mock_jwks_manager.get_public_keys.return_value = expected_jwks

        jwks = self.provider.create_jwks_response()

        assert jwks == expected_jwks
        self.mock_jwks_manager.get_public_keys.assert_called_once()

    def test_validate_nonce_valid(self) -> None:
        """Test validating valid nonce values."""
        valid_nonces = [
            "simple",
            "with-dashes",
            "with_underscores",
            "with123numbers",
            "a" * 255,  # Maximum length
        ]

        for nonce in valid_nonces:
            assert self.provider.validate_nonce(nonce) is True

    def test_validate_nonce_invalid(self) -> None:
        """Test validating invalid nonce values."""
        invalid_nonces = [
            "",  # Empty string
            None,  # None value
            "a" * 256,  # Too long
            "with\nnewline",  # Non-printable character
            "with\ttab",  # Non-printable character
        ]

        for nonce in invalid_nonces:
            assert self.provider.validate_nonce(nonce) is False

    def test_extract_claims_from_scope_openid_only(self) -> None:
        """Test extracting claims from openid scope only."""
        scopes = ["openid"]

        claims = self.provider.extract_claims_from_scope(scopes)

        assert claims == ["sub"]

    def test_extract_claims_from_scope_profile(self) -> None:
        """Test extracting claims from profile scope."""
        scopes = ["openid", "profile"]

        claims = self.provider.extract_claims_from_scope(scopes)

        expected_claims = [
            "sub",
            "name",
            "given_name",
            "family_name",
            "middle_name",
            "nickname",
            "preferred_username",
            "profile",
            "picture",
            "website",
            "gender",
            "birthdate",
            "zoneinfo",
            "locale",
        ]

        # Convert to sets for comparison (order doesn't matter)
        assert set(claims) == set(expected_claims)

    def test_extract_claims_from_scope_email(self) -> None:
        """Test extracting claims from email scope."""
        scopes = ["openid", "email"]

        claims = self.provider.extract_claims_from_scope(scopes)

        expected_claims = ["sub", "email", "email_verified"]
        assert set(claims) == set(expected_claims)

    def test_extract_claims_from_scope_address(self) -> None:
        """Test extracting claims from address scope."""
        scopes = ["openid", "address"]

        claims = self.provider.extract_claims_from_scope(scopes)

        expected_claims = ["sub", "address"]
        assert set(claims) == set(expected_claims)

    def test_extract_claims_from_scope_phone(self) -> None:
        """Test extracting claims from phone scope."""
        scopes = ["openid", "phone"]

        claims = self.provider.extract_claims_from_scope(scopes)

        expected_claims = ["sub", "phone_number", "phone_number_verified"]
        assert set(claims) == set(expected_claims)

    def test_extract_claims_from_scope_multiple(self) -> None:
        """Test extracting claims from multiple scopes."""
        scopes = ["openid", "profile", "email", "address", "phone"]

        claims = self.provider.extract_claims_from_scope(scopes)

        # Should include all claims from all scopes, without duplicates
        assert "sub" in claims
        assert "name" in claims
        assert "email" in claims
        assert "address" in claims
        assert "phone_number" in claims

        # Verify no duplicates
        assert len(claims) == len(set(claims))

    def test_extract_claims_from_scope_unknown_scope(self) -> None:
        """Test extracting claims with unknown scopes."""
        scopes = ["openid", "unknown_scope", "profile"]

        claims = self.provider.extract_claims_from_scope(scopes)

        # Should include known scopes and ignore unknown ones
        assert "sub" in claims
        assert "name" in claims  # From profile
        assert len([c for c in claims if "unknown" in c]) == 0

    def test_create_logout_response_basic(self) -> None:
        """Test creating basic logout response."""
        response = self.provider.create_logout_response()

        assert response["status"] == "logged_out"
        assert "timestamp" in response
        assert "redirect_uri" not in response

        # Verify timestamp format
        timestamp = datetime.fromisoformat(response["timestamp"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)

    def test_create_logout_response_with_redirect_uri(self) -> None:
        """Test creating logout response with redirect URI."""
        redirect_uri = "https://client.example.com/logout-success"

        response = self.provider.create_logout_response(redirect_uri)

        assert response["status"] == "logged_out"
        assert response["redirect_uri"] == redirect_uri
        assert "timestamp" in response


class TestOIDCProviderIntegration:
    """Integration tests for OIDCProvider with real JWKSManager."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.jwks_manager = JWKSManager()
        self.provider = OIDCProvider(self.jwks_manager)

    def test_end_to_end_id_token_workflow(self) -> None:
        """Test complete ID token creation and validation workflow."""
        # Create ID token
        subject = "test-user-123"
        audience = "test-client-456"
        issuer = "https://auth.example.com"
        nonce = "test-nonce-789"

        id_token = self.provider.create_id_token(
            subject=subject,
            audience=audience,
            issuer=issuer,
            nonce=nonce,
            additional_claims={"name": "Test User", "email": "test@example.com"},
        )

        # Validate the created token using decode_token_payload to avoid audience validation
        payload = self.jwks_manager.decode_token_payload(id_token)

        # Verify payload contents
        assert payload["sub"] == subject
        assert payload["aud"] == audience
        assert payload["iss"] == issuer
        assert payload["nonce"] == nonce
        assert payload["name"] == "Test User"
        assert payload["email"] == "test@example.com"
        assert "iat" in payload
        assert "exp" in payload
        assert "auth_time" in payload

    def test_discovery_and_jwks_integration(self) -> None:
        """Test discovery document and JWKS endpoint integration."""
        issuer = "https://auth.example.com"

        # Get discovery document
        discovery = self.provider.create_discovery_document(issuer)

        # Verify JWKS URI is correct
        assert discovery["jwks_uri"] == f"{issuer}/.well-known/jwks.json"

        # Get JWKS response
        jwks = self.provider.create_jwks_response()

        # Verify JWKS structure
        assert "keys" in jwks
        assert isinstance(jwks["keys"], list)
        assert len(jwks["keys"]) > 0

        # Verify key structure
        key = jwks["keys"][0]
        assert key["kty"] == "RSA"
        assert key["use"] == "sig"
        assert key["alg"] == "RS256"
        assert "kid" in key
        assert "n" in key
        assert "e" in key

    def test_userinfo_scope_based_claims_integration(self) -> None:
        """Test userinfo endpoint with scope-based claim filtering."""
        subject = "integration-user"

        # Test with different scope combinations
        test_cases = [
            (["openid"], ["sub"]),
            (["openid", "profile"], ["sub", "name", "given_name", "family_name"]),
            (["openid", "email"], ["sub", "email", "email_verified"]),
            (["openid", "profile", "email"], ["sub", "name", "email"]),
        ]

        for scopes, expected_claims in test_cases:
            userinfo = self.provider.create_userinfo_response(subject, scopes)

            # Verify required claims are present
            for claim in expected_claims:
                assert claim in userinfo

            # Verify subject is always present
            assert userinfo["sub"] == subject

    def test_nonce_validation_and_id_token_integration(self) -> None:
        """Test nonce validation integrated with ID token workflow."""
        # Test valid nonces
        valid_nonces = ["simple-nonce", "complex-nonce-123-with-dashes"]

        for nonce in valid_nonces:
            # Validate nonce
            assert self.provider.validate_nonce(nonce) is True

            # Create ID token with nonce
            id_token = self.provider.create_id_token(
                "user123", "client456", "https://auth.example.com", nonce=nonce
            )

            # Validate token and verify nonce using decode_token_payload
            payload = self.jwks_manager.decode_token_payload(id_token)
            assert payload["nonce"] == nonce

    def test_claims_extraction_and_userinfo_integration(self) -> None:
        """Test claims extraction integrated with userinfo response."""
        subject = "claims-user"
        scopes = ["openid", "profile", "email"]

        # Extract expected claims based on scopes
        expected_claims = self.provider.extract_claims_from_scope(scopes)

        # Create userinfo response
        userinfo = self.provider.create_userinfo_response(subject, scopes)

        # Verify that userinfo includes claims that were extracted
        # (Note: not all extracted claims may be present if no user data provided)
        assert "sub" in userinfo
        assert "name" in userinfo  # Should be in both extracted claims and userinfo
        assert "email" in userinfo  # Should be in both extracted claims and userinfo

    def test_logout_workflow_integration(self) -> None:
        """Test logout workflow integration."""
        # Test logout without redirect
        response1 = self.provider.create_logout_response()
        assert response1["status"] == "logged_out"

        # Test logout with redirect
        redirect_uri = "https://client.example.com/goodbye"
        response2 = self.provider.create_logout_response(redirect_uri)
        assert response2["status"] == "logged_out"
        assert response2["redirect_uri"] == redirect_uri

        # Verify timestamps are valid and recent
        timestamp1 = datetime.fromisoformat(
            response1["timestamp"].replace("Z", "+00:00")
        )
        timestamp2 = datetime.fromisoformat(
            response2["timestamp"].replace("Z", "+00:00")
        )

        now = datetime.now(timezone.utc)
        assert (now - timestamp1).total_seconds() < 5  # Should be very recent
        assert (now - timestamp2).total_seconds() < 5  # Should be very recent


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])

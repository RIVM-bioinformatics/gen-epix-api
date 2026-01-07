"""
Test OAuth OIDC Client Credential Authentication Flow

This module implements a comprehensive test for the OAuth 2.0 Client Credentials flow
as described in RFC 6749 Section 4.4: https://datatracker.ietf.org/doc/html/rfc6749#section-4.4

Test scenario:
1. Start OAuth server on port 9000
2. Add a machine-to-machine (M2M) app identity called RequestorApp with audience ReceiverApp
3. Create ReceiverApp FastAPI app with OIDC client and protected endpoint
4. Start ReceiverApp on port 9001
5. Create RequestorApp class with OIDC client
6. RequestorApp gets access token and calls ReceiverApp endpoint (success case)
7. RequestorApp uses invalid token to call ReceiverApp endpoint (failure case)
"""

import asyncio
import base64
import json
import logging
import time
from collections.abc import Generator
from test.end_to_end.client_credential_flow.apps import (  # pylint: disable=import-error
    RequestorApp,
)
from test.test_client.enum import ServerType
from test.test_client.server_manager import ServerManager
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import httpx
import jwt
import pytest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def oauth_server() -> Generator[ServerManager, None, None]:
    """Start and manage OAuth server for the test session."""
    with ServerManager(service=ServerType.OAUTH, port=8080) as server:
        if not server.start():
            pytest.fail("Failed to start OAuth server")

        # Create demo clients
        import httpx

        # Create demo-client
        demo_client_data = {
            "client_id": "demo-client",
            "client_secret": "demo-secret",
            "client_name": "Demo Client",
            "scopes": ["read", "write", "openid", "profile"],
            "grant_types": ["client_credentials"],
            "redirect_uris": [],
            "audience": None,
        }

        # Create test-client
        test_client_data = {
            "client_id": "test-client",
            "client_secret": "test-secret",
            "client_name": "Test Client",
            "scopes": ["read", "openid"],
            "grant_types": ["client_credentials"],
            "redirect_uris": [],
            "audience": None,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                # Create demo client
                response = client.post(
                    f"{server.base_url}/admin/clients", json=demo_client_data
                )
                if response.status_code not in [201, 409]:  # 409 = already exists
                    logger.warning(
                        f"Failed to create demo client: {response.status_code}"
                    )

                # Create test client
                response = client.post(
                    f"{server.base_url}/admin/clients", json=test_client_data
                )
                if response.status_code not in [201, 409]:  # 409 = already exists
                    logger.warning(
                        f"Failed to create test client: {response.status_code}"
                    )

        except Exception as e:
            logger.warning(f"Failed to create demo clients: {e}")

        # Add M2M client for RequestorApp
        if not server.add_client(
            client_id="RequestorApp",
            client_secret="requestor_app_secret",
            audience="ReceiverApp",
        ):
            pytest.fail("Failed to add M2M client")

        yield server


@pytest.fixture(scope="session")
def receiver_app(
    oauth_server: ServerManager,  # pylint: disable=redefined-outer-name
) -> Generator[ServerManager, None, None]:
    """Start and manage ReceiverApp for the test session."""
    discovery_url = oauth_server.get_discovery_url()

    with ServerManager(
        service=ServerType.OAUTH_RECEIVER, port=9001, oauth_discovery_url=discovery_url
    ) as app:
        if not app.start():
            pytest.fail("Failed to start ReceiverApp")
        yield app


@pytest.fixture(scope="session")
def requestor_app(
    oauth_server: ServerManager,  # pylint: disable=redefined-outer-name
) -> RequestorApp:
    """Create RequestorApp instance."""
    discovery_url = oauth_server.get_discovery_url()

    return RequestorApp(
        client_id="RequestorApp",
        client_secret="requestor_app_secret",
        oauth_discovery_url=discovery_url,
    )


def test_oauth_client_credentials_flow_success(
    oauth_server: ServerManager,  # pylint: disable=redefined-outer-name
    receiver_app: ServerManager,  # pylint: disable=redefined-outer-name
    requestor_app: RequestorApp,  # pylint: disable=redefined-outer-name
) -> None:
    """Test successful OAuth Client Credentials flow."""

    # Step 1: RequestorApp gets access token for ReceiverApp
    access_token = requestor_app.get_access_token("ReceiverApp")

    # Step 2: RequestorApp calls protected endpoint on ReceiverApp
    endpoint_url = f"{receiver_app.base_url}/test_client_credential_flow"
    response = requestor_app.call_protected_endpoint(endpoint_url, access_token)

    # Step 3: Verify successful response
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"

    response_data = response.json()
    assert response_data["status"] == "OK", "Should receive OK status"
    assert (
        "Authentication successful" in response_data["message"]
    ), "Should contain success message"

    logger.info("✅ Successful OAuth Client Credentials flow test passed")


def test_oauth_client_credentials_flow_invalid_token(
    oauth_server: ServerManager,  # pylint: disable=redefined-outer-name,unused-argument
    receiver_app: ServerManager,  # pylint: disable=redefined-outer-name
    requestor_app: RequestorApp,  # pylint: disable=redefined-outer-name
) -> None:
    """Test OAuth Client Credentials flow with invalid token."""

    # Step 1: Create invalid token
    invalid_token = requestor_app.create_invalid_token("ReceiverApp")

    # Step 2: Try to call protected endpoint with invalid token
    endpoint_url = f"{receiver_app.base_url}/test_client_credential_flow"
    response = requestor_app.call_protected_endpoint(endpoint_url, invalid_token)

    # Step 3: Verify unauthorized response
    assert (
        response.status_code == 401
    ), f"Expected 401, got {response.status_code}: {response.text}"

    logger.info("✅ Invalid token test passed")


def test_oauth_client_credentials_flow_missing_token(
    receiver_app: ServerManager,  # pylint: disable=redefined-outer-name
) -> None:
    """Test OAuth Client Credentials flow with missing token."""

    # Call protected endpoint without token
    endpoint_url = f"{receiver_app.base_url}/test_client_credential_flow"

    with httpx.Client() as client:
        response = client.get(endpoint_url, timeout=10.0)

    # Should receive 401 due to missing Bearer token
    assert (
        response.status_code == 401
    ), f"Expected 401, got {response.status_code}: {response.text}"

    logger.info("✅ Missing token test passed")


def test_oauth_discovery_endpoint(
    oauth_server: ServerManager,  # pylint: disable=redefined-outer-name
) -> None:
    """Test that OAuth discovery endpoint is working."""

    discovery_url = oauth_server.get_discovery_url()

    with httpx.Client() as client:
        response = client.get(discovery_url)

    assert response.status_code == 200
    discovery_data = response.json()

    # Verify required OIDC discovery fields
    required_fields = [
        "issuer",
        "authorization_endpoint",
        "token_endpoint",
        "jwks_uri",
        "response_types_supported",
        "subject_types_supported",
        "id_token_signing_alg_values_supported",
    ]

    for field in required_fields:
        assert field in discovery_data, f"Missing required field: {field}"

    # Verify client credentials is supported
    assert "client_credentials" in discovery_data.get("grant_types_supported", [])

    logger.info("✅ OAuth discovery endpoint test passed")


def test_oauth_jwks_endpoint(
    oauth_server: ServerManager,  # pylint: disable=redefined-outer-name
) -> None:
    """Test that JWKS endpoint is working."""

    jwks_url = f"{oauth_server.base_url}/.well-known/jwks.json"

    with httpx.Client() as client:
        response = client.get(jwks_url)

    assert response.status_code == 200
    jwks_data = response.json()

    # Verify JWKS structure
    assert "keys" in jwks_data
    assert len(jwks_data["keys"]) > 0

    # Verify key structure
    key = jwks_data["keys"][0]
    required_key_fields = ["kty", "use", "kid", "alg", "n", "e"]
    for field in required_key_fields:
        assert field in key, f"Missing required key field: {field}"

    logger.info("✅ JWKS endpoint test passed")


def test_client_management_endpoints(
    oauth_server: ServerManager,  # pylint: disable=redefined-outer-name
) -> None:
    """Test client management endpoints."""

    base_url = oauth_server.base_url

    with httpx.Client() as client:
        # Test creating a new client
        client_data = {
            "client_id": "test-mgmt-client",
            "client_secret": "test-mgmt-secret",
            "client_name": "Test Management Client",
            "scopes": ["read", "write"],
            "grant_types": ["client_credentials"],
            "redirect_uris": [],
            "audience": None,
        }

        # Create client
        response = client.post(f"{base_url}/admin/clients", json=client_data)
        assert response.status_code == 201

        created_client = response.json()
        assert created_client["client_id"] == "test-mgmt-client"
        assert created_client["client_name"] == "Test Management Client"
        assert created_client["scopes"] == ["read", "write"]

        # Test getting the client
        response = client.get(f"{base_url}/admin/clients/test-mgmt-client")
        assert response.status_code == 200

        retrieved_client = response.json()
        assert retrieved_client["client_id"] == "test-mgmt-client"

        # Test listing clients
        response = client.get(f"{base_url}/admin/clients")
        assert response.status_code == 200

        clients_list = response.json()
        assert isinstance(clients_list, list)
        client_ids = [c["client_id"] for c in clients_list]
        assert "test-mgmt-client" in client_ids

        # Test deleting the client
        response = client.delete(f"{base_url}/admin/clients/test-mgmt-client")
        assert response.status_code == 204

        # Verify client is deleted
        response = client.get(f"{base_url}/admin/clients/test-mgmt-client")
        assert response.status_code == 404

    logger.info("✅ Client management endpoints test passed")


def _b64url_encode_no_pad(obj: Any) -> str:
    """Encode JSON-able object, bytes or str to base64url without padding."""
    if isinstance(obj, (dict, list)):
        raw = json.dumps(obj, separators=(",", ":"), sort_keys=False).encode("utf-8")
    elif isinstance(obj, (bytes, bytearray)):
        raw = bytes(obj)
    elif isinstance(obj, str):
        raw = obj.encode("utf-8")
    else:
        # Fallback to JSON serialization for other types
        raw = json.dumps(obj, separators=(",", ":"), sort_keys=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("utf-8")


def test_jwt_sensitive_info_disclosure(requestor_app: RequestorApp) -> None:
    """Test that JWT tokens do not disclose sensitive information."""

    jwt_token = (
        requestor_app.oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
            "openid"
        )
    )

    decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})

    # Check for sensitive fields
    sensitive_fields = [
        requestor_app.client_secret,
        requestor_app.client_id,
    ]
    for field in sensitive_fields:
        assert (
            field not in decoded_token
        ), f"Token should not contain sensitive field: {field}"


def test_expiry_jwt_token(requestor_app: RequestorApp) -> None:
    """Test that JWT tokens have proper expiry set."""

    jwt_token = (
        requestor_app.oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
            "openid"
        )
    )

    decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})

    assert "exp" in decoded_token, "Token should have an expiry (exp) claim"

    current_time = int(time.time())
    assert decoded_token["exp"] > current_time, "Token expiry should be in the future"


def test_jwt_is_using_aws_cognito(
    oauth_server: ServerManager, requestor_app: RequestorApp
) -> None:
    """Test that JWT tokens are issued by AWS Cognito."""

    jwt_token = (
        requestor_app.oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
            "openid"
        )
    )

    decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})

    assert "iss" in decoded_token, "Token should have an issuer (iss) claim"

    expected_issuer = requestor_app.oauth_idp_client.issuer
    assert (
        decoded_token["iss"] == expected_issuer
    ), f"Token issuer should be {expected_issuer}"


def test_check_jwt_if_using_asymmetric(requestor_app: RequestorApp) -> None:
    """Test that JWT tokens are signed using asymmetric keys."""

    jwt_token = (
        requestor_app.oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
            "openid"
        )
    )

    decoded_header = jwt.get_unverified_header(jwt_token)

    assert "alg" in decoded_header, "Token header should have an alg field"

    alg = decoded_header["alg"]
    assert alg in [
        "RS256",
    ], "Token should be signed with an asymmetric algorithm"


def test_try_changing_jwt_signing_algorithm(
    oauth_server: ServerManager, requestor_app: RequestorApp
) -> None:
    """Test that changing the JWT algorithm invalidates the token."""

    jwt_token = (
        requestor_app.oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
            "openid"
        )
    )
    original_token = jwt_token
    _, _, signature_b64 = original_token.split(".")

    decoded_header = jwt.get_unverified_header(jwt_token)
    decoded_payload = jwt.decode(jwt_token, options={"verify_signature": False})
    decoded_header["alg"] = "HS256"

    modified_token = f"{_b64url_encode_no_pad(decoded_header)}.{_b64url_encode_no_pad(decoded_payload)}.{signature_b64}"

    endpoint_url = f"http://localhost:9001/test_client_credential_flow"
    response = requestor_app.call_protected_endpoint(endpoint_url, modified_token)

    assert (
        response.status_code == 401
    ), f"Expected 401, got {response.status_code}: {response.text}"


def test_try_modifying_payload_without_chaning_signature(
    requestor_app: RequestorApp,
) -> None:
    """Test that modifying the JWT payload invalidates the token."""

    jwt_token = (
        requestor_app.oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
            "openid"
        )
    )

    decoded_header = jwt.get_unverified_header(jwt_token)
    decoded_payload = jwt.decode(jwt_token, options={"verify_signature": False})
    decoded_payload["aud"] = "ModifiedAudience"

    original_token = jwt_token
    _, _, signature_b64 = original_token.split(".")

    modified_token = f"{_b64url_encode_no_pad(decoded_header)}.{_b64url_encode_no_pad(decoded_payload)}.{signature_b64}"

    endpoint_url = "http://localhost:9001/test_client_credential_flow"
    response = requestor_app.call_protected_endpoint(endpoint_url, modified_token)

    assert (
        response.status_code == 401
    ), f"Expected 401, got {response.status_code}: {response.text}"


def test_try_removing_signature_part(requestor_app: RequestorApp) -> None:
    """Test that removing the JWT signature invalidates the token."""

    jwt_token = (
        requestor_app.oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
            "openid"
        )
    )

    header_b64, payload_b64, _ = jwt_token.split(".")
    modified_token = f"{header_b64}.{payload_b64}."

    endpoint_url = "http://localhost:9001/test_client_credential_flow"
    response = requestor_app.call_protected_endpoint(endpoint_url, modified_token)

    assert (
        response.status_code == 401
    ), f"Expected 401, got {response.status_code}: {response.text}"


@pytest.mark.parametrize(
    "header_field, injection",
    [
        ("jwk", {"kty": "RSA", "kid": "injected-key-id"}),
        ("kid", "injected-key-id"),
        ("jku", "http://malicious.example.com/jwks.json"),
    ],
)
def test_try_jwt_header_injections(
    header_field: str,
    injection: str | dict[str, str],
    requestor_app: RequestorApp,
) -> None:
    """Parametrized test that JWT header injections ('jwk', 'kid', 'jku') are handled properly."""
    jwt_token = (
        requestor_app.oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
            "openid"
        )
    )

    decoded_header = jwt.get_unverified_header(jwt_token)
    decoded_payload = jwt.decode(jwt_token, options={"verify_signature": False})
    decoded_header[header_field] = injection

    modified_token = f"{_b64url_encode_no_pad(decoded_header)}.{_b64url_encode_no_pad(decoded_payload)}.{jwt_token.split('.')[2]}"

    endpoint_url = "http://localhost:9001/test_client_credential_flow"
    response = requestor_app.call_protected_endpoint(endpoint_url, modified_token)

    assert (
        response.status_code == 401
    ), f"Expected 401 for injected header '{header_field}', got {response.status_code}: {response.text}"


def test_verify_if_within_scope(requestor_app: RequestorApp) -> None:
    """Test that JWT tokens have correct scopes."""

    jwt_token = (
        requestor_app.oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
            "openid read write"
        )
    )

    decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
    assert "scope" in decoded_token

    scopes = decoded_token["scope"].split()
    expected_scopes = {"openid"}  # potentially more scopes here later
    assert expected_scopes.issubset(set(scopes))


def test_get_jwk_from_jwt_returns_existing_key(
    requestor_app: RequestorApp,
) -> None:
    """Test that get_jwk_from_jwt returns the correct JWK for a given JWT."""

    jwt_token = (
        requestor_app.oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
            "openid"
        )
    )

    jwk = asyncio.run(requestor_app.oauth_idp_client.get_jwk_from_jwt(jwt_token))

    assert jwk is not None
    assert jwk.public_key_use == "sig"
    assert jwk.key_type == "RSA"


@pytest.mark.parametrize(
    "invalid_key",
    [
        # key with wrong `use`
        {
            "use": "enc",
            "kty": "RSA",
            "kid": "bad-use-kid",
            "n": "dummy_n",
            "e": "AQAB",
        },
        # key with unsupported `kty`
        {
            "use": "sig",
            "kty": "EC",
            "kid": "bad-kty-kid",
            "crv": "P-256",
            "x": "dummy",
            "y": "dummy",
        },
    ],
)
def test_load_keys_ignores_invalid_key(
    requestor_app: RequestorApp, invalid_key: dict
) -> None:
    """Ensure invalid keys (wrong `use`, unsupported `kty`, disallowed `alg`) are ignored."""

    requestor_app.oauth_idp_client.server_cfg.jwks_uri = (
        "https://idp.example/.well-known/jwks.json"
    )

    valid_key = {
        "use": "sig",
        "kty": "RSA",
        "kid": "valid-kid",
        "n": "dummy_n",
        "e": "AQAB",
    }

    mock_client = MagicMock()
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"keys": [invalid_key, valid_key]}
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None

    with patch("httpx.Client", return_value=mock_client):
        # Keep PyJWK.from_dict simple and return the dict directly for these tests
        with patch("jwt.PyJWK.from_dict", side_effect=lambda d: d):
            requestor_app.oauth_idp_client._signing_keys.clear()
            requestor_app.oauth_idp_client._load_keys()

    assert invalid_key["kid"] not in requestor_app.oauth_idp_client._signing_keys
    assert valid_key == requestor_app.oauth_idp_client._signing_keys.get("valid-kid")
    assert len(requestor_app.oauth_idp_client._signing_keys) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

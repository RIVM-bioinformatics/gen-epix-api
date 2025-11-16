"""
Test OAuth OIDC Client Credential Authentication Flow

This module implements a comprehensive test for the OAuth 2.0 Client Credentials flow
as described in RFC 6749 Section 4.4: https://datatracker.ietf.org/doc/html/rfc6749#section-4.4

Test scenario:
1. Start OAuth server on port 8000
2. Add a machine-to-machine (M2M) app identity called RequestorApp with audience ReceiverApp
3. Create ReceiverApp FastAPI app with OIDC client and protected endpoint
4. Start ReceiverApp on port 8001
5. Create RequestorApp class with OIDC client
6. RequestorApp gets access token and calls ReceiverApp endpoint (success case)
7. RequestorApp uses invalid token to call ReceiverApp endpoint (failure case)
"""

import logging
from collections.abc import Generator
from test.end_to_end.client_credential_flow.apps import (  # pylint: disable=import-error
    OAuthServerManager,
    ReceiverAppManager,
    RequestorApp,
)

import httpx
import pytest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pytest fixtures and tests


@pytest.fixture(scope="session")
def oauth_server() -> Generator[OAuthServerManager, None, None]:
    """Start and manage OAuth server for the test session."""
    with OAuthServerManager(port=8000) as server:
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
    oauth_server: OAuthServerManager,  # pylint: disable=redefined-outer-name
) -> Generator[ReceiverAppManager, None, None]:
    """Start and manage ReceiverApp for the test session."""
    discovery_url = oauth_server.get_discovery_url()

    with ReceiverAppManager(port=8001, oauth_discovery_url=discovery_url) as app:
        if not app.start():
            pytest.fail("Failed to start ReceiverApp")
        yield app


@pytest.fixture(scope="session")
def requestor_app(
    oauth_server: OAuthServerManager,  # pylint: disable=redefined-outer-name
) -> RequestorApp:
    """Create RequestorApp instance."""
    discovery_url = oauth_server.get_discovery_url()

    return RequestorApp(
        client_id="RequestorApp",
        client_secret="requestor_app_secret",
        oauth_discovery_url=discovery_url,
    )


def test_oauth_client_credentials_flow_success(
    oauth_server: OAuthServerManager,  # pylint: disable=redefined-outer-name
    receiver_app: ReceiverAppManager,  # pylint: disable=redefined-outer-name
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
    oauth_server: OAuthServerManager,  # pylint: disable=redefined-outer-name,unused-argument
    receiver_app: ReceiverAppManager,  # pylint: disable=redefined-outer-name
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
    receiver_app: ReceiverAppManager,  # pylint: disable=redefined-outer-name
) -> None:
    """Test OAuth Client Credentials flow with missing token."""

    # Call protected endpoint without token
    endpoint_url = f"{receiver_app.base_url}/test_client_credential_flow"

    with httpx.Client() as client:
        response = client.get(endpoint_url, timeout=10.0)

    # Should receive 403 due to missing Bearer token
    assert (
        response.status_code == 403
    ), f"Expected 403, got {response.status_code}: {response.text}"

    logger.info("✅ Missing token test passed")


def test_oauth_discovery_endpoint(
    oauth_server: OAuthServerManager,  # pylint: disable=redefined-outer-name
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
    oauth_server: OAuthServerManager,  # pylint: disable=redefined-outer-name
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
    oauth_server: OAuthServerManager,  # pylint: disable=redefined-outer-name
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

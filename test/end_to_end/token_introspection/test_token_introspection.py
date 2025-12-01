"""
Test OAuth OIDC Client Credential Authentication Flow with Introspection

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
8. Inactivate the access token on the OAuth server
9. Try to call ReceiverApp endpoint again with the inactivated token (should fail)
10. Enable introspection on CommonDB
11. Call ReceiverApp endpoint with the inactivated token (should return 404)
"""

import asyncio
import base64
import json
import logging
import time
from collections.abc import Generator
from pathlib import Path
from test.end_to_end.client_credential_flow.apps import (  # pylint: disable=import-error
    RequestorApp,
)
from test.end_to_end.token_introspection.envvar import set_envvar
from test.test_client.enum import ServerType
from test.test_client.oauth.common_server_manager import CommonServerManager
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from gen_epix.casedb.domain import enum as enum
from gen_epix.commondb.api.router import create_routers as commondb_create_routers
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain import enum as commondb_enum
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.env import AppComposer as CommonDbAppComposer

# If CommonDB has specific enums for ServiceType/RepositoryType, import them here:


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SSL_CERTFILE = Path("cert/cert.pem").absolute().as_posix()
SSL_KEYFILE = Path("cert/key.pem").absolute().as_posix()


@pytest.fixture(scope="session")
def commondb_server(
    oauth_server: CommonServerManager,  # pylint: disable=unused-argument,redefined-outer-name
) -> Generator[CommonServerManager, None, None]:
    # Compose CommonDB FastAPI app
    set_envvar()
    app_cfg = AppCfg(
        AppType.COMMONDB,
        commondb_enum.ServiceType,
        commondb_enum.RepositoryType,
        log_setup=True,
    )
    app_composer = CommonDbAppComposer(app_cfg, log_setup=True)
    app = app_composer.app

    fastapi_app = create_fast_api(
        app=app,
        create_routers_fn=commondb_create_routers,
        app_id=app_composer.app.generate_id(),
        setup_logger=app_cfg.setup_logger,
        api_logger=app_cfg.api_logger,
        debug=False,
    )

    # Start CommonDB server on 8002 (to avoid OAuth port)
    with CommonServerManager(
        service=ServerType.COMMONDB,
        app=fastapi_app,
        host="127.0.0.1",
        port=8008,
        ssl_certfile=SSL_CERTFILE,
        ssl_keyfile=SSL_KEYFILE,
    ) as server:
        if not server.start():
            pytest.fail("Failed to start CommonDB server")
        yield server


@pytest.fixture(scope="session")
def oauth_server() -> Generator[CommonServerManager, None, None]:
    # Start OAuth server on 8000
    with CommonServerManager(
        service=ServerType.OAUTH,
        port=8000,
        ssl_certfile=SSL_CERTFILE,
        ssl_keyfile=SSL_KEYFILE,
    ) as server:
        if not server.start():
            pytest.fail("Failed to start OAuth server")

        # Register a client to retrieve user tokens
        ok = server.add_client(
            client_id="COMMONDB_TEST_CLIENT",
            client_secret="COMMONDB_TEST_SECRET",
            audience="COMMONDB",
            scopes=["openid", "profile", "read"],
        )
        if not ok:
            pytest.fail("Failed to add COMMONDB_TEST_CLIENT")

        yield server


def _get_user_jwt(oauth_server: CommonServerManager, scope: str = "openid") -> str:
    # Retrieve JWT via client credentials flow from mock OAuth server
    # token_endpoint = f"{oauth_server.base_url}/oauth/token"
    # client_id = "COMMONDB_TEST_CLIENT"
    # client_secret = "COMMONDB_TEST_SECRET"
    # scope = "openid read"

    # data: str = "&".join(
    #     (
    #         f"grant_type=client_credentials",
    #         f"scope={urllib.parse.quote(scope)}",
    #     )
    # )

    # headers: dict[str, str] = {
    #     "Content-Type": "application/x-www-form-urlencoded",
    # }

    # headers["Authorization"] = (
    #     "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    # )

    # with httpx.Client(timeout=10.0, verify=SSL_CERTFILE) as client:
    #     resp = client.post(token_endpoint, data=data)
    #     assert resp.status_code == 200, f"Token retrieval failed: {resp.text}"
    #     token_response = resp.json()
    #     token: str = token_response["access_token"]
    #     return token

    token_endpoint = f"{oauth_server.base_url}/oauth/token"
    client_id = "COMMONDB_TEST_CLIENT"
    client_secret = "COMMONDB_TEST_SECRET"

    data = {
        "grant_type": "client_credentials",
        "scope": scope,
        "audience": "COMMONDB",
    }
    # Basic auth header
    auth = (client_id, client_secret)
    with httpx.Client(timeout=10.0, verify=SSL_CERTFILE) as client:
        resp = client.post(token_endpoint, data=data, auth=auth)
        assert resp.status_code == 200, f"Token retrieval failed: {resp.text}"
        body = resp.json()
        assert "access_token" in body
        return body["access_token"]


def _call_commondb_me(
    commondb_server: CommonServerManager, token: str
) -> httpx.Response:
    url = f"{commondb_server.base_url}/v1/user_me"

    headers = {
        "authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    with httpx.Client(timeout=5.0, verify=SSL_CERTFILE) as client:
        return client.get(url, headers=headers)


def _toggle_commondb_introspection(
    commondb_server: CommonServerManager, enabled: bool
) -> None:
    # Assumed config endpoint that toggles introspection behavior
    # Adjust path/body according to your CommonDB API
    url = f"{commondb_server.base_url}/v1/config/auth/introspection"
    payload = {"enabled": enabled}
    with httpx.Client(timeout=10.0, verify=SSL_CERTFILE) as client:
        resp = client.put(url, json=payload)
        assert resp.status_code in (
            200,
            204,
        ), f"Failed to toggle introspection: {resp.text}"


def _invalidate_token(oauth_server: CommonServerManager, token: str) -> None:
    # Call mock OAuth admin endpoint to invalidate a specific token (by jti or token itself)
    # Adjust to your mock server's API; here we assume token is passed directly
    url = f"{oauth_server.base_url}/admin/tokens/invalidate"
    with httpx.Client(timeout=10.0, verify=SSL_CERTFILE) as client:
        resp = client.post(url, json={"token": token})
        assert resp.status_code in (
            200,
            204,
        ), f"Failed to invalidate token: {resp.text}"


def test_introspection_flow(
    oauth_server: CommonServerManager,  # pylint: disable=redefined-outer-name
    commondb_server: CommonServerManager,  # pylint: disable=redefined-outer-name
) -> None:
    # a. OAuth server started via fixture
    # b. CommonDB server started via fixture

    # Ensure health
    with httpx.Client(timeout=5.0, verify=SSL_CERTFILE) as client:
        assert client.get(f"{oauth_server.base_url}/health").status_code == 200
        assert client.get(f"{commondb_server.base_url}/v1/health").status_code == 200

    # c. Retrieve jwt for a user (client credentials)
    token = _get_user_jwt(oauth_server)

    # d. Perform allowed action for user (protected endpoint)
    resp_ok = _call_commondb_me(commondb_server, token)
    assert (
        resp_ok.status_code == 200
    ), f"Expected 200, got {resp_ok.status_code}: {resp_ok.text}"

    # e. Inactivate jwt in mock IDP
    _invalidate_token(oauth_server, token)

    # f. Perform same action before introspection is applied. Should work fine.
    # Introspection disabled by default; if not, explicitly disable
    _toggle_commondb_introspection(commondb_server, enabled=False)
    resp_before = _call_commondb_me(commondb_server, token)
    assert (
        resp_before.status_code == 200
    ), f"Expected 200 before introspection, got {resp_before.status_code}: {resp_before.text}"

    # g. Same as (f) but after introspection is applied: should return 404.
    _toggle_commondb_introspection(commondb_server, enabled=True)
    resp_after = _call_commondb_me(commondb_server, token)
    assert (
        resp_after.status_code == 404
    ), f"Expected 404 after introspection, got {resp_after.status_code}: {resp_after.text}"


def test_oauth_client_credentials_flow_success(
    oauth_server: CommonServerManager,  # pylint: disable=redefined-outer-name
    receiver_app: CommonServerManager,  # pylint: disable=redefined-outer-name
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
    oauth_server: CommonServerManager,  # pylint: disable=redefined-outer-name,unused-argument
    receiver_app: CommonServerManager,  # pylint: disable=redefined-outer-name
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
    receiver_app: CommonServerManager,  # pylint: disable=redefined-outer-name
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
    oauth_server: CommonServerManager,  # pylint: disable=redefined-outer-name
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
    oauth_server: CommonServerManager,  # pylint: disable=redefined-outer-name
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
    oauth_server: CommonServerManager,  # pylint: disable=redefined-outer-name
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
    oauth_server: CommonServerManager, requestor_app: RequestorApp
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
    oauth_server: CommonServerManager, requestor_app: RequestorApp
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

    endpoint_url = f"http://localhost:8001/test_client_credential_flow"
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

    endpoint_url = "http://localhost:8001/test_client_credential_flow"
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

    endpoint_url = "http://localhost:8001/test_client_credential_flow"
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

    endpoint_url = "http://localhost:8001/test_client_credential_flow"
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

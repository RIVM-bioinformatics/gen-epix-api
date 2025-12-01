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

import logging
from collections.abc import Generator
from pathlib import Path
from test.end_to_end.token_introspection.envvar import set_envvar
from test.test_client.enum import ServerType
from test.test_client.oauth.common_server_manager import CommonServerManager

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


def _retrieve_access_token(oauth_server: CommonServerManager, scope: str = "openid") -> str:

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


def _call_commondb_user_me(
    commondb_server: CommonServerManager, token: str
) -> httpx.Response:
    url = f"{commondb_server.base_url}/v1/user_me"

    headers = {
        "authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    with httpx.Client(timeout=5.0, verify=SSL_CERTFILE) as client:
        return client.get(url, headers=headers)


def test_introspection_flow(
    oauth_server: CommonServerManager,
    commondb_server: CommonServerManager,
) -> None:
    
    with httpx.Client(timeout=5.0, verify=SSL_CERTFILE) as client:
        assert client.get(f"{oauth_server.base_url}/health").status_code == 200
        assert client.get(f"{commondb_server.base_url}/v1/health").status_code == 200

    # c. Retrieve jwt for a client (client credentials)
    token = _retrieve_access_token(oauth_server)

    # call protected endpoint and expect success
    resp = _call_commondb_user_me(commondb_server, token)
    assert resp.status_code == 200

    # e. Verify token via the correct introspection endpoint on the IDP
    introspect_url = f"{oauth_server.base_url}/oauth/introspect"
    with httpx.Client(timeout=5.0, verify=SSL_CERTFILE) as client:
        # Basic auth or form-based client auth depending on server config; here we use client_secret_basic style:
        resp_introspect = client.post(
            introspect_url,
            data={"token": token},
            auth=("COMMONDB_TEST_CLIENT", "COMMONDB_TEST_SECRET"),
        )
    assert resp_introspect.status_code == 200
    
    body = resp_introspect.json()
    is_active = body.get("active", False)
    
    assert is_active is True, f"Token should be active: {body}"


# def test_oauth_client_credentials_flow_success(
#     oauth_server: CommonServerManager,  # pylint: disable=redefined-outer-name
#     receiver_app: CommonServerManager,  # pylint: disable=redefined-outer-name
#     requestor_app: RequestorApp,  # pylint: disable=redefined-outer-name
# ) -> None:
#     """Test successful OAuth Client Credentials flow."""

#     # Step 1: RequestorApp gets access token for ReceiverApp
#     access_token = requestor_app.get_access_token("ReceiverApp")

#     # Step 2: RequestorApp calls protected endpoint on ReceiverApp
#     endpoint_url = (
#         f"{receiver_app.base_url}/test_client_credential_flow"  # Use fixture URL
#     )
#     response = requestor_app.call_protected_endpoint(endpoint_url, access_token)

#     # Step 3: Verify successful response
#     assert (
#         response.status_code == 200
#     ), f"Expected 200, got {response.status_code}: {response.text}"

#     response_data = response.json()
#     assert response_data["status"] == "OK", "Should receive OK status"
#     assert (
#         "Authentication successful" in response_data["message"]
#     ), "Should contain success message"

#     logger.info("✅ Successful OAuth Client Credentials flow test passed")


# def test_oauth_client_credentials_flow_invalid_token(
#     oauth_server: CommonServerManager,  # pylint: disable=redefined-outer-name,unused-argument
#     receiver_app: CommonServerManager,  # pylint: disable=redefined-outer-name
#     requestor_app: RequestorApp,  # pylint: disable=redefined-outer-name
# ) -> None:
#     """Test OAuth Client Credentials flow with invalid token."""

#     # Step 1: Create invalid token
#     invalid_token = requestor_app.create_invalid_token("ReceiverApp")

#     # Step 2: Try to call protected endpoint with invalid token
#     endpoint_url = f"{receiver_app.base_url}/test_client_credential_flow"
#     response = requestor_app.call_protected_endpoint(endpoint_url, invalid_token)

#     # Step 3: Verify unauthorized response
#     assert (
#         response.status_code == 401
#     ), f"Expected 401, got {response.status_code}: {response.text}"

#     logger.info("✅ Invalid token test passed")


# def test_oauth_client_credentials_flow_missing_token(
#     receiver_app: CommonServerManager,  # pylint: disable=redefined-outer-name
# ) -> None:
#     """Test OAuth Client Credentials flow with missing token."""

#     # Call protected endpoint without token
#     endpoint_url = f"{receiver_app.base_url}/test_client_credential_flow"

#     with httpx.Client() as client:
#         response = client.get(endpoint_url, timeout=10.0)

#     # Should receive 403 due to missing Bearer token
#     assert (
#         response.status_code == 403
#     ), f"Expected 403, got {response.status_code}: {response.text}"

#     logger.info("✅ Missing token test passed")

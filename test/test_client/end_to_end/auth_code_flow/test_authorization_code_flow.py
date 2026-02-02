import urllib.parse
from test.test_client.enum import ServerType
from test.test_client.server_manager import ServerManager
from typing import Any

import httpx
import pytest


@pytest.fixture(scope="module")
def oauth_server() -> Any:
    with ServerManager(service=ServerType.OAUTH, host="localhost", port=9000) as sm:
        started = sm.start()
        assert started, "Failed to start OAuth server"
        yield sm
        # ServerManager context will stop server


def test_authorization_code_flow(oauth_server: ServerManager) -> None:
    client_id = "auth-code-client"
    client_secret = "auth-code-secret"
    redirect_uri = "http://localhost:9001/callback"
    scopes = ["openid", "profile", "read"]

    # Register client supporting authorization_code
    ok = oauth_server.add_client(
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
        grant_types=["authorization_code"],
        redirect_uris=[redirect_uri],
    )
    assert ok, "Failed to register authorization_code client"

    base_url = oauth_server.base_url

    # Step 1: GET /oauth/authorize -> 302 with code
    authorize_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "openid profile",
        "state": "xyz",
        "login_hint": "user123",
    }

    with httpx.Client(timeout=10.0, follow_redirects=False) as client:
        r = client.get(f"{base_url}/oauth/authorize", params=authorize_params)
        assert r.status_code == 302
        location = r.headers.get("location") or r.headers.get("Location")
        assert location, "Missing redirect Location header"

    # Extract code from redirect URL
    parsed = urllib.parse.urlparse(location)
    qs = urllib.parse.parse_qs(parsed.query)
    code_values = qs.get("code")
    assert code_values and code_values[0], "Missing authorization code"
    code = code_values[0]

    # Step 2: POST /oauth/token to exchange code
    token_form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    with httpx.Client(timeout=10.0) as client:
        tr = client.post(f"{base_url}/oauth/token", data=token_form)
        assert tr.status_code == 200, tr.text
        body = tr.json()
        assert "access_token" in body
        assert body.get("token_type") == "Bearer"
        assert body.get("expires_in")
        assert "scope" in body
        # openid scope should produce an ID token
        assert "id_token" in body

    # Negative: invalid code
    bad_form = {
        "grant_type": "authorization_code",
        "code": "invalid-code",
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    with httpx.Client(timeout=10.0) as client:
        br = client.post(f"{base_url}/oauth/token", data=bad_form)
        assert br.status_code == 400

    # Negative: mismatched redirect_uri
    # Re-authorize to get a fresh code
    with httpx.Client(timeout=10.0, follow_redirects=False) as client:
        r2 = client.get(f"{base_url}/oauth/authorize", params=authorize_params)
        location2 = r2.headers.get("location") or r2.headers.get("Location")
        parsed2 = urllib.parse.urlparse(location2)
        code2 = urllib.parse.parse_qs(parsed2.query)["code"][0]

    wrong_form = {
        "grant_type": "authorization_code",
        "code": code2,
        "redirect_uri": "http://localhost:9999/wrong",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    with httpx.Client(timeout=10.0) as client:
        wr = client.post(f"{base_url}/oauth/token", data=wrong_form)
        assert wr.status_code == 400

    # Negative: code reuse (should be single-use)
    with httpx.Client(timeout=10.0) as client:
        reuse = client.post(f"{base_url}/oauth/token", data=token_form)
        assert reuse.status_code == 400

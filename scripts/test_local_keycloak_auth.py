"""Verify a real local Keycloak token against CASEDB's existing root user.

Run from the API repository with ``uv run python scripts/test_local_keycloak_auth.py``.
Set PPR_USER_ROOT_PASSWORD privately; optional Keycloak settings use PPR_KEYCLOAK_*
environment variables. Add --connect to use an already running CASEDB instance.
No application users are provisioned, and credentials and tokens are never printed.

Usage:
    uv run --env-file ../gen-epix-ppr/gen_epix_ppr/.env.local \
  python scripts/test_local_keycloak_auth.py
"""

import argparse
import math
import os
import signal
import socket
import ssl
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlsplit

import httpx
import jwt

REPO_ROOT = Path(__file__).resolve().parents[1]
USERNAME = "lsppoc.rivm1@rivmnl.onmicrosoft.com"
ISSUER = "http://127.0.0.1:8080/realms/labsentinel"
CLIENT_ID = "LabSentiNL-dev"
API_COMMAND = ["uv", "run", "run.py", "api", "CASEDB", "IDPS", "DICT_DEMO"]


class AuthenticationTestError(RuntimeError):
    """Represent an authentication check failure safe to display to the caller."""


def read_json(response: httpx.Response, stage: str) -> dict[str, Any]:
    """Read a JSON object without exposing a response that might contain a token.

    Args:
        response: Response returned by the service being checked.
        stage: Non-secret description of the request.

    Returns:
        The decoded JSON object.

    Raises:
        AuthenticationTestError: If the response is unsuccessful or malformed.
    """
    if response.status_code != 200:
        hints = {
            "invalid_grant": "Check the password, user profile and required actions.",
            "unauthorized_client": "Enable Direct Access Grants on LabSentiNL-dev.",
            "invalid_client": "Check the client ID and optional client secret.",
        }
        hint = ""
        try:
            body = response.json()
            if isinstance(body, dict):
                hint = hints.get(body.get("error"), "")
        except (ValueError, TypeError):
            pass
        raise AuthenticationTestError(
            f"{stage}: HTTP {response.status_code}. {hint}".rstrip()
        )
    try:
        body = response.json()
    except ValueError:
        raise AuthenticationTestError(f"{stage}: response is not JSON.") from None
    if not isinstance(body, dict):
        raise AuthenticationTestError(f"{stage}: expected a JSON object.")
    return body


def obtain_token(client: httpx.Client) -> str:
    """Obtain and cryptographically verify the expected local user's access token.

    Args:
        client: HTTP client with bounded timeouts and certificate verification.

    Returns:
        The verified access token, for use only in memory.

    Raises:
        AuthenticationTestError: If configuration, token retrieval or claims fail.
        httpx.HTTPError: If Keycloak cannot be reached.
    """
    password = os.environ.get("PPR_USER_ROOT_PASSWORD", "")
    if not password:
        raise AuthenticationTestError("Set PPR_USER_ROOT_PASSWORD privately first.")
    expected_settings = {
        "PPR_KEYCLOAK_BASE_URL": "http://127.0.0.1:8080",
        "PPR_KEYCLOAK_REALM": "labsentinel",
        "PPR_KEYCLOAK_USER_CLIENT_ID": CLIENT_ID,
    }
    for name, expected in expected_settings.items():
        if os.environ.get(name, expected).rstrip("/") != expected:
            raise AuthenticationTestError(f"{name} must match the local API provider.")
    discovery = read_json(
        client.get(f"{ISSUER}/.well-known/openid-configuration"),
        "Keycloak discovery",
    )
    expected_endpoints = {
        "issuer": ISSUER,
        "token_endpoint": f"{ISSUER}/protocol/openid-connect/token",
        "jwks_uri": f"{ISSUER}/protocol/openid-connect/certs",
    }
    for name, expected in expected_endpoints.items():
        if discovery.get(name) != expected:
            raise AuthenticationTestError(
                f"Keycloak discovery {name} differs from the canonical local URL. "
                "Check Keycloak hostname/frontend URL settings."
            )
    payload = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "username": USERNAME,
        "password": password,
        "scope": "openid profile email",
    }
    secret = os.environ.get("PPR_KEYCLOAK_USER_CLIENT_SECRET")
    if secret:
        payload["client_secret"] = secret
    body = read_json(
        client.post(expected_endpoints["token_endpoint"], data=payload),
        "Keycloak token request",
    )
    token = body.get("access_token")
    if not isinstance(token, str) or not token.strip():
        raise AuthenticationTestError("Keycloak response has no access token.")
    keys = read_json(
        client.get(expected_endpoints["jwks_uri"]), "Keycloak signing keys"
    )
    try:
        key_id = jwt.get_unverified_header(token).get("kid")
        key = next(
            key for key in jwt.PyJWKSet.from_dict(keys).keys if key.key_id == key_id
        )
        claims = jwt.decode(
            token,
            key=key.key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=ISSUER,
            options={"require": ["iss", "sub", "aud", "exp", "iat"]},
        )
    except (jwt.PyJWTError, StopIteration, ValueError, KeyError, TypeError):
        raise AuthenticationTestError(
            "Token signature, issuer, audience or timestamps are invalid."
        ) from None
    if claims.get("preferred_username") != USERNAME:
        raise AuthenticationTestError("Token does not identify the expected username.")
    return token


def tls_context(ca_file: str | None) -> ssl.SSLContext:
    """Use an explicit CA, the local mkcert CA, or the system trust store."""
    if not ca_file:
        try:
            result = subprocess.run(
                ["mkcert", "-CAROOT"],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            root_ca = Path(result.stdout.strip()) / "rootCA.pem"
            if root_ca.is_file():
                ca_file = str(root_ca)
        except (OSError, subprocess.SubprocessError):
            pass
    return ssl.create_default_context(cafile=ca_file)


@contextmanager
def running_api(connect: bool, api_url: str) -> Iterator[subprocess.Popen | None]:
    """Start CASEDB when requested and always stop its complete process group.

    Args:
        connect: Whether to leave process management to the caller.
        api_url: Loopback address whose port must be free before starting CASEDB.

    Yields:
        The owned launcher process, or None when connecting to an existing app.

    Raises:
        AuthenticationTestError: If the requested local port is already occupied.
        OSError: If the launcher cannot start.
    """
    if connect:
        yield None
        return
    address = urlsplit(api_url)
    try:
        with socket.create_connection((address.hostname, address.port or 8000), 1):
            pass
    except OSError:
        pass
    else:
        raise AuthenticationTestError(
            "CASEDB port is already in use. Use --connect for an existing instance."
        )
    process = subprocess.Popen(
        API_COMMAND,
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        yield process
    finally:
        # uvicorn's reload worker belongs to the launcher's process group too.
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=5)


def wait_for_api(
    client: httpx.Client,
    api_url: str,
    timeout: float,
    process: subprocess.Popen | None,
) -> None:
    """Wait for OpenAPI and confirm that the expected versioned route exists.

    Args:
        client: Verified HTTP client used to probe CASEDB.
        api_url: CASEDB origin without a route prefix.
        timeout: Maximum readiness wait in seconds.
        process: Owned launcher, checked for early exit when provided.

    Raises:
        AuthenticationTestError: If CASEDB exits, times out or lacks the route.
    """
    deadline = time.monotonic() + timeout
    last_error = "No HTTP response"
    while time.monotonic() < deadline:
        if process is not None and process.poll() is not None:
            raise AuthenticationTestError(
                f"CASEDB launcher exited with status {process.returncode}. "
                "Run 'uv run run.py api CASEDB IDPS DICT_DEMO' to inspect its logs."
            )
        try:
            response = client.get(
                f"{api_url}/openapi.json",
                timeout=min(5, max(0.1, deadline - time.monotonic())),
            )
            if response.status_code == 200:
                document = read_json(response, "CASEDB OpenAPI")
                if "/v1/user_me" not in document.get("paths", {}):
                    raise AuthenticationTestError("CASEDB has no /v1/user_me route.")
                return
            last_error = f"HTTP {response.status_code}"
        except httpx.HTTPError as error:
            last_error = type(error).__name__
            if (
                isinstance(error, httpx.ConnectError)
                and isinstance(error.__cause__, Exception)
                and "CERTIFICATE_VERIFY_FAILED" in str(error)
            ):
                raise AuthenticationTestError(
                    "CASEDB TLS certificate verification failed. Supply its CA "
                    "with --ca-file; verification remains enabled."
                ) from None
        time.sleep(min(0.5, max(0, deadline - time.monotonic())))
    raise AuthenticationTestError(f"CASEDB readiness timed out ({last_error}).")


def verify_user(client: httpx.Client, api_url: str, token: str) -> None:
    """Check rejection of unauthenticated calls and acceptance of the root token.

    Args:
        client: Verified HTTP client used for all CASEDB requests.
        api_url: CASEDB origin without a route prefix.
        token: Cryptographically verified Keycloak access token.

    Raises:
        AuthenticationTestError: If a status or returned identity is incorrect.
        httpx.HTTPError: If CASEDB becomes unreachable.
    """
    endpoint = f"{api_url}/v1/user_me"
    for label, headers in (
        ("missing token", {}),
        ("malformed token", {"Authorization": "Bearer invalid-token"}),
    ):
        response = client.get(endpoint, headers=headers)
        if response.status_code not in (401, 403):
            raise AuthenticationTestError(
                f"CASEDB {label}: expected 401/403, got {response.status_code}."
            )
    user = read_json(
        client.get(endpoint, headers={"Authorization": f"Bearer {token}"}),
        "CASEDB /v1/user_me",
    )
    if (
        user.get("key") != USERNAME
        or user.get("is_active") is not True
        or "CASEDB_ROOT" not in (user.get("roles") or [])
    ):
        raise AuthenticationTestError(
            "CASEDB returned 200 but did not return the expected active CASEDB root user."
        )


def main() -> int:
    """Run the local authentication smoke test and return a process exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--connect", action="store_true", help="Use an existing CASEDB."
    )
    has_tls = all(
        (REPO_ROOT / "cert" / name).is_file() for name in ("key.pem", "cert.pem")
    )
    parser.add_argument(
        "--api-url", default=f"{'https' if has_tls else 'http'}://127.0.0.1:8000"
    )
    parser.add_argument(
        "--ca-file",
        default=os.environ.get("CASEDB_SSL_CERT_FILE")
        or os.environ.get("SSL_CERT_FILE"),
    )
    parser.add_argument("--startup-timeout", type=float, default=120)
    args = parser.parse_args()
    address = urlsplit(args.api_url)
    if (
        address.scheme not in ("http", "https")
        or address.hostname not in ("127.0.0.1", "localhost", "::1")
        or address.username is not None
        or address.password is not None
        or address.path not in ("", "/")
        or address.query
        or address.fragment
    ):
        parser.error("--api-url must be a loopback HTTP(S) origin without credentials.")
    if not args.connect and address.port != 8000:
        parser.error(
            "Starting CASEDB requires port 8000; use --connect for other ports."
        )
    if not math.isfinite(args.startup_timeout) or args.startup_timeout <= 0:
        parser.error("--startup-timeout must be finite and positive.")
    stage = "TLS setup"
    try:
        with httpx.Client(
            verify=tls_context(args.ca_file),
            timeout=10,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            stage = "Keycloak login"
            token = obtain_token(client)
            print(f"Token: {token}")
            print(f"PASS: Keycloak issued a verified token for {USERNAME}.", flush=True)
            stage = "CASEDB startup"
            with running_api(args.connect, args.api_url) as process:
                wait_for_api(
                    client, args.api_url.rstrip("/"), args.startup_timeout, process
                )
                stage = "CASEDB authentication"
                verify_user(client, args.api_url.rstrip("/"), token)
            print("PASS: Missing and malformed tokens were rejected.")
            print(
                "PASS: /v1/user_me returned HTTP 200 for the active CASEDB_ROOT user."
            )
        return 0
    except AuthenticationTestError as error:
        print(f"FAIL [{stage}]: {error}", file=sys.stderr)
    except (httpx.HTTPError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(
            f"FAIL [{stage}]: {type(error).__name__}. Check local service access, "
            "dependencies and the trusted CA file.",
            file=sys.stderr,
        )
    except KeyboardInterrupt:
        print(
            f"FAIL [{stage}]: Interrupted; owned CASEDB processes stopped.",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())

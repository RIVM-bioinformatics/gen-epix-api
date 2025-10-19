"""
OAuth 2.0 Provider Server with OIDC Support

This module implements an OAuth 2.0 authorization server with OpenID Connect (OIDC) support
using oauthlib. It supports the Client Credentials flow and can be extended for other flows.

The server includes:
- OAuth 2.0 Client Credentials flow
- OpenID Connect Discovery
- JWT token generation with proper claims
- Client authentication and validation
- Token introspection endpoint
"""

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from test.test_client.oauth.client_store import Client, ClientStore
from test.test_client.oauth.jwks import JWKSManager
from test.test_client.oauth.oidc_provider import OIDCProvider
from test.test_client.oauth.token_store import Token, TokenStore
from test.test_client.oauth.validators import OAuth2Validator
from typing import Any, AsyncGenerator, Dict

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
client_store = ClientStore()
token_store = TokenStore()
jwks_manager = JWKSManager()
oauth_validator = OAuth2Validator(client_store, token_store)
oidc_provider = OIDCProvider(jwks_manager)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize the OAuth server with demo clients."""
    logger.info("Starting OAuth 2.0 Provider with OIDC support")

    # Create demo clients
    demo_client = Client(
        client_id="demo-client",
        client_secret="demo-secret",
        client_name="Demo Client",
        scopes=["read", "write", "openid", "profile"],
        grant_types=["client_credentials"],
    )
    client_store.store_client(demo_client)

    test_client = Client(
        client_id="test-client",
        client_secret="test-secret",
        client_name="Test Client",
        scopes=["read", "openid"],
        grant_types=["client_credentials"],
    )
    client_store.store_client(test_client)

    logger.info("Demo clients created:")
    logger.info("- demo-client / demo-secret (scopes: read, write, openid, profile)")
    logger.info("- test-client / test-secret (scopes: read, openid)")

    yield  # This is where the app runs

    # Cleanup code would go here if needed
    logger.info("Shutting down OAuth 2.0 Provider")


# FastAPI app
app = FastAPI(
    title="OAuth 2.0 Provider with OIDC",
    description="OAuth 2.0 Authorization Server with OpenID Connect support",
    version="1.0.0",
    lifespan=lifespan,
)

# HTTP Basic Authentication for client credentials
security = HTTPBasic()


def get_client_credentials(
    credentials: HTTPBasicCredentials = Depends(security),
) -> Client:
    """Extract and validate client credentials from HTTP Basic Auth."""
    client = client_store.get_client(credentials.username)
    if not client or not client.check_secret(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return client


@app.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request) -> Dict[str, Any]:
    """OpenID Connect Discovery endpoint."""
    base_url = f"{request.url.scheme}://{request.url.netloc}"

    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "userinfo_endpoint": f"{base_url}/oauth/userinfo",
        "jwks_uri": f"{base_url}/.well-known/jwks.json",
        "introspection_endpoint": f"{base_url}/oauth/introspect",
        "response_types_supported": ["code", "token"],
        "grant_types_supported": ["client_credentials", "authorization_code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "profile", "email", "read", "write"],
        "token_endpoint_auth_methods_supported": [
            "client_secret_basic",
            "client_secret_post",
        ],
        "claims_supported": ["sub", "iss", "aud", "exp", "iat", "auth_time", "nonce"],
    }


@app.get("/.well-known/jwks.json")
async def jwks_endpoint() -> Dict[str, Any]:
    """JSON Web Key Set (JWKS) endpoint."""
    return jwks_manager.get_public_keys()


@app.post("/oauth/token")
async def token_endpoint(
    request: Request, client: Client = Depends(get_client_credentials)
) -> JSONResponse:
    """OAuth 2.0 Token endpoint supporting Client Credentials flow."""

    # Parse form data
    form_data = await request.form()
    grant_type = form_data.get("grant_type")
    scope_value = form_data.get("scope", "")

    if grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported_grant_type"
        )

    # Validate scope - handle both string and UploadFile
    scope_str = scope_value if isinstance(scope_value, str) else ""
    requested_scopes = scope_str.split() if scope_str else []
    allowed_scopes = client.validate_scopes(requested_scopes)

    # Generate tokens
    now = datetime.now(timezone.utc)
    expires_in = 3600  # 1 hour
    expires_at = now + timedelta(seconds=expires_in)

    # Create access token
    access_token_payload = {
        "iss": f"{request.url.scheme}://{request.url.netloc}",
        "sub": client.client_id,
        "aud": client.client_id,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "scope": " ".join(allowed_scopes),
        "client_id": client.client_id,
        "token_type": "Bearer",
    }

    access_token = jwks_manager.create_jwt(access_token_payload)

    # Store token
    token = Token(
        access_token=access_token,
        token_type="Bearer",
        expires_in=expires_in,
        scope=" ".join(allowed_scopes),
        client_id=client.client_id,
    )
    token_store.store_token(access_token, token)

    response_data = {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "scope": " ".join(allowed_scopes),
    }

    # Add ID token if openid scope is requested
    if "openid" in allowed_scopes:
        id_token_payload = {
            "iss": f"{request.url.scheme}://{request.url.netloc}",
            "sub": client.client_id,
            "aud": client.client_id,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "auth_time": int(now.timestamp()),
        }
        id_token = jwks_manager.create_jwt(id_token_payload)
        response_data["id_token"] = id_token

    logger.info(
        f"Issued token for client {client.client_id} with scopes: {allowed_scopes}"
    )

    return JSONResponse(
        content=response_data,
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )


@app.post("/oauth/introspect")
async def token_introspection(
    request: Request, client: Client = Depends(get_client_credentials)
) -> JSONResponse:
    """RFC 7662 Token Introspection endpoint."""

    form_data = await request.form()
    token_value = form_data.get("token")

    if not token_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="token parameter is required",
        )

    # Handle both string and UploadFile
    token_str = token_value if isinstance(token_value, str) else ""
    if not token_str:
        return JSONResponse(content={"active": False})

    # Look up token
    stored_token = token_store.get_token(token_str)

    if not stored_token:
        return JSONResponse(content={"active": False})

    # Check if token is expired
    try:
        payload = jwks_manager.verify_jwt(token_str)
        exp = payload.get("exp", 0)
        if exp < time.time():
            return JSONResponse(content={"active": False})
    except jwt.InvalidTokenError:
        return JSONResponse(content={"active": False})

    # Return token info
    response_data = {
        "active": True,
        "client_id": stored_token.client_id,
        "scope": stored_token.scope,
        "token_type": stored_token.token_type,
        "exp": payload.get("exp"),
        "iat": payload.get("iat"),
        "sub": payload.get("sub"),
        "aud": payload.get("aud"),
        "iss": payload.get("iss"),
    }

    return JSONResponse(content=response_data)


@app.get("/oauth/userinfo")
async def userinfo_endpoint(request: Request) -> JSONResponse:
    """OpenID Connect UserInfo endpoint."""

    # Extract Bearer token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required"
        )

    access_token = auth_header[7:]  # Remove "Bearer " prefix

    # Validate token
    try:
        payload = jwks_manager.verify_jwt(access_token)
        logger.info(f"JWT validation successful for token: {access_token[:20]}...")
    except jwt.InvalidTokenError as e:
        logger.error(
            f"JWT validation failed for token: {access_token[:20]}... Error: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # Check if token has openid scope
    stored_token = token_store.get_token(access_token)
    logger.info(f"Token lookup result: {stored_token is not None}")
    if stored_token:
        logger.info(f"Token scope: {stored_token.scope}")

    if not stored_token or "openid" not in stored_token.scope:
        logger.error(
            f"Token validation failed: stored_token={stored_token is not None}, scope={stored_token.scope if stored_token else 'None'}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient scope"
        )

    # Return user info (for client credentials, this is limited)
    return JSONResponse(
        content={
            "sub": payload.get("sub"),
            "client_id": payload.get("client_id"),
            "aud": payload.get("aud"),
            "iss": payload.get("iss"),
        }
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

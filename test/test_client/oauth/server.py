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
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from test.test_client.oauth.authorization_code_store import \
    AuthorizationCodeStore
from test.test_client.oauth.client_store import Client, ClientStore
from test.test_client.oauth.jwks import JWKSManager
from test.test_client.oauth.oidc_provider import OIDCProvider
from test.test_client.oauth.token_store import Token, TokenStore
from test.test_client.oauth.validators import OAuth2Validator
from typing import Any

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
client_store = ClientStore()
token_store = TokenStore()
jwks_manager = JWKSManager()
oauth_validator = OAuth2Validator(client_store, token_store)
oidc_provider = OIDCProvider(jwks_manager)
authorization_code_store = AuthorizationCodeStore()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize the OAuth server."""
    logger.info("Starting OAuth 2.0 Provider with OIDC support")

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


# Pydantic models for API requests
class ClientCreateRequest(BaseModel):
    """Request model for creating a new OAuth client."""

    client_id: str
    client_secret: str
    client_name: str
    scopes: list[str]
    grant_types: list[str] = ["client_credentials"]
    redirect_uris: list[str] = []
    audience: str | None = None


class ClientResponse(BaseModel):
    """Response model for client information."""

    client_id: str
    client_name: str
    scopes: list[str]
    grant_types: list[str]
    redirect_uris: list[str]
    audience: str | None = None
    created_at: str
    is_active: bool


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


async def authenticate_client(request: Request) -> Client:
    """Authenticate client using HTTP Basic Auth or form data."""
    client_id = None
    client_secret = None

    # Try HTTP Basic Auth first
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Basic "):
        try:
            import base64

            encoded_credentials = auth_header[6:]  # Remove "Basic "
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            client_id, client_secret = decoded_credentials.split(":", 1)
        except Exception:
            pass

    # If no basic auth, try form data
    if not client_id or not client_secret:
        form_data = await request.form()
        client_id_form = form_data.get("client_id")
        client_secret_form = form_data.get("client_secret")

        # Handle UploadFile vs string types
        client_id = client_id_form if isinstance(client_id_form, str) else None
        client_secret = (
            client_secret_form if isinstance(client_secret_form, str) else None
        )

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Client authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    client = client_store.get_client(client_id)
    if not client or not client.check_secret(client_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return client


@app.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request) -> dict[str, Any]:
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
async def jwks_endpoint() -> dict[str, Any]:
    """JSON Web Key Set (JWKS) endpoint."""
    return jwks_manager.get_public_keys()


@app.post("/oauth/token")
async def token_endpoint(request: Request) -> JSONResponse:
    """OAuth 2.0 Token endpoint supporting Client Credentials and Authorization Code flows."""

    # Authenticate client using either HTTP Basic Auth or form data
    client = await authenticate_client(request)

    # Parse form data
    form_data = await request.form()
    grant_type = form_data.get("grant_type")
    scope_value = form_data.get("scope", "")

    if grant_type == "authorization_code":
        code_value = form_data.get("code")
        redirect_uri_value = form_data.get("redirect_uri")
        code_verifier_value = form_data.get("code_verifier")

        code_str = code_value if isinstance(code_value, str) else ""
        redirect_uri_str = (
            redirect_uri_value if isinstance(redirect_uri_value, str) else ""
        )
        code_verifier_str = (
            code_verifier_value if isinstance(code_verifier_value, str) else ""
        )

        if not code_str or not redirect_uri_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid_request",
            )

        auth_code = authorization_code_store.validate(
            code_str, client.client_id, redirect_uri_str
        )
        if not auth_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_grant"
            )

        if not AuthorizationCodeStore.verify_pkce(
            code_verifier_str, auth_code.code_challenge, auth_code.code_challenge_method
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_grant"
            )

        authorization_code_store.consume(code_str)

        now = datetime.now(timezone.utc)
        expires_in = 3600
        expires_at = now + timedelta(seconds=expires_in)

        access_token_payload = {
            "iss": f"{request.url.scheme}://{request.url.netloc}",
            "sub": auth_code.user_id,
            "aud": client.audience or client.client_id,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "scope": " ".join(auth_code.scopes),
            "client_id": client.client_id,
            "token_type": "Bearer",
        }

        access_token = jwks_manager.create_jwt(access_token_payload)

        token = Token(
            access_token=access_token,
            token_type="Bearer",
            expires_in=expires_in,
            scope=" ".join(auth_code.scopes),
            client_id=client.client_id,
        )
        token_store.store_token(access_token, token)

        response_data: dict[str, Any] = {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "scope": " ".join(auth_code.scopes),
        }

        if "openid" in auth_code.scopes:
            id_token_payload = {
                "iss": f"{request.url.scheme}://{request.url.netloc}",
                "sub": auth_code.user_id,
                "aud": client.audience or client.client_id,
                "iat": int(now.timestamp()),
                "exp": int(expires_at.timestamp()),
            }
            if auth_code.nonce:
                id_token_payload["nonce"] = auth_code.nonce
            id_token = jwks_manager.create_jwt(id_token_payload)
            response_data["id_token"] = id_token

        logger.info(
            f"Exchanged authorization code for client {client.client_id} with scopes: {auth_code.scopes}"
        )

        return JSONResponse(
            content=response_data,
            headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
        )

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
        "aud": client.audience or client.client_id,  # Use client's audience if set
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
            "aud": client.audience or client.client_id,  # Use client's audience if set
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


@app.get("/oauth/authorize")
async def authorize_endpoint(request: Request) -> RedirectResponse:
    response_type = request.query_params.get("response_type")
    client_id = request.query_params.get("client_id")
    redirect_uri = request.query_params.get("redirect_uri")
    scope = request.query_params.get("scope", "")
    state = request.query_params.get("state")
    nonce = request.query_params.get("nonce")
    code_challenge = request.query_params.get("code_challenge")
    code_challenge_method = request.query_params.get("code_challenge_method")
    user_id = request.query_params.get("user_id")

    if response_type != "code" or not client_id or not redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_request"
        )

    client = client_store.get_client(client_id)
    if not client or "authorization_code" not in client.grant_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="unauthorized_client"
        )

    if redirect_uri not in client.redirect_uris:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_request"
        )

    scope_str = scope if isinstance(scope, str) else ""
    requested_scopes = scope_str.split() if scope_str else []
    allowed_scopes = client.validate_scopes(requested_scopes)

    if not user_id:
        user_id = "demo-user"

    auth_code = authorization_code_store.issue_code(
        client_id=client.client_id,
        user_id=user_id,
        scopes=allowed_scopes,
        redirect_uri=redirect_uri,
        nonce=nonce,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )

    logger.info(
        f"Issued authorization code for client {client.client_id} scopes={allowed_scopes} user={user_id}"
    )

    sep = "&" if ("?" in redirect_uri) else "?"
    location = f"{redirect_uri}{sep}code={auth_code.code}"
    if state:
        location += f"&state={state}"

    return RedirectResponse(url=location, status_code=status.HTTP_302_FOUND)


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


@app.post("/admin/clients", status_code=status.HTTP_201_CREATED)
async def create_client(client_request: ClientCreateRequest) -> ClientResponse:
    """Create a new OAuth client."""
    # Check if client already exists
    if client_store.client_exists(client_request.client_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Client with ID '{client_request.client_id}' already exists",
        )

    # Create new client
    client = Client(
        client_id=client_request.client_id,
        client_secret=client_request.client_secret,
        client_name=client_request.client_name,
        scopes=client_request.scopes,
        grant_types=client_request.grant_types,
        redirect_uris=client_request.redirect_uris,
        audience=client_request.audience,
    )

    client_store.store_client(client)

    logger.info(f"Created new client: {client_request.client_id}")

    # Return client info (without secret)
    return ClientResponse(
        client_id=client.client_id,
        client_name=client.client_name,
        scopes=client.scopes,
        grant_types=client.grant_types,
        redirect_uris=client.redirect_uris,
        audience=client.audience,
        created_at=client.created_at.isoformat(),
        is_active=client.is_active,
    )


@app.delete("/admin/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: str) -> None:
    """Delete an OAuth client."""
    if not client_store.delete_client(client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID '{client_id}' not found",
        )

    logger.info(f"Deleted client: {client_id}")


@app.get("/admin/clients")
async def list_clients() -> list[ClientResponse]:
    """List all OAuth clients."""
    clients = client_store.list_clients()
    return [
        ClientResponse(
            client_id=client.client_id,
            client_name=client.client_name,
            scopes=client.scopes,
            grant_types=client.grant_types,
            redirect_uris=client.redirect_uris,
            audience=client.audience,
            created_at=client.created_at.isoformat(),
            is_active=client.is_active,
        )
        for client in clients
    ]


@app.get("/admin/clients/{client_id}")
async def get_client(client_id: str) -> ClientResponse:
    """Get a specific OAuth client."""
    client = client_store.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID '{client_id}' not found",
        )

    return ClientResponse(
        client_id=client.client_id,
        client_name=client.client_name,
        scopes=client.scopes,
        grant_types=client.grant_types,
        redirect_uris=client.redirect_uris,
        audience=client.audience,
        created_at=client.created_at.isoformat(),
        is_active=client.is_active,
    )

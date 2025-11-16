"""
ReceiverApp Module

This module contains the ReceiverApp FastAPI application that validates OAuth tokens.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from gen_epix.fastapp.services.auth.model import OidcServerCfg
from gen_epix.fastapp.services.auth.oidc_client import OidcClient

# Configure logging
logger = logging.getLogger(__name__)


class ReceiverApp:  # pylint: disable=too-few-public-methods
    """FastAPI app that receives and validates access tokens."""

    def __init__(self, port: int = 8001, oauth_discovery_url: str = ""):
        self.port = port
        self.oauth_discovery_url = oauth_discovery_url
        self.app = FastAPI(title="ReceiverApp", lifespan=self._lifespan)
        self.oidc_client: "OidcClient | None" = None
        self.base_url = f"http://localhost:{port}"
        self._setup_routes()

    @asynccontextmanager
    async def _lifespan(
        self, app: FastAPI  # pylint: disable=unused-argument
    ) -> AsyncGenerator[None, None]:
        """Initialize OIDC client on startup."""
        try:
            # Configure OIDC client for token validation
            # The client_id should be the audience this service expects
            server_cfg = OidcServerCfg(
                name="oauth-server",
                label="OAuth Server",
                client_id="ReceiverApp",  # This service's identifier (expected audience)
                client_secret="receiver-secret",  # Not used for validation
                scope="openid profile",  # Required field - default OIDC scopes
                discovery_url=self.oauth_discovery_url,
            )

            self.oidc_client = OidcClient(
                server_cfg=server_cfg,
                discovery_url=self.oauth_discovery_url,
            )

            logger.info("ReceiverApp OIDC client initialized")
            yield
        finally:
            logger.info("ReceiverApp shutting down")

    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""
        security = HTTPBearer()

        @self.app.get("/test_client_credential_flow")
        async def test_endpoint(
            request: Request,  # pylint: disable=unused-argument
            token: HTTPAuthorizationCredentials = Depends(security),
        ) -> JSONResponse:
            """Protected endpoint that validates access tokens."""
            try:
                if not self.oidc_client:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="OIDC client not initialized",
                    )

                # Get claims from the token - this validates signature, issuer, audience, and expiry
                claims_data = await self.oidc_client.get_claims_from_jwt(
                    token.credentials
                )

                if not claims_data:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                # Token is valid and audience is correct (validated by OIDC client)
                logger.info(
                    f"Successfully validated token for subject: {claims_data.get('sub')}"
                )
                return JSONResponse(
                    content={"status": "OK", "message": "Authentication successful"}
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Token validation error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token validation failed",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from e

        @self.app.get("/health")
        async def health() -> dict[str, str]:
            """Health check endpoint."""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}

"""
RequestorApp Module

This module contains the RequestorApp client that requests access tokens and calls protected endpoints.
"""

import logging
from datetime import datetime, timedelta, timezone

import httpx
import jwt

from gen_epix.fastapp.services.auth.model import OidcServerCfg
from gen_epix.fastapp.services.auth.oauth_idp_client import OauthIdpClient

# Configure logging
logger = logging.getLogger(__name__)


class RequestorApp:
    """Client application that requests access tokens and calls protected endpoints."""

    def __init__(self, client_id: str, client_secret: str, oauth_discovery_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.oauth_discovery_url = oauth_discovery_url
        self.oauth_idp_client: "OauthIdpClient | None" = None
        self._initialize_oauth_idp_client()

    def _initialize_oauth_idp_client(self) -> None:
        """Initialize the OIDC client."""
        try:
            server_cfg = OidcServerCfg(
                name="oauth-server",
                label="OAuth Server",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scope="openid profile",  # Required field - default OIDC scopes
                discovery_url=self.oauth_discovery_url,
            )

            self.oauth_idp_client = OauthIdpClient(
                server_cfg=server_cfg,
                discovery_url=self.oauth_discovery_url,
            )

            logger.info(f"RequestorApp OIDC client initialized for {self.client_id}")
        except Exception as e:
            logger.error(f"Failed to initialize RequestorApp OIDC client: {e}")
            raise

    def get_access_token(self, audience: str) -> str:
        """Get an access token for the specified audience."""
        if not self.oauth_idp_client:
            raise RuntimeError("OIDC client not initialized")

        try:
            # Request token with appropriate scope
            scope = "openid read write"
            token = self.oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
                scope
            )
            logger.info(f"Retrieved access token for audience {audience}")
            return token
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise

    def call_protected_endpoint(
        self, endpoint_url: str, access_token: str
    ) -> httpx.Response:
        """Call a protected endpoint with the access token."""
        headers = {"Authorization": f"Bearer {access_token}"}

        with httpx.Client() as client:
            response = client.get(endpoint_url, headers=headers, timeout=10.0)
            return response

    def create_invalid_token(self, audience: str) -> str:
        """Create a properly formatted but invalid JWT token for testing."""
        # Create a token with invalid signature
        now = datetime.now(timezone.utc)
        payload: dict[str, str | int] = {
            "iss": "http://localhost:8000",
            "sub": self.client_id,
            "aud": audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "scope": "openid read write",
        }

        # Use a dummy secret to create an invalid signature
        invalid_token = jwt.encode(payload, "invalid-secret", algorithm="HS256")
        return invalid_token

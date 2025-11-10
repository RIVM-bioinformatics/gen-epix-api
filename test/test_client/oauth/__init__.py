"""
OAuth 2.0 Provider with OpenID Connect Support

This package provides a complete OAuth 2.0 authorization server with OIDC support,
implementing the Client Credentials flow and all standard OAuth endpoints.

Main components:
- server: FastAPI application with OAuth endpoints
- client_store: Client registration and management
- token_store: Token storage and validation
- jwks: JWT token generation and key management
- validators: OAuth 2.0 request validation
- oidc_provider: OpenID Connect functionality
- demo_client: Example client implementation

Usage:
    python server.py    # Start the OAuth server
    python demo_client.py    # Test the server
"""

from .client_store import Client, ClientStore
from .jwks import JWKSManager
from .oidc_provider import OIDCProvider
from .server import app
from .token_store import Token, TokenStore
from .validators import OAuth2Validator

__version__ = "1.0.0"
__author__ = "Gen-EpiX Team"
__all__ = [
    "app",
    "Client",
    "ClientStore",
    "Token",
    "TokenStore",
    "JWKSManager",
    "OAuth2Validator",
    "OIDCProvider",
]

"""
OAuth 2.0 Validators

This module provides validation logic for OAuth 2.0 requests
using the oauthlib framework. It implements the RequestValidator
interface required by oauthlib's OAuth2Provider.
"""

from test.test_client.oauth.client_store import ClientStore
from test.test_client.oauth.token_store import Token, TokenStore
from typing import Any

from oauthlib.oauth2 import RequestValidator


class OAuth2Validator(RequestValidator):
    """OAuth 2.0 request validator for oauthlib integration."""

    def __init__(self, client_store: ClientStore, token_store: TokenStore):
        """Initialize the validator with stores."""
        self.client_store = client_store
        self.token_store = token_store
        super().__init__()

    def client_authentication_required(
        self, request: Any, *args: Any, **kwargs: Any
    ) -> bool:
        """Determine if client authentication is required."""
        # Client credentials flow always requires authentication
        return bool(request.grant_type == "client_credentials")

    def authenticate_client(self, request: Any, *args: Any, **kwargs: Any) -> bool:
        """Authenticate the client."""
        client_id = getattr(request, "client_id", None)
        client_secret = getattr(request, "client_secret", None)

        if not client_id or not client_secret:
            return False

        client = self.client_store.get_client(client_id)
        if not client:
            return False

        # Set the client on the request for later use
        request.client = client
        return bool(client.check_secret(client_secret))

    def validate_client_id(
        self, client_id: str, request: Any, *args: Any, **kwargs: Any
    ) -> bool:
        """Validate that the client_id exists."""
        return bool(self.client_store.client_exists(client_id))

    def get_default_scopes(
        self, client_id: str, request: Any, *args: Any, **kwargs: Any
    ) -> list[str]:
        """Get default scopes for a client."""
        client = self.client_store.get_client(client_id)
        if client:
            # Return first scope as default, or empty list
            return client.scopes[:1] if client.scopes else []
        return []

    def validate_scopes(
        self,
        client_id: str,
        scopes: list[str],
        client: Any,
        request: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """Validate that the requested scopes are allowed for the client."""
        oauth_client = self.client_store.get_client(client_id)
        if not oauth_client:
            return False

        # Check if all requested scopes are in the client's allowed scopes
        allowed_scopes = set(oauth_client.scopes)
        requested_scopes = set(scopes)

        return requested_scopes.issubset(allowed_scopes)

    def validate_response_type(
        self,
        client_id: str,
        response_type: str,
        client: Any,
        request: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """Validate the response type."""
        # For client credentials flow, we don't use response_type
        return True

    def save_authorization_code(
        self, client_id: str, code: dict, request: Any, *args: Any, **kwargs: Any
    ) -> None:
        """Save authorization code (not used in client credentials flow)."""
        pass

    def validate_code(
        self,
        client_id: str,
        code: str,
        client: Any,
        request: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """Validate authorization code (not used in client credentials flow)."""
        return False

    def confirm_redirect_uri(
        self,
        client_id: str,
        code: str,
        redirect_uri: str,
        client: Any,
        request: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """Confirm redirect URI (not used in client credentials flow)."""
        return False

    def validate_grant_type(
        self,
        client_id: str,
        grant_type: str,
        client: Any,
        request: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """Validate that the grant type is supported by the client."""
        oauth_client = self.client_store.get_client(client_id)
        if not oauth_client:
            return False

        return bool(oauth_client.supports_grant_type(grant_type))

    def save_bearer_token(
        self, token: dict, request: Any, *args: Any, **kwargs: Any
    ) -> None:
        """Save bearer token."""
        client_id = getattr(request, "client_id", "") or ""
        scope = token.get("scope", "")

        token_obj = Token(
            access_token=token["access_token"],
            token_type=token.get("token_type", "Bearer"),
            expires_in=token.get("expires_in", 3600),
            scope=scope,
            client_id=client_id,
            refresh_token=token.get("refresh_token"),
        )

        self.token_store.store_token(token["access_token"], token_obj)

    def revoke_token(self, token: str, request: Any, *args: Any, **kwargs: Any) -> None:
        """Revoke a token."""
        self.token_store.delete_token(token)

    def validate_bearer_token(
        self, token: str, scopes: list[str], request: Any
    ) -> bool:
        """Validate bearer token and scopes."""
        stored_token = self.token_store.get_token(token)
        if not stored_token:
            return False

        # Check if token has required scopes
        token_scopes = stored_token.scopes
        required_scopes = set(scopes) if scopes else set()

        return required_scopes.issubset(token_scopes)

    def get_default_redirect_uri(
        self, client_id: str, request: Any, *args: Any, **kwargs: Any
    ) -> str:
        """Get default redirect URI for a client."""
        client = self.client_store.get_client(client_id)
        if client and client.redirect_uris:
            return str(client.redirect_uris[0])
        return ""

    def validate_redirect_uri(
        self, client_id: str, redirect_uri: str, request: Any, *args: Any, **kwargs: Any
    ) -> bool:
        """Validate redirect URI."""
        client = self.client_store.get_client(client_id)
        if not client:
            return False

        return bool(client.supports_redirect_uri(redirect_uri))

    def is_within_original_scope(
        self,
        request_scopes: list[str],
        refresh_token: str,
        request: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        """Check if requested scopes are within original scope."""
        token = self.token_store.get_token_by_refresh(refresh_token)
        if not token:
            return False

        original_scopes = token.scopes
        requested_scopes = set(request_scopes)

        return requested_scopes.issubset(original_scopes)

    def validate_refresh_token(
        self, refresh_token: str, client: Any, request: Any, *args: Any, **kwargs: Any
    ) -> bool:
        """Validate refresh token."""
        token = self.token_store.get_token_by_refresh(refresh_token)
        return token is not None

    def get_default_scopes_for_client_credentials(
        self, client_id: str, request: Any, *args: Any, **kwargs: Any
    ) -> list[str]:
        """Get default scopes for client credentials grant."""
        return self.get_default_scopes(client_id, request, *args, **kwargs)

    def introspect_token(
        self,
        token: str,
        token_type_hint: str | None,
        request: Any,
        *args: Any,
        **kwargs: Any,
    ) -> dict:
        """Introspect token for RFC 7662 compliance."""
        stored_token = self.token_store.get_token(token)

        if not stored_token:
            return {"active": False}

        return {
            "active": True,
            "client_id": stored_token.client_id,
            "scope": stored_token.scope,
            "token_type": stored_token.token_type,
            "exp": int(stored_token.expires_at.timestamp()),
            "iat": int(stored_token.created_at.timestamp()),
            "sub": stored_token.client_id,  # For client credentials, subject is client_id
        }

"""
OAuth 2.0 Token Store

This module manages OAuth 2.0 access tokens and refresh tokens.
It provides in-memory storage for demo purposes but can be extended
to use a database backend with proper expiration handling.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass
class Token:
    """OAuth 2.0 Token representation."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    scope: str = ""
    client_id: str = ""
    refresh_token: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def expires_at(self) -> datetime:
        """Calculate the expiration time of the token."""
        return self.created_at + timedelta(seconds=self.expires_in)

    @property
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def scopes(self) -> set[str]:
        """Get the token scopes as a set."""
        return set(self.scope.split()) if self.scope else set()

    def has_scope(self, scope: str) -> bool:
        """Check if the token has a specific scope."""
        return scope in self.scopes

    def to_dict(self) -> dict:
        """Convert token to dictionary."""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "scope": self.scope,
            "client_id": self.client_id,
            "refresh_token": self.refresh_token,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_expired": self.is_expired,
        }


class TokenStore:
    """In-memory store for OAuth 2.0 tokens."""

    def __init__(self) -> None:
        self._tokens: dict[str, Token] = {}
        self._refresh_tokens: dict[str, str] = (
            {}
        )  # refresh_token -> access_token mapping

    def store_token(self, access_token: str, token: Token) -> None:
        """Store an access token."""
        self._tokens[access_token] = token

        # If there's a refresh token, store the mapping
        if token.refresh_token:
            self._refresh_tokens[token.refresh_token] = access_token

    def get_token(self, access_token: str) -> Token | None:
        """Retrieve a token by access token."""
        token = self._tokens.get(access_token)
        if token and not token.is_expired:
            return token
        elif token and token.is_expired:
            # Clean up expired token
            self.delete_token(access_token)
        return None

    def get_token_by_refresh(self, refresh_token: str) -> Token | None:
        """Retrieve a token by refresh token."""
        access_token = self._refresh_tokens.get(refresh_token)
        if access_token:
            return self.get_token(access_token)
        return None

    def delete_token(self, access_token: str) -> bool:
        """Delete a token and its refresh token mapping."""
        token = self._tokens.get(access_token)
        if token:
            # Remove refresh token mapping if it exists
            if token.refresh_token and token.refresh_token in self._refresh_tokens:
                del self._refresh_tokens[token.refresh_token]

            # Remove access token
            del self._tokens[access_token]
            return True
        return False

    def delete_refresh_token(self, refresh_token: str) -> bool:
        """Delete a refresh token and its associated access token."""
        access_token = self._refresh_tokens.get(refresh_token)
        if access_token:
            return self.delete_token(access_token)
        return False

    def revoke_tokens_for_client(self, client_id: str) -> int:
        """Revoke all tokens for a specific client."""
        tokens_to_delete = []
        for access_token, token in self._tokens.items():
            if token.client_id == client_id:
                tokens_to_delete.append(access_token)

        for access_token in tokens_to_delete:
            self.delete_token(access_token)

        return len(tokens_to_delete)

    def cleanup_expired_tokens(self) -> int:
        """Remove all expired tokens from the store."""
        expired_tokens = []
        for access_token, token in self._tokens.items():
            if token.is_expired:
                expired_tokens.append(access_token)

        for access_token in expired_tokens:
            self.delete_token(access_token)

        return len(expired_tokens)

    def list_active_tokens(self, client_id: str | None = None) -> list[Token]:
        """List all active (non-expired) tokens, optionally filtered by client."""
        active_tokens = []
        for token in self._tokens.values():
            if not token.is_expired:
                if client_id is None or token.client_id == client_id:
                    active_tokens.append(token)
        return active_tokens

    def token_exists(self, access_token: str) -> bool:
        """Check if a token exists and is not expired."""
        return self.get_token(access_token) is not None

    def get_token_info(self, access_token: str) -> dict | None:
        """Get token information without the actual token value."""
        token = self.get_token(access_token)
        if token:
            info = token.to_dict()
            # Remove the actual token value for security
            info.pop("access_token", None)
            info.pop("refresh_token", None)
            return info
        return None

    def clear(self) -> None:
        """Clear all tokens (for testing)."""
        self._tokens.clear()
        self._refresh_tokens.clear()

    def size(self) -> int:
        """Get the number of stored tokens."""
        return len(self._tokens)

    def get_stats(self) -> dict:
        """Get token store statistics."""
        total_tokens = len(self._tokens)
        expired_tokens = sum(1 for token in self._tokens.values() if token.is_expired)
        active_tokens = total_tokens - expired_tokens

        return {
            "total_tokens": total_tokens,
            "active_tokens": active_tokens,
            "expired_tokens": expired_tokens,
            "refresh_tokens": len(self._refresh_tokens),
        }

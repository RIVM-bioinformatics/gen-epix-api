"""
OAuth 2.0 Client Store

This module manages OAuth 2.0 client registration and validation.
It provides in-memory storage for demo purposes but can be extended
to use a database backend.
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Client:
    """OAuth 2.0 Client representation."""

    client_id: str
    client_secret: str
    client_name: str
    scopes: list[str] = field(default_factory=list)
    grant_types: list[str] = field(default_factory=lambda: ["client_credentials"])
    redirect_uris: list[str] = field(default_factory=list)
    audience: str | None = field(default=None)  # Target audience for M2M clients
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

    def __post_init__(self) -> None:
        """Hash the client secret for security."""
        if not self.client_secret.startswith("$hashed$"):
            self.client_secret = self._hash_secret(self.client_secret)

    @staticmethod
    def _hash_secret(secret: str) -> str:
        """Hash a client secret using SHA-256."""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((secret + salt).encode()).hexdigest()
        return f"$hashed${salt}${hashed}"

    def check_secret(self, secret: str) -> bool:
        """Verify a client secret against the stored hash."""
        if not self.client_secret.startswith("$hashed$"):
            # For backward compatibility with unhashed secrets
            return self.client_secret == secret

        try:
            parts = self.client_secret.split("$")
            if len(parts) != 4:  # ['', 'hashed', 'salt', 'hash']
                return False
            _, hashed_marker, salt, stored_hash = parts
            computed_hash = hashlib.sha256((secret + salt).encode()).hexdigest()
            return secrets.compare_digest(stored_hash, computed_hash)
        except (ValueError, IndexError):
            return False

    def validate_scopes(self, requested_scopes: list[str]) -> list[str]:
        """Validate and filter requested scopes against allowed scopes."""
        if not requested_scopes:
            return []

        allowed_scope_set = set(self.scopes)
        requested_scope_set = set(requested_scopes)

        # Return only scopes that are both requested and allowed
        valid_scopes = list(requested_scope_set.intersection(allowed_scope_set))
        return valid_scopes

    def supports_grant_type(self, grant_type: str) -> bool:
        """Check if the client supports a specific grant type."""
        return grant_type in self.grant_types

    def supports_redirect_uri(self, redirect_uri: str) -> bool:
        """Check if the redirect URI is registered for this client."""
        return redirect_uri in self.redirect_uris

    def to_dict(self) -> dict:
        """Convert client to dictionary (excluding sensitive data)."""
        return {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "scopes": self.scopes,
            "grant_types": self.grant_types,
            "redirect_uris": self.redirect_uris,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
        }


class ClientStore:
    """In-memory store for OAuth 2.0 clients."""

    def __init__(self) -> None:
        self._clients: dict[str, Client] = {}

    def store_client(self, client: Client) -> None:
        """Store a client in the store."""
        self._clients[client.client_id] = client

    def get_client(self, client_id: str) -> Client | None:
        """Retrieve a client by client ID."""
        client = self._clients.get(client_id)
        if client and client.is_active:
            return client
        return None

    def delete_client(self, client_id: str) -> bool:
        """Delete a client from the store."""
        if client_id in self._clients:
            del self._clients[client_id]
            return True
        return False

    def deactivate_client(self, client_id: str) -> bool:
        """Deactivate a client (soft delete)."""
        client = self._clients.get(client_id)
        if client:
            client.is_active = False
            return True
        return False

    def list_clients(self) -> list[Client]:
        """List all active clients."""
        return [client for client in self._clients.values() if client.is_active]

    def client_exists(self, client_id: str) -> bool:
        """Check if a client exists and is active."""
        return self.get_client(client_id) is not None

    def update_client(self, client_id: str, **kwargs: Any) -> bool:
        """Update client properties."""
        client = self.get_client(client_id)
        if not client:
            return False

        # Update allowed fields
        allowed_fields = {
            "client_name",
            "scopes",
            "grant_types",
            "redirect_uris",
            "is_active",
        }
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(client, field, value)

        return True

    def create_client(
        self,
        client_name: str,
        scopes: list[str],
        grant_types: list[str] | None = None,
        redirect_uris: list[str] | None = None,
        audience: str | None = None,
    ) -> Client:
        """Create a new client with auto-generated credentials."""
        client_id = f"client_{secrets.token_urlsafe(16)}"
        client_secret = secrets.token_urlsafe(32)

        if grant_types is None:
            grant_types = ["client_credentials"]
        if redirect_uris is None:
            redirect_uris = []

        client = Client(
            client_id=client_id,
            client_secret=client_secret,
            client_name=client_name,
            scopes=scopes,
            grant_types=grant_types,
            redirect_uris=redirect_uris,
            audience=audience,
        )

        self.store_client(client)
        return client

    def clear(self) -> None:
        """Clear all clients (for testing)."""
        self._clients.clear()

    def size(self) -> int:
        """Get the number of stored clients."""
        return len(self._clients)

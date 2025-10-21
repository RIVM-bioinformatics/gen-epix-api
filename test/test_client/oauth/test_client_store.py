"""
Unit tests for OAuth 2.0 Client Store

This module contains comprehensive pytest unit tests for the Client and ClientStore classes
in client_store.py. It tests all functionality including client creation, validation,
secret hashing, scope validation, and store operations.

Run tests with:
    pytest test_client_store.py -v
    pytest test_client_store.py::TestClient -v
    pytest test_client_store.py::TestClientStore -v
"""

import os
import sys
from datetime import datetime
from test.test_client.oauth.client_store import Client, ClientStore
from typing import Any
from unittest.mock import patch

import pytest

# Add the oauth directory to the path for imports
oauth_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, oauth_path)


class TestClient:
    """Test cases for the Client class."""

    def test_client_creation_basic(self) -> None:
        """Test basic client creation with required fields."""
        client = Client(
            client_id="test-client",
            client_secret="test-secret",
            client_name="Test Client",
        )

        assert client.client_id == "test-client"
        assert client.client_name == "Test Client"
        assert client.is_active is True
        assert client.scopes == []
        assert client.grant_types == ["client_credentials"]
        assert client.redirect_uris == []
        assert isinstance(client.created_at, datetime)

    def test_client_creation_with_all_fields(self) -> None:
        """Test client creation with all optional fields."""
        created_at = datetime(2023, 1, 1, 12, 0, 0)

        client = Client(
            client_id="full-client",
            client_secret="full-secret",
            client_name="Full Client",
            scopes=["read", "write", "admin"],
            grant_types=["client_credentials", "authorization_code"],
            redirect_uris=["https://example.com/callback"],
            created_at=created_at,
            is_active=False,
        )

        assert client.client_id == "full-client"
        assert client.client_name == "Full Client"
        assert client.scopes == ["read", "write", "admin"]
        assert client.grant_types == ["client_credentials", "authorization_code"]
        assert client.redirect_uris == ["https://example.com/callback"]
        assert client.created_at == created_at
        assert client.is_active is False

    def test_client_secret_hashing_on_creation(self) -> None:
        """Test that client secrets are automatically hashed on creation."""
        original_secret = "my-plain-secret"

        client = Client(
            client_id="hash-test",
            client_secret=original_secret,
            client_name="Hash Test Client",
        )

        # Secret should be hashed and not equal to original
        assert client.client_secret != original_secret
        assert client.client_secret.startswith("$hashed$")

        # Should be able to verify the original secret
        assert client.check_secret(original_secret) is True
        assert client.check_secret("wrong-secret") is False

    def test_client_secret_no_double_hashing(self) -> None:
        """Test that already hashed secrets are not hashed again."""
        hashed_secret = "$hashed$abc123$def456"

        client = Client(
            client_id="no-double-hash",
            client_secret=hashed_secret,
            client_name="No Double Hash Client",
        )

        # Secret should remain unchanged
        assert client.client_secret == hashed_secret

    def test_hash_secret_static_method(self) -> None:
        """Test the _hash_secret static method."""
        secret = "test-secret"
        hashed = Client._hash_secret(secret)

        assert hashed.startswith("$hashed$")
        assert hashed != secret

        # Each call should produce different hash (due to random salt)
        hashed2 = Client._hash_secret(secret)
        assert hashed != hashed2

    def test_check_secret_with_hashed_secret(self) -> None:
        """Test secret verification with properly hashed secrets."""
        original_secret = "verify-me"
        client = Client(
            client_id="verify-test",
            client_secret=original_secret,
            client_name="Verify Test",
        )

        # Correct secret should verify
        assert client.check_secret(original_secret) is True

        # Wrong secrets should not verify
        assert client.check_secret("wrong-secret") is False
        assert client.check_secret("") is False
        assert client.check_secret("verify-ME") is False  # Case sensitive

    def test_check_secret_backward_compatibility(self) -> None:
        """Test backward compatibility with unhashed secrets."""
        unhashed_secret = "plain-secret"

        # Manually create client with unhashed secret
        client = Client(
            client_id="backward-test",
            client_secret="placeholder",
            client_name="Backward Test",
        )
        # Override the hashed secret to test backward compatibility
        client.client_secret = unhashed_secret

        # Should work with plain text comparison
        assert client.check_secret(unhashed_secret) is True
        assert client.check_secret("wrong") is False

    def test_check_secret_with_malformed_hash(self) -> None:
        """Test secret verification with malformed hash format."""
        client = Client(
            client_id="malformed-test",
            client_secret="placeholder",
            client_name="Malformed Test",
        )

        # Set malformed hash formats
        malformed_hashes = [
            "$hashed$",  # Missing parts
            "$hashed$salt",  # Missing hash
            "hashed$salt$hash",  # Missing prefix $
            "$hashed$salt$hash$extra",  # Too many parts
        ]

        for malformed_hash in malformed_hashes:
            client.client_secret = malformed_hash
            assert client.check_secret("any-secret") is False

    def test_validate_scopes_empty_request(self) -> None:
        """Test scope validation with empty requested scopes."""
        client = Client(
            client_id="scope-test",
            client_secret="secret",
            client_name="Scope Test",
            scopes=["read", "write", "admin"],
        )

        # Empty request should return empty list
        assert client.validate_scopes([]) == []

    def test_validate_scopes_all_valid(self) -> None:
        """Test scope validation with all valid requested scopes."""
        client = Client(
            client_id="scope-test",
            client_secret="secret",
            client_name="Scope Test",
            scopes=["read", "write", "admin"],
        )

        # All requested scopes are allowed
        requested = ["read", "write"]
        validated = client.validate_scopes(requested)
        assert set(validated) == set(requested)

    def test_validate_scopes_some_invalid(self) -> None:
        """Test scope validation with mix of valid and invalid scopes."""
        client = Client(
            client_id="scope-test",
            client_secret="secret",
            client_name="Scope Test",
            scopes=["read", "write"],
        )

        # Mix of valid and invalid scopes
        requested = ["read", "admin", "write", "delete"]
        validated = client.validate_scopes(requested)

        # Should only return valid scopes
        assert set(validated) == {"read", "write"}

    def test_validate_scopes_none_valid(self) -> None:
        """Test scope validation with no valid requested scopes."""
        client = Client(
            client_id="scope-test",
            client_secret="secret",
            client_name="Scope Test",
            scopes=["read", "write"],
        )

        # None of the requested scopes are allowed
        requested = ["admin", "delete", "create"]
        validated = client.validate_scopes(requested)
        assert validated == []

    def test_validate_scopes_duplicates(self) -> None:
        """Test scope validation removes duplicates."""
        client = Client(
            client_id="scope-test",
            client_secret="secret",
            client_name="Scope Test",
            scopes=["read", "write", "admin"],
        )

        # Request with duplicates
        requested = ["read", "write", "read", "write"]
        validated = client.validate_scopes(requested)

        # Should return unique scopes
        assert set(validated) == {"read", "write"}
        assert len(validated) == 2

    def test_supports_grant_type(self) -> None:
        """Test grant type support checking."""
        client = Client(
            client_id="grant-test",
            client_secret="secret",
            client_name="Grant Test",
            grant_types=["client_credentials", "authorization_code"],
        )

        assert client.supports_grant_type("client_credentials") is True
        assert client.supports_grant_type("authorization_code") is True
        assert client.supports_grant_type("refresh_token") is False
        assert client.supports_grant_type("invalid_grant") is False

    def test_supports_redirect_uri(self) -> None:
        """Test redirect URI support checking."""
        client = Client(
            client_id="redirect-test",
            client_secret="secret",
            client_name="Redirect Test",
            redirect_uris=[
                "https://example.com/callback",
                "https://app.example.com/auth/callback",
            ],
        )

        assert client.supports_redirect_uri("https://example.com/callback") is True
        assert (
            client.supports_redirect_uri("https://app.example.com/auth/callback")
            is True
        )
        assert client.supports_redirect_uri("https://evil.com/callback") is False
        assert client.supports_redirect_uri("") is False

    def test_to_dict_excludes_sensitive_data(self) -> None:
        """Test that to_dict excludes sensitive information."""
        created_at = datetime(2023, 1, 1, 12, 0, 0)

        client = Client(
            client_id="dict-test",
            client_secret="sensitive-secret",
            client_name="Dict Test",
            scopes=["read", "write"],
            grant_types=["client_credentials"],
            redirect_uris=["https://example.com/callback"],
            created_at=created_at,
            is_active=True,
        )

        client_dict = client.to_dict()

        # Should include non-sensitive fields
        assert client_dict["client_id"] == "dict-test"
        assert client_dict["client_name"] == "Dict Test"
        assert client_dict["scopes"] == ["read", "write"]
        assert client_dict["grant_types"] == ["client_credentials"]
        assert client_dict["redirect_uris"] == ["https://example.com/callback"]
        assert client_dict["created_at"] == created_at.isoformat()
        assert client_dict["is_active"] is True

        # Should NOT include sensitive fields
        assert "client_secret" not in client_dict

    def test_default_factory_functions(self) -> None:
        """Test that default factory functions work correctly for multiple instances."""
        client1 = Client(
            client_id="default1", client_secret="secret1", client_name="Default Test 1"
        )

        client2 = Client(
            client_id="default2", client_secret="secret2", client_name="Default Test 2"
        )

        # Each client should have its own list instances
        client1.scopes.append("read")
        client1.grant_types.append("authorization_code")

        # client2 should not be affected
        assert "read" not in client2.scopes
        assert "authorization_code" not in client2.grant_types
        assert client2.grant_types == ["client_credentials"]


class TestClientStore:
    """Test cases for the ClientStore class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.store = ClientStore()

        # Create test clients
        self.test_client1 = Client(
            client_id="client1",
            client_secret="secret1",
            client_name="Test Client 1",
            scopes=["read", "write"],
        )

        self.test_client2 = Client(
            client_id="client2",
            client_secret="secret2",
            client_name="Test Client 2",
            scopes=["read"],
            is_active=False,  # Inactive client
        )

    def test_store_initialization(self) -> None:
        """Test ClientStore initialization."""
        store = ClientStore()
        assert isinstance(store._clients, dict)
        assert len(store._clients) == 0
        assert store.size() == 0

    def test_store_client(self) -> None:
        """Test storing a client."""
        assert self.store.size() == 0

        self.store.store_client(self.test_client1)

        assert self.store.size() == 1
        assert "client1" in self.store._clients
        assert self.store._clients["client1"] == self.test_client1

    def test_store_multiple_clients(self) -> None:
        """Test storing multiple clients."""
        self.store.store_client(self.test_client1)
        self.store.store_client(self.test_client2)

        assert self.store.size() == 2
        assert self.store._clients["client1"] == self.test_client1
        assert self.store._clients["client2"] == self.test_client2

    def test_store_client_overwrites(self) -> None:
        """Test that storing a client with same ID overwrites the previous one."""
        self.store.store_client(self.test_client1)

        # Create new client with same ID
        new_client = Client(
            client_id="client1",  # Same ID
            client_secret="new-secret",
            client_name="New Client 1",
        )

        self.store.store_client(new_client)

        assert self.store.size() == 1
        retrieved = self.store.get_client("client1")
        assert retrieved is not None
        assert retrieved == new_client
        assert retrieved.client_name == "New Client 1"

    def test_get_client_existing_active(self) -> None:
        """Test retrieving an existing active client."""
        self.store.store_client(self.test_client1)

        retrieved = self.store.get_client("client1")

        assert retrieved is not None
        assert retrieved == self.test_client1
        assert retrieved.client_id == "client1"

    def test_get_client_existing_inactive(self) -> None:
        """Test retrieving an existing but inactive client returns None."""
        self.store.store_client(self.test_client2)  # Inactive client

        retrieved = self.store.get_client("client2")

        assert retrieved is None

    def test_get_client_nonexistent(self) -> None:
        """Test retrieving a non-existent client returns None."""
        retrieved = self.store.get_client("nonexistent")
        assert retrieved is None

    def test_delete_client_existing(self) -> None:
        """Test deleting an existing client."""
        self.store.store_client(self.test_client1)
        assert self.store.size() == 1

        result = self.store.delete_client("client1")

        assert result is True
        assert self.store.size() == 0
        assert self.store.get_client("client1") is None

    def test_delete_client_nonexistent(self) -> None:
        """Test deleting a non-existent client."""
        result = self.store.delete_client("nonexistent")
        assert result is False

    def test_deactivate_client_existing(self) -> None:
        """Test deactivating an existing client."""
        self.store.store_client(self.test_client1)
        assert self.test_client1.is_active is True

        result = self.store.deactivate_client("client1")

        assert result is True
        assert self.test_client1.is_active is False
        assert (
            self.store.get_client("client1") is None
        )  # Should not return inactive clients

    def test_deactivate_client_nonexistent(self) -> None:
        """Test deactivating a non-existent client."""
        result = self.store.deactivate_client("nonexistent")
        assert result is False

    def test_list_clients_active_only(self) -> None:
        """Test listing clients returns only active clients."""
        self.store.store_client(self.test_client1)  # Active
        self.store.store_client(self.test_client2)  # Inactive

        # Add another active client
        active_client = Client(
            client_id="active",
            client_secret="secret",
            client_name="Active Client",
            is_active=True,
        )
        self.store.store_client(active_client)

        clients = self.store.list_clients()

        assert len(clients) == 2  # Only active clients
        client_ids = [c.client_id for c in clients]
        assert "client1" in client_ids
        assert "active" in client_ids
        assert "client2" not in client_ids  # Inactive client excluded

    def test_list_clients_empty_store(self) -> None:
        """Test listing clients from empty store."""
        clients = self.store.list_clients()
        assert clients == []

    def test_client_exists_active(self) -> None:
        """Test client_exists returns True for active clients."""
        self.store.store_client(self.test_client1)

        assert self.store.client_exists("client1") is True

    def test_client_exists_inactive(self) -> None:
        """Test client_exists returns False for inactive clients."""
        self.store.store_client(self.test_client2)  # Inactive

        assert self.store.client_exists("client2") is False

    def test_client_exists_nonexistent(self) -> None:
        """Test client_exists returns False for non-existent clients."""
        assert self.store.client_exists("nonexistent") is False

    def test_update_client_existing(self) -> None:
        """Test updating an existing client."""
        self.store.store_client(self.test_client1)

        result = self.store.update_client(
            "client1",
            client_name="Updated Name",
            scopes=["read", "write", "admin"],
            is_active=False,
        )

        assert result is True

        updated_client = self.store._clients[
            "client1"
        ]  # Access directly since it's inactive
        assert updated_client.client_name == "Updated Name"
        assert updated_client.scopes == ["read", "write", "admin"]
        assert updated_client.is_active is False

    def test_update_client_nonexistent(self) -> None:
        """Test updating a non-existent client."""
        result = self.store.update_client("nonexistent", client_name="New Name")
        assert result is False

    def test_update_client_restricted_fields(self) -> None:
        """Test that only allowed fields can be updated."""
        self.store.store_client(self.test_client1)
        original_id = self.test_client1.client_id
        original_secret = self.test_client1.client_secret

        # Try to update restricted fields
        result = self.store.update_client(
            "client1",
            client_secret="new-secret",  # Not allowed
            client_name="Updated Name",  # Allowed
        )

        assert result is True

        updated_client = self.store.get_client("client1")
        assert updated_client is not None
        assert updated_client.client_id == original_id  # Unchanged
        assert updated_client.client_secret == original_secret  # Unchanged
        assert updated_client.client_name == "Updated Name"  # Updated

    def test_create_client_basic(self) -> None:
        """Test creating a client with auto-generated credentials."""
        client = self.store.create_client(
            client_name="Auto Client", scopes=["read", "write"]
        )

        assert client.client_name == "Auto Client"
        assert client.scopes == ["read", "write"]
        assert client.grant_types == ["client_credentials"]  # Default
        assert client.redirect_uris == []  # Default
        assert client.client_id.startswith("client_")
        assert len(client.client_id) > 10  # Should be reasonably long
        assert client.client_secret.startswith("$hashed$")  # Should be hashed
        assert client.is_active is True

        # Should be stored in the store
        assert self.store.size() == 1
        assert self.store.get_client(client.client_id) == client

    def test_create_client_with_options(self) -> None:
        """Test creating a client with all optional parameters."""
        client = self.store.create_client(
            client_name="Full Auto Client",
            scopes=["read", "write", "admin"],
            grant_types=["client_credentials", "authorization_code"],
            redirect_uris=["https://example.com/callback"],
        )

        assert client.client_name == "Full Auto Client"
        assert client.scopes == ["read", "write", "admin"]
        assert client.grant_types == ["client_credentials", "authorization_code"]
        assert client.redirect_uris == ["https://example.com/callback"]

    @patch("secrets.token_urlsafe")
    def test_create_client_unique_ids(self, mock_token: Any) -> None:
        """Test that created clients have unique IDs."""
        # Mock to return predictable values
        mock_token.side_effect = ["abc123", "secret1", "def456", "secret2"]

        client1 = self.store.create_client("Client 1", ["read"])
        client2 = self.store.create_client("Client 2", ["write"])

        assert client1.client_id == "client_abc123"
        assert client2.client_id == "client_def456"
        assert client1.client_id != client2.client_id

    def test_clear_store(self) -> None:
        """Test clearing all clients from the store."""
        self.store.store_client(self.test_client1)
        self.store.store_client(self.test_client2)
        assert self.store.size() == 2

        self.store.clear()

        assert self.store.size() == 0
        assert self.store.list_clients() == []
        assert self.store.get_client("client1") is None

    def test_size_tracking(self) -> None:
        """Test that size() accurately tracks the number of clients."""
        assert self.store.size() == 0

        self.store.store_client(self.test_client1)
        assert self.store.size() == 1

        self.store.store_client(self.test_client2)
        assert self.store.size() == 2

        self.store.delete_client("client1")
        assert self.store.size() == 1

        self.store.clear()
        assert self.store.size() == 0


class TestClientStoreIntegration:
    """Integration tests for Client and ClientStore working together."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.store = ClientStore()

    def test_end_to_end_client_lifecycle(self) -> None:
        """Test complete client lifecycle: create, retrieve, update, deactivate, delete."""
        # Create client
        client = self.store.create_client(
            client_name="Lifecycle Test", scopes=["read", "write"]
        )
        client_id = client.client_id
        original_secret = client.client_secret

        # Retrieve and verify
        retrieved = self.store.get_client(client_id)
        assert retrieved is not None
        assert retrieved.client_name == "Lifecycle Test"

        # Update client
        self.store.update_client(
            client_id,
            client_name="Updated Lifecycle Test",
            scopes=["read", "write", "admin"],
        )

        updated = self.store.get_client(client_id)
        assert updated is not None
        assert updated.client_name == "Updated Lifecycle Test"
        assert updated.scopes == ["read", "write", "admin"]
        assert updated.client_secret == original_secret  # Secret unchanged

        # Deactivate client
        self.store.deactivate_client(client_id)
        assert self.store.get_client(client_id) is None  # Should not be retrievable
        assert not self.store.client_exists(client_id)

        # Delete client completely
        assert self.store.delete_client(client_id) is True
        assert self.store.size() == 0

    def test_multiple_clients_independence(self) -> None:
        """Test that multiple clients in the store are independent."""
        # Create multiple clients
        client1 = self.store.create_client("Client 1", ["read"])
        client2 = self.store.create_client("Client 2", ["write"])
        client3 = self.store.create_client("Client 3", ["admin"])

        # Verify all are stored and retrievable
        assert self.store.size() == 3
        assert self.store.get_client(client1.client_id) == client1
        assert self.store.get_client(client2.client_id) == client2
        assert self.store.get_client(client3.client_id) == client3

        # Update one client
        self.store.update_client(client2.client_id, client_name="Updated Client 2")

        # Verify others are unchanged
        updated_client2 = self.store.get_client(client2.client_id)
        assert updated_client2 is not None
        assert updated_client2.client_name == "Updated Client 2"

        client1_check = self.store.get_client(client1.client_id)
        client3_check = self.store.get_client(client3.client_id)
        assert client1_check is not None
        assert client3_check is not None
        assert client1_check.client_name == "Client 1"
        assert client3_check.client_name == "Client 3"

        # Deactivate one client
        self.store.deactivate_client(client3.client_id)

        # Verify others are still active
        assert self.store.client_exists(client1.client_id) is True
        assert self.store.client_exists(client2.client_id) is True
        assert self.store.client_exists(client3.client_id) is False

        active_clients = self.store.list_clients()
        assert len(active_clients) == 2

    def test_secret_verification_after_storage(self) -> None:
        """Test that secret verification works after storing and retrieving clients."""
        original_secret = "my-test-secret"

        # Create client with known secret (it will be hashed)
        client = Client(
            client_id="secret-test",
            client_secret=original_secret,
            client_name="Secret Test",
        )

        self.store.store_client(client)

        # Retrieve and verify secret still works
        retrieved = self.store.get_client("secret-test")
        assert retrieved is not None
        assert retrieved.check_secret(original_secret) is True
        assert retrieved.check_secret("wrong-secret") is False


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])

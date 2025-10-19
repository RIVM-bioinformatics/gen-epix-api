"""
Unit tests for OAuth 2.0 Token Store

This module contains comprehensive pytest unit tests for the Token and TokenStore classes
in token_store.py. It tests all functionality including token creation, validation,
expiration handling, scope management, and store operations.

Run tests with:
    pytest test_token_store.py -v
    pytest test_token_store.py::TestToken -v
    pytest test_token_store.py::TestTokenStore -v
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from test.test_client.oauth.token_store import Token, TokenStore
from typing import Any
from unittest.mock import patch

import pytest

# Add the oauth directory to the path for imports
oauth_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, oauth_path)


class TestToken:
    """Test cases for the Token class."""

    def test_token_creation_basic(self) -> None:
        """Test basic token creation with required fields."""
        token = Token(access_token="test-token-123")

        assert token.access_token == "test-token-123"
        assert token.token_type == "Bearer"
        assert token.expires_in == 3600  # Default 1 hour
        assert token.scope == ""
        assert token.client_id == ""
        assert token.refresh_token is None
        assert isinstance(token.created_at, datetime)
        assert token.created_at.tzinfo == timezone.utc

    def test_token_creation_with_all_fields(self) -> None:
        """Test token creation with all optional fields."""
        created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        token = Token(
            access_token="full-token-456",
            token_type="MAC",
            expires_in=7200,
            scope="read write admin",
            client_id="client-123",
            refresh_token="refresh-789",
            created_at=created_at,
        )

        assert token.access_token == "full-token-456"
        assert token.token_type == "MAC"
        assert token.expires_in == 7200
        assert token.scope == "read write admin"
        assert token.client_id == "client-123"
        assert token.refresh_token == "refresh-789"
        assert token.created_at == created_at

    def test_expires_at_calculation(self) -> None:
        """Test that expires_at is calculated correctly."""
        created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        token = Token(
            access_token="expires-test",
            expires_in=3600,
            created_at=created_at,
        )

        expected_expires_at = created_at + timedelta(seconds=3600)
        assert token.expires_at == expected_expires_at

    def test_is_expired_false_for_valid_token(self) -> None:
        """Test that a valid token is not expired."""
        # Create a token that expires in the future
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        token = Token(
            access_token="valid-token",
            expires_in=7200,  # 2 hours
            created_at=future_time - timedelta(hours=1),  # Created 1 hour ago
        )

        assert token.is_expired is False

    @patch("token_store.datetime")
    def test_is_expired_true_for_expired_token(self, mock_datetime: Any) -> None:
        """Test that an expired token is marked as expired."""
        # Mock current time
        current_time = datetime(2023, 1, 1, 14, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = current_time

        # Create token that was created 2 hours ago with 1 hour expiry
        created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        token = Token(
            access_token="expired-token",
            expires_in=3600,  # 1 hour
            created_at=created_at,
        )

        assert token.is_expired is True

    def test_scopes_property_with_multiple_scopes(self) -> None:
        """Test scopes property with multiple scopes."""
        token = Token(
            access_token="scope-test",
            scope="read write admin delete",
        )

        scopes = token.scopes
        assert isinstance(scopes, set)
        assert scopes == {"read", "write", "admin", "delete"}

    def test_scopes_property_with_single_scope(self) -> None:
        """Test scopes property with single scope."""
        token = Token(
            access_token="single-scope",
            scope="read",
        )

        assert token.scopes == {"read"}

    def test_scopes_property_with_empty_scope(self) -> None:
        """Test scopes property with empty scope."""
        token = Token(
            access_token="no-scope",
            scope="",
        )

        assert token.scopes == set()

    def test_scopes_property_with_whitespace_handling(self) -> None:
        """Test scopes property handles extra whitespace."""
        token = Token(
            access_token="whitespace-test",
            scope="  read   write  admin  ",
        )

        assert token.scopes == {"read", "write", "admin"}

    def test_has_scope_true_for_existing_scope(self) -> None:
        """Test has_scope returns True for existing scopes."""
        token = Token(
            access_token="has-scope-test",
            scope="read write admin",
        )

        assert token.has_scope("read") is True
        assert token.has_scope("write") is True
        assert token.has_scope("admin") is True

    def test_has_scope_false_for_missing_scope(self) -> None:
        """Test has_scope returns False for missing scopes."""
        token = Token(
            access_token="missing-scope-test",
            scope="read write",
        )

        assert token.has_scope("admin") is False
        assert token.has_scope("delete") is False
        assert token.has_scope("") is False

    def test_has_scope_case_sensitive(self) -> None:
        """Test has_scope is case sensitive."""
        token = Token(
            access_token="case-test",
            scope="read write",
        )

        assert token.has_scope("read") is True
        assert token.has_scope("READ") is False
        assert token.has_scope("Read") is False

    def test_to_dict_contains_all_fields(self) -> None:
        """Test to_dict includes all token fields."""
        created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        token = Token(
            access_token="dict-test",
            token_type="Bearer",
            expires_in=3600,
            scope="read write",
            client_id="client-123",
            refresh_token="refresh-456",
            created_at=created_at,
        )

        token_dict = token.to_dict()

        assert token_dict["access_token"] == "dict-test"
        assert token_dict["token_type"] == "Bearer"
        assert token_dict["expires_in"] == 3600
        assert token_dict["scope"] == "read write"
        assert token_dict["client_id"] == "client-123"
        assert token_dict["refresh_token"] == "refresh-456"
        assert token_dict["created_at"] == created_at.isoformat()
        assert token_dict["expires_at"] == token.expires_at.isoformat()
        assert isinstance(token_dict["is_expired"], bool)

    def test_to_dict_with_none_refresh_token(self) -> None:
        """Test to_dict handles None refresh token."""
        token = Token(access_token="none-refresh")

        token_dict = token.to_dict()
        assert token_dict["refresh_token"] is None

    @patch("token_store.datetime")
    def test_to_dict_expiration_status_dynamic(self, mock_datetime: Any) -> None:
        """Test that to_dict reflects current expiration status."""
        # Test with non-expired token
        current_time = datetime(2023, 1, 1, 12, 30, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = current_time

        created_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        token = Token(
            access_token="dynamic-test",
            expires_in=3600,
            created_at=created_at,
        )

        token_dict = token.to_dict()
        assert token_dict["is_expired"] is False

        # Test with expired token
        future_time = datetime(2023, 1, 1, 14, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = future_time

        token_dict = token.to_dict()
        assert token_dict["is_expired"] is True


class TestTokenStore:
    """Test cases for the TokenStore class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.store = TokenStore()

        # Create test tokens
        self.test_token1 = Token(
            access_token="token1",
            client_id="client1",
            scope="read write",
            refresh_token="refresh1",
        )

        self.test_token2 = Token(
            access_token="token2",
            client_id="client2",
            scope="read",
            expires_in=7200,
        )

        # Create an expired token for testing
        past_time = datetime.now(timezone.utc) - timedelta(hours=2)
        self.expired_token = Token(
            access_token="expired-token",
            client_id="client1",
            scope="read",
            expires_in=3600,
            created_at=past_time,
        )

    def test_store_initialization(self) -> None:
        """Test TokenStore initialization."""
        store = TokenStore()
        assert isinstance(store._tokens, dict)
        assert isinstance(store._refresh_tokens, dict)
        assert len(store._tokens) == 0
        assert len(store._refresh_tokens) == 0
        assert store.size() == 0

    def test_store_token_basic(self) -> None:
        """Test storing a basic token."""
        self.store.store_token("token1", self.test_token1)

        assert self.store.size() == 1
        assert "token1" in self.store._tokens
        assert self.store._tokens["token1"] == self.test_token1

    def test_store_token_with_refresh_token(self) -> None:
        """Test storing a token with refresh token creates mapping."""
        self.store.store_token("token1", self.test_token1)

        assert "refresh1" in self.store._refresh_tokens
        assert self.store._refresh_tokens["refresh1"] == "token1"

    def test_store_token_without_refresh_token(self) -> None:
        """Test storing a token without refresh token."""
        self.store.store_token("token2", self.test_token2)

        assert self.store.size() == 1
        assert len(self.store._refresh_tokens) == 0

    def test_store_multiple_tokens(self) -> None:
        """Test storing multiple tokens."""
        self.store.store_token("token1", self.test_token1)
        self.store.store_token("token2", self.test_token2)

        assert self.store.size() == 2
        assert self.store._tokens["token1"] == self.test_token1
        assert self.store._tokens["token2"] == self.test_token2

    def test_get_token_existing_valid(self) -> None:
        """Test retrieving an existing valid token."""
        self.store.store_token("token1", self.test_token1)

        retrieved = self.store.get_token("token1")

        assert retrieved is not None
        assert retrieved == self.test_token1
        assert retrieved.access_token == "token1"

    def test_get_token_nonexistent(self) -> None:
        """Test retrieving a non-existent token returns None."""
        retrieved = self.store.get_token("nonexistent")
        assert retrieved is None

    def test_get_token_expired_auto_cleanup(self) -> None:
        """Test that retrieving expired token auto-cleans it."""
        self.store.store_token("expired-token", self.expired_token)
        assert self.store.size() == 1

        retrieved = self.store.get_token("expired-token")

        assert retrieved is None
        assert self.store.size() == 0  # Should be cleaned up

    def test_get_token_by_refresh_existing(self) -> None:
        """Test retrieving token by refresh token."""
        self.store.store_token("token1", self.test_token1)

        retrieved = self.store.get_token_by_refresh("refresh1")

        assert retrieved is not None
        assert retrieved == self.test_token1

    def test_get_token_by_refresh_nonexistent(self) -> None:
        """Test retrieving token by non-existent refresh token."""
        retrieved = self.store.get_token_by_refresh("nonexistent")
        assert retrieved is None

    def test_get_token_by_refresh_expired_token(self) -> None:
        """Test retrieving expired token by refresh token."""
        expired_with_refresh = Token(
            access_token="expired-refresh",
            refresh_token="expired-refresh-token",
            expires_in=3600,
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        self.store.store_token("expired-refresh", expired_with_refresh)

        retrieved = self.store.get_token_by_refresh("expired-refresh-token")

        assert retrieved is None  # Should return None for expired token

    def test_delete_token_existing(self) -> None:
        """Test deleting an existing token."""
        self.store.store_token("token1", self.test_token1)
        assert self.store.size() == 1
        assert "refresh1" in self.store._refresh_tokens

        result = self.store.delete_token("token1")

        assert result is True
        assert self.store.size() == 0
        assert "refresh1" not in self.store._refresh_tokens

    def test_delete_token_nonexistent(self) -> None:
        """Test deleting a non-existent token."""
        result = self.store.delete_token("nonexistent")
        assert result is False

    def test_delete_token_without_refresh_token(self) -> None:
        """Test deleting token without refresh token."""
        self.store.store_token("token2", self.test_token2)

        result = self.store.delete_token("token2")

        assert result is True
        assert self.store.size() == 0

    def test_delete_refresh_token_existing(self) -> None:
        """Test deleting by refresh token."""
        self.store.store_token("token1", self.test_token1)

        result = self.store.delete_refresh_token("refresh1")

        assert result is True
        assert self.store.size() == 0
        assert "refresh1" not in self.store._refresh_tokens

    def test_delete_refresh_token_nonexistent(self) -> None:
        """Test deleting by non-existent refresh token."""
        result = self.store.delete_refresh_token("nonexistent")
        assert result is False

    def test_revoke_tokens_for_client_single_client(self) -> None:
        """Test revoking all tokens for a specific client."""
        # Add tokens for different clients
        self.store.store_token("token1", self.test_token1)  # client1
        self.store.store_token("token2", self.test_token2)  # client2

        revoked_count = self.store.revoke_tokens_for_client("client1")

        assert revoked_count == 1
        assert self.store.size() == 1
        assert self.store.get_token("token1") is None
        assert self.store.get_token("token2") is not None

    def test_revoke_tokens_for_client_multiple_tokens(self) -> None:
        """Test revoking multiple tokens for same client."""
        # Create additional token for client1
        token3 = Token(
            access_token="token3",
            client_id="client1",
            scope="admin",
        )

        self.store.store_token("token1", self.test_token1)  # client1
        self.store.store_token("token2", self.test_token2)  # client2
        self.store.store_token("token3", token3)  # client1

        revoked_count = self.store.revoke_tokens_for_client("client1")

        assert revoked_count == 2
        assert self.store.size() == 1
        assert self.store.get_token("token2") is not None  # client2 token remains

    def test_revoke_tokens_for_client_nonexistent_client(self) -> None:
        """Test revoking tokens for non-existent client."""
        self.store.store_token("token1", self.test_token1)

        revoked_count = self.store.revoke_tokens_for_client("nonexistent")

        assert revoked_count == 0
        assert self.store.size() == 1

    def test_cleanup_expired_tokens(self) -> None:
        """Test cleaning up expired tokens."""
        # Add mix of valid and expired tokens
        self.store.store_token("token1", self.test_token1)  # Valid
        self.store.store_token("expired-token", self.expired_token)  # Expired
        self.store.store_token("token2", self.test_token2)  # Valid

        cleanup_count = self.store.cleanup_expired_tokens()

        assert cleanup_count == 1
        assert self.store.size() == 2
        assert self.store.get_token("token1") is not None
        assert self.store.get_token("token2") is not None
        assert self.store.get_token("expired-token") is None

    def test_cleanup_expired_tokens_none_expired(self) -> None:
        """Test cleanup when no tokens are expired."""
        self.store.store_token("token1", self.test_token1)
        self.store.store_token("token2", self.test_token2)

        cleanup_count = self.store.cleanup_expired_tokens()

        assert cleanup_count == 0
        assert self.store.size() == 2

    def test_list_active_tokens_all_clients(self) -> None:
        """Test listing all active tokens."""
        self.store.store_token("token1", self.test_token1)
        self.store.store_token("token2", self.test_token2)
        self.store.store_token("expired-token", self.expired_token)

        active_tokens = self.store.list_active_tokens()

        assert len(active_tokens) == 2
        token_ids = [token.access_token for token in active_tokens]
        assert "token1" in token_ids
        assert "token2" in token_ids
        assert "expired-token" not in token_ids

    def test_list_active_tokens_filtered_by_client(self) -> None:
        """Test listing active tokens filtered by client."""
        self.store.store_token("token1", self.test_token1)  # client1
        self.store.store_token("token2", self.test_token2)  # client2

        active_tokens = self.store.list_active_tokens("client1")

        assert len(active_tokens) == 1
        assert active_tokens[0].access_token == "token1"
        assert active_tokens[0].client_id == "client1"

    def test_list_active_tokens_empty_store(self) -> None:
        """Test listing active tokens from empty store."""
        active_tokens = self.store.list_active_tokens()
        assert active_tokens == []

    def test_token_exists_valid_token(self) -> None:
        """Test token_exists returns True for valid tokens."""
        self.store.store_token("token1", self.test_token1)

        assert self.store.token_exists("token1") is True

    def test_token_exists_expired_token(self) -> None:
        """Test token_exists returns False for expired tokens."""
        self.store.store_token("expired-token", self.expired_token)

        assert self.store.token_exists("expired-token") is False

    def test_token_exists_nonexistent_token(self) -> None:
        """Test token_exists returns False for non-existent tokens."""
        assert self.store.token_exists("nonexistent") is False

    def test_get_token_info_existing_token(self) -> None:
        """Test getting token info excludes sensitive data."""
        self.store.store_token("token1", self.test_token1)

        info = self.store.get_token_info("token1")

        assert info is not None
        assert "access_token" not in info
        assert "refresh_token" not in info
        assert info["token_type"] == "Bearer"
        assert info["client_id"] == "client1"
        assert info["scope"] == "read write"

    def test_get_token_info_nonexistent_token(self) -> None:
        """Test getting info for non-existent token."""
        info = self.store.get_token_info("nonexistent")
        assert info is None

    def test_get_token_info_expired_token(self) -> None:
        """Test getting info for expired token."""
        self.store.store_token("expired-token", self.expired_token)

        info = self.store.get_token_info("expired-token")
        assert info is None  # Should return None for expired tokens

    def test_clear_store(self) -> None:
        """Test clearing all tokens from the store."""
        self.store.store_token("token1", self.test_token1)
        self.store.store_token("token2", self.test_token2)
        assert self.store.size() == 2

        self.store.clear()

        assert self.store.size() == 0
        assert len(self.store._refresh_tokens) == 0
        assert self.store.list_active_tokens() == []

    def test_size_tracking(self) -> None:
        """Test that size() accurately tracks the number of tokens."""
        assert self.store.size() == 0

        self.store.store_token("token1", self.test_token1)
        assert self.store.size() == 1

        self.store.store_token("token2", self.test_token2)
        assert self.store.size() == 2

        self.store.delete_token("token1")
        assert self.store.size() == 1

        self.store.clear()
        assert self.store.size() == 0

    def test_get_stats_comprehensive(self) -> None:
        """Test get_stats returns accurate statistics."""
        # Add mix of active, expired tokens, and refresh tokens
        self.store.store_token("token1", self.test_token1)  # Active with refresh
        self.store.store_token("token2", self.test_token2)  # Active without refresh
        self.store.store_token("expired-token", self.expired_token)  # Expired

        stats = self.store.get_stats()

        assert stats["total_tokens"] == 3
        assert stats["active_tokens"] == 2
        assert stats["expired_tokens"] == 1
        assert stats["refresh_tokens"] == 1  # Only token1 has refresh token

    def test_get_stats_empty_store(self) -> None:
        """Test get_stats for empty store."""
        stats = self.store.get_stats()

        assert stats["total_tokens"] == 0
        assert stats["active_tokens"] == 0
        assert stats["expired_tokens"] == 0
        assert stats["refresh_tokens"] == 0


class TestTokenStoreIntegration:
    """Integration tests for Token and TokenStore working together."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.store = TokenStore()

    def test_complete_token_lifecycle(self) -> None:
        """Test complete token lifecycle: create, store, retrieve, delete."""
        # Create token
        token = Token(
            access_token="lifecycle-test",
            client_id="test-client",
            scope="read write admin",
            refresh_token="lifecycle-refresh",
            expires_in=7200,
        )

        # Store token
        self.store.store_token("lifecycle-test", token)
        assert self.store.size() == 1

        # Retrieve by access token
        retrieved = self.store.get_token("lifecycle-test")
        assert retrieved is not None
        assert retrieved.access_token == "lifecycle-test"

        # Retrieve by refresh token
        by_refresh = self.store.get_token_by_refresh("lifecycle-refresh")
        assert by_refresh is not None
        assert by_refresh == retrieved

        # Verify token properties
        assert token.has_scope("read")
        assert token.has_scope("write")
        assert token.has_scope("admin")
        assert not token.is_expired

        # Delete token
        self.store.delete_token("lifecycle-test")
        assert self.store.size() == 0
        assert self.store.get_token("lifecycle-test") is None

    def test_token_expiration_workflow(self) -> None:
        """Test workflow with token expiration."""
        # Create token with short expiry
        past_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        token = Token(
            access_token="expiry-test",
            expires_in=1800,  # 30 minutes
            created_at=past_time,
        )

        self.store.store_token("expiry-test", token)

        # Token should be expired
        assert token.is_expired is True

        # Store should auto-cleanup on retrieval
        retrieved = self.store.get_token("expiry-test")
        assert retrieved is None
        assert self.store.size() == 0

    def test_multiple_clients_token_management(self) -> None:
        """Test managing tokens for multiple clients."""
        # Create tokens for different clients
        client1_token1 = Token(
            access_token="client1-token1",
            client_id="client1",
            scope="read",
        )
        client1_token2 = Token(
            access_token="client1-token2",
            client_id="client1",
            scope="write",
        )
        client2_token = Token(
            access_token="client2-token",
            client_id="client2",
            scope="admin",
        )

        # Store all tokens
        self.store.store_token("client1-token1", client1_token1)
        self.store.store_token("client1-token2", client1_token2)
        self.store.store_token("client2-token", client2_token)

        assert self.store.size() == 3

        # List tokens for specific client
        client1_tokens = self.store.list_active_tokens("client1")
        assert len(client1_tokens) == 2

        client2_tokens = self.store.list_active_tokens("client2")
        assert len(client2_tokens) == 1

        # Revoke all tokens for client1
        revoked = self.store.revoke_tokens_for_client("client1")
        assert revoked == 2
        assert self.store.size() == 1

        # Only client2 token should remain
        remaining_tokens = self.store.list_active_tokens()
        assert len(remaining_tokens) == 1
        assert remaining_tokens[0].client_id == "client2"

    def test_refresh_token_workflow(self) -> None:
        """Test complete refresh token workflow."""
        # Create token with refresh token
        original_token = Token(
            access_token="original-access",
            refresh_token="refresh-123",
            client_id="refresh-client",
            scope="read write",
        )

        self.store.store_token("original-access", original_token)

        # Verify refresh token mapping
        assert "refresh-123" in self.store._refresh_tokens
        assert self.store._refresh_tokens["refresh-123"] == "original-access"

        # Retrieve by refresh token
        retrieved = self.store.get_token_by_refresh("refresh-123")
        assert retrieved is not None
        assert retrieved.access_token == "original-access"

        # Simulate token refresh - delete old token and create new one
        self.store.delete_refresh_token("refresh-123")
        assert self.store.size() == 0

        # Create new token with new refresh token
        new_token = Token(
            access_token="new-access",
            refresh_token="refresh-456",
            client_id="refresh-client",
            scope="read write",
        )

        self.store.store_token("new-access", new_token)

        # Old refresh token should not work
        assert self.store.get_token_by_refresh("refresh-123") is None

        # New refresh token should work
        new_retrieved = self.store.get_token_by_refresh("refresh-456")
        assert new_retrieved is not None
        assert new_retrieved.access_token == "new-access"

    def test_scope_validation_integration(self) -> None:
        """Test scope validation in integration context."""
        token = Token(
            access_token="scope-integration",
            scope="read write user:profile user:email",
        )

        self.store.store_token("scope-integration", token)

        retrieved = self.store.get_token("scope-integration")
        assert retrieved is not None

        # Test various scope checks
        assert retrieved.has_scope("read") is True
        assert retrieved.has_scope("write") is True
        assert retrieved.has_scope("user:profile") is True
        assert retrieved.has_scope("user:email") is True
        assert retrieved.has_scope("admin") is False

        # Test scope set
        expected_scopes = {"read", "write", "user:profile", "user:email"}
        assert retrieved.scopes == expected_scopes


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])

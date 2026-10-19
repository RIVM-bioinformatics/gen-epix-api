"""Exercise user-manager claim key derivation and abstract operations."""

from types import SimpleNamespace

import pytest

from gen_epix.fastapp.user_manager import BaseUserManager


@pytest.mark.parametrize(
    ("claims", "expected"),
    [
        ({}, None),
        ({"email": None}, None),
        ({"email": ""}, None),
        ({"email": "User@Example.COM"}, "user@example.com"),
    ],
    ids=["missing-email", "none-email", "empty-email", "normalizes-case"],
)
def test_get_user_key_from_claims_uses_email_default(
    claims: dict[str, str | None], expected: str | None
) -> None:
    """Return normalized keys for the default email claim cases."""
    manager = SimpleNamespace(STANDARD_EMAIL_CLAIM="email")

    assert BaseUserManager.get_user_key_from_claims(manager, claims) == expected


def test_get_user_key_from_claims_uses_configured_claim_without_mutation() -> None:
    """Use the configured claim name without changing the claims mapping."""
    manager = SimpleNamespace(STANDARD_EMAIL_CLAIM="preferred_username")
    claims = {"preferred_username": "User.Name", "email": "other@example.com"}
    original_claims = claims.copy()

    assert BaseUserManager.get_user_key_from_claims(manager, claims) == "user.name"
    assert claims == original_claims


def test_base_user_manager_declares_required_abstract_operations() -> None:
    """Keep the user-resolution operations abstract for concrete managers."""
    assert BaseUserManager.__abstractmethods__ == {
        "construct_user_instance_from_claims",
        "create_root_user_from_claims",
        "is_root_user_claims",
        "is_root_user",
        "auto_create_new_user",
        "create_new_user_from_token",
        "is_existing_user_by_key",
        "retrieve_user_by_key",
        "retrieve_user_by_id",
        "retrieve_user_permissions",
        "get_user_name_from_claims",
        "update_user_name",
    }

from datetime import datetime, timedelta
from math import floor
from test.fastapp.auth_test_client import AuthTestClient
from test.fastapp.user_manager import MOCK_USER, MockUser
from typing import Any

import pytest

from gen_epix.fastapp.services.auth.util import get_name_from_claims


class CommonAuthTestClient(AuthTestClient):

    pass


@pytest.fixture(scope="module", name="env")
def get_test_client() -> CommonAuthTestClient:
    return (
        CommonAuthTestClient.get_test_client()
    )  # type:ignore[no-any-return,no-untyped_call]


class TestAuth:
    NON_SECURE_ENDPOINT = "/non_secure"
    CURRENT_USER_ENDPOINT = "/secure/current_user"

    NOW = datetime.now()
    INVALID_CLAIMS = {
        "aud": "wrong_aud",  # client id
        "iss": "http://localhost:5003",  # authorization server
        "nbf": floor((NOW + timedelta(seconds=1000)).timestamp()),
        "exp": floor((NOW - timedelta(seconds=1000)).timestamp()),
        "iat": floor((NOW + timedelta(seconds=1000)).timestamp()),
    }

    INVALID_JWK = {
        "alg": "RS384",
        "kid": "wrong_key_id",
        #
        # The following jwk fields are not being checked:
        #
        # "issuer": "wrong_issuer",
        # "use": "wrong_use",
        # "x5t": "wrong_x5t",
        # "kty": "wrong_kty",
    }

    def test_extracts_name_prefers_name(self) -> None:
        claims: dict[str, Any] = {
            "name": "Jane Doe",
            "preferred_username": "jane",
        }
        assert get_name_from_claims(claims, ["name"]) == "Jane Doe"

    def test_extracts_name_given_family(self) -> None:
        claims: dict[str, Any] = {
            "given_name": "Ada",
            "family_name": "Lovelace",
        }
        assert (
            get_name_from_claims(claims, [["given_name", "family_name"]])
            == "Ada Lovelace"
        )

    def test_extracts_preferred_username(self) -> None:
        claims: dict[str, Any] = {
            "preferred_username": "mockuser",
        }
        assert get_name_from_claims(claims, ["preferred_username"]) == "mockuser"

    def test_extracts_name_fallback_email(self) -> None:
        claims: dict[str, Any] = {"email": "user1@org1.org"}
        # No name-like claims present in provided list
        assert get_name_from_claims(claims, ["name"]) is None

    def test_update_user_name_no_change(self, env: AuthTestClient) -> None:
        user: MockUser | None = env.user_manager.update_user_name(MOCK_USER, "John")
        assert user == MOCK_USER
        if user:
            assert user.name == "John"

    def test_update_user_name_changed(self, env: AuthTestClient) -> None:
        user: MockUser | None = env.user_manager.update_user_name(MOCK_USER, "")
        if user:
            assert user.name == ""

    def test_update_user_name_real_user(self, env: AuthTestClient) -> None:
        new_name = "Johnny"
        user: MockUser | None = env.user_manager.update_user_name(MOCK_USER, new_name)
        if user:
            assert user.name == new_name

    def test_update_user_name_real_user_last_name(self, env: AuthTestClient) -> None:
        new_name = "John Doe"
        user: MockUser | None = env.user_manager.update_user_name(MOCK_USER, new_name)
        if user:
            assert user.name == new_name

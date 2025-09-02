from datetime import datetime, timedelta
from math import floor
from test.fastapp.unit.auth.test_auth import MOCK_JWK_TOKEN, AuthTestClient
from test.fastapp.user_manager import MOCK_USER, MockUser
from typing import Any
from unittest.mock import MagicMock

import pytest

from gen_epix.fastapp.services.auth.oidc_client import OIDCClient
from gen_epix.fastapp.services.auth.util import get_name_from_claims


class CommonAuthTestClient(AuthTestClient):

    pass


@pytest.fixture(scope="module", name="env")
def get_test_client() -> CommonAuthTestClient:
    return CommonAuthTestClient.get_test_client()


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

    def test_non_secure_happy_flow(self, env: AuthTestClient) -> None:
        response = env.test_client.get(TestAuth.NON_SECURE_ENDPOINT)
        assert response.status_code == 200

    def test_valid_jwt_token_happy_flow(self, env: AuthTestClient) -> None:
        response = env.test_client.get(
            TestAuth.CURRENT_USER_ENDPOINT,
            headers=env.mock_create_token_header(MOCK_JWK_TOKEN.token),
        )
        assert response.status_code == 200

    def test_secure_no_token(self, env: AuthTestClient) -> None:
        response = env.test_client.get(self.CURRENT_USER_ENDPOINT)
        assert response.status_code == 401

    def test_invalid_jwt_token(self, env: AuthTestClient) -> None:
        response = env.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=env.mock_create_token_header(
                MOCK_JWK_TOKEN.token + "invalid_token"
            ),
        )
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "key,value", INVALID_CLAIMS.items(), ids=INVALID_CLAIMS.keys()
    )
    def test_invalid_claims(self, env: AuthTestClient, key: str, value: str) -> None:
        edited_token = MOCK_JWK_TOKEN.edit_claim(key, value)
        response = env.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=env.mock_create_token_header(edited_token),
        )
        assert response.status_code in (401, 403)

    @pytest.mark.parametrize("key,value", INVALID_JWK.items(), ids=INVALID_JWK.keys())
    def test_invalid_jwk(self, env: AuthTestClient, key: str, value: str) -> None:
        for idp_client in env.auth_service.idp_clients:
            if isinstance(idp_client, OIDCClient):
                idp_client._load_keys = MagicMock(return_value=None)
            else:
                raise NotImplementedError
        edited_token = MOCK_JWK_TOKEN.edit_jwk(key, value)
        response = env.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=env.mock_create_token_header(edited_token),
        )
        assert response.status_code in (401, 403)

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

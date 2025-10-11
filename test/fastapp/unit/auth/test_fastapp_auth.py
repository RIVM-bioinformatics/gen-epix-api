from datetime import datetime, timedelta
from math import floor
from test.fastapp.auth_test_client import AuthTestClient
from unittest.mock import MagicMock

import pytest

from gen_epix.fastapp.services.auth import OidcClient


@pytest.fixture(scope="module", name="env")
def get_test_client() -> AuthTestClient:
    return (
        AuthTestClient.get_test_client()
    )  # type:ignore[no-any-return,no-untyped-call]


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
            headers=env.mock_create_token_header(env.MOCK_JWK_TOKEN.token),
        )
        assert response.status_code == 200

    def test_secure_no_token(self, env: AuthTestClient) -> None:
        response = env.test_client.get(self.CURRENT_USER_ENDPOINT)
        assert response.status_code == 401

    def test_invalid_jwt_token(self, env: AuthTestClient) -> None:
        response = env.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=env.mock_create_token_header(
                env.MOCK_JWK_TOKEN.token + "invalid_token"
            ),
        )
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "key,value", INVALID_CLAIMS.items(), ids=INVALID_CLAIMS.keys()
    )
    def test_invalid_claims(self, env: AuthTestClient, key: str, value: str) -> None:
        edited_token = env.MOCK_JWK_TOKEN.edit_claim(key, value)
        response = env.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=env.mock_create_token_header(edited_token),
        )
        assert response.status_code in (401, 403)

    @pytest.mark.parametrize("key,value", INVALID_JWK.items(), ids=INVALID_JWK.keys())
    def test_invalid_jwk(self, env: AuthTestClient, key: str, value: str) -> None:
        for idp_client in env.auth_service.idp_clients:
            if isinstance(idp_client, OidcClient):
                idp_client._load_keys = MagicMock(return_value=None)
            else:
                raise NotImplementedError
        edited_token = env.MOCK_JWK_TOKEN.edit_jwk(key, value)
        response = env.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=env.mock_create_token_header(edited_token),
        )
        assert response.status_code in (401, 403)

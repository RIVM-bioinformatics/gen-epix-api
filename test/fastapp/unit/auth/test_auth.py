from datetime import datetime, timedelta
from math import floor
from test.fastapp.enum import ServiceType
from test.fastapp.unit.auth.mock_jwk_and_token import MockJWKAndToken
from test.fastapp.user_manager import UserManager
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwk

from gen_epix.fastapp.app import App
from gen_epix.fastapp.middleware import HandleAuthExceptionMiddleware
from gen_epix.fastapp.services.auth import AuthService, OIDCClient

MOCK_JWK_TOKEN = MockJWKAndToken(token_expiration_minutes=10)


class AuthTestClient:

    TEST_CLIENTS = None

    @classmethod
    def get_test_client(cls):
        if cls.TEST_CLIENTS is None:
            cls.TEST_CLIENTS = AuthTestClient()
        return cls.TEST_CLIENTS

    def __init__(self) -> None:
        # Generate fast_api and test client
        user_manager = UserManager()
        app = App(user_manager=user_manager, logger=None)
        idps_cfg: list[dict[str, str | list]] = [
            {
                "name": "idp1",
                "label": "idp1",
                "protocol": "OIDC",
                "issuer": MOCK_JWK_TOKEN.payload["iss"],
                "discovery_url": "https://idp1.org/configuration",
                "client_id": MOCK_JWK_TOKEN.payload["aud"],
                "scope": "openid profile email",
                "authorization_endpoint": "https://idp1.org/authenticate",
                "token_endpoint": "https://idp1.org/token",
                "jwks_uri": "https://idp1.org/certs",
                "userinfo_endpoint": "https://idp1.org/userinfo",
                "response_types_supported": ["code"],
                "subject_types_supported": ["public"],
                "id_token_signing_alg_values_supported": ["RS256"],
            }
        ]
        auth_service = AuthService(
            app, service_type=ServiceType.AUTH, idps_cfg=idps_cfg
        )
        for idp_client in auth_service.idp_clients:
            if isinstance(idp_client, OIDCClient):
                idp_client._signing_keys = {
                    MOCK_JWK_TOKEN.public_jwk_dict["kid"]: jwk.construct(
                        MOCK_JWK_TOKEN.public_jwk_dict
                    )
                }
        # Create user dependencies
        registered_user_dependency, new_user_dependency, idp_user_dependency = (
            auth_service.create_user_dependencies()
        )
        fast_api = FastAPI()
        fast_api.add_middleware(HandleAuthExceptionMiddleware, fast_app=app)

        @fast_api.get("/non_secure")
        async def non_secure() -> str:
            return "OK"

        @fast_api.get("/secure/current_user")
        async def secure__current_user(user: registered_user_dependency) -> str:  # type: ignore
            return "OK"

        @fast_api.get("/secure/new_user")
        async def secure__new(user: new_user_dependency) -> str:  # type: ignore
            return "OK"

        @fast_api.get("/secure/idp_user")
        async def secure__idp_user(user: idp_user_dependency) -> str:  # type: ignore
            return "OK"

        # Set attributes
        self.fast_api = fast_api
        self.auth_service = auth_service
        self.user_manager = user_manager
        self.app = app
        self.test_client = TestClient(fast_api)
        self.registered_user_dependency = registered_user_dependency
        self.new_user_dependency = new_user_dependency
        self.idp_user_dependency = idp_user_dependency

    @staticmethod
    def mock_create_token_header(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def mock_get_claims_from_userinfo(
        self, access_token: str
    ) -> dict[str, str | int | bool | list[str]]:
        return {}


@pytest.fixture(scope="module", name="env")
def get_test_client() -> AuthTestClient:
    return AuthTestClient.get_test_client()


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

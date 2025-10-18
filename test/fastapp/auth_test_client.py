from test.fastapp.enum import ServiceType
from test.fastapp.unit.auth.mock_jwk_and_token import MockJWKAndToken
from test.fastapp.user_manager import UserManager

from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwk

from gen_epix.fastapp.app import App
from gen_epix.fastapp.middleware import HandleAuthExceptionMiddleware
from gen_epix.fastapp.services.auth import AuthService, OidcClient


class AuthTestClient:

    MOCK_JWK_TOKEN = MockJWKAndToken(token_expiration_minutes=10)
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
                "issuer": AuthTestClient.MOCK_JWK_TOKEN.payload["iss"],
                "discovery_url": "https://idp1.org/configuration",
                "client_id": AuthTestClient.MOCK_JWK_TOKEN.payload["aud"],
                "claim_map": {"__key__": "email"},
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
            if isinstance(idp_client, OidcClient):
                idp_client._signing_keys = {
                    AuthTestClient.MOCK_JWK_TOKEN.public_jwk_dict["kid"]: jwk.construct(
                        AuthTestClient.MOCK_JWK_TOKEN.public_jwk_dict
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

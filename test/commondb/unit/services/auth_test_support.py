import datetime
from contextlib import contextmanager
from test.fastapp.enum import ServiceType
from test.fastapp.unit.auth.mock_jwk_and_token import MockJWKAndToken
from typing import Any, Generator
from uuid import UUID, uuid4

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from gen_epix.commondb.domain import enum as commondb_enum
from gen_epix.commondb.domain import exc as commondb_exc
from gen_epix.commondb.domain import model as commondb_model
from gen_epix.commondb.services.user_manager import UserManager
from gen_epix.fastapp import exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.middleware import HandleAuthExceptionMiddleware
from gen_epix.fastapp.services.auth import AuthService, OauthIdpClient
from gen_epix.fastapp.services.auth.model import Claims

DEFAULT_USER_EMAIL = "user1@org1.org"
UNKNOWN_USER_EMAIL = "unknown@other.org"
ROOT_ORG_ID = UUID("00000000-0000-0000-0000-000000000001")
AUTO_CREATE_ORG_ID = UUID("00000000-0000-0000-0000-000000000002")
MOCK_USER_ID = UUID("00000000-0000-0000-0000-000000000010")
CREATOR_USER_ID = UUID("00000000-0000-0000-0000-000000000011")
OLD_IAT_MINUTES = 5

ROOT_ROLE = commondb_enum.Role.ROOT.value
GUEST_ROLE = commondb_enum.Role.GUEST.value
ALL_ROLES = {role.value for role in commondb_enum.Role}

BASE_IDP_CFG: dict[str, Any] = {
    "name": "idp1",
    "label": "idp1",
    "protocol": "OIDC",
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


def make_cdb_user(
    user_id: UUID | None = None,
    email: str = DEFAULT_USER_EMAIL,
    name: str = "user1",
    roles: set[str] | None = None,
    organization_id: UUID | None = None,
) -> commondb_model.User:
    return commondb_model.User(
        id=user_id or uuid4(),
        key=email,
        email=email,
        name=name,
        is_active=True,
        roles=roles or {GUEST_ROLE},
        organization_id=organization_id or ROOT_ORG_ID,
    )


def make_cdb_organization(
    org_id: UUID | None = None,
    name: str = "Test Org",
    code: str = "TEST",
) -> commondb_model.Organization:
    return commondb_model.Organization(id=org_id or uuid4(), name=name, code=code)


def make_cdb_invitation(
    invited_by_user_id: UUID,
    organization_id: UUID,
    token: str,
    key: str | None = None,
    roles: set[str] | None = None,
) -> commondb_model.UserInvitation:
    return commondb_model.UserInvitation(
        id=uuid4(),
        key=key,
        email=key,
        token=token,
        invited_by_user_id=invited_by_user_id,
        organization_id=organization_id,
        roles=roles or {GUEST_ROLE},
        expires_at=datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(seconds=3600),
    )


def make_idps_cfg(mock_jwk_token: MockJWKAndToken) -> list[dict[str, Any]]:
    return [
        {
            **BASE_IDP_CFG,
            "issuer": mock_jwk_token.payload["iss"],
            "client_id": mock_jwk_token.payload["aud"],
        }
    ]


def make_root_cfg(root_key: str = DEFAULT_USER_EMAIL) -> dict[str, dict[str, Any]]:
    return {
        "organization": {
            "id": ROOT_ORG_ID,
            "name": "Root Organization",
            "code": "ROOT_ORGANIZATION",
        },
        "user": {"key": root_key, "email": root_key, "name": "Root User"},
    }


class InMemoryOrganizationRepository:
    def __init__(self) -> None:
        self._users: dict[UUID, commondb_model.User] = {}
        self._users_by_key: dict[str, commondb_model.User] = {}
        self._orgs: dict[UUID, commondb_model.Organization] = {}
        self._invitations: list[commondb_model.UserInvitation] = []

    def add_user(self, user: commondb_model.User) -> None:
        if user.id is not None:
            self._users[user.id] = user
        if user.key:
            self._users_by_key[user.key] = user

    def add_organization(self, organization: commondb_model.Organization) -> None:
        if organization.id is not None:
            self._orgs[organization.id] = organization

    def add_invitation(self, invitation: commondb_model.UserInvitation) -> None:
        self._invitations.append(invitation)

    def get_user_by_key(self, key: str) -> commondb_model.User | None:
        return self._users_by_key.get(key)

    def user_exists_by_key(self, key: str) -> bool:
        return key in self._users_by_key

    @contextmanager
    def uow(self) -> Generator[object, None, None]:
        yield object()

    def crud(
        self,
        uow: Any,
        user_id: Any,
        model_class: type,
        operation: CrudOperation,
        objs: Any = None,
        obj_ids: Any = None,
        filter: Any = None,
        **kwargs: Any,
    ) -> Any:
        is_org = issubclass(model_class, commondb_model.Organization)
        is_invitation = issubclass(model_class, commondb_model.UserInvitation)

        if operation == CrudOperation.EXISTS_ONE:
            return obj_ids in (self._orgs if is_org else self._users)
        if operation == CrudOperation.CREATE_ONE:
            if is_org:
                org_id = objs.id if objs.id is not None else user_id
                self._orgs[org_id] = objs
                return objs
            new_id = objs.id if objs.id is not None else user_id
            self._users[new_id] = objs
            if objs.key:
                self._users_by_key[objs.key] = objs
            return objs
        if operation == CrudOperation.READ_ONE:
            collection = self._orgs if is_org else self._users
            if obj_ids not in collection:
                raise commondb_exc.NoResultsError(f"Object {obj_ids} not found")
            return collection[obj_ids]
        if operation == CrudOperation.READ_ALL and is_invitation:
            return [
                invitation
                for invitation in self._invitations
                if invitation.invited_by_user_id == user_id
            ]
        if operation == CrudOperation.UPDATE_ONE:
            self._users[user_id] = objs
            if objs.key:
                self._users_by_key[objs.key] = objs
            return objs
        raise NotImplementedError(f"Operation {operation} not implemented in mock")

    def is_existing_user_by_key(self, uow: Any, key: str | None) -> bool:
        return key is not None and key in self._users_by_key


def make_mock_rbac_service() -> Any:
    from test.util.mock_compat import Mock

    service = Mock()
    service.root_role = ROOT_ROLE
    service.guest_role = GUEST_ROLE
    service.get_roles.return_value = ALL_ROLES
    service.retrieve_user_is_root.side_effect = lambda user: ROOT_ROLE in user.roles
    service.retrieve_user_permissions.return_value = set()
    return service


def _retrieve_user_by_key(
    repo: InMemoryOrganizationRepository, key: str
) -> commondb_model.User:
    user = repo.get_user_by_key(key)
    if user is None:
        raise exc.NoResultsError("8c95c4db", f"User with key '{key}' not found")
    return user


def make_commondb_user_manager(
    repo: InMemoryOrganizationRepository,
    root_key: str = DEFAULT_USER_EMAIL,
    auto_created_user_cfg: dict[str, Any] | None = None,
) -> UserManager:
    from test.util.mock_compat import Mock

    organization_service = Mock()
    organization_service.repository = repo
    organization_service.app = Mock()
    organization_service.app.impl = Mock()
    organization_service.app.impl.get_mapped_class.side_effect = lambda cls: cls
    organization_service.generate_id.side_effect = lambda: uuid4()
    organization_service.retrieve_user_by_key.side_effect = lambda key: (
        _retrieve_user_by_key(repo, key)
    )
    return UserManager(
        organization_service=organization_service,
        rbac_service=make_mock_rbac_service(),
        root_cfg=make_root_cfg(root_key),
        auto_created_user_cfg=auto_created_user_cfg,
    )


class AuthEnv:
    SECURE_ENDPOINT = "/secure/current_user"

    def __init__(
        self,
        auto_create_new_users: bool = False,
        root_token_time_to_live: int | None = None,
        token_iat_minutes_ago: int = 0,
        token_expiration_minutes: int = 10,
        initial_users: list[commondb_model.User] | None = None,
        root_key: str = DEFAULT_USER_EMAIL,
        with_http: bool = True,
    ) -> None:
        self.mock_jwk_token = MockJWKAndToken(
            token_expiration_minutes=token_expiration_minutes,
            token_iat_minutes_ago=token_iat_minutes_ago,
        )
        self.repo = InMemoryOrganizationRepository()
        for user in initial_users or []:
            self.repo.add_user(user)

        auto_created_user_cfg = None
        if auto_create_new_users:
            self.repo.add_organization(
                make_cdb_organization(AUTO_CREATE_ORG_ID, "Auto-Create Org", "AUTO")
            )
            auto_created_user_cfg = {
                "organization_id": str(AUTO_CREATE_ORG_ID),
                "roles": [GUEST_ROLE],
            }
        self.user_manager = make_commondb_user_manager(
            self.repo, root_key=root_key, auto_created_user_cfg=auto_created_user_cfg
        )
        self.app = App(user_manager=self.user_manager, logger=None)
        self.auth_service = AuthService(
            self.app,
            service_type=ServiceType.AUTH,
            idps_cfg=make_idps_cfg(self.mock_jwk_token),
            auto_create_new_users=auto_create_new_users,
            root_token_time_to_live=root_token_time_to_live,
        )
        for idp_client in self.auth_service.idp_clients:
            if isinstance(idp_client, OauthIdpClient):
                idp_client._signing_keys = {
                    self.mock_jwk_token.public_jwk_dict["kid"]: jwt.PyJWK.from_dict(
                        self.mock_jwk_token.public_jwk_dict
                    )
                }
        self.token = self.mock_jwk_token.token
        self.test_client: TestClient | None = None
        if with_http:
            self._setup_http()

    def _setup_http(self) -> None:
        registered_dependency, _new_dependency, _idp_dependency = (
            self.auth_service.create_user_dependencies()
        )
        fast_api = FastAPI()
        fast_api.add_middleware(HandleAuthExceptionMiddleware, fast_app=self.app)

        @fast_api.get(self.SECURE_ENDPOINT)
        async def secure(user: registered_dependency) -> str:  # type: ignore[valid-type]
            return "OK"

        self.test_client = TestClient(fast_api)

    def get_secure(self, token: str) -> Any:
        assert self.test_client is not None
        return self.test_client.get(
            self.SECURE_ENDPOINT,
            headers={"Authorization": f"Bearer {token}"},
        )

    def make_claims(self, extra_claims: dict[str, Any] | None = None) -> Claims:
        idp_client_id = self.auth_service.idp_clients[0].id
        claims = dict(self.mock_jwk_token.payload)
        if "email" in claims:
            claims["__key__"] = claims["email"]
        if extra_claims:
            claims.update(extra_claims)
        return Claims(
            scheme="BEARER",
            token=self.token,
            idp_client_id=idp_client_id,
            claims=claims,
        )

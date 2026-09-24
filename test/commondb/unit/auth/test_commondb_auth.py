"""
Unit tests for commondb auth – uses the real commondb.services.user_manager.UserManager
backed by an in-memory repository mock, so no database process is required.
"""

import asyncio
import datetime
from contextlib import contextmanager
from test.fastapp.enum import ServiceType
from test.fastapp.unit.auth.mock_jwk_and_token import MockJWKAndToken
from test.util.mock_compat import Mock, patch
from typing import Any, Generator
from uuid import UUID, uuid4

import jwt
import pytest
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
from gen_epix.fastapp.services.auth.util import get_name_from_claims

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_DEFAULT_USER_EMAIL = "user1@org1.org"
_UNKNOWN_USER_EMAIL = "unknown@other.org"
_ROOT_ORG_ID: UUID = UUID("00000000-0000-0000-0000-000000000001")
_AUTO_CREATE_ORG_ID: UUID = UUID("00000000-0000-0000-0000-000000000002")
_MOCK_USER_ID: UUID = UUID("00000000-0000-0000-0000-000000000010")
_CREATOR_USER_ID: UUID = UUID("00000000-0000-0000-0000-000000000011")

_ROOT_ROLE: str = commondb_enum.Role.ROOT.value  # "COMMONDB_ROOT"
_GUEST_ROLE: str = commondb_enum.Role.GUEST.value  # "COMMONDB_GUEST"
_ALL_ROLES: set[str] = {r.value for r in commondb_enum.Role}

_BASE_IDP_CFG: dict[str, Any] = {
    "name": "idp1",
    "label": "idp1",
    "protocol": "OIDC",
    # claim_map validator wraps string values in a list automatically
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

# ---------------------------------------------------------------------------
# Model factories
# ---------------------------------------------------------------------------


def make_cdb_user(
    user_id: UUID | None = None,
    email: str = _DEFAULT_USER_EMAIL,
    name: str = "user1",
    roles: set[str] | None = None,
    organization_id: UUID | None = None,
) -> commondb_model.User:
    """Return a fresh commondb User with the given attributes."""
    return commondb_model.User(
        id=user_id or uuid4(),
        key=email,
        email=email,
        name=name,
        is_active=True,
        roles=roles or {_GUEST_ROLE},
        organization_id=organization_id or _ROOT_ORG_ID,
    )


def make_cdb_organization(
    org_id: UUID | None = None,
    name: str = "Test Org",
    code: str = "TEST",
) -> commondb_model.Organization:
    """Return a fresh commondb Organization."""
    return commondb_model.Organization(
        id=org_id or uuid4(),
        name=name,
        code=code,
    )


def make_cdb_invitation(
    invited_by_user_id: UUID,
    organization_id: UUID,
    token: str,
    key: str | None = None,
    roles: set[str] | None = None,
    expires_in_seconds: int = 3600,
) -> commondb_model.UserInvitation:
    """Return a valid future-expiring UserInvitation."""
    return commondb_model.UserInvitation(
        id=uuid4(),
        key=key,
        email=key,
        token=token,
        invited_by_user_id=invited_by_user_id,
        organization_id=organization_id,
        roles=roles or {_GUEST_ROLE},
        expires_at=datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(seconds=expires_in_seconds),
    )


def make_idps_cfg(mock_jwk_token: MockJWKAndToken) -> list[dict[str, Any]]:
    """Return IDP config list derived from the given mock JWK/token."""
    return [
        {
            **_BASE_IDP_CFG,
            "issuer": mock_jwk_token.payload["iss"],
            "client_id": mock_jwk_token.payload["aud"],
        }
    ]


def make_root_cfg(root_key: str = _DEFAULT_USER_EMAIL) -> dict[str, dict[str, Any]]:
    """Return a root_cfg dict suitable for BaseUserManager.init_root_cfg."""
    return {
        "organization": {
            "id": _ROOT_ORG_ID,
            "name": "Root Organization",
            "code": "ROOT_ORGANIZATION",
        },
        "user": {
            "key": root_key,
            "email": root_key,
            "name": "Root User",
        },
    }


# ---------------------------------------------------------------------------
# In-memory repository
# ---------------------------------------------------------------------------


class InMemoryOrganizationRepository:
    """Simulates an organisation repository entirely in memory.

    Supports EXISTS_ONE, CREATE_ONE, READ_ONE, READ_ALL and UPDATE_ONE
    operations for Organization, User and UserInvitation model classes.
    """

    def __init__(self) -> None:
        self._users: dict[UUID, commondb_model.User] = {}
        self._users_by_key: dict[str, commondb_model.User] = {}
        self._orgs: dict[UUID, commondb_model.Organization] = {}
        self._invitations: list[commondb_model.UserInvitation] = []

    # ------------------------------------------------------------------
    # Helpers to pre-populate the repository in tests
    # ------------------------------------------------------------------

    def add_user(self, user: commondb_model.User) -> None:
        if user.id is not None:
            self._users[user.id] = user
        if user.key:
            self._users_by_key[user.key] = user

    def add_organization(self, org: commondb_model.Organization) -> None:
        if org.id is not None:
            self._orgs[org.id] = org

    def add_invitation(self, invitation: commondb_model.UserInvitation) -> None:
        self._invitations.append(invitation)

    def get_user_by_key(self, key: str) -> commondb_model.User | None:
        return self._users_by_key.get(key)

    def user_exists_by_key(self, key: str) -> bool:
        return key in self._users_by_key

    # ------------------------------------------------------------------
    # Repository interface (called by the real UserManager)
    # ------------------------------------------------------------------

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
            if is_org:
                return obj_ids in self._orgs
            # User: check by obj_ids (UUID)
            return obj_ids in self._users

        elif operation == CrudOperation.CREATE_ONE:
            if is_org:
                org_id = objs.id if objs.id is not None else user_id
                self._orgs[org_id] = objs
                return objs
            # User: always use objs.id (user_id may be the creating user's id)
            new_id = objs.id if objs.id is not None else user_id
            self._users[new_id] = objs
            if objs.key:
                self._users_by_key[objs.key] = objs
            return objs

        elif operation == CrudOperation.READ_ONE:
            if is_org:
                if obj_ids not in self._orgs:
                    raise commondb_exc.NoResultsError(
                        f"Organization {obj_ids} not found"
                    )
                return self._orgs[obj_ids]
            # User
            if obj_ids not in self._users:
                raise commondb_exc.NoResultsError(f"User {obj_ids} not found")
            return self._users[obj_ids]

        elif operation == CrudOperation.READ_ALL:
            if is_invitation:
                # user_id is invited_by_user_id
                return [x for x in self._invitations if x.invited_by_user_id == user_id]
            return []

        elif operation == CrudOperation.UPDATE_ONE:
            self._users[user_id] = objs
            if objs.key:
                self._users_by_key[objs.key] = objs
            return objs

        raise NotImplementedError(f"Operation {operation} not implemented in mock")

    def is_existing_user_by_key(self, uow: Any, key: str | None) -> bool:
        return key is not None and key in self._users_by_key


# ---------------------------------------------------------------------------
# Service mock factories
# ---------------------------------------------------------------------------


def make_mock_rbac_service() -> Mock:
    """Return a minimal mock satisfying BaseRbacService interface requirements."""
    rbac_service = Mock()
    rbac_service.root_role = _ROOT_ROLE
    rbac_service.guest_role = _GUEST_ROLE
    rbac_service.get_roles.return_value = _ALL_ROLES
    rbac_service.retrieve_user_is_root.side_effect = (
        lambda user: _ROOT_ROLE in user.roles
    )
    rbac_service.retrieve_user_permissions.return_value = set()
    return rbac_service


def _retrieve_user_by_key_from_repo(
    repo: InMemoryOrganizationRepository, key: str
) -> commondb_model.User:
    user = repo.get_user_by_key(key)
    if user is None:
        raise exc.NoResultsError("8c95c4db", f"User with key '{key}' not found")
    return user


def make_mock_organization_service(repo: InMemoryOrganizationRepository) -> Mock:
    """Return a mock BaseOrganizationService backed by the given in-memory repo."""
    org_service = Mock()
    org_service.repository = repo
    org_service.app = Mock()
    org_service.app.impl = Mock()
    # get_mapped_class returns the base model class so no SA-mapping is needed
    org_service.app.impl.get_mapped_class.side_effect = lambda cls: cls
    org_service.generate_id.side_effect = lambda: uuid4()
    org_service.retrieve_user_by_key.side_effect = lambda key: (
        _retrieve_user_by_key_from_repo(repo, key)
    )
    return org_service


def make_commondb_user_manager(
    repo: InMemoryOrganizationRepository,
    root_key: str = _DEFAULT_USER_EMAIL,
    auto_created_user_cfg: dict[str, Any] | None = None,
) -> UserManager:
    """Build a real commondb UserManager with mocked service dependencies."""
    rbac_service = make_mock_rbac_service()
    org_service = make_mock_organization_service(repo)
    return UserManager(
        organization_service=org_service,
        rbac_service=rbac_service,
        root_cfg=make_root_cfg(root_key),
        auto_created_user_cfg=auto_created_user_cfg,
    )


# ---------------------------------------------------------------------------
# AuthEnv – self-contained per-test environment
# ---------------------------------------------------------------------------


class AuthEnv:
    """Self-contained, per-test auth environment built around the real
    commondb.services.user_manager.UserManager.

    Parameters
    ----------
    auto_create_new_users:
        When True the AuthService will attempt to auto-create unknown users.
        This also configures the UserManager with a corresponding
        ``auto_created_user_cfg`` (required for the real implementation).
    root_token_time_to_live:
        Passed directly to AuthService.
    token_iat_minutes_ago:
        How many minutes before "now" the test JWT was issued.
    token_expiration_minutes:
        How many minutes after "now" the test JWT expires.
    initial_users:
        Users to pre-populate in the in-memory repository.
    root_key:
        The email / key that the root_cfg will register as the root user.
    with_http:
        When True, also spin up a minimal FastAPI TestClient.
    """

    SECURE_ENDPOINT = "/secure/current_user"

    def __init__(
        self,
        auto_create_new_users: bool = False,
        root_token_time_to_live: int | None = None,
        token_iat_minutes_ago: int = 0,
        token_expiration_minutes: int = 10,
        initial_users: list[commondb_model.User] | None = None,
        root_key: str = _DEFAULT_USER_EMAIL,
        with_http: bool = True,
    ) -> None:
        self.mock_jwk_token = MockJWKAndToken(
            token_expiration_minutes=token_expiration_minutes,
            token_iat_minutes_ago=token_iat_minutes_ago,
        )

        # Build in-memory repository and pre-populate users
        self.repo = InMemoryOrganizationRepository()
        for user in initial_users or []:
            self.repo.add_user(user)

        # If auto-create is enabled, configure the UserManager and ensure the
        # target organisation exists in the repo.
        auto_created_user_cfg: dict[str, Any] | None = None
        if auto_create_new_users:
            self.repo.add_organization(
                make_cdb_organization(_AUTO_CREATE_ORG_ID, "Auto-Create Org", "AUTO")
            )
            auto_created_user_cfg = {
                "organization_id": str(_AUTO_CREATE_ORG_ID),
                "roles": [_GUEST_ROLE],
            }

        # Build real UserManager
        self.user_manager = make_commondb_user_manager(
            self.repo,
            root_key=root_key,
            auto_created_user_cfg=auto_created_user_cfg,
        )

        # Build AuthService
        self.app = App(
            user_manager=self.user_manager,
            logger=None,
        )
        idps_cfg = make_idps_cfg(self.mock_jwk_token)
        self.auth_service = AuthService(
            self.app,
            service_type=ServiceType.AUTH,
            idps_cfg=idps_cfg,
            auto_create_new_users=auto_create_new_users,
            root_token_time_to_live=root_token_time_to_live,
        )
        # Inject pre-generated signing keys so no JWKS endpoint is contacted
        for idp_client in self.auth_service.idp_clients:
            if isinstance(idp_client, OauthIdpClient):
                idp_client._signing_keys = {
                    self.mock_jwk_token.public_jwk_dict["kid"]: jwt.PyJWK.from_dict(
                        self.mock_jwk_token.public_jwk_dict
                    )
                }

        self.token: str = self.mock_jwk_token.token
        self.test_client: TestClient | None = None
        if with_http:
            self._setup_http()

    def _setup_http(self) -> None:
        registered_dep, _new_dep, _idp_dep = (
            self.auth_service.create_user_dependencies()
        )
        fast_api = FastAPI()
        fast_api.add_middleware(HandleAuthExceptionMiddleware, fast_app=self.app)

        @fast_api.get(self.SECURE_ENDPOINT)
        async def secure(user: registered_dep) -> str:  # type: ignore[valid-type]
            return "OK"

        self.test_client = TestClient(fast_api)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @staticmethod
    def make_token_header(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    def get_secure(self, token: str) -> Any:
        assert self.test_client is not None, "AuthEnv built with with_http=False"
        return self.test_client.get(
            self.SECURE_ENDPOINT,
            headers=self.make_token_header(token),
        )

    def make_claims(self, extra_claims: dict[str, Any] | None = None) -> Claims:
        """Build a Claims object from the mock token payload.

        Also adds ``__key__`` to simulate the claim remapping that the
        OauthIdpClient performs (claim_map ``email -> __key__``).
        """
        assert self.auth_service.idp_clients, "No IDP clients configured"
        idp_client_id = self.auth_service.idp_clients[0].id
        claims_dict: dict[str, Any] = dict(self.mock_jwk_token.payload)
        # Simulate OauthIdpClient._map_claims({"__key__": ["email"]})
        if "email" in claims_dict:
            claims_dict["__key__"] = claims_dict["email"]
        if extra_claims:
            claims_dict.update(extra_claims)
        return Claims(
            scheme="BEARER",
            token=self.token,
            idp_client_id=idp_client_id,
            claims=claims_dict,
        )


# ===========================================================================
# TestAuth - name-extraction unit tests and update_user_name via UserManager
# ===========================================================================


@pytest.mark.scenario_ids("TC-SEC-30-01")
class TestAuth:
    """Pure unit tests for claim name-extraction helpers and update_user_name."""

    def _make_env_with_user(self, user: commondb_model.User) -> AuthEnv:
        return AuthEnv(initial_users=[user], with_http=False)

    # -------------------------------------------------------------------
    # Name extraction (no env dependency)
    # -------------------------------------------------------------------

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
        claims: dict[str, Any] = {"preferred_username": "mockuser"}
        assert get_name_from_claims(claims, ["preferred_username"]) == "mockuser"

    def test_extracts_name_fallback_email(self) -> None:
        claims: dict[str, Any] = {"email": "user1@org1.org"}
        assert get_name_from_claims(claims, ["name"]) is None

    def test_extracts_name_returns_none_when_no_claims_present(self) -> None:
        assert get_name_from_claims({}, ["name", "preferred_username"]) is None

    # -------------------------------------------------------------------
    # update_user_name via real UserManager (each test gets a fresh user)
    # -------------------------------------------------------------------

    def test_update_user_name_no_change(self) -> None:
        user = make_cdb_user(user_id=_MOCK_USER_ID, name="John")
        env = self._make_env_with_user(user)
        returned = env.user_manager.update_user_name(user, "John")
        # update_user_name returns the same object when name is unchanged
        assert returned is user
        assert user.name == "John"

    def test_update_user_name_changed(self) -> None:
        user = make_cdb_user(user_id=_MOCK_USER_ID, name="John")
        env = self._make_env_with_user(user)
        returned = env.user_manager.update_user_name(user, "")
        assert returned is not None
        assert returned.name == ""

    def test_update_user_name_real_user(self) -> None:
        new_name = "Johnny"
        user = make_cdb_user(user_id=_MOCK_USER_ID, name="John")
        env = self._make_env_with_user(user)
        returned = env.user_manager.update_user_name(user, new_name)
        assert returned is not None
        assert returned.name == new_name

    def test_update_user_name_real_user_last_name(self) -> None:
        new_name = "John Doe"
        user = make_cdb_user(user_id=_MOCK_USER_ID, name="John")
        env = self._make_env_with_user(user)
        returned = env.user_manager.update_user_name(user, new_name)
        assert returned is not None
        assert returned.name == new_name

    def test_update_user_name_persisted_in_repo(self) -> None:
        """Verify the real UserManager writes the name change to the repo."""
        new_name = "Updated Name"
        user = make_cdb_user(user_id=_MOCK_USER_ID, name="Original Name")
        env = self._make_env_with_user(user)
        env.user_manager.update_user_name(user, new_name)
        stored = env.repo.get_user_by_key(_DEFAULT_USER_EMAIL)
        assert stored is not None
        assert stored.name == new_name


# ===========================================================================
# TestAutoCreateUser - auto_create_new_users on/off behaviour
# ===========================================================================


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestAutoCreateUser:
    """Verify that unknown users are auto-created when the flag is on,
    and rejected when it is off.  Known users (already in the store)
    are allowed regardless of the flag.

    Note: the real commondb UserManager requires ``auto_created_user_cfg``
    in addition to ``auto_create_new_users=True`` on the AuthService.
    AuthEnv configures both together when ``auto_create_new_users=True``.
    """

    def test_unknown_user_rejected_when_auto_create_disabled(self) -> None:
        env = AuthEnv(auto_create_new_users=False)
        token = env.mock_jwk_token.edit_claim("email", _UNKNOWN_USER_EMAIL)
        response = env.get_secure(token)
        assert response.status_code == 401

    def test_known_user_allowed_when_auto_create_disabled(self) -> None:
        user = make_cdb_user(user_id=_MOCK_USER_ID)
        env = AuthEnv(auto_create_new_users=False, initial_users=[user])
        response = env.get_secure(env.token)
        assert response.status_code == 200

    def test_unknown_user_auto_created_when_enabled(self) -> None:
        env = AuthEnv(auto_create_new_users=True)
        token = env.mock_jwk_token.edit_claim("email", _UNKNOWN_USER_EMAIL)
        response = env.get_secure(token)
        assert response.status_code == 200
        assert env.repo.user_exists_by_key(_UNKNOWN_USER_EMAIL)

    def test_auto_create_enabled_does_not_duplicate_existing_user(self) -> None:
        user = make_cdb_user(user_id=_MOCK_USER_ID)
        env = AuthEnv(auto_create_new_users=True, initial_users=[user])
        response = env.get_secure(env.token)
        assert response.status_code == 200
        # The existing user must still be the same object in the repo
        assert env.repo.get_user_by_key(_DEFAULT_USER_EMAIL) is user

    def test_auto_create_calls_user_manager_method(self) -> None:
        env = AuthEnv(auto_create_new_users=True)
        auto_created = make_cdb_user(user_id=uuid4(), email=_UNKNOWN_USER_EMAIL)
        token = env.mock_jwk_token.edit_claim("email", _UNKNOWN_USER_EMAIL)
        with patch.object(
            env.user_manager,
            "auto_create_new_user",
            return_value=auto_created,
        ) as mock_auto_create:
            response = env.get_secure(token)
        assert response.status_code == 200
        mock_auto_create.assert_called_once()

    def test_auto_create_disabled_does_not_call_auto_create_method(self) -> None:
        env = AuthEnv(auto_create_new_users=False)
        token = env.mock_jwk_token.edit_claim("email", _UNKNOWN_USER_EMAIL)
        with patch.object(env.user_manager, "auto_create_new_user") as mock_auto:
            env.get_secure(token)
        mock_auto.assert_not_called()

    def test_auto_created_user_has_configured_role(self) -> None:
        env = AuthEnv(auto_create_new_users=True)
        token = env.mock_jwk_token.edit_claim("email", _UNKNOWN_USER_EMAIL)
        env.get_secure(token)
        user = env.repo.get_user_by_key(_UNKNOWN_USER_EMAIL)
        assert user is not None
        assert _GUEST_ROLE in user.roles

    def test_auto_created_user_key_matches_email_claim(self) -> None:
        env = AuthEnv(auto_create_new_users=True)
        token = env.mock_jwk_token.edit_claim("email", _UNKNOWN_USER_EMAIL)
        env.get_secure(token)
        user = env.repo.get_user_by_key(_UNKNOWN_USER_EMAIL)
        assert user is not None
        assert user.key == _UNKNOWN_USER_EMAIL


# ===========================================================================
# TestRootTokenTTL - root_token_time_to_live on/off behaviour
# ===========================================================================


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestRootTokenTTL:
    """Verify the root-token time-to-live enforcement.

    A *very* short TTL (1 second) is used so tests complete quickly.
    The old token is issued 5 minutes ago, which exceeds any reasonable
    TTL under test.

    Root user detection: the real UserManager.is_root_user checks
    ``root_role in user.roles`` so the pre-stored user must carry the ROOT role.
    """

    _TTL_SECONDS = 1
    _OLD_IAT_MINUTES = 5  # 300 s old; far exceeds TTL of 1 s

    def _make_root_env(
        self,
        token_iat_minutes_ago: int = 0,
        root_token_time_to_live: int | None = _TTL_SECONDS,
    ) -> AuthEnv:
        """Build an AuthEnv with a pre-stored root user."""
        root_user = make_cdb_user(
            user_id=_MOCK_USER_ID,
            email=_DEFAULT_USER_EMAIL,
            roles={_ROOT_ROLE},
        )
        return AuthEnv(
            root_token_time_to_live=root_token_time_to_live,
            token_iat_minutes_ago=token_iat_minutes_ago,
            initial_users=[root_user],
        )

    def test_fresh_root_token_within_ttl_is_accepted(self) -> None:
        env = self._make_root_env(token_iat_minutes_ago=0)
        assert env.get_secure(env.token).status_code == 200

    def test_old_root_token_exceeding_ttl_is_rejected(self) -> None:
        env = self._make_root_env(token_iat_minutes_ago=self._OLD_IAT_MINUTES)
        assert env.get_secure(env.token).status_code == 401

    def test_ttl_disabled_allows_old_root_token(self) -> None:
        env = self._make_root_env(
            token_iat_minutes_ago=self._OLD_IAT_MINUTES,
            root_token_time_to_live=0,
        )
        assert env.get_secure(env.token).status_code == 200

    def test_ttl_none_uses_default_ttl(self) -> None:
        root_user = make_cdb_user(user_id=_MOCK_USER_ID, roles={_ROOT_ROLE})
        env = AuthEnv(root_token_time_to_live=None, initial_users=[root_user])
        assert (
            env.auth_service._root_token_time_to_live
            == AuthService.DEFAULT_ROOT_TOKEN_TIME_TO_LIVE
        )

    def test_ttl_zero_disables_expiry(self) -> None:
        root_user = make_cdb_user(user_id=_MOCK_USER_ID, roles={_ROOT_ROLE})
        env = AuthEnv(root_token_time_to_live=0, initial_users=[root_user])
        assert env.auth_service._root_token_time_to_live == 0

    def test_non_root_user_not_affected_by_ttl(self) -> None:
        regular_user = make_cdb_user(user_id=_MOCK_USER_ID, roles={_GUEST_ROLE})
        env = AuthEnv(
            root_token_time_to_live=self._TTL_SECONDS,
            token_iat_minutes_ago=self._OLD_IAT_MINUTES,
            initial_users=[regular_user],
        )
        assert env.get_secure(env.token).status_code == 200

    def test_verify_root_ttl_directly_accepts_fresh_token(self) -> None:
        env = self._make_root_env(token_iat_minutes_ago=0, root_token_time_to_live=2)
        root_user = make_cdb_user(user_id=_MOCK_USER_ID, roles={_ROOT_ROLE})
        claims = env.make_claims()
        # Should not raise
        env.auth_service._verify_root_user_for_token_time_to_live(claims, root_user)

    def test_verify_root_ttl_directly_rejects_old_token(self) -> None:
        env = self._make_root_env(
            token_iat_minutes_ago=self._OLD_IAT_MINUTES,
            root_token_time_to_live=self._TTL_SECONDS,
        )
        root_user = make_cdb_user(user_id=_MOCK_USER_ID, roles={_ROOT_ROLE})
        claims = env.make_claims()
        with pytest.raises(exc.UnauthorizedAuthError):
            env.auth_service._verify_root_user_for_token_time_to_live(claims, root_user)


# ===========================================================================
# TestCreateUserFromToken - invitation-based user creation
# ===========================================================================


@pytest.mark.scenario_ids("TC-SEC-30-04")
class TestCreateUserFromToken:
    """Verify that the commondb UserManager correctly creates a user from an
    invitation token and raises on invalid or duplicate registrations.

    The real create_new_user_from_token implementation requires:
    - ``created_by_user_id`` kwarg identifying the inviting user
    - A matching UserInvitation in the repository
    """

    _INVITATION_TOKEN = "invitation-token-abc123"

    def _make_env_with_creator(self) -> tuple[AuthEnv, commondb_model.User]:
        """Build an AuthEnv with a pre-stored creator (inviting) user."""
        creator = make_cdb_user(user_id=_CREATOR_USER_ID, email="creator@org.org")
        env = AuthEnv(initial_users=[creator], with_http=False)
        # Pre-store the organisation that new users will join
        env.repo.add_organization(
            make_cdb_organization(_ROOT_ORG_ID, "Root Organization", "ROOT")
        )
        return env, creator

    def _make_pending_user(
        self,
        user_id: UUID | None = None,
        email: str = "newuser@org.org",
    ) -> commondb_model.User:
        """Return a User that is not yet stored in the repository."""
        return make_cdb_user(
            user_id=user_id or uuid4(),
            email=email,
            organization_id=_ROOT_ORG_ID,
        )

    def _add_invitation(
        self,
        repo: InMemoryOrganizationRepository,
        creator_id: UUID,
        token: str,
        user_email: str | None = None,
    ) -> commondb_model.UserInvitation:
        invitation = make_cdb_invitation(
            invited_by_user_id=creator_id,
            organization_id=_ROOT_ORG_ID,
            token=token,
            key=user_email,
        )
        repo.add_invitation(invitation)
        return invitation

    def test_create_new_user_from_token_stores_user(self) -> None:
        env, creator = self._make_env_with_creator()
        self._add_invitation(env.repo, creator.id, self._INVITATION_TOKEN)
        new_user = self._make_pending_user()
        returned = env.user_manager.create_new_user_from_token(
            new_user, self._INVITATION_TOKEN, created_by_user_id=creator.id
        )
        assert returned is not None
        assert env.repo.user_exists_by_key(new_user.email)

    def test_create_new_user_from_token_user_is_retrievable(self) -> None:
        env, creator = self._make_env_with_creator()
        self._add_invitation(env.repo, creator.id, self._INVITATION_TOKEN)
        new_user = self._make_pending_user(email="retrievable@org.org")
        env.user_manager.create_new_user_from_token(
            new_user, self._INVITATION_TOKEN, created_by_user_id=creator.id
        )
        retrieved = env.repo.get_user_by_key("retrievable@org.org")
        assert retrieved is not None
        assert retrieved.key == "retrievable@org.org"

    def test_create_new_user_from_token_duplicate_raises(self) -> None:
        env, creator = self._make_env_with_creator()
        self._add_invitation(env.repo, creator.id, self._INVITATION_TOKEN)
        new_user = self._make_pending_user(email="dup@org.org")
        env.user_manager.create_new_user_from_token(
            new_user, self._INVITATION_TOKEN, created_by_user_id=creator.id
        )
        with pytest.raises(exc.UnauthorizedAuthError):
            env.user_manager.create_new_user_from_token(
                new_user, self._INVITATION_TOKEN, created_by_user_id=creator.id
            )

    def test_create_new_user_missing_invitation_raises(self) -> None:
        env, creator = self._make_env_with_creator()
        new_user = self._make_pending_user()
        with pytest.raises(exc.UnauthorizedAuthError):
            env.user_manager.create_new_user_from_token(
                new_user, "nonexistent-token", created_by_user_id=creator.id
            )

    def test_create_new_user_nonexistent_creator_raises(self) -> None:
        env = AuthEnv(with_http=False)
        env.repo.add_organization(
            make_cdb_organization(_ROOT_ORG_ID, "Root Organization", "ROOT")
        )
        new_user = self._make_pending_user()
        with pytest.raises(exc.UnauthorizedAuthError):
            env.user_manager.create_new_user_from_token(
                new_user, self._INVITATION_TOKEN, created_by_user_id=uuid4()
            )

    def test_create_new_user_from_token_does_not_affect_other_users(self) -> None:
        env, creator = self._make_env_with_creator()
        other_user = make_cdb_user(user_id=uuid4(), email="other@org.org")
        env.repo.add_user(other_user)
        self._add_invitation(env.repo, creator.id, self._INVITATION_TOKEN)
        new_user = self._make_pending_user(email="brand-new@org.org")
        env.user_manager.create_new_user_from_token(
            new_user, self._INVITATION_TOKEN, created_by_user_id=creator.id
        )
        assert env.repo.get_user_by_key("other@org.org") is other_user

    @pytest.mark.parametrize(
        "token_value",
        ["token-alpha", "token-beta", "00000000-0000-0000-0000-000000000000"],
        ids=["short_token", "another_token", "uuid_token"],
    )
    def test_create_new_user_accepts_various_token_formats(
        self, token_value: str
    ) -> None:
        env, creator = self._make_env_with_creator()
        self._add_invitation(env.repo, creator.id, token_value)
        new_user = self._make_pending_user(email=f"{token_value}@org.org")
        returned = env.user_manager.create_new_user_from_token(
            new_user, token_value, created_by_user_id=creator.id
        )
        assert returned is not None


# ===========================================================================
# TestRootUserLogin - first login and key-matching behaviour
# ===========================================================================


@pytest.mark.scenario_ids("TC-SEC-30-05")
class TestRootUserLogin:
    """Verify that a root user can log in for the first time (triggering
    create_root_user_from_claims), that subsequent logins succeed, and
    that the stored user key matches the configured root identity.

    Root user detection: the real UserManager checks
    ``_root_user.key == claims["__key__"]`` (is_root_user_claims) and
    ``root_role in user.roles`` (is_root_user).
    """

    def test_root_user_first_login_creates_user(self) -> None:
        # Root user is NOT yet in the store - only the root_cfg designates them
        env = AuthEnv()
        assert not env.repo.user_exists_by_key(_DEFAULT_USER_EMAIL)
        response = env.get_secure(env.token)
        assert response.status_code == 200
        assert env.repo.user_exists_by_key(_DEFAULT_USER_EMAIL)

    def test_root_user_first_login_assigns_root_role(self) -> None:
        env = AuthEnv()
        env.get_secure(env.token)
        user = env.repo.get_user_by_key(_DEFAULT_USER_EMAIL)
        assert user is not None
        assert _ROOT_ROLE in user.roles

    def test_root_user_subsequent_login_succeeds(self) -> None:
        root_user = make_cdb_user(
            user_id=_MOCK_USER_ID,
            email=_DEFAULT_USER_EMAIL,
            roles={_ROOT_ROLE},
        )
        env = AuthEnv(initial_users=[root_user])
        assert env.get_secure(env.token).status_code == 200

    def test_root_user_key_matches_configured_identity(self) -> None:
        env = AuthEnv()
        env.get_secure(env.token)
        user = env.repo.get_user_by_key(_DEFAULT_USER_EMAIL)
        assert user is not None
        assert user.key == _DEFAULT_USER_EMAIL

    def test_root_user_is_detected_as_root_after_first_login(self) -> None:
        env = AuthEnv()
        env.get_secure(env.token)
        user = env.repo.get_user_by_key(_DEFAULT_USER_EMAIL)
        assert user is not None
        assert env.user_manager.is_root_user(user)

    def test_non_root_user_not_detected_as_root(self) -> None:
        regular_user = make_cdb_user(
            user_id=_MOCK_USER_ID,
            email=_DEFAULT_USER_EMAIL,
            roles={_GUEST_ROLE},
        )
        env = AuthEnv(initial_users=[regular_user])
        user = env.repo.get_user_by_key(_DEFAULT_USER_EMAIL)
        assert user is not None
        assert not env.user_manager.is_root_user(user)

    def test_unknown_non_root_user_rejected_without_auto_create(self) -> None:
        env = AuthEnv(auto_create_new_users=False)
        token = env.mock_jwk_token.edit_claim("email", _UNKNOWN_USER_EMAIL)
        assert env.get_secure(token).status_code == 401

    def test_is_root_user_claims_true_for_root_key(self) -> None:
        # root_cfg configures _DEFAULT_USER_EMAIL as root; __key__ carries that value
        env = AuthEnv(with_http=False)
        claims = {"__key__": _DEFAULT_USER_EMAIL}
        assert env.user_manager.is_root_user_claims(claims) is True

    def test_is_root_user_claims_false_for_non_root_email(self) -> None:
        env = AuthEnv(with_http=False)
        claims = {"__key__": _UNKNOWN_USER_EMAIL}
        assert env.user_manager.is_root_user_claims(claims) is False

    def test_root_user_login_via_async_service_method(self) -> None:
        """Drive get_existing_user_from_claims directly (no HTTP stack)."""
        env = AuthEnv(with_http=False)
        claims = env.make_claims()  # includes __key__ = _DEFAULT_USER_EMAIL
        user = asyncio.run(env.auth_service.get_existing_user_from_claims(claims))
        assert user is not None
        assert user.key == _DEFAULT_USER_EMAIL
        assert _ROOT_ROLE in user.roles

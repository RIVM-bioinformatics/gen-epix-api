import asyncio
from datetime import datetime, timedelta, timezone
from math import floor
from test.fastapp.auth_test_client import AuthTestClient
from test.fastapp.enum import ServiceType
from test.fastapp.unit.auth.mock_jwk_and_token import MockJWKAndToken
from test.fastapp.user_manager import MOCK_USER, MockUser, UserManager
from typing import Any
from unittest.mock import patch

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from gen_epix.fastapp import exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.middleware import HandleAuthExceptionMiddleware
from gen_epix.fastapp.model import User
from gen_epix.fastapp.services.auth import AuthService, OauthIdpClient
from gen_epix.fastapp.services.auth.model import Claims
from gen_epix.fastapp.services.auth.util import get_name_from_claims

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_BASE_IDP_CFG: dict[str, Any] = {
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

_DEFAULT_USER_EMAIL = "user1@org1.org"
_UNKNOWN_USER_EMAIL = "unknown@other.org"


def make_idps_cfg(mock_jwk_token: MockJWKAndToken) -> list[dict[str, Any]]:
    """Return IDP config list derived from the given mock JWK/token."""
    return [
        {
            **_BASE_IDP_CFG,
            "issuer": mock_jwk_token.payload["iss"],
            "client_id": mock_jwk_token.payload["aud"],
        }
    ]


def make_mock_user(
    user_id: str = "id1",
    email: str = _DEFAULT_USER_EMAIL,
    name: str = "user1",
) -> MockUser:
    """Return a fresh MockUser instance with the given attributes."""
    return MockUser(id=user_id, key=email, email=email, name=name)


class AuthEnv:
    """Self-contained, per-test auth environment.

    Builds a UserManager, App, AuthService, and (optionally) a FastAPI
    TestClient in one place so individual tests can control every
    configuration axis independently.
    """

    SECURE_ENDPOINT = "/secure/current_user"

    def __init__(
        self,
        auto_create_new_users: bool = False,
        root_token_time_to_live: int | None = None,
        token_iat_minutes_ago: int = 0,
        token_expiration_minutes: int = 10,
        initial_users: dict[str, Any] | None = None,
        # Keys put into root_users to satisfy is_root_user_claims checks
        root_user_keys: set[str] | None = None,
        # IDs put into root_users to satisfy is_root_user(user) checks
        root_user_ids: set[str] | None = None,
        with_http: bool = True,
    ) -> None:
        self.mock_jwk_token = MockJWKAndToken(
            token_expiration_minutes=token_expiration_minutes,
            token_iat_minutes_ago=token_iat_minutes_ago,
        )

        # Build user manager
        self.user_manager = UserManager()
        self.user_manager.users = dict(initial_users or {})
        self.user_manager.root_users = {}
        for key in root_user_keys or []:
            self.user_manager.root_users[key] = True
        for uid in root_user_ids or []:
            self.user_manager.root_users[uid] = True

        # Build auth service
        self.app = App(user_manager=self.user_manager, logger=None)
        idps_cfg = make_idps_cfg(self.mock_jwk_token)
        self.auth_service = AuthService(
            self.app,
            service_type=ServiceType.AUTH,
            idps_cfg=idps_cfg,
            auto_create_new_users=auto_create_new_users,
            root_token_time_to_live=root_token_time_to_live,
        )
        # Inject signing keys directly so no real JWKS endpoint is hit
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
    # Convenience request helpers
    # ------------------------------------------------------------------

    @staticmethod
    def make_token_header(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    def get_secure(self, token: str) -> Any:
        assert self.test_client is not None
        return self.test_client.get(
            self.SECURE_ENDPOINT,
            headers=self.make_token_header(token),
        )

    def make_claims(self, extra_claims: dict[str, Any] | None = None) -> Claims:
        """Build a Claims object from the mock token payload."""
        assert self.auth_service.idp_clients, "No IDP clients configured"
        idp_client_id = self.auth_service.idp_clients[0].id
        claims_dict: dict[str, Any] = dict(self.mock_jwk_token.payload)
        if extra_claims:
            claims_dict.update(extra_claims)
        return Claims(
            scheme="BEARER",
            token=self.token,
            idp_client_id=idp_client_id,
            claims=claims_dict,
        )


# ---------------------------------------------------------------------------
# Legacy module-scoped fixture (kept for TestAuth below)
# ---------------------------------------------------------------------------


class CommonAuthTestClient(AuthTestClient):
    pass


@pytest.fixture(scope="module", name="env")
def get_test_client() -> CommonAuthTestClient:
    return (
        CommonAuthTestClient.get_test_client()
    )  # type: ignore[no-any-return,no-untyped_call]


# ===========================================================================
# TestAuth – existing name-extraction and user-name-update unit tests
# ===========================================================================


@pytest.mark.scenario_ids("TC-SEC-30-01")
class TestAuth:
    NON_SECURE_ENDPOINT = "/non_secure"
    CURRENT_USER_ENDPOINT = "/secure/current_user"

    NOW = datetime.now(timezone.utc)
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

    def test_extracts_name_returns_none_when_no_claims_present(self) -> None:
        claims: dict[str, Any] = {}
        assert get_name_from_claims(claims, ["name", "preferred_username"]) is None

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


# ===========================================================================
# TestAutoCreateUser – auto_create_new_users on/off behaviour
# ===========================================================================


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestAutoCreateUser:
    """Verify that unknown users are auto-created when the flag is on,
    and rejected when it is off.  Known users (already in the store)
    are allowed regardless of the flag.
    """

    def test_unknown_user_rejected_when_auto_create_disabled(self) -> None:
        env = AuthEnv(auto_create_new_users=False)
        # Token for an address that is not in user_manager.users
        token = env.mock_jwk_token.edit_claim("email", _UNKNOWN_USER_EMAIL)
        response = env.get_secure(token)
        assert response.status_code == 401

    def test_known_user_allowed_when_auto_create_disabled(self) -> None:
        mock_user = make_mock_user()
        env = AuthEnv(
            auto_create_new_users=False,
            initial_users={_DEFAULT_USER_EMAIL: mock_user},
        )
        response = env.get_secure(env.token)
        assert response.status_code == 200

    def test_unknown_user_auto_created_when_enabled(self) -> None:
        env = AuthEnv(auto_create_new_users=True)
        # Unknown email – user is not pre-populated in the store
        token = env.mock_jwk_token.edit_claim("email", _UNKNOWN_USER_EMAIL)
        response = env.get_secure(token)
        assert response.status_code == 200
        # The user must now exist in the store
        assert _UNKNOWN_USER_EMAIL in env.user_manager.users

    def test_auto_create_enabled_does_not_duplicate_existing_user(self) -> None:
        mock_user = make_mock_user()
        env = AuthEnv(
            auto_create_new_users=True,
            initial_users={_DEFAULT_USER_EMAIL: mock_user},
        )
        response = env.get_secure(env.token)
        assert response.status_code == 200
        # auto_create_new_user must NOT have been invoked for an existing user
        assert env.user_manager.users[_DEFAULT_USER_EMAIL] is mock_user

    def test_auto_create_calls_user_manager_method(self) -> None:
        env = AuthEnv(auto_create_new_users=True)
        auto_created = make_mock_user(user_id="new1", email=_UNKNOWN_USER_EMAIL)
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
        with patch.object(
            env.user_manager,
            "auto_create_new_user",
        ) as mock_auto_create:
            env.get_secure(token)
        mock_auto_create.assert_not_called()


# ===========================================================================
# TestRootTokenTTL – root_token_time_to_live on/off behaviour
# ===========================================================================


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestRootTokenTTL:
    """Verify the root-token time-to-live enforcement.

    A *very* short TTL (1 second) is used so tests complete quickly.
    The 'old' token is issued 5 minutes ago, which exceeds any
    reasonable TTL under test.
    """

    _TTL_SECONDS = 1
    # Token issued 5 minutes ago → 300 s old → exceeds TTL of 1 s
    _OLD_IAT_MINUTES = 5

    def _make_root_env(
        self,
        token_iat_minutes_ago: int = 0,
        root_token_time_to_live: int | None = _TTL_SECONDS,
    ) -> AuthEnv:
        mock_user = make_mock_user()
        return AuthEnv(
            root_token_time_to_live=root_token_time_to_live,
            token_iat_minutes_ago=token_iat_minutes_ago,
            initial_users={_DEFAULT_USER_EMAIL: mock_user},
            # is_root_user_claims uses the email key; is_root_user uses user.id
            root_user_keys={_DEFAULT_USER_EMAIL},
            root_user_ids={mock_user.id},
        )

    def test_fresh_root_token_within_ttl_is_accepted(self) -> None:
        env = self._make_root_env(token_iat_minutes_ago=0)
        response = env.get_secure(env.token)
        assert response.status_code == 200

    def test_old_root_token_exceeding_ttl_is_rejected(self) -> None:
        env = self._make_root_env(token_iat_minutes_ago=self._OLD_IAT_MINUTES)
        response = env.get_secure(env.token)
        assert response.status_code == 401

    def test_ttl_disabled_allows_old_root_token(self) -> None:
        # root_token_time_to_live <= 0 disables the TTL check
        env = self._make_root_env(
            token_iat_minutes_ago=self._OLD_IAT_MINUTES,
            root_token_time_to_live=0,
        )
        response = env.get_secure(env.token)
        assert response.status_code == 200

    def test_ttl_none_uses_default_ttl(self) -> None:
        # Passing None must apply DEFAULT_ROOT_TOKEN_TIME_TO_LIVE (15 min)
        mock_user = make_mock_user()
        env = AuthEnv(
            root_token_time_to_live=None,
            initial_users={_DEFAULT_USER_EMAIL: mock_user},
            root_user_keys={_DEFAULT_USER_EMAIL},
            root_user_ids={mock_user.id},
        )
        assert (
            env.auth_service._root_token_time_to_live
            == AuthService.DEFAULT_ROOT_TOKEN_TIME_TO_LIVE
        )

    def test_ttl_zero_disables_expiry(self) -> None:
        mock_user = make_mock_user()
        env = AuthEnv(
            root_token_time_to_live=0,
            initial_users={_DEFAULT_USER_EMAIL: mock_user},
            root_user_keys={_DEFAULT_USER_EMAIL},
            root_user_ids={mock_user.id},
        )
        assert env.auth_service._root_token_time_to_live is None

    def test_non_root_user_not_affected_by_ttl(self) -> None:
        # A regular (non-root) user with an old-token IAT must still pass
        mock_user = make_mock_user()
        env = AuthEnv(
            root_token_time_to_live=self._TTL_SECONDS,
            token_iat_minutes_ago=self._OLD_IAT_MINUTES,
            initial_users={_DEFAULT_USER_EMAIL: mock_user},
            # No root_user_ids → is_root_user returns False
        )
        response = env.get_secure(env.token)
        assert response.status_code == 200

    def test_verify_root_ttl_directly_accepts_fresh_token(self) -> None:
        env = self._make_root_env(token_iat_minutes_ago=0, root_token_time_to_live=2)
        mock_user = make_mock_user()
        claims = env.make_claims()
        # Should not raise
        env.auth_service._verify_root_user_for_token_time_to_live(claims, mock_user)

    def test_verify_root_ttl_directly_rejects_old_token(self) -> None:
        env = self._make_root_env(
            token_iat_minutes_ago=self._OLD_IAT_MINUTES,
            root_token_time_to_live=self._TTL_SECONDS,
        )
        mock_user = make_mock_user()
        claims = env.make_claims()
        with pytest.raises(exc.UnauthorizedAuthError):
            env.auth_service._verify_root_user_for_token_time_to_live(claims, mock_user)


# ===========================================================================
# TestCreateUserFromToken – invitation-based user creation
# ===========================================================================


@pytest.mark.scenario_ids("TC-SEC-30-04")
class TestCreateUserFromToken:
    """Verify that the UserManager correctly stores a user created from
    an invitation token and raises on duplicate registrations.
    """

    _INVITATION_TOKEN = "invitation-token-abc123"

    def _make_new_user(
        self, user_id: str = "new_user_id", email: str = "newuser@org.org"
    ) -> User:
        return User(id=user_id)

    def test_create_new_user_from_token_stores_user(self) -> None:
        env = AuthEnv(with_http=False)
        new_user = self._make_new_user()
        returned = env.user_manager.create_new_user_from_token(
            new_user, self._INVITATION_TOKEN
        )
        assert returned is new_user
        assert env.user_manager.retrieve_user_by_id(new_user.id) is new_user

    def test_create_new_user_from_token_user_is_retrievable(self) -> None:
        env = AuthEnv(with_http=False)
        new_user = self._make_new_user(user_id="retrieve_me")
        env.user_manager.create_new_user_from_token(new_user, self._INVITATION_TOKEN)
        retrieved = env.user_manager.retrieve_user_by_id("retrieve_me")
        assert retrieved is new_user

    def test_create_new_user_from_token_duplicate_raises(self) -> None:
        env = AuthEnv(with_http=False)
        new_user = self._make_new_user(user_id="dup_id")
        env.user_manager.create_new_user_from_token(new_user, self._INVITATION_TOKEN)
        with pytest.raises(exc.AlreadyExistingIdsError):
            env.user_manager.create_new_user_from_token(
                new_user, self._INVITATION_TOKEN
            )

    def test_create_new_user_from_token_does_not_affect_other_users(self) -> None:
        existing_user = make_mock_user()
        env = AuthEnv(
            with_http=False,
            initial_users={_DEFAULT_USER_EMAIL: existing_user},
        )
        new_user = self._make_new_user(user_id="separate_id")
        env.user_manager.create_new_user_from_token(new_user, self._INVITATION_TOKEN)
        # Existing user must still be intact
        assert env.user_manager.users[_DEFAULT_USER_EMAIL] is existing_user

    @pytest.mark.parametrize(
        "token_value",
        ["token-alpha", "token-beta", "00000000-0000-0000-0000-000000000000"],
        ids=["short_token", "another_token", "uuid_token"],
    )
    def test_create_new_user_from_token_accepts_various_token_formats(
        self, token_value: str
    ) -> None:
        env = AuthEnv(with_http=False)
        new_user = self._make_new_user(user_id=f"uid-{token_value}")
        returned = env.user_manager.create_new_user_from_token(new_user, token_value)
        assert returned is new_user

    def test_retrieve_nonexistent_user_raises(self) -> None:
        env = AuthEnv(with_http=False)
        with pytest.raises(exc.NoResultsError):
            env.user_manager.retrieve_user_by_id("does_not_exist")


# ===========================================================================
# TestRootUserLogin – first login and key-matching behaviour
# ===========================================================================


@pytest.mark.scenario_ids("TC-SEC-30-05")
class TestRootUserLogin:
    """Verify that a root user can log in for the first time (triggering
    create_root_user_from_claims), that subsequent logins succeed, and
    that the stored user key matches the configured root identity.
    """

    def test_root_user_first_login_creates_user(self) -> None:
        # Root user is not yet in the store; only their key is white-listed
        env = AuthEnv(
            root_user_keys={_DEFAULT_USER_EMAIL},
        )
        assert _DEFAULT_USER_EMAIL not in env.user_manager.users
        response = env.get_secure(env.token)
        assert response.status_code == 200
        # After the first login the root user must be in the store
        assert _DEFAULT_USER_EMAIL in env.user_manager.users

    def test_root_user_subsequent_login_succeeds(self) -> None:
        mock_user = make_mock_user()
        env = AuthEnv(
            initial_users={_DEFAULT_USER_EMAIL: mock_user},
            root_user_keys={_DEFAULT_USER_EMAIL},
            root_user_ids={mock_user.id},
        )
        response = env.get_secure(env.token)
        assert response.status_code == 200

    def test_root_user_key_matches_configured_identity(self) -> None:
        # When create_root_user_from_claims is triggered the stored user's id
        # must equal the email (the key extracted from claims by the mock
        # UserManager which has no explicit root config).
        env = AuthEnv(
            root_user_keys={_DEFAULT_USER_EMAIL},
        )
        env.get_secure(env.token)
        created_user = env.user_manager.users.get(_DEFAULT_USER_EMAIL)
        assert created_user is not None
        assert str(created_user.id) == _DEFAULT_USER_EMAIL

    def test_root_user_stored_in_root_users_after_first_login(self) -> None:
        env = AuthEnv(root_user_keys={_DEFAULT_USER_EMAIL})
        env.get_secure(env.token)
        # The mock's create_root_user_from_claims stores by user.id in root_users
        created_user = env.user_manager.users.get(_DEFAULT_USER_EMAIL)
        assert created_user is not None
        assert created_user.id in env.user_manager.root_users

    def test_non_root_user_not_created_as_root(self) -> None:
        mock_user = make_mock_user()
        env = AuthEnv(
            initial_users={_DEFAULT_USER_EMAIL: mock_user},
            # No root_user_keys → is_root_user_claims returns False
        )
        response = env.get_secure(env.token)
        assert response.status_code == 200
        assert mock_user.id not in env.user_manager.root_users

    def test_unknown_non_root_user_rejected_without_auto_create(self) -> None:
        env = AuthEnv(auto_create_new_users=False)
        token = env.mock_jwk_token.edit_claim("email", _UNKNOWN_USER_EMAIL)
        # Unknown address, not marked as root, auto-create off → 401
        response = env.get_secure(token)
        assert response.status_code == 401

    def test_is_root_user_claims_true_for_whitelisted_key(self) -> None:
        env = AuthEnv(root_user_keys={_DEFAULT_USER_EMAIL}, with_http=False)
        claims = dict(env.mock_jwk_token.payload)
        assert env.user_manager.is_root_user_claims(claims) is True

    def test_is_root_user_claims_false_for_non_whitelisted_key(self) -> None:
        env = AuthEnv(with_http=False)
        claims = dict(env.mock_jwk_token.payload)
        assert env.user_manager.is_root_user_claims(claims) is False

    def test_root_user_login_via_async_service_method(self) -> None:
        """Test get_existing_user_from_claims directly (no HTTP stack)."""
        env = AuthEnv(
            with_http=False,
            root_user_keys={_DEFAULT_USER_EMAIL},
        )
        claims = env.make_claims()
        user = asyncio.run(env.auth_service.get_existing_user_from_claims(claims))
        assert user is not None
        assert str(user.id) == _DEFAULT_USER_EMAIL

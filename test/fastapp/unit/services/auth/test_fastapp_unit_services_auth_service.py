import asyncio
from datetime import datetime, timedelta, timezone
from math import floor
from test.commondb.unit.services.auth_test_support import (
    DEFAULT_USER_EMAIL,
    GUEST_ROLE,
    MOCK_USER_ID,
    OLD_IAT_MINUTES,
    ROOT_ROLE,
    AuthEnv,
    make_cdb_user,
)
from test.fastapp.auth_test_client import AuthTestClient
from test.util.mock_compat import AsyncMock, MagicMock, Mock, patch
from typing import Any, cast
from uuid import UUID, uuid4

import pytest

from gen_epix.fastapp import App, exc, model
from gen_epix.fastapp.services.auth.command import GetIdentityProvidersCommand
from gen_epix.fastapp.services.auth.idp_client import IdpClient
from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider, IDPUser
from gen_epix.fastapp.services.auth.oauth_idp_client import OauthIdpClient
from gen_epix.fastapp.services.auth.service import AuthService


@pytest.mark.scenario_ids("TC-SEC-28-05")
class BaseAuthServiceTestCase:
    """Base test case with common fixtures and utilities."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Logger and App
        self.logger: Mock = Mock()
        self.user_manager: Mock = Mock()
        self.app: Mock = Mock(spec=App)
        self.app.logger = self.logger
        self.app.user_manager = self.user_manager
        self.app.log_item_class = MagicMock()
        self.app.cfg = {
            "service": {
                "auth": {
                    "props": {
                        "root": {
                            "user": {
                                # Keep disabled by default in tests unless a test explicitly enables it.
                                "token_time_to_live": None
                            }
                        }
                    }
                }
            }
        }
        self.user_manager.is_root_user.return_value = False

        # Users
        self.user: MagicMock = MagicMock(spec=model.User)
        self.other_user: MagicMock = MagicMock(spec=model.User)
        self.updated_user: MagicMock = MagicMock(spec=model.User)
        self.root_user: MagicMock = MagicMock(spec=model.User)
        self.created_user: MagicMock = MagicMock(spec=model.User)

        # Service (no IDPs by default)
        self.service: AuthService = AuthService(
            app=self.app,
            logger=self.logger,
            idps_cfg=[],
            ssl_context=False,
        )

        # Common IDs and Claims
        self.idp1_id: UUID = uuid4()
        self.idp2_id: UUID = uuid4()
        self.claims_dict: dict[str, Any] = {"iss": "issuer", "sub": "subject"}
        self.claims_token: str = "token"

    # Helpers

    def run_async(self, coro: Any) -> Any:
        """Run async coroutine synchronously."""
        return asyncio.run(coro)

    def create_claims(
        self, idp_client_id: UUID, extra: dict[str, Any] | None = None
    ) -> Claims:
        """Create Claims with optional extra fields."""
        claims: dict[str, Any] = dict(self.claims_dict)
        if extra:
            claims.update(extra)
        return Claims(
            claims=claims,
            scheme="BEARER",
            token=self.claims_token,
            idp_client_id=idp_client_id,
        )

    def make_idp_client(self, idp_id: UUID) -> Mock:
        """Create an IdpClient mock with minimal interface."""
        client: Mock = Mock(spec=IdpClient)
        client.id = idp_id
        client.get_claims_from_jwt = AsyncMock()
        client.get_identity_provider = Mock()
        client.get_claims_from_userinfo = Mock()
        client.__call__ = AsyncMock()  # type: ignore[method-assign]
        return client

    def extract_security_callable(self, annotated_dep: Any) -> Any:
        """Extract the callable function from Annotated[*, Security(...)]"""
        security_obj = annotated_dep.__metadata__[0]
        return security_obj.dependency  # the underlying function


# Property: idp_clients
class TestIdpClientsProperty(BaseAuthServiceTestCase):
    """Test idp_clients property."""

    def test_idp_clients_returns_copy(self) -> None:
        """idp_clients property returns a copy, not the original list."""
        # Create input
        idp_client1: Mock = self.make_idp_client(self.idp1_id)
        idp_client2: Mock = self.make_idp_client(self.idp2_id)
        # Set up mocks
        self.service._idp_clients = [idp_client1, idp_client2]
        # Execute
        clients_copy = self.service.idp_clients
        clients_copy.append(self.make_idp_client(uuid4()))
        # Verify
        assert len(self.service._idp_clients) == 2
        assert len(clients_copy) == 3


# get_existing_user_from_token
class TestGetExistingUserFromToken(BaseAuthServiceTestCase):
    """Test scenarios for get_existing_user_from_token."""

    def test_existing_user_from_token_second_idp_succeeds(self) -> None:
        """First IDP unauthorized, second IDP succeeds."""
        # Create input
        token: str = "jwt-token"
        idp_client1: Mock = self.make_idp_client(self.idp1_id)
        idp_client2: Mock = self.make_idp_client(self.idp2_id)
        # Set up mocks
        self.service._idp_clients = [idp_client1, idp_client2]
        idp_client1.get_claims_from_jwt.return_value = self.claims_dict
        idp_client2.get_claims_from_jwt.return_value = self.claims_dict
        with patch.object(
            self.service,
            "get_existing_user_from_claims",
            new=AsyncMock(
                side_effect=[exc.UnauthorizedAuthError("code", "message"), self.user]
            ),
        ):
            # Execute
            user = self.run_async(self.service.get_existing_user_from_token(token))
        # Verify
        assert user is self.user
        idp_client1.get_claims_from_jwt.assert_awaited_once_with(token)
        idp_client2.get_claims_from_jwt.assert_awaited_once_with(token)

    def test_existing_user_from_token_no_valid_user_raises(self) -> None:
        """No IDP yields a valid user -> UnauthorizedAuthError."""
        # Create input
        token: str = "jwt-token"
        idp_client1: Mock = self.make_idp_client(self.idp1_id)
        idp_client2: Mock = self.make_idp_client(self.idp2_id)
        # Set up mocks
        self.service._idp_clients = [idp_client1, idp_client2]
        idp_client1.get_claims_from_jwt.return_value = None
        idp_client2.get_claims_from_jwt.return_value = None
        # Execute/Verify
        with pytest.raises(exc.UnauthorizedAuthError):
            self.run_async(self.service.get_existing_user_from_token(token))
        idp_client1.get_claims_from_jwt.assert_awaited_once_with(token)
        idp_client2.get_claims_from_jwt.assert_awaited_once_with(token)


# create_user_dependencies
class TestCreateUserDependenciesNoIdp(BaseAuthServiceTestCase):
    """Test create_user_dependencies with no IDP clients configured."""

    def test_dependencies_no_idp_happy_paths(self) -> None:
        """Dummy deps return user or new user, and fallback to no-auth user."""
        # Create input
        request: Mock = Mock()
        scopes: Mock = Mock()
        # Set up mocks
        # Root user creation
        self.user_manager.create_root_user_from_claims.return_value = self.root_user
        # _no_auth_idp_client returns Claims
        claims: Claims = self.create_claims(uuid4())
        self.service._no_auth_idp_client = AsyncMock(return_value=claims)
        # get_existing_user_from_claims returns a user, then None (fallback)
        self.service.get_existing_user_from_claims = AsyncMock(  # type: ignore[method-assign]
            side_effect=[self.user, None]
        )
        # get_new_user_from_claims returns a new user
        self.service.get_new_user_from_claims = AsyncMock(return_value=self.other_user)  # type: ignore[method-assign]
        # Execute
        registered_dep, new_dep, idp_user_dep = self.service.create_user_dependencies()
        # Verify side-effects
        assert self.service._no_auth_user is self.root_user
        # Call registered user dependency -> returns existing user
        registered_func = self.extract_security_callable(registered_dep)
        user1 = self.run_async(registered_func(request, scopes))
        assert user1 is self.user
        # Next call -> fallback to no-auth user
        user2 = self.run_async(registered_func(request, scopes))
        assert user2 is self.root_user
        # Call new user dependency -> returns new user
        new_func = self.extract_security_callable(new_dep)
        new_user = self.run_async(new_func(request, scopes))
        assert new_user is self.other_user
        # IDP user dependency returns a new user in no-IDP mode (same callable)
        idp_func = self.extract_security_callable(idp_user_dep)
        idp_user = self.run_async(idp_func(request, scopes))
        assert idp_user is self.other_user

    def test_dependencies_no_idp_missing_claims_raises(self) -> None:
        """Dummy new-user dep raises when claims missing."""
        # Create input
        request: Mock = Mock()
        scopes: Mock = Mock()
        # Set up mocks
        self.user_manager.create_root_user_from_claims.return_value = self.root_user
        self.service._no_auth_idp_client = AsyncMock(return_value=None)
        # Execute
        _, new_dep, _ = self.service.create_user_dependencies()
        new_func = self.extract_security_callable(new_dep)
        # Verify
        with pytest.raises(exc.UnauthorizedAuthError):
            self.run_async(new_func(request, scopes))


class TestCreateUserDependenciesWithIdps(BaseAuthServiceTestCase):
    """Test create_user_dependencies with IDP clients configured."""

    def test_dependencies_multiple_idps_resolution(self) -> None:
        """Resolve current user via first and second IDPs, and IDP user from claims."""
        # Create input
        request: Mock = Mock()
        scopes: Mock = Mock()
        idp_client1: Mock = self.make_idp_client(self.idp1_id)
        idp_client2: Mock = self.make_idp_client(self.idp2_id)
        claims1: Claims = self.create_claims(self.idp1_id)
        claims2: Claims = self.create_claims(self.idp2_id)
        # Set up mocks
        self.service._idp_clients = [idp_client1, idp_client2]
        idp_client1.__call__.return_value = claims1  # type: ignore[attr-defined]
        idp_client2.__call__.return_value = claims2  # type: ignore[attr-defined]
        # get_existing_user_from_claims returns user for idp1 then idp2
        self.service.get_existing_user_from_claims = AsyncMock(  # type: ignore[method-assign]
            side_effect=[self.user, self.other_user]
        )
        # get_idp_user_from_claims returns IDPUser
        self.service.get_idp_user_from_claims = AsyncMock(  # type: ignore[method-assign]
            return_value=IDPUser(issuer="issuer", sub="subject")
        )
        # Execute
        registered_dep, _, idp_user_dep = self.service.create_user_dependencies()
        registered_func = self.extract_security_callable(registered_dep)
        idp_user_func = self.extract_security_callable(idp_user_dep)
        # Verify: first claims path
        user1 = self.run_async(registered_func(request, scopes, claims_0=claims1))
        assert user1 is self.user
        # Verify: fallback to second claims path
        user2 = self.run_async(
            registered_func(request, scopes, claims_0=None, claims_1=claims2)
        )
        assert user2 is self.other_user
        # Verify: idp user from claims
        idp_user = self.run_async(idp_user_func(request, scopes, claims_0=claims1))
        assert isinstance(idp_user, IDPUser)

    def test_dependencies_multiple_idps_unauthorized(self) -> None:
        """No claims provided -> UnauthorizedAuthError."""
        # Create input
        request: Mock = Mock()
        scopes: Mock = Mock()
        idp_client1: Mock = self.make_idp_client(self.idp1_id)
        # Set up mocks
        self.service._idp_clients = [idp_client1]
        # Execute
        registered_dep, _, _ = self.service.create_user_dependencies()
        registered_func = self.extract_security_callable(registered_dep)
        # Verify
        with pytest.raises(exc.UnauthorizedAuthError):
            self.run_async(registered_func(request, scopes, claims_0=None))


# get_identity_providers
class TestGetIdentityProviders(BaseAuthServiceTestCase):
    """Test scenarios for get_identity_providers."""

    def test_identity_providers_filters_public_and_handles_retry_errors(self) -> None:
        """Filter public providers and ignore retry errors."""
        # Create input
        cmd_public: GetIdentityProvidersCommand = (
            GetIdentityProvidersCommand.model_construct(user=self.user, public=True)
        )
        cmd_all: GetIdentityProvidersCommand = (
            GetIdentityProvidersCommand.model_construct(user=self.user, public=False)
        )
        idp_client1: Mock = self.make_idp_client(self.idp1_id)
        idp_client2: Mock = self.make_idp_client(self.idp2_id)
        provider_public: MagicMock = MagicMock(spec=IdentityProvider)
        provider_public.public = True
        provider_private: MagicMock = MagicMock(spec=IdentityProvider)
        provider_private.public = False
        # Set up mocks
        self.service._idp_clients = [idp_client1, idp_client2]
        idp_client1.get_identity_provider.return_value = provider_public
        idp_client2.get_identity_provider.return_value = provider_private
        with patch.object(
            self.service,
            "_retry_pending_idp_clients",
            side_effect=Exception("transient"),
        ):
            # Execute
            public_only = self.service.get_identity_providers(cmd_public)
            all_ids = self.service.get_identity_providers(cmd_all)
        # Verify
        assert public_only == [provider_public]
        assert all_ids == [provider_public, provider_private]

    def test_identity_providers_retry_initializes_pending_clients(self) -> None:
        """Retry initializes a pending client and adds it to service."""
        # Create input
        pending_cfg: dict[str, Any] = {"name": "idpX", "protocol": "OIDC"}
        # Set up mocks
        self.service._pending_idp_client_cfgs = [pending_cfg]
        new_client: Mock = self.make_idp_client(uuid4())
        with patch.object(self.service, "_init_idp_client", return_value=new_client):
            # Execute
            cmd: GetIdentityProvidersCommand = (
                GetIdentityProvidersCommand.model_construct(
                    user=self.user, public=False
                )
            )
            _ = self.service.get_identity_providers(cmd)
        # Verify
        assert new_client in self.service._idp_clients
        assert new_client.id in self.service._idp_client_by_id
        assert len(self.service._pending_idp_client_cfgs) == 0


# get_idp_user_from_claims
class TestGetIdpUserFromClaims(BaseAuthServiceTestCase):
    """Test get_idp_user_from_claims."""

    def test_get_idp_user_from_claims_returns_idp_user(self) -> None:
        """Should parse issuer and sub from claims."""
        # Create input
        claims: Claims = self.create_claims(uuid4())
        # Execute
        idp_user: IDPUser = self.run_async(
            self.service.get_idp_user_from_claims(claims)
        )
        # Verify
        assert idp_user.issuer == self.claims_dict["iss"]
        assert idp_user.sub == self.claims_dict["sub"]


# get_new_user_from_claims
class TestGetNewUserFromClaims(BaseAuthServiceTestCase):
    """Test scenarios for get_new_user_from_claims."""

    def test_get_new_user_from_claims_userinfo_and_user_manager(self) -> None:
        """With userinfo and user manager -> returns instance."""
        # Create input
        idp_client: Mock = self.make_idp_client(self.idp1_id)
        claims: Claims = self.create_claims(idp_client.id)
        # Set up mocks
        self.service._idp_client_by_id[idp_client.id] = idp_client
        idp_client.get_claims_from_userinfo.return_value = {"email": "user@example.com"}
        self.user_manager.construct_user_instance_from_claims.return_value = self.user
        # Execute
        new_user = self.run_async(self.service.get_new_user_from_claims(claims))
        # Verify
        assert new_user is self.user
        idp_client.get_claims_from_userinfo.assert_called_once_with(self.claims_token)
        self.user_manager.construct_user_instance_from_claims.assert_called_once()

    def test_get_new_user_from_claims_user_manager_none_raises(self) -> None:
        """User manager unable to create -> UnauthorizedAuthError."""
        # Create input
        idp_client: Mock = self.make_idp_client(self.idp1_id)
        claims: Claims = self.create_claims(idp_client.id)
        # Set up mocks
        self.service._idp_client_by_id[idp_client.id] = idp_client
        idp_client.get_claims_from_userinfo.return_value = (
            {}
        )  # ensure dict for update()
        self.user_manager.construct_user_instance_from_claims.return_value = None
        # Execute/Verify
        with pytest.raises(exc.UnauthorizedAuthError):
            self.run_async(self.service.get_new_user_from_claims(claims))

    def test_get_new_user_from_claims_no_user_manager_constructs_user(self) -> None:
        """No user manager -> construct model.User from claims."""
        # Create input
        claims: Claims = self.create_claims(uuid4(), {"email": "user@example.com"})
        # Set up mocks
        self.app.user_manager = None
        with patch("gen_epix.fastapp.model.User", return_value=self.user):
            # Execute
            new_user = self.run_async(
                self.service.get_new_user_from_claims(claims, request_userinfo=False)
            )
        # Verify
        assert new_user is self.user


# get_existing_user_from_claims
class TestGetExistingUserFromClaims(BaseAuthServiceTestCase):
    """Test scenarios for get_existing_user_from_claims."""

    def test_get_existing_user_no_user_manager_unauthorized(self) -> None:
        """No user manager -> UnauthorizedAuthError."""
        # Create input
        claims: Claims = self.create_claims(uuid4())
        # Set up mocks
        self.app.user_manager = None
        # Execute/Verify
        with pytest.raises(exc.UnauthorizedAuthError):
            self.run_async(self.service.get_existing_user_from_claims(claims))

    def test_get_existing_user_found_updates_name(self) -> None:
        """User found, name updated -> returns updated user."""
        # Create input
        claims: Claims = self.create_claims(uuid4(), {"email": "u@example.com"})
        # Set up mocks
        self.user_manager.get_user_key_from_claims.return_value = "key"
        self.user_manager.retrieve_user_by_key.return_value = self.user
        self.user_manager.get_user_name_from_claims.return_value = "New Name"
        self.user_manager.update_user_name.return_value = self.updated_user

        # Execute
        retval = self.run_async(self.service.get_existing_user_from_claims(claims))
        # Verify
        assert retval is self.updated_user
        self.user_manager.update_user_name.assert_called_once_with(
            self.user, "New Name"
        )

    def test_get_existing_user_update_name_domain_exception(self) -> None:
        """Update user name raises DomainException -> returns original user."""
        # Create input
        claims: Claims = self.create_claims(uuid4(), {"email": "u@example.com"})
        # Set up mocks
        self.user_manager.get_user_key_from_claims.return_value = "key"
        self.user_manager.retrieve_user_by_key.return_value = self.user
        self.user_manager.get_user_name_from_claims.return_value = "New Name"
        self.user_manager.update_user_name.side_effect = exc.DomainException(
            "code", "failed"
        )
        # Execute
        retval = self.run_async(self.service.get_existing_user_from_claims(claims))
        # Verify
        assert retval is self.user

    def test_get_existing_user_key_from_userinfo_then_found(self) -> None:
        """No user key initially; after userinfo, key resolves -> returns user."""
        # Create input
        idp_client: Mock = self.make_idp_client(self.idp1_id)
        claims: Claims = self.create_claims(idp_client.id)
        # Set up mocks
        self.service._idp_client_by_id[idp_client.id] = idp_client
        self.user_manager.get_user_key_from_claims.side_effect = ["", "key"]
        idp_client.get_claims_from_userinfo.return_value = {"email": "user@example.com"}
        self.user_manager.retrieve_user_by_key.return_value = self.user
        self.user_manager.get_user_name_from_claims.return_value = None
        # Execute
        retval = self.run_async(self.service.get_existing_user_from_claims(claims))
        # Verify
        assert retval is self.user
        idp_client.get_claims_from_userinfo.assert_called_once_with(self.claims_token)

    def test_get_existing_user_no_results_root_user(self) -> None:
        """User not found; claims match root -> create root user."""
        # Create input
        claims: Claims = self.create_claims(uuid4(), {"email": "root@example.com"})
        # Set up mocks
        self.user_manager.get_user_key_from_claims.return_value = "key"
        self.user_manager.retrieve_user_by_key.side_effect = exc.NoResultsError(
            "code", "no user"
        )
        self.user_manager.is_root_user_claims.return_value = True
        self.user_manager.create_root_user_from_claims.return_value = self.root_user
        # Execute
        retval = self.run_async(self.service.get_existing_user_from_claims(claims))
        # Verify
        assert retval is self.root_user

    def test_get_existing_user_no_results_auto_create_success(self) -> None:
        """User not found; auto-create -> success."""
        # Create input
        claims: Claims = self.create_claims(uuid4(), {"email": "user@example.com"})
        # Set up mocks
        self.user_manager.get_user_key_from_claims.return_value = "key"
        self.user_manager.retrieve_user_by_key.side_effect = exc.NoResultsError(
            "code", "no user"
        )
        self.user_manager.is_root_user_claims.return_value = False
        self.user_manager.auto_create_new_user.return_value = self.created_user
        # Execute
        self.service._auto_create_new_users = True
        retval = self.run_async(self.service.get_existing_user_from_claims(claims))
        # Verify
        assert retval is self.created_user

    def test_get_existing_user_no_results_auto_create_failure(self) -> None:
        """User not found; auto-create returns None -> Unauthorized."""
        # Create input
        claims: Claims = self.create_claims(uuid4(), {"email": "user@example.com"})
        # Set up mocks
        self.user_manager.get_user_key_from_claims.return_value = "key"
        self.user_manager.retrieve_user_by_key.side_effect = exc.NoResultsError(
            "code", "no user"
        )
        self.user_manager.is_root_user_claims.return_value = False
        self.user_manager.create_user_from_claims.return_value = None
        self.service._auto_create_new_users = False
        # Execute/Verify
        with pytest.raises(exc.UnauthorizedAuthError):
            self.run_async(self.service.get_existing_user_from_claims(claims))


class TestRootUserTokenTimeToLive(BaseAuthServiceTestCase):
    """Test root token TTL enforcement helper."""

    def test_root_token_within_15_minutes_is_allowed(self) -> None:
        """Root token younger than configured TTL should pass."""
        # Create input
        now = 2_000_000
        claims: Claims = self.create_claims(uuid4(), {"iat": now - 300})
        # Set up mocks
        self.app.cfg["service"]["auth"]["props"]["root"]["user"][
            "token_time_to_live"
        ] = 900
        self.user_manager.is_root_user.return_value = True
        # Execute/Verify
        with patch(
            "gen_epix.fastapp.services.auth.service.time.time", return_value=now
        ):
            self.service._verify_root_user_for_token_time_to_live(
                claims, self.root_user
            )

    def test_root_token_older_than_15_minutes_is_rejected(self) -> None:
        """Root token older than configured TTL should raise UnauthorizedAuthError."""
        # Create input
        now = 2_000_000
        claims: Claims = self.create_claims(uuid4(), {"iat": now - 901})
        # Set up mocks
        self.app.cfg["service"]["auth"]["props"]["root"]["user"][
            "token_time_to_live"
        ] = 900
        self.user_manager.is_root_user.return_value = True
        # Execute/Verify
        with patch(
            "gen_epix.fastapp.services.auth.service.time.time", return_value=now
        ):
            with pytest.raises(exc.UnauthorizedAuthError):
                self.service._verify_root_user_for_token_time_to_live(
                    claims, self.root_user
                )


# __init__ _validate_idp_cfgs behavior via constructor
class TestInitializationValidation(BaseAuthServiceTestCase):
    """Test IDP configuration validation during initialization."""

    def test_duplicate_idp_names_raise_initialization_error(self) -> None:
        """Duplicate names raise InitializationServiceError."""
        # Create input
        idps_cfg: list[dict[str, Any]] = [
            {"name": "same", "label": "A", "protocol": "OIDC"},
            {"name": "same", "label": "B", "protocol": "OIDC"},
        ]
        # Set up mocks
        # Execute/Verify
        with pytest.raises(exc.InitializationServiceError):
            AuthService(
                app=self.app, logger=self.logger, idps_cfg=idps_cfg, ssl_context=False
            )

    def test_pending_idp_when_init_returns_none(self) -> None:
        """If IDP init returns None, it is added to pending list."""
        # Create input
        idps_cfg: list[dict[str, Any]] = [
            {"name": "idp", "label": "L", "protocol": "OIDC"}
        ]
        # Set up mocks
        with patch.object(AuthService, "_init_idp_client", return_value=None):
            # Execute
            svc = AuthService(
                app=self.app, logger=self.logger, idps_cfg=idps_cfg, ssl_context=False
            )
        # Verify
        assert len(svc._pending_idp_client_cfgs) == 1


class TestRetryPendingIdpClients(BaseAuthServiceTestCase):
    def create_idp_config(self, name: str, label: str) -> dict[str, str | list]:
        return cast(
            dict[str, str | list],
            {
                "name": name,
                "label": label,
                "protocol": "OIDC",
                "issuer": "https://late-idp.org/",
                "client_id": "late-client",
                "client_secret": "late-secret",
                "claim_map": {"__key__": "email"},
                "scope": "openid",
                "authorization_endpoint": "https://late-idp.org/auth",
                "token_endpoint": "https://late-idp.org/token",
                "jwks_uri": "https://late-idp.org/certs",
                "userinfo_endpoint": "https://late-idp.org/userinfo",
                "response_types_supported": ["code"],
                "subject_types_supported": ["public"],
                "id_token_signing_alg_values_supported": ["RS256"],
            },
        )

    def test_retry_adds_late_idp_without_replacing_existing_clients(self) -> None:
        existing_client = self.make_idp_client(self.idp1_id)
        self.service._idp_clients = [existing_client]
        self.service._idp_client_by_name = {"existing": existing_client}
        self.service._idp_client_by_id = {self.idp1_id: existing_client}
        pending_cfg = self.create_idp_config("late_idp", "Late IDP")
        self.service._pending_idp_client_cfgs = [pending_cfg]

        self.service._retry_pending_idp_clients()

        assert len(self.service._idp_clients) == 2
        assert self.service._idp_clients[0] is existing_client
        new_client = self.service._idp_client_by_name["late_idp"]
        assert new_client in self.service._idp_clients
        assert self.service._idp_client_by_id[new_client.id] is new_client
        assert self.service._pending_idp_client_cfgs == []

    def test_retry_discards_pending_duplicate_name(self) -> None:
        existing_client = self.make_idp_client(self.idp1_id)
        self.service._idp_clients = [existing_client]
        self.service._idp_client_by_name = {"idp1": existing_client}
        pending_cfg = self.create_idp_config("idp1", "Duplicate IDP")
        self.service._pending_idp_client_cfgs = [pending_cfg]

        with patch.object(self.service, "_init_idp_client") as initialize:
            self.service._retry_pending_idp_clients()

        initialize.assert_not_called()
        assert self.service._idp_clients == [existing_client]
        assert self.service._pending_idp_client_cfgs == []


@pytest.fixture
def auth_test_client() -> AuthTestClient:
    return AuthTestClient()


@pytest.mark.scenario_ids("TC-SEC-28-01")
class TestAuthHttpFlow:
    NON_SECURE_ENDPOINT = "/non_secure"
    CURRENT_USER_ENDPOINT = "/secure/current_user"

    NOW = datetime.now(timezone.utc)
    INVALID_CLAIMS: dict[str, Any] = {
        "aud": "wrong_aud",
        "iss": "http://localhost:5003",
        "nbf": floor((NOW + timedelta(seconds=1000)).timestamp()),
        "exp": floor((NOW - timedelta(seconds=1000)).timestamp()),
        "iat": floor((NOW + timedelta(seconds=1000)).timestamp()),
    }
    INVALID_JWK: dict[str, str] = {"alg": "RS384", "kid": "wrong_key_id"}

    def test_non_secure_happy_flow(self, auth_test_client: AuthTestClient) -> None:
        response = auth_test_client.test_client.get(self.NON_SECURE_ENDPOINT)
        assert response.status_code == 200

    def test_valid_jwt_token_happy_flow(self, auth_test_client: AuthTestClient) -> None:
        response = auth_test_client.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=auth_test_client.mock_create_token_header(
                auth_test_client.MOCK_JWK_TOKEN.token
            ),
        )
        assert response.status_code == 200

    def test_secure_no_token(self, auth_test_client: AuthTestClient) -> None:
        response = auth_test_client.test_client.get(self.CURRENT_USER_ENDPOINT)
        assert response.status_code == 401

    def test_invalid_jwt_token(self, auth_test_client: AuthTestClient) -> None:
        response = auth_test_client.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=auth_test_client.mock_create_token_header(
                auth_test_client.MOCK_JWK_TOKEN.token + "invalid_token"
            ),
        )
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "key,value", INVALID_CLAIMS.items(), ids=INVALID_CLAIMS.keys()
    )
    def test_invalid_claims(
        self, auth_test_client: AuthTestClient, key: str, value: Any
    ) -> None:
        edited_token = auth_test_client.MOCK_JWK_TOKEN.edit_claim(key, value)
        response = auth_test_client.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=auth_test_client.mock_create_token_header(edited_token),
        )
        assert response.status_code in (401, 403)

    @pytest.mark.parametrize("key,value", INVALID_JWK.items(), ids=INVALID_JWK.keys())
    def test_invalid_jwk(
        self, auth_test_client: AuthTestClient, key: str, value: str
    ) -> None:
        for idp_client in auth_test_client.auth_service.idp_clients:
            if isinstance(idp_client, OauthIdpClient):
                idp_client._load_keys = MagicMock(return_value=None)
            else:
                raise NotImplementedError
        edited_token = auth_test_client.MOCK_JWK_TOKEN.edit_jwk(key, value)
        response = auth_test_client.test_client.get(
            self.CURRENT_USER_ENDPOINT,
            headers=auth_test_client.mock_create_token_header(edited_token),
        )
        assert response.status_code in (401, 403)


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestAutoCreateUserHttpFlow:
    def test_unknown_user_rejected_when_auto_create_disabled(self) -> None:
        env = AuthEnv(auto_create_new_users=False)
        token = env.mock_jwk_token.edit_claim("email", "unknown@other.org")
        assert env.get_secure(token).status_code == 401

    def test_known_user_allowed_when_auto_create_disabled(self) -> None:
        user = make_cdb_user(user_id=MOCK_USER_ID)
        env = AuthEnv(auto_create_new_users=False, initial_users=[user])
        assert env.get_secure(env.token).status_code == 200

    def test_unknown_user_auto_created_when_enabled(self) -> None:
        env = AuthEnv(auto_create_new_users=True)
        token = env.mock_jwk_token.edit_claim("email", "unknown@other.org")
        assert env.get_secure(token).status_code == 200
        assert env.repo.user_exists_by_key("unknown@other.org")

    def test_auto_create_enabled_does_not_duplicate_existing_user(self) -> None:
        user = make_cdb_user(user_id=MOCK_USER_ID)
        env = AuthEnv(auto_create_new_users=True, initial_users=[user])
        assert env.get_secure(env.token).status_code == 200
        assert env.repo.get_user_by_key("user1@org1.org") is user

    def test_auto_create_calls_user_manager_method(self) -> None:
        env = AuthEnv(auto_create_new_users=True)
        auto_created = make_cdb_user(email="unknown@other.org")
        token = env.mock_jwk_token.edit_claim("email", "unknown@other.org")
        with patch.object(
            env.user_manager, "auto_create_new_user", return_value=auto_created
        ) as auto_create:
            response = env.get_secure(token)
        assert response.status_code == 200
        auto_create.assert_called_once()

    def test_auto_create_disabled_does_not_call_auto_create_method(self) -> None:
        env = AuthEnv(auto_create_new_users=False)
        token = env.mock_jwk_token.edit_claim("email", "unknown@other.org")
        with patch.object(env.user_manager, "auto_create_new_user") as auto_create:
            env.get_secure(token)
        auto_create.assert_not_called()

    def test_auto_created_user_has_configured_role(self) -> None:
        env = AuthEnv(auto_create_new_users=True)
        token = env.mock_jwk_token.edit_claim("email", "unknown@other.org")
        env.get_secure(token)
        user = env.repo.get_user_by_key("unknown@other.org")
        assert user is not None
        assert GUEST_ROLE in user.roles

    def test_auto_created_user_key_matches_email_claim(self) -> None:
        env = AuthEnv(auto_create_new_users=True)
        token = env.mock_jwk_token.edit_claim("email", "unknown@other.org")
        env.get_secure(token)
        user = env.repo.get_user_by_key("unknown@other.org")
        assert user is not None
        assert user.key == "unknown@other.org"


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestRootTokenTtlHttpFlow:
    TTL_SECONDS = 1

    def make_root_env(
        self,
        token_iat_minutes_ago: int = 0,
        root_token_time_to_live: int | None = TTL_SECONDS,
    ) -> AuthEnv:
        root_user = make_cdb_user(user_id=MOCK_USER_ID, roles={ROOT_ROLE})
        return AuthEnv(
            root_token_time_to_live=root_token_time_to_live,
            token_iat_minutes_ago=token_iat_minutes_ago,
            initial_users=[root_user],
        )

    def test_fresh_root_token_within_ttl_is_accepted(self) -> None:
        env = self.make_root_env()
        assert env.get_secure(env.token).status_code == 200

    def test_old_root_token_exceeding_ttl_is_rejected(self) -> None:
        env = self.make_root_env(token_iat_minutes_ago=OLD_IAT_MINUTES)
        assert env.get_secure(env.token).status_code == 401

    def test_ttl_disabled_allows_old_root_token(self) -> None:
        env = self.make_root_env(
            token_iat_minutes_ago=OLD_IAT_MINUTES,
            root_token_time_to_live=0,
        )
        assert env.get_secure(env.token).status_code == 200

    def test_ttl_none_uses_default_ttl(self) -> None:
        root_user = make_cdb_user(user_id=MOCK_USER_ID, roles={ROOT_ROLE})
        env = AuthEnv(root_token_time_to_live=None, initial_users=[root_user])
        assert (
            env.auth_service._root_token_time_to_live
            == AuthService.DEFAULT_ROOT_TOKEN_TIME_TO_LIVE
        )

    def test_ttl_zero_disables_expiry(self) -> None:
        root_user = make_cdb_user(user_id=MOCK_USER_ID, roles={ROOT_ROLE})
        env = AuthEnv(root_token_time_to_live=0, initial_users=[root_user])
        assert env.auth_service._root_token_time_to_live == 0

    def test_non_root_user_not_affected_by_ttl(self) -> None:
        regular_user = make_cdb_user(user_id=MOCK_USER_ID, roles={GUEST_ROLE})
        env = AuthEnv(
            root_token_time_to_live=self.TTL_SECONDS,
            token_iat_minutes_ago=OLD_IAT_MINUTES,
            initial_users=[regular_user],
        )
        assert env.get_secure(env.token).status_code == 200

    def test_verify_root_ttl_directly_accepts_fresh_token(self) -> None:
        env = self.make_root_env(root_token_time_to_live=2)
        root_user = make_cdb_user(user_id=MOCK_USER_ID, roles={ROOT_ROLE})
        env.auth_service._verify_root_user_for_token_time_to_live(
            env.make_claims(), root_user
        )

    def test_verify_root_ttl_directly_rejects_old_token(self) -> None:
        env = self.make_root_env(
            token_iat_minutes_ago=OLD_IAT_MINUTES,
            root_token_time_to_live=self.TTL_SECONDS,
        )
        root_user = make_cdb_user(user_id=MOCK_USER_ID, roles={ROOT_ROLE})
        with pytest.raises(exc.UnauthorizedAuthError):
            env.auth_service._verify_root_user_for_token_time_to_live(
                env.make_claims(), root_user
            )


class TestCommonDbRootLoginFlow:
    def test_first_root_login_over_http_creates_root_user(self) -> None:
        env = AuthEnv()
        assert not env.repo.user_exists_by_key(DEFAULT_USER_EMAIL)
        response = env.get_secure(env.token)
        user = env.repo.get_user_by_key(DEFAULT_USER_EMAIL)
        assert response.status_code == 200
        assert user is not None
        assert user.key == DEFAULT_USER_EMAIL
        assert ROOT_ROLE in user.roles
        assert env.user_manager.is_root_user(user)

    def test_existing_root_user_can_login_over_http(self) -> None:
        root_user = make_cdb_user(user_id=MOCK_USER_ID, roles={ROOT_ROLE})
        env = AuthEnv(initial_users=[root_user])
        assert env.get_secure(env.token).status_code == 200

    def test_first_root_login_creates_configured_root_user(self) -> None:
        env = AuthEnv(with_http=False)
        claims = env.make_claims()
        user = asyncio.run(env.auth_service.get_existing_user_from_claims(claims))
        assert user is not None
        assert user.key == DEFAULT_USER_EMAIL
        assert GUEST_ROLE not in user.roles
        assert ROOT_ROLE in user.roles

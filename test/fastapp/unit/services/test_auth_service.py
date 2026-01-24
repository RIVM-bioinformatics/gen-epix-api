import asyncio
from typing import Any
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import UUID, uuid4

import pytest

from gen_epix.fastapp import App, exc, model
from gen_epix.fastapp.services.auth.command import GetIdentityProvidersCommand
from gen_epix.fastapp.services.auth.idp_client import IdpClient
from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider, IDPUser
from gen_epix.fastapp.services.auth.service import AuthService


@pytest.mark.scenario_ids("TC-SEC-28-05")
class BaseAuthServiceTestCase(TestCase):
    """Base test case with common fixtures and utilities."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Logger and App
        self.logger: Mock = Mock()
        self.user_manager: Mock = Mock()
        self.app: Mock = Mock(spec=App)
        self.app.logger = self.logger
        self.app.user_manager = self.user_manager
        self.app.log_item_class = MagicMock()

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
        self.assertEqual(len(self.service._idp_clients), 2)
        self.assertEqual(len(clients_copy), 3)


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
            new=AsyncMock(side_effect=[exc.UnauthorizedAuthError(), self.user]),
        ):
            # Execute
            user = self.run_async(self.service.get_existing_user_from_token(token))
        # Verify
        self.assertIs(user, self.user)
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
        with self.assertRaises(exc.UnauthorizedAuthError):
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
        self.assertIs(self.service._no_auth_user, self.root_user)
        # Call registered user dependency -> returns existing user
        registered_func = self.extract_security_callable(registered_dep)
        user1 = self.run_async(registered_func(request, scopes))
        self.assertIs(user1, self.user)
        # Next call -> fallback to no-auth user
        user2 = self.run_async(registered_func(request, scopes))
        self.assertIs(user2, self.root_user)
        # Call new user dependency -> returns new user
        new_func = self.extract_security_callable(new_dep)
        new_user = self.run_async(new_func(request, scopes))
        self.assertIs(new_user, self.other_user)
        # IDP user dependency returns a new user in no-IDP mode (same callable)
        idp_func = self.extract_security_callable(idp_user_dep)
        idp_user = self.run_async(idp_func(request, scopes))
        self.assertIs(idp_user, self.other_user)

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
        with self.assertRaises(exc.UnauthorizedAuthError):
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
        self.assertIs(user1, self.user)
        # Verify: fallback to second claims path
        user2 = self.run_async(
            registered_func(request, scopes, claims_0=None, claims_1=claims2)
        )
        self.assertIs(user2, self.other_user)
        # Verify: idp user from claims
        idp_user = self.run_async(idp_user_func(request, scopes, claims_0=claims1))
        self.assertIsInstance(idp_user, IDPUser)

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
        with self.assertRaises(exc.UnauthorizedAuthError):
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
        self.assertEqual(public_only, [provider_public])
        self.assertEqual(all_ids, [provider_public, provider_private])

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
        self.assertIn(new_client, self.service._idp_clients)
        self.assertIn(new_client.id, self.service._idp_client_by_id)
        self.assertEqual(len(self.service._pending_idp_client_cfgs), 0)


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
        self.assertEqual(idp_user.issuer, self.claims_dict["iss"])
        self.assertEqual(idp_user.sub, self.claims_dict["sub"])


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
        self.user_manager.get_user_instance_from_claims.return_value = self.user
        # Execute
        new_user = self.run_async(self.service.get_new_user_from_claims(claims))
        # Verify
        self.assertIs(new_user, self.user)
        idp_client.get_claims_from_userinfo.assert_called_once_with(self.claims_token)
        self.user_manager.get_user_instance_from_claims.assert_called_once()

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
        self.user_manager.get_user_instance_from_claims.return_value = None
        # Execute/Verify
        with self.assertRaises(exc.UnauthorizedAuthError):
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
        self.assertIs(new_user, self.user)


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
        with self.assertRaises(exc.UnauthorizedAuthError):
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
        self.assertIs(retval, self.updated_user)
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
        self.user_manager.update_user_name.side_effect = exc.DomainException("failed")
        # Execute
        retval = self.run_async(self.service.get_existing_user_from_claims(claims))
        # Verify
        self.assertIs(retval, self.user)

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
        self.assertIs(retval, self.user)
        idp_client.get_claims_from_userinfo.assert_called_once_with(self.claims_token)

    def test_get_existing_user_no_results_root_user(self) -> None:
        """User not found; claims match root -> create root user."""
        # Create input
        claims: Claims = self.create_claims(uuid4(), {"email": "root@example.com"})
        # Set up mocks
        self.user_manager.get_user_key_from_claims.return_value = "key"
        self.user_manager.retrieve_user_by_key.side_effect = exc.NoResultsError()
        self.user_manager.is_root_user_claims.return_value = True
        self.user_manager.create_root_user_from_claims.return_value = self.root_user
        # Execute
        retval = self.run_async(self.service.get_existing_user_from_claims(claims))
        # Verify
        self.assertIs(retval, self.root_user)

    def test_get_existing_user_no_results_auto_create_success(self) -> None:
        """User not found; auto-create -> success."""
        # Create input
        claims: Claims = self.create_claims(uuid4(), {"email": "user@example.com"})
        # Set up mocks
        self.user_manager.get_user_key_from_claims.return_value = "key"
        self.user_manager.retrieve_user_by_key.side_effect = exc.NoResultsError()
        self.user_manager.is_root_user_claims.return_value = False
        self.user_manager.create_user_from_claims.return_value = self.created_user
        # Execute
        retval = self.run_async(self.service.get_existing_user_from_claims(claims))
        # Verify
        self.assertIs(retval, self.created_user)

    def test_get_existing_user_no_results_auto_create_failure(self) -> None:
        """User not found; auto-create returns None -> Unauthorized."""
        # Create input
        claims: Claims = self.create_claims(uuid4(), {"email": "user@example.com"})
        # Set up mocks
        self.user_manager.get_user_key_from_claims.return_value = "key"
        self.user_manager.retrieve_user_by_key.side_effect = exc.NoResultsError()
        self.user_manager.is_root_user_claims.return_value = False
        self.user_manager.create_user_from_claims.return_value = None
        # Execute/Verify
        with self.assertRaises(exc.UnauthorizedAuthError):
            self.run_async(self.service.get_existing_user_from_claims(claims))


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
        with self.assertRaises(exc.InitializationServiceError):
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
        self.assertEqual(len(svc._pending_idp_client_cfgs), 1)

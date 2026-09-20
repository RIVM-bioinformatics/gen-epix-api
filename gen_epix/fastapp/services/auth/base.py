"""Base authentication service contract."""

from abc import abstractmethod

from gen_epix.fastapp import model
from gen_epix.fastapp.service import BaseService
from gen_epix.fastapp.services.auth.command import GetIdentityProvidersCommand
from gen_epix.fastapp.services.auth.idp_client import IdpClient
from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider, IDPUser


class BaseAuthService(BaseService):
    """Encapsulates a service that handles authentication logic.

    This is a base class intended to be subclassed for specific authentication services.
    """

    def register_handlers(self) -> None:
        """Register handlers."""
        self.app.register_handler(
            GetIdentityProvidersCommand, self.get_identity_providers
        )

    @property
    @abstractmethod
    def idp_clients(self) -> list[IdpClient]:
        """Idp clients."""
        raise NotImplementedError()

    @abstractmethod
    async def get_existing_user_from_token(self, token: str) -> model.User | None:
        """Resolve an existing application user from an identity-provider token.

        Tries each configured provider and rejects a token when none yields an
        authorized existing user. Root-user tokens are also checked against the
        configured maximum lifetime.

        Args:
            token: Bearer token supplied by a client.

        Returns:
            The authenticated existing user.

        Raises:
            UnauthorizedAuthError: If no configured provider can authenticate an
                existing user from ``token``.
        """
        raise NotImplementedError()

    @abstractmethod
    def create_user_dependencies(
        self,
    ) -> tuple[model.User, model.User, IDPUser]:
        """Create FastAPI dependencies for existing, new, and provider users.

        When no providers are configured, dependencies follow the root-user fallback
        path. Provider-backed dependencies support at most five configured clients.

        Returns:
            Dependencies for existing users, newly provisioned users, and provider
            identities, respectively.

        Raises:
            InitializationServiceError: If more than five identity providers are
                configured.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_identity_providers(
        self,
        cmd: GetIdentityProvidersCommand,
    ) -> list[IdentityProvider]:
        """Retrieve a list of available identity providers for authentication."""
        raise NotImplementedError()

    @abstractmethod
    async def get_idp_user_from_claims(self, claims: Claims) -> IDPUser:
        """Return idp user from claims."""
        raise NotImplementedError()

    @abstractmethod
    async def get_new_user_from_claims(
        self, claims: Claims, request_userinfo: bool = True
    ) -> model.User:
        """Construct a new application user from provider claims.

        Optionally enriches claims from the provider userinfo endpoint before asking
        the configured user manager to construct the user.

        Args:
            claims: Validated identity-provider claims and token metadata.
            request_userinfo: Whether to request additional provider userinfo claims.

        Returns:
            Newly constructed application user.

        Raises:
            UnauthorizedAuthError: If the user manager cannot construct a user.
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_existing_user_from_claims(
        self, claims: Claims, request_userinfo: bool = True
    ) -> model.User:
        """Return existing user from claims."""
        raise NotImplementedError()

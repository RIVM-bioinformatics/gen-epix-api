"""Identity-provider client interface and shared response models."""

import abc
import ssl
import uuid
from uuid import UUID

from fastapi import Request
from fastapi.openapi.models import SecurityBase

from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider


class IdpClient(abc.ABC):
    """Provide the idp client framework abstraction."""

    DEFAULT_TOKEN = "id_token"

    def __init__(
        self,
        scheme_name: str,
        token_name: str | None = None,
        id: UUID | None = None,
        ssl_context: ssl.SSLContext | bool = True,
        **kwargs: dict,
    ) -> None:
        """Initialize the instance."""
        self.id: UUID = id or uuid.uuid4()

        self.ssl_context = ssl_context

        # Set SecurityBase properties
        self.scheme_name = scheme_name
        self.token_name = token_name or self.DEFAULT_TOKEN
        self.model: SecurityBase  # type: ignore

    @abc.abstractmethod
    def get_identity_provider(self) -> IdentityProvider:
        """Get identity provider configuration."""
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_claims_from_jwt(
        self, jwt_token: str
    ) -> dict[str, str | int | bool | list[str]] | None:
        """Extract claims from JWT token."""
        raise NotImplementedError()

    # TODO: make async
    @abc.abstractmethod
    def get_claims_from_userinfo(
        self, access_token: str
    ) -> dict[str, str | int | bool | list[str]]:
        """Extract claims from userinfo endpoint using access token."""
        raise NotImplementedError()

    @abc.abstractmethod
    async def __call__(self, request: Request) -> Claims | None:
        """
        Returns the claims of the user from the request or None if claims cannot be
        processed by this client.

        """
        raise NotImplementedError()

import abc
from uuid import UUID

from fastapi import Request

from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider


class IDPClient(abc.ABC):

    @property
    @abc.abstractmethod
    def id(self) -> UUID:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_identity_provider(self) -> IdentityProvider:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_claims_from_userinfo(
        self, access_token: str
    ) -> dict[str, str | int | bool | list[str]]:
        raise NotImplementedError()

    @abc.abstractmethod
    async def __call__(self, request: Request) -> Claims | None:
        """
        Returns the claims of the user from the request or None if claims cannot be
        processed by this client.
        """
        raise NotImplementedError()

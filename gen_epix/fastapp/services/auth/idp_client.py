import abc
from uuid import UUID

from fastapi import Request

from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider


class IdpClient(abc.ABC):

    DEFAULT_TOKEN = "id_token"

    def __init__(
        self,
        scheme_name: str,
        token_name: str | None = None,
        id: UUID | None = None,
        **kwargs: dict,
    ) -> None:
        self._id: UUID = id or UUID()

        # Set SecurityBase properties
        self.scheme_name = scheme_name
        self.token_name = token_name or self.DEFAULT_TOKEN

    @property
    def id(self) -> UUID:
        return self._id

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

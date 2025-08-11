import logging
import uuid
from typing import Any, Type

from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt

from gen_epix.fastapp import exc
from gen_epix.fastapp.log import BaseLogItem, LogItem
from gen_epix.fastapp.services.auth.idp_client import IDPClient
from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider


class MockIDPClient(IDPClient):

    def __init__(
        self,
        logger: logging.Logger | None = None,
        log_item_class: Type[BaseLogItem] = LogItem,
        **kwargs: Any,
    ):
        self._id: uuid.UUID = kwargs.get("id", uuid.uuid4())  # type: ignore[assignment]
        # Set input properties and initialise some
        self._logger = logger
        self._log_item_class = log_item_class

    @property
    def id(self) -> uuid.UUID:
        return self._id

    def get_identity_provider(self) -> IdentityProvider:
        raise NotImplementedError()

    def get_claims_from_userinfo(
        self, access_token: str
    ) -> dict[str, str | int | bool | list[str]]:
        raise NotImplementedError()

    async def __call__(self, request: Request) -> Claims | None:
        if authorization := request.headers.get("authorization"):
            scheme, token = get_authorization_scheme_param(authorization)
            if scheme.upper() == "BEARER":
                # TODO: check if this is a security risk
                # or whether it should return an error
                try:
                    claims = jwt.get_unverified_claims(token)
                    if not claims:
                        return None
                    return Claims(
                        claims=claims, scheme=scheme, token=token, idp_client_id=self.id
                    )
                except exc.AuthException as exception:
                    if self._logger:
                        self._logger.warning(
                            self._log_item_class(
                                code="e86a3bd6",  # type: ignore[arg-type]
                                exception=exception,  # type: ignore[arg-type]
                            ).dumps()
                        )
                    return None

            else:
                # Authorization scheme not implemented
                if self._logger:
                    self._logger.warning(
                        self._log_item_class(
                            code="dec5fffe",  # type: ignore[arg-type]
                            msg=f"Authorization scheme {scheme} not implemented",  # type: ignore[arg-type]
                        ).dumps()
                    )
                return None

        if self._logger:
            self._logger.warning(
                self._log_item_class(
                    code="e14344c3",  # type: ignore[arg-type]
                    msg="No authorisation information provided in header",  # type: ignore[arg-type]
                ).dumps()
            )
        return None

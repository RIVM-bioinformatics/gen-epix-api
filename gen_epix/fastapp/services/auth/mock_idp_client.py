"""In-process identity-provider client for tests and local development."""

import logging
import uuid
from typing import Any

import jwt
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param

from gen_epix.fastapp import exc
from gen_epix.fastapp.log import BaseLogItem, LogItem
from gen_epix.fastapp.services.auth.idp_client import IdpClient
from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider


class MockIDPClient(IdpClient):
    """Encapsulates identity-provider client that serves configured mock claims."""

    def __init__(
        self,
        logger: logging.Logger | None = None,
        log_item_class: type[BaseLogItem] = LogItem,
        **kwargs: Any,
    ):
        """Initialize a MockIDPClient instance."""
        self._id: uuid.UUID = kwargs.get("id", uuid.uuid4())  # type: ignore[assignment]
        # Set input properties and initialise some
        self._logger = logger
        self._log_item_class = log_item_class

    @property
    def id(self) -> uuid.UUID:
        """Id the requested value."""
        return self._id

    def get_identity_provider(self) -> IdentityProvider:
        """Return identity provider."""
        raise NotImplementedError("Method not yet implemented")

    async def get_claims_from_jwt(
        self, jwt_token: str
    ) -> dict[str, str | int | bool | list[str]] | None:
        """Return claims from jwt."""
        raise NotImplementedError("Method not yet implemented")

    def get_claims_from_userinfo(
        self, access_token: str
    ) -> dict[str, str | int | bool | list[str]]:
        """Return claims from userinfo."""
        raise NotImplementedError("Method not yet implemented")

    async def __call__(self, request: Request) -> Claims | None:
        """Call the requested value."""
        if authorization := request.headers.get("authorization"):
            scheme, token = get_authorization_scheme_param(authorization)
            if scheme.upper() == "BEARER":
                # TODO: check if this is a security risk
                # or whether it should return an error
                try:
                    claims = jwt.decode(token, options={"verify_signature": False})
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

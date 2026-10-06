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

_METHOD_NOT_YET_IMPLEMENTED = "Method not yet implemented"


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
        raise NotImplementedError(_METHOD_NOT_YET_IMPLEMENTED)

    async def get_claims_from_jwt(
        self, jwt_token: str
    ) -> dict[str, str | int | bool | list[str]] | None:
        """Return claims from jwt."""
        raise NotImplementedError(_METHOD_NOT_YET_IMPLEMENTED)

    def get_claims_from_userinfo(
        self, access_token: str
    ) -> dict[str, str | int | bool | list[str]]:
        """Return claims from userinfo."""
        raise NotImplementedError(_METHOD_NOT_YET_IMPLEMENTED)

    def _log_warning(self, code: str, msg: str | None = None) -> None:
        """Log a mock authentication warning when logging is configured."""
        if self._logger:
            self._logger.warning(
                self._log_item_class(
                    code=code,  # type: ignore[arg-type]
                    msg=msg,  # type: ignore[arg-type]
                ).dumps()
            )

    def _decode_bearer_token(self, scheme: str, token: str) -> Claims | None:
        """Decode a mock bearer token into claims without signature verification."""
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

    async def __call__(self, request: Request) -> Claims | None:
        """Call the requested value."""
        authorization = request.headers.get("authorization")
        if not authorization:
            self._log_warning(
                "e14344c3", "No authorisation information provided in header"
            )
            return None
        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.upper() != "BEARER":
            self._log_warning(
                "dec5fffe", f"Authorization scheme {scheme} not implemented"
            )
            return None
        return self._decode_bearer_token(scheme, token)

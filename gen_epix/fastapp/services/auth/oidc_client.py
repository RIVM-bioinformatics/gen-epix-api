import json
import logging
import uuid
from datetime import datetime
from typing import Any, Type

import httpx
from fastapi import Request
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from fastapi.security.open_id_connect_url import OpenIdConnect
from fastapi.security.utils import get_authorization_scheme_param
from jose import ExpiredSignatureError, JWTError, jwk, jwt
from jose.backends.base import Key
from jose.exceptions import JWTClaimsError

from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import AuthProtocol, OauthFlowType
from gen_epix.fastapp.log import BaseLogItem, LogItem
from gen_epix.fastapp.services.auth.idp_client import IDPClient
from gen_epix.fastapp.services.auth.model import (
    Claims,
    IdentityProvider,
    OIDCConfiguration,
)


class OIDCClient(IDPClient, OpenIdConnect):

    def __init__(
        self,
        oidc_configuration: OIDCConfiguration,
        logger: logging.Logger | None = None,
        log_item_class: Type[BaseLogItem] = LogItem,
        **kwargs: Any,
    ):
        self._id = kwargs.get("id", uuid.uuid4())
        # Set input properties and initialize some
        self._logger = logger
        self._log_item_class = log_item_class
        self._cfg = oidc_configuration
        self._signing_keys: dict[str, Key] = {}

        # Retrieve remaining information
        self._init_from_discovery_url(
            discovery_document=kwargs.get("discovery_document")
        )
        self._signing_keys = {}
        # self._load_keys()
        flows = OAuthFlows()
        flows.authorizationCode = OAuthFlowAuthorizationCode(
            authorizationUrl=self._authorization_endpoint,
            tokenUrl=self._token_endpoint,
            scopes={k: k for k in self._cfg.scope.split()},
        )

        # Set SecurityBase properties
        self.model = OAuth2(flows=flows)
        self.scheme_name = self._issuer
        self.token_name = "id_token"

    @property
    def issuer(self) -> str:
        return self._issuer

    @property
    def audience(self) -> str:
        return self._cfg.client_id

    @property
    def id(self) -> uuid.UUID:
        return self._id

    def _should_verify_ssl(self, url: str) -> bool:
        return "127.0.0.1" not in url and "localhost" not in url

    def _init_from_discovery_url(self, discovery_document: dict | None = None) -> None:
        try:
            if discovery_document is None:
                with httpx.Client(
                    verify=self._should_verify_ssl(self._cfg.discovery_url)
                ) as client:
                    response = client.get(self._cfg.discovery_url)
                    discovery_document = response.json()
            self._issuer = discovery_document["issuer"]
            self._authorization_endpoint = discovery_document["authorization_endpoint"]
            self._token_endpoint = discovery_document["token_endpoint"]
            self._jwks_uri = discovery_document["jwks_uri"]
            self._userinfo_endpoint = discovery_document["userinfo_endpoint"]
            self._response_types_supported = discovery_document[
                "response_types_supported"
            ]
            self._subject_types_supported = discovery_document[
                "subject_types_supported"
            ]
            self._id_token_signing_alg_values_supported = discovery_document[
                "id_token_signing_alg_values_supported"
            ]
        except Exception as exception:
            msg = f"Error access discovery URL for OIDC service: {exception}"
            if self._logger:
                self._logger.error(
                    self._log_item_class(
                        code="cfe970aa", msg=msg, exception=exception
                    ).dumps()
                )
            raise exc.InitializationServiceError(msg) from exception

    async def get_jwk_from_jwt_token(self, jwt_token: str) -> Key:
        try:
            header = jwt.get_unverified_header(jwt_token)
        except JWTError as e:
            if self._logger:
                self._logger.warning(
                    self._log_item_class(
                        code="4cff1367",
                        msg="Unable to parse header from token",
                        jwt=jwt_token,
                        exception=e,
                    ).dumps()
                )
            raise exc.UnauthorizedAuthError() from e

        key_id = header.get("kid")
        if not key_id:
            if self._logger:
                self._logger.warning(
                    self._log_item_class(
                        code="0184bc35",
                        msg="No key ID found in token header",
                        jwt=jwt_token,
                    ).dumps()
                )
            raise exc.UnauthorizedAuthError()

        # Verify that the signing key in this session is outdated, fetch new one if so
        # TODO: verify if fetching new signing keys is ok
        key = self._signing_keys.get(key_id)
        if not key:
            if self._logger:
                self._logger.info(
                    self._log_item_class(
                        code="e90dd1aa",
                        msg="Key ID not found among signing keys, fetching new ones",
                        jwt=jwt_token,
                        key_id=key_id,
                    ).dumps()
                )
            self._load_keys()
            key = self._signing_keys.get(key_id)
            if not key:
                if self._logger:
                    self._logger.warning(
                        self._log_item_class(
                            code="2a5975ff",
                            msg="Key ID not found amoung newly fetched signing keys",
                            key_id=key_id,
                        ).dumps()
                    )
                raise exc.UnauthorizedAuthError()
            if self._logger:
                self._logger.info(
                    self._log_item_class(
                        code="c448ead5",
                        msg="Key ID found among newly fetched signing keys",
                        jwt=jwt_token,
                        key_id=key_id,
                    ).dumps()
                )
        return key

    async def get_claims_from_token(
        self, jwt_token: str
    ) -> dict[str, str | int | bool | list[str]] | None:
        # Decode token without verifying signature to make sure this token is generated
        # by this OIDC server
        claims = jwt.get_unverified_claims(jwt_token)
        if claims["iss"] != self._issuer or claims.get("aud") != self._cfg.client_id:
            # Different OIDC server
            return None

        iat: int = claims.get("iat", -1)
        if iat == -1 or iat > int(datetime.now().timestamp()):
            # Token issued in the future
            return None

        # Get key to verify signature and decode again
        key = await self.get_jwk_from_jwt_token(jwt_token)
        try:
            claims = jwt.decode(
                jwt_token,
                key=key,
                algorithms=self._id_token_signing_alg_values_supported,
                audience=self._cfg.client_id,
                issuer=self._issuer,
                # TODO: Check if this is not a security risk
                options={"verify_at_hash": False},
            )
        except Exception as exception:
            msg = "Unable to decode JWT: "
            if isinstance(exception, ExpiredSignatureError):
                msg += "signature has expired"
            elif isinstance(exception, JWTClaimsError):
                msg += "some claims are invalid"
            elif isinstance(exception, JWTError):
                msg += "signature is invalid"
            else:
                msg += "unknown issue"
            if self._logger:
                self._logger.warning(
                    self._log_item_class(
                        code="f4b73564",
                        msg=msg,
                        jwt=jwt_token,
                        exception=exception,
                    ).dumps()
                )
            raise exc.CredentialsAuthError(
                http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            ) from exception

        issuer = claims["iss"]
        sub = claims.get("sub")
        if not issuer or not sub:
            if not issuer and not sub:
                msg_part = "no issuer and no sub"
            elif issuer and not sub:
                msg_part = "no sub"
            else:
                msg_part = "no issuer"
            if self._logger:
                self._logger.warning(
                    self._log_item_class(
                        code="b4a1d49b",
                        msg=f"JWT does not contain required claims: {msg_part}",
                        jwt=jwt_token,
                    ).dumps()
                )
            raise exc.CredentialsAuthError(
                http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            )
        return claims

    def get_claims_from_userinfo(
        self, access_token: str
    ) -> dict[str, str | int | bool | list[str]]:
        try:
            with httpx.Client(
                verify=self._should_verify_ssl(self._userinfo_endpoint)
            ) as client:
                response = client.get(
                    self._userinfo_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                claims = json.loads(response.content)
                if not isinstance(claims, dict) or "error" in claims:
                    # Currently e.g. "InvalidAuthenticationToken"
                    if self._logger:
                        self._logger.warning(
                            self._log_item_class(
                                code="ce05d050",
                                msg=f"Unable to get claims from {self._userinfo_endpoint}: claims contain error",
                                claims=claims,
                            ).dumps()
                        )
                    raise exc.ServiceUnavailableError()
                return claims
        except Exception as exception:
            if self._logger:
                self._logger.warning(
                    self._log_item_class(
                        code="ac6c84f7",
                        msg=f"Unable to get claims from {self._userinfo_endpoint}",
                        exception=exception,
                    ).dumps()
                )
            return {}

    def get_identity_provider(self) -> IdentityProvider:
        return IdentityProvider(
            name=self._cfg.name,
            label=self._cfg.label,
            client_id=self._cfg.client_id,
            client_secret=self._cfg.client_secret,
            discovery_url=self._cfg.discovery_url,
            issuer=self._issuer,
            auth_protocol=AuthProtocol.OIDC,
            oauth_flow=OauthFlowType.AUTHORIZATION_CODE,
            scope=self._cfg.scope,
        )

    def _load_keys(self) -> None:
        try:
            with httpx.Client(verify=self._should_verify_ssl(self._jwks_uri)) as client:
                # get keys
                response = client.get(self._jwks_uri)
                response.raise_for_status()
                response_dict = response.json()

                self._signing_keys = {
                    key_data["kid"]: jwk.construct(
                        key_data=key_data,
                        algorithm=key_data.get(
                            "alg", "RS256"
                        ),  # Assume RS256 if alg is not specified
                    )
                    for key_data in response_dict["keys"]
                    if key_data["use"] == "sig"
                }
        except Exception as exception:
            if self._logger:
                self._logger.warning(
                    self._log_item_class(
                        code="edab2e97",
                        msg=f"Unable to load new signing keys from {self._jwks_uri}",
                        exception=exception,
                    ).dumps()
                )
            raise exc.ServiceUnavailableError() from exception

    async def __call__(self, request: Request) -> Claims | None:  # type: ignore
        """
        Retrieve verified claims for the user based on the request.
        """
        if authorization := request.headers.get("authorization"):
            scheme, token = get_authorization_scheme_param(authorization)
            if scheme.upper() == "BEARER":
                # TODO: check if this is a security risk
                # or whether it should return an error
                try:
                    claims = await self.get_claims_from_token(token)
                    if not claims:
                        return None
                    return Claims(
                        claims=claims, scheme=scheme, token=token, idp_client_id=self.id
                    )
                except exc.AuthException as exception:
                    if self._logger:
                        self._logger.warning(
                            self._log_item_class(
                                code="ac521d94",
                                exception=exception,
                            ).dumps()
                        )
                    return None

            else:
                # Authorization scheme not implemented
                if self._logger:
                    self._logger.warning(
                        self._log_item_class(
                            code="ecb88df4",
                            msg=f"Authorization scheme {scheme} not implemented",
                        ).dumps()
                    )
                return None
        if self._logger:
            self._logger.warning(
                self._log_item_class(
                    code="e1dad160",
                    msg="No authorisation information provided in header",
                ).dumps()
            )
        return None

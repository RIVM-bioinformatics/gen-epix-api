import json
import logging
from datetime import datetime
from typing import Any, Type
from uuid import UUID

import httpx
from fastapi import Request

# from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from fastapi.security.open_id_connect_url import OpenIdConnect
from fastapi.security.utils import get_authorization_scheme_param
from jose import ExpiredSignatureError, JWTError, jwk, jwt
from jose.backends.base import Key
from jose.exceptions import JWTClaimsError

from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import AuthProtocol, OauthFlow
from gen_epix.fastapp.log import BaseLogItem, LogItem
from gen_epix.fastapp.services.auth.idp_client import IdpClient
from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider, OidcCfg


class OidcClient(IdpClient, OpenIdConnect):
    LOCAL_HOSTS = {"localhost", "127.0.0.1"}

    def __init__(
        self,
        oidc_configuration: OidcCfg,
        token_name: str | None = None,
        logger: logging.Logger | None = None,
        log_item_class: Type[BaseLogItem] = LogItem,
        discovery_url: str | None = None,
        discovery_doc: dict[str, Any] | None = None,
        id: UUID | None = None,
        **kwargs: Any,
    ):
        # Set cfg and retrieve remaining information
        self._cfg = oidc_configuration.model_copy()
        self.update_config_from_discovery(url=discovery_url, doc=discovery_doc)

        # Set IdpClient properties
        issuer = self._cfg.issuer
        assert issuer is not None
        super().__init__(
            issuer, token_name=token_name or self.DEFAULT_TOKEN, id=id, **kwargs
        )

        # Set input properties and initialize some
        self._logger = logger
        self._log_item_class = log_item_class
        self._signing_keys: dict[str, Key] = {}

        # self._load_keys()
        # authorization_endpoint = self._cfg.authorization_endpoint
        # token_endpoint = self._cfg.token_endpoint
        # scopes_supported = self._cfg.scopes_supported
        # assert authorization_endpoint is not None
        # assert token_endpoint is not None
        # assert scopes_supported is not None
        # flows = OAuthFlows()
        # flows.authorizationCode = OAuthFlowAuthorizationCode(
        #     authorizationUrl=authorization_endpoint,
        #     tokenUrl=token_endpoint,
        #     scopes={x: x for x in scopes_supported},
        # )
        # self.model = OAuth2(flows=flows)

    @property
    def issuer(self) -> str:
        assert self._cfg.issuer is not None
        return self._cfg.issuer

    @property
    def audience(self) -> str:
        return self._cfg.client_id

    def update_config_from_discovery(
        self, url: str | None = None, doc: dict[str, Any] | None = None
    ) -> None:
        """
        Update the OIDC configuration from the discovery URL or, if provided, the
        discovery document.
        """

        # Special case: discovery document provided
        if doc:
            # Update current configuration from provided discovery document
            for key, value in doc.items():
                setattr(self._cfg, key, value)
            return

        # Get discovery URL
        url = url or self._cfg.discovery_url
        if not url:
            raise exc.InitializationServiceError(
                "No discovery URL or document provided for OIDC configuration"
            )

        # Update from discovery URL
        try:
            # Create new config from discovery URL
            oidc_cfg = OidcClient.create_config_for_discovery_url(
                url, name=self._cfg.name, label=self._cfg.label
            )
            # Update current configuration with data from new config
            for key, value in oidc_cfg.model_dump(
                exclude=OidcCfg.NON_SPEC_FIELDS
            ).items():
                setattr(self._cfg, key, value)
            if not oidc_cfg.is_valid():
                invalid_fields = oidc_cfg.get_invalid_fields()
                raise exc.InitializationServiceError(
                    f"OIDC configuration from discovery URL is not valid. Invalid fields: {invalid_fields}"
                )
        except Exception as exception:
            msg = f"Error accessing discovery URL for OIDC service {self._cfg.name}: {exception}"
            if self._logger:
                self._logger.error(
                    self._log_item_class(
                        code="cfe970aa", msg=msg, exception=exception
                    ).dumps()
                )
            raise exc.InitializationServiceError(msg) from exception

    async def get_jwk_from_jwt(self, jwt_token: str) -> Key:
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

    async def get_claims_from_jwt(
        self, jwt_token: str
    ) -> dict[str, str | int | bool | list[str]] | None:
        # Decode token without verifying signature to make sure this token is generated
        # by this OIDC server
        claims = jwt.get_unverified_claims(jwt_token)
        if (
            claims["iss"] != self._cfg.issuer
            or claims.get("aud") != self._cfg.client_id
        ):
            # Different OIDC server
            return None

        iat: int = claims.get("iat", -1)
        if iat == -1 or iat > int(datetime.now().timestamp()):
            # Token issued in the future
            return None

        # Get key to verify signature and decode again
        key = await self.get_jwk_from_jwt(jwt_token)
        try:
            claims = jwt.decode(
                jwt_token,
                key=key,
                algorithms=self._cfg.id_token_signing_alg_values_supported,
                audience=self._cfg.client_id,
                issuer=self._cfg.issuer,
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
        userinfo_endpoint = self._cfg.userinfo_endpoint
        assert userinfo_endpoint is not None
        try:
            with httpx.Client(
                verify=OidcClient.should_verify_ssl(userinfo_endpoint)
            ) as client:
                response = client.get(
                    userinfo_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                claims = json.loads(response.content)
                if not isinstance(claims, dict) or "error" in claims:
                    # Currently e.g. "InvalidAuthenticationToken"
                    if self._logger:
                        self._logger.warning(
                            self._log_item_class(
                                code="ce05d050",
                                msg=f"Unable to get claims from {userinfo_endpoint}: claims contain error",
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
                        msg=f"Unable to get claims from {userinfo_endpoint}",
                        exception=exception,
                    ).dumps()
                )
            return {}

    def get_identity_provider(self) -> IdentityProvider:
        issuer = self._cfg.issuer
        scopes_supported = self._cfg.scopes_supported
        assert issuer is not None
        assert scopes_supported is not None
        scope = " ".join(scopes_supported)
        return IdentityProvider(
            name=self._cfg.name,
            label=self._cfg.label,
            client_id=self._cfg.client_id,
            client_secret=self._cfg.client_secret,
            discovery_url=self._cfg.discovery_url,
            issuer=issuer,
            auth_protocol=AuthProtocol.OIDC,
            oauth_flow=OauthFlow.AUTHORIZATION_CODE,
            scope=scope,
        )

    def _load_keys(self) -> None:
        jwks_uri = self._cfg.jwks_uri
        assert jwks_uri is not None
        try:
            with httpx.Client(verify=OidcClient.should_verify_ssl(jwks_uri)) as client:
                # get keys
                response = client.get(jwks_uri)
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
                        msg=f"Unable to load new signing keys from {jwks_uri}",
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
                    claims = await self.get_claims_from_jwt(token)
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

    @staticmethod
    def should_verify_ssl(url: str) -> bool:
        return not any(x in url.lower() for x in OidcClient.LOCAL_HOSTS)

    @staticmethod
    def create_config_for_discovery_url(
        url: str, name: str = "", label: str = ""
    ) -> OidcCfg:
        with httpx.Client(verify=OidcClient.should_verify_ssl(url)) as client:
            response = client.get(url)
            discovery_doc = response.json()
        oidc_cfg = OidcCfg(name=name, label=label, discovery_url=url, **discovery_doc)
        return oidc_cfg

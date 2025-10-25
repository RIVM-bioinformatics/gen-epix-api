import base64
import json
import logging
import ssl
import time
import urllib.parse
from datetime import datetime
from typing import Any, Type
from uuid import UUID

import httpx
from fastapi import Request
from fastapi.openapi.models import OAuthFlowAuthorizationCode, OAuthFlows, SecurityBase
from fastapi.security import OAuth2

# from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from fastapi.security.open_id_connect_url import OpenIdConnect
from fastapi.security.utils import get_authorization_scheme_param
from jose import ExpiredSignatureError, JWTError, jwk, jwt
from jose.backends.base import Key
from jose.exceptions import JWTClaimsError

from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import AuthProtocol, OAuthFlow
from gen_epix.fastapp.log import BaseLogItem, LogItem
from gen_epix.fastapp.services.auth.idp_client import IdpClient
from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider, OidcServerCfg


class OidcClient(IdpClient, OpenIdConnect):

    DEFAULT_CLIENT_CREDENTIAL_FLOW_REQUEST_HEADERS: dict[str, str] = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    DEFAULT_CLIENT_CREDENTIAL_FLOW_MAX_RETRIES: int = 3
    DEFAULT_CLIENT_CREDENTIAL_FLOW_BASE_DELAY: float = 1.0  # in seconds

    def __init__(
        self,
        server_cfg: OidcServerCfg,
        token_name: str | None = None,
        logger: logging.Logger | None = None,
        log_item_class: Type[BaseLogItem] = LogItem,
        discovery_url: str | None = None,
        discovery_doc: dict[str, Any] | None = None,
        id: UUID | None = None,
        ssl_context: ssl.SSLContext | bool = False,
        client_credential_flow_request_headers: dict[str, str] | None = None,
        client_credential_flow_max_retries: int | None = None,
        client_credential_flow_base_delay: float | None = None,
        **kwargs: Any,
    ):
        # Set IdpClient properties
        issuer = server_cfg.issuer
        if issuer is None:
            # Fetch issuer later from discovery document
            issuer = ""
        super().__init__(
            issuer,
            token_name=token_name or self.DEFAULT_TOKEN,
            id=id,
            ssl_context=ssl_context,
            **kwargs,
        )

        # Set input properties
        self.server_cfg = server_cfg.model_copy()
        self.logger = logger
        self._log_item_class = log_item_class
        self._signing_keys: dict[str, Key] = {}
        self._client_credential_flow_request_headers = (
            client_credential_flow_request_headers
            or self.DEFAULT_CLIENT_CREDENTIAL_FLOW_REQUEST_HEADERS
        )
        self._client_credential_flow_max_retries = (
            client_credential_flow_max_retries
            or self.DEFAULT_CLIENT_CREDENTIAL_FLOW_MAX_RETRIES
        )
        self._client_credential_flow_base_delay = (
            client_credential_flow_base_delay
            or self.DEFAULT_CLIENT_CREDENTIAL_FLOW_BASE_DELAY
        )

        # Set cfg and retrieve remaining information
        self.update_server_config_from_discovery(url=discovery_url, doc=discovery_doc)
        if issuer == "":
            self.scheme_name = self.server_cfg.issuer or ""

        # Set SecurityBase properties
        authorization_endpoint = (
            self.server_cfg.authorization_endpoint or ""
        )  # In case of client credentials flow or development, this may not be set
        token_endpoint = (
            self.server_cfg.token_endpoint or ""
        )  # In case of client credentials flow or development, this may not be set
        flows = OAuthFlows()
        flows.authorizationCode = OAuthFlowAuthorizationCode(
            authorizationUrl=authorization_endpoint,
            tokenUrl=token_endpoint,
            scopes={x: x for x in self.server_cfg.scope.split()},
        )
        self.model: SecurityBase = OAuth2(flows=flows)

    @property
    def issuer(self) -> str:
        assert self.server_cfg.issuer is not None
        return self.server_cfg.issuer

    @property
    def audience(self) -> str:
        return self.server_cfg.audience or self.server_cfg.client_id

    @property
    def scope(self) -> str:
        assert self.server_cfg.scope is not None
        return self.server_cfg.scope

    def update_server_config_from_discovery(
        self,
        url: str | None = None,
        doc: dict[str, Any] | None = None,
    ) -> None:
        """
        Update the OIDC configuration from the discovery URL or, if provided, the
        discovery document.
        """
        url = url or self.server_cfg.discovery_url
        if url is None and doc is None:
            raise exc.InitializationServiceError(
                "No discovery URL or document provided for OIDC configuration"
            )

        # Special case: discovery document provided -> update from that first
        if doc:
            # Update current configuration from provided discovery document
            for key, value in doc.items():
                setattr(self.server_cfg, key, value)

        # Update from discovery URL
        if not url:
            return
        try:
            # Get discovery document
            with httpx.Client(verify=self.ssl_context) as client:
                response = client.get(url)
                discovery_doc = response.json()

            # Update current configuration with discovery data, preserving client credentials
            for key, value in discovery_doc.items():
                if (
                    key not in OidcServerCfg.NON_SPEC_FIELDS
                    and key in self.server_cfg.__class__.model_fields
                ):
                    setattr(self.server_cfg, key, value)

            if not self.server_cfg.is_valid():
                invalid_fields = self.server_cfg.get_invalid_fields()
                raise exc.InitializationServiceError(
                    f"OIDC configuration from discovery URL is not valid. Invalid fields: {invalid_fields}"
                )
        except Exception as exception:
            msg = f"Error accessing discovery URL for OIDC service {self.server_cfg.name}: {exception}"
            if self.logger:
                self.logger.error(
                    self._log_item_class(
                        code="cfe970aa", msg=msg, exception=exception
                    ).dumps()
                )
            raise exc.InitializationServiceError(msg) from exception

    async def get_jwk_from_jwt(self, jwt_token: str) -> Key:
        try:
            header = jwt.get_unverified_header(jwt_token)
        except JWTError as e:
            if self.logger:
                self.logger.warning(
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
            if self.logger:
                self.logger.warning(
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
            if self.logger:
                self.logger.info(
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
                if self.logger:
                    self.logger.warning(
                        self._log_item_class(
                            code="2a5975ff",
                            msg="Key ID not found amoung newly fetched signing keys",
                            key_id=key_id,
                        ).dumps()
                    )
                raise exc.UnauthorizedAuthError()
            if self.logger:
                self.logger.info(
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
        server_cfg = self.server_cfg
        # TODO: check audience claim as well?
        if claims["iss"] != server_cfg.issuer or claims.get("aud") != self.audience:
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
                algorithms=server_cfg.id_token_signing_alg_values_supported,
                audience=self.audience,
                issuer=server_cfg.issuer,
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
            if self.logger:
                self.logger.warning(
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

        # Get issuer and sub
        issuer = claims["iss"]
        sub = claims.get("sub")
        if not issuer or not sub:
            if not issuer and not sub:
                msg_part = "no issuer and no sub"
            elif issuer and not sub:
                msg_part = "no sub"
            else:
                msg_part = "no issuer"
            if self.logger:
                self.logger.warning(
                    self._log_item_class(
                        code="b4a1d49b",
                        msg=f"JWT does not contain required claims: {msg_part}",
                        jwt=jwt_token,
                    ).dumps()
                )
            raise exc.CredentialsAuthError(
                http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            )

        # Map claims according to claim_map, allowing e.g. to standardize claim names across IDPs
        for new_claim_name, orig_claim_names in server_cfg.claim_map.items():
            for orig_claim_name in orig_claim_names:
                claims[new_claim_name] = claims.get(orig_claim_name)
                if claims[new_claim_name] is not None:
                    break

        return claims

    def retrieve_jwt_with_client_credentials_flow(
        self,
        scope: str,
        headers: dict[str, str] | None = None,
        max_retries: int | None = None,
        base_delay: float | None = None,
    ) -> str:
        """
        Call server to get token through OAuth Client Credentials flow.
        """
        # Parse input
        headers = dict(headers or self._client_credential_flow_request_headers)
        max_retries = max_retries or self._client_credential_flow_max_retries
        base_delay = base_delay or self._client_credential_flow_base_delay

        # Add basic auth header
        headers["Authorization"] = (
            "Basic "
            + base64.b64encode(
                f"{self.server_cfg.client_id}:{self.server_cfg.client_secret}".encode()
            ).decode()
        )

        # Get token endpoint URL
        url = self.server_cfg.token_endpoint
        print(
            f"DEBUG: OidcClient[{self.server_cfg.name}].retrieve_jwt_with_client_credentials_flow: token endpoint URL: {url}"
        )
        if not isinstance(url, str):
            # Try to get from discovery document
            if self.logger:
                self.logger.info(
                    self._log_item_class(
                        code="8f3a2b1c",
                        msg=f"Token endpoint URL is not set in OIDC server configuration for server {self.server_cfg.name}, trying to update from discovery URL",
                    ).dumps()
                )
            self.update_server_config_from_discovery()
            url = self.server_cfg.token_endpoint
        if not isinstance(url, str):
            raise exc.ServiceUnavailableError("Token endpoint URL is not set")

        # Create request body
        token_data: str = "&".join(
            (
                f"grant_type=client_credentials",
                f"scope={urllib.parse.quote(scope)}",
            )
        )
        # token_data = {
        #     "grant_type": "client_credentials",
        #     "client_id": self.server_cfg.client_id,
        #     "client_secret": self.server_cfg.client_secret,
        #     "scope": scope,
        # }

        # Call server with retries
        print(
            f"DEBUG: OidcClient[{self.server_cfg.name}].retrieve_jwt_with_client_credentials_flow: calling IDP with {token_data}"
        )
        last_exception: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                with httpx.Client(verify=self.ssl_context) as client:
                    response = client.post(
                        url,
                        data=token_data,
                        headers=headers,
                    )
                    print(
                        f"DEBUG: OidcClient[{self.server_cfg.name}].retrieve_jwt_with_client_credentials_flow: received response {response.status_code} with content {response.content}"
                    )
                    response.raise_for_status()
                    token_response = response.json()
                    token: str = token_response["access_token"]
                    return token
            except Exception as exception:
                last_exception = exception
                print(
                    f"DEBUG: OidcClient[{self.server_cfg.name}].retrieve_jwt_with_client_credentials_flow: exception during attempt {attempt}: {exception}"
                )
                if self.logger:
                    self.logger.warning(
                        self._log_item_class(
                            code="a7f3e9d2",
                            msg=f"OAuth Client Credentials flow token retrieval attempt {attempt + 1} failed for server {self.server_cfg.name}",
                            exception=exception,
                        ).dumps()
                    )
            # Wait before next retry (but not after the last attempt)
            if attempt < max_retries:
                time.sleep(base_delay)

        # All retries failed
        print(
            f"DEBUG: OidcClient[{self.server_cfg.name}].retrieve_jwt_with_client_credentials_flow: all attempts failed"
        )
        if self.logger:
            self.logger.error(
                self._log_item_class(
                    code="f8a3d7b2",
                    msg=f"OAuth Client Credentials flow token retrieval failed after {max_retries + 1} attempts for server {self.server_cfg.name}",
                ).dumps()
            )
        raise exc.ServiceUnavailableError(
            f"Token retrieval failed for server {self.server_cfg.name}: {last_exception}"
        )

    def get_claims_from_userinfo(
        self, access_token: str
    ) -> dict[str, str | int | bool | list[str]]:
        userinfo_endpoint = self.server_cfg.userinfo_endpoint
        assert userinfo_endpoint is not None
        try:
            with httpx.Client(verify=self.ssl_context) as client:
                response = client.get(
                    userinfo_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                claims = json.loads(response.content)
                if not isinstance(claims, dict) or "error" in claims:
                    # Currently e.g. "InvalidAuthenticationToken"
                    if self.logger:
                        self.logger.warning(
                            self._log_item_class(
                                code="ce05d050",
                                msg=f"Unable to get claims from {userinfo_endpoint}: claims contain error",
                                claims=claims,
                            ).dumps()
                        )
                    raise exc.ServiceUnavailableError()
                return claims
        except Exception as exception:
            if self.logger:
                self.logger.warning(
                    self._log_item_class(
                        code="ac6c84f7",
                        msg=f"Unable to get claims from {userinfo_endpoint}",
                        exception=exception,
                    ).dumps()
                )
            return {}

    def get_identity_provider(self) -> IdentityProvider:
        issuer = self.server_cfg.issuer
        assert issuer is not None
        return IdentityProvider(
            name=self.server_cfg.name,
            label=self.server_cfg.label,
            client_id=self.server_cfg.client_id,
            client_secret=self.server_cfg.client_secret,
            discovery_url=self.server_cfg.discovery_url,
            issuer=issuer,
            auth_protocol=AuthProtocol.OIDC,
            oauth_flow=OAuthFlow.AUTHORIZATION_CODE,
            scope=self.server_cfg.scope,
            public=self.server_cfg.public,
        )

    def _load_keys(self) -> None:
        jwks_uri = self.server_cfg.jwks_uri
        assert jwks_uri is not None
        try:
            with httpx.Client(verify=self.ssl_context) as client:
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
            if self.logger:
                self.logger.warning(
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
        print(f"DEBUG: OidcClient[{self.server_cfg.name}].__call__: start.")
        if authorization := request.headers.get("authorization"):
            scheme, token = get_authorization_scheme_param(authorization)
            if scheme.upper() == "BEARER":
                # TODO: check if this is a security risk
                # or whether it should return an error
                try:
                    print(
                        f"DEBUG: OidcClient[{self.server_cfg.name}].__call__: processing token."
                    )
                    claims = await self.get_claims_from_jwt(token)
                    if not claims:
                        print(
                            f"DEBUG: OidcClient[{self.server_cfg.name}].__call__: not authenticated."
                        )
                        return None
                    print(
                        f"DEBUG: OidcClient[{self.server_cfg.name}].__call__: authenticated."
                    )
                    return Claims(
                        claims=claims, scheme=scheme, token=token, idp_client_id=self.id
                    )
                except exc.AuthException as exception:
                    print(
                        f"DEBUG: OidcClient[{self.server_cfg.name}].__call__: exception."
                    )
                    if self.logger:
                        self.logger.warning(
                            self._log_item_class(
                                code="ac521d94",
                                exception=exception,
                            ).dumps()
                        )
                    return None
            else:
                # Authorization scheme not implemented
                if self.logger:
                    self.logger.warning(
                        self._log_item_class(
                            code="ecb88df4",
                            msg=f"Authorization scheme {scheme} not implemented",
                        ).dumps()
                    )
                return None
        if self.logger:
            self.logger.warning(
                self._log_item_class(
                    code="e1dad160",
                    msg="No authorisation information provided in header",
                ).dumps()
            )
        return None

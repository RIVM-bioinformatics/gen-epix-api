import base64
import json
import logging
import ssl
import time
import urllib.parse
from typing import Any, TypedDict
from uuid import UUID

import httpx
from fastapi import Request
from fastapi.openapi.models import OAuthFlowAuthorizationCode, OAuthFlows, SecurityBase
from fastapi.security import OAuth2

# from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from fastapi.security.open_id_connect_url import OpenIdConnect
from fastapi.security.utils import get_authorization_scheme_param
from jose import ExpiredSignatureError, JOSEError, JWSError, JWTError, jwk, jwt
from jose.backends.base import Key

from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import AuthProtocol, OAuthFlow
from gen_epix.fastapp.log import BaseLogItem, LogItem
from gen_epix.fastapp.services.auth.idp_client import IdpClient
from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider, OidcServerCfg


class OidcClient(IdpClient, OpenIdConnect):

    DEFAULT_INTROSPECTION_REQUEST_HEADERS: dict[str, str] = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    DEFAULT_INTROSPECTION_AUTH_METHOD: str = "client_secret_basic"
    DEFAULT_CLIENT_CREDENTIAL_FLOW_REQUEST_HEADERS: dict[str, str] = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    DEFAULT_CLIENT_CREDENTIAL_FLOW_MAX_RETRIES: int = 3
    DEFAULT_CLIENT_CREDENTIAL_FLOW_BASE_DELAY: float = 1.0  # in seconds
    DEFAULT_ALLOWED_SIGNING_ALGORITHMS: list[str] = ["RS256"]

    def __init__(
        self,
        server_cfg: OidcServerCfg,
        token_name: str | None = None,
        logger: logging.Logger | None = None,
        log_item_class: type[BaseLogItem] = LogItem,
        discovery_url: str | None = None,
        discovery_doc: dict[str, Any] | None = None,
        id: UUID | None = None,
        ssl_context: ssl.SSLContext | bool = True,
        introspect_token_request_headers: dict[str, str] | None = None,
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
        self._introspection_request_headers = (
            introspect_token_request_headers
            or self.DEFAULT_INTROSPECTION_REQUEST_HEADERS
        )
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
        self._allowed_signing_algorithms = (
            self.server_cfg.id_token_signing_alg_values_supported
            or self.DEFAULT_ALLOWED_SIGNING_ALGORITHMS
        )

        # Introspection cache entry type
        class IntrospectionCacheEntry(TypedDict):
            active: bool | None
            last_checked: int
            exp: int

        self._introspection_cache: dict[str, IntrospectionCacheEntry] = {}

        if self.server_cfg.enable_introspection:
            # dynamically determine the introspection endpoint
            self.introspection_endpoint: str = self._get_introspection_endpoint()

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
            if self.logger:
                self.logger.error(
                    self._log_item_class(
                        code="cfe970aa",
                        msg="Error accessing discovery URL",
                        scheme_name=self.server_cfg.name,
                        exception=exception,
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
                        scheme_name=self.scheme_name,
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
                        scheme_name=self.scheme_name,
                        jwt=jwt_token,
                    ).dumps()
                )
            raise exc.UnauthorizedAuthError()

        # Verify that the signing key in this session is outdated, fetch new one if so
        # TODO: verify if fetching new signing keys is ok
        key = self._signing_keys.get(key_id)
        if not key:
            if self.logger and self.logger.level <= logging.DEBUG:
                self.logger.debug(
                    self._log_item_class(
                        code="e90dd1aa",
                        msg="Key ID not found among signing keys, fetching new ones",
                        scheme_name=self.scheme_name,
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
                            scheme_name=self.scheme_name,
                            key_id=key_id,
                        ).dumps()
                    )
                raise exc.UnauthorizedAuthError()
            if self.logger and self.logger.level <= logging.DEBUG:
                self.logger.debug(
                    self._log_item_class(
                        code="c448ead5",
                        msg="Key ID found among newly fetched signing keys",
                        scheme_name=self.scheme_name,
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

        if claims["iss"] != server_cfg.issuer:
            if self.logger and self.logger.level <= logging.DEBUG:
                self.logger.debug(
                    self._log_item_class(
                        code="7e2a1c4d",
                        msg="JWT issuer does not match OIDC server configuration",
                        scheme_name=self.scheme_name,
                        token_issuer=claims["iss"],
                        token_subject=claims.get("sub"),
                        expected_issuer=server_cfg.issuer,
                    ).dumps()
                )
            return None

        # Get key to verify signature and decode again
        key = await self.get_jwk_from_jwt(jwt_token)
        try:
            claims = jwt.decode(
                jwt_token,
                key=key,
                algorithms=self._allowed_signing_algorithms,
                audience=self.audience,
                issuer=server_cfg.issuer,
                options={
                    "require_iat": True,
                    "verify_iat": True,
                    "require_exp": True,
                    "verify_exp": True,
                },
            )
        except Exception as exception:
            msg = "Unable to decode JWT: "

            if isinstance(exception, ExpiredSignatureError):
                msg += "signature has expired"
            elif isinstance(exception, JOSEError):
                msg += "general JOSE error"
            elif isinstance(exception, JWSError):
                msg += "general JWS error"
            elif isinstance(exception, JWTError):
                msg += "signature is invalid"
            else:
                msg += "unknown issue"
            if self.logger:
                self.logger.warning(
                    self._log_item_class(
                        code="f4b73564",
                        msg=msg,
                        scheme_name=self.scheme_name,
                        exception=exception,
                    ).dumps()
                )
            raise exc.CredentialsAuthError(
                http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            ) from exception

        # optionally apply token introspection
        if self.server_cfg.enable_introspection:
            self.introspect_token(jwt_token, claims)

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
                        scheme_name=self.scheme_name,
                    ).dumps()
                )
            raise exc.CredentialsAuthError(
                http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            )

        # Log for debugging
        if self.logger and self.logger.level <= logging.DEBUG:
            self.logger.debug(
                self._log_item_class(
                    code="8a7c4e92",
                    msg="JWT is valid",
                    scheme_name=self.scheme_name,
                    token_issuer=claims["iss"],
                ).dumps()
            )

        # Map claims according to claim_map, allowing e.g. to standardize claim names across IDPs
        for new_claim_name, orig_claim_names in server_cfg.claim_map.items():
            for orig_claim_name in orig_claim_names:
                claims[new_claim_name] = claims.get(orig_claim_name)
                if claims[new_claim_name] is not None:
                    break

        return claims

    def introspect_token(self, jwt_token: str, claims: dict[str, Any]) -> None:
        now = self._now()
        self._prune_expired_introspection_cache(now)
        if self._is_cached_introspection_token_inactive(jwt_token):
            if self.logger:
                self.logger.warning(
                    self._log_item_class(
                        code="0ce44f1a",
                        msg="Token previously marked inactive by introspection; denying",
                    ).dumps()
                )
            raise exc.CredentialsAuthError(
                http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            )
        if self._is_recheck_introspection(jwt_token, now):
            if self.logger:
                self.logger.info(
                    self._log_item_class(
                        code="9deaa6b2",
                        msg="Performing token introspection re-check",
                    ).dumps()
                )
            is_active = self._introspect_token_with_server(jwt_token)
            if is_active is None:
                # network or parse error
                raise exc.CredentialsAuthError(
                    http_props={"headers": {"WWW-Authenticate": "Bearer"}}
                )
            exp_val = int(claims.get("exp", now))
            if is_active:
                self._update_introspection_cache(jwt_token, True, exp_val, now)
            else:
                if is_active is False:
                    self._update_introspection_cache(jwt_token, False, exp_val, now)
                    if self.logger:
                        self.logger.warning(
                            self._log_item_class(
                                code="b1c2d3e4",
                                msg="Token marked inactive by introspection; denying",
                            ).dumps()
                        )
                raise exc.CredentialsAuthError(
                    http_props={"headers": {"WWW-Authenticate": "Bearer"}}
                )

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
        if not isinstance(url, str):
            # Try to get from discovery document
            if self.logger and self.logger.level <= logging.DEBUG:
                self.logger.debug(
                    self._log_item_class(
                        code="8f3a2b1c",
                        msg=f"Token endpoint URL is not set in OIDC server configuration for server {self.server_cfg.name}, trying to update from discovery URL",
                        scheme_name=self.scheme_name,
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

        # Call server with retries
        last_exception: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                with httpx.Client(verify=self.ssl_context) as client:
                    response = client.post(
                        url,
                        data=token_data,
                        headers=headers,
                    )
                    response.raise_for_status()
                    token_response = response.json()
                    token: str = token_response["access_token"]
                    return token
            except Exception as exception:
                last_exception = exception
                if self.logger:
                    self.logger.warning(
                        self._log_item_class(
                            code="a7f3e9d2",
                            msg=f"OAuth Client Credentials flow token retrieval attempt {attempt + 1} failed for server {self.server_cfg.name}",
                            scheme_name=self.scheme_name,
                            exception=exception,
                        ).dumps()
                    )
            # Wait before next retry (but not after the last attempt)
            if attempt < max_retries:
                time.sleep(base_delay)

        # All retries failed
        if self.logger:
            self.logger.error(
                self._log_item_class(
                    code="f8a3d7b2",
                    msg=f"OAuth Client Credentials flow token retrieval failed after {max_retries + 1} attempts for server {self.server_cfg.name}",
                    scheme_name=self.scheme_name,
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
                                scheme_name=self.scheme_name,
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
                        scheme_name=self.scheme_name,
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

    def _get_introspection_endpoint(self) -> str:
        if self.server_cfg.introspection_endpoint:
            return self.server_cfg.introspection_endpoint
        # dynamically determine from discovery document
        try:
            url: str | None = self.server_cfg.discovery_url
            if not url:
                raise exc.AuthException(
                    "Token introspection was enabled but endpoint URL is not set and could also not be determined from discovery URL"
                )
            with httpx.Client(verify=self.ssl_context) as client:
                response = client.get(url)
                discovery_doc = response.json()
            introspection_endpoint: str = discovery_doc.get("introspection_endpoint")
            return introspection_endpoint
        except Exception as exception:
            if self.logger:
                self.logger.error(
                    self._log_item_class(
                        code="d1234abc",
                        msg="Error accessing discovery URL to determine introspection endpoint",
                        scheme_name=self.scheme_name,
                        exception=exception,
                    ).dumps()
                )
            raise exc.UnauthorizedAuthError(
                http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            ) from exception

    def _introspect_token_with_server(self, jwt_token: str) -> bool | None:
        if not self.introspection_endpoint:
            return None
        timeout_seconds = self.server_cfg.introspection_timeout_seconds
        # Prepare headers and body
        headers = self._introspection_request_headers
        data: dict[str, str] = {
            "token": jwt_token,
            "token_type_hint": "access_token",
        }
        method = (
            self.server_cfg.introspection_auth_method
            or self.DEFAULT_INTROSPECTION_AUTH_METHOD
        ).lower()
        if method not in {"client_secret_basic", "client_secret_post", "none"}:
            if self.logger:
                self.logger.warning(
                    self._log_item_class(
                        code="6f4a8e22",
                        msg=(
                            "Unknown introspection auth method; defaulting to client_secret_basic"
                        ),
                        method=method,
                    ).dumps()
                )
            method = "client_secret_basic"
        if method == "client_secret_basic":
            # Add Basic auth
            basic = base64.b64encode(
                f"{self.server_cfg.client_id}:{self.server_cfg.client_secret}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {basic}"
        elif method == "client_secret_post":
            data["client_id"] = self.server_cfg.client_id
            if self.server_cfg.client_secret is not None:
                data["client_secret"] = self.server_cfg.client_secret
        elif method == "none":
            pass

        try:
            with httpx.Client(
                verify=self.ssl_context, timeout=timeout_seconds
            ) as client:
                response = client.post(
                    self.introspection_endpoint, data=data, headers=headers
                )
            if response.status_code != 200:
                if self.logger:
                    self.logger.warning(
                        self._log_item_class(
                            code="7a3e6d1f",
                            msg=("Token introspection returned non-200 status"),
                            status=response.status_code,
                        ).dumps()
                    )
                raise exc.UnauthorizedAuthError(
                    http_props={"headers": {"WWW-Authenticate": "Bearer"}}
                )
            payload = response.json()
            active = payload.get("active")
            if isinstance(active, bool):
                return active
            # Unexpected payload shape
            return None
        except Exception as exc_:  # broad: treat any failure as unknown
            if self.logger:
                self.logger.warning(
                    self._log_item_class(
                        code="f2b3c9aa",
                        msg=("Token introspection failed (timeout/network/parse)"),
                        exception=exc_,
                    ).dumps()
                )
            raise exc.UnauthorizedAuthError(
                http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            ) from exc_

    def _now(self) -> int:
        return int(time.time())

    def _prune_expired_introspection_cache(self, now: int | None = None) -> None:
        time_stamp = now or self._now()
        expired_keys = [
            x for x, y in self._introspection_cache.items() if y["exp"] <= time_stamp
        ]
        for x in expired_keys:
            self._introspection_cache.pop(x, None)

    def _is_cached_introspection_token_inactive(self, jwt_token: str) -> bool:
        introspection_token = self._introspection_cache.get(jwt_token)
        return bool(introspection_token and introspection_token.get("active") is False)

    def _is_recheck_introspection(self, jwt_token: str, now: int | None = None) -> bool:
        introspection_token = self._introspection_cache.get(jwt_token)
        if not introspection_token:
            return True
        interval = self.server_cfg.introspection_interval_seconds
        last = int(introspection_token.get("last_checked", 0))
        time_stamp = now or self._now()
        return (time_stamp - last) >= interval

    def _update_introspection_cache(
        self,
        jwt_token: str,
        active: bool | None,
        exp: int,
        now: int | None = None,
    ) -> None:
        self._introspection_cache[jwt_token] = {
            "active": active,
            "last_checked": now or self._now(),
            "exp": exp,
        }

    def _load_keys(self) -> None:
        jwks_uri = self.server_cfg.jwks_uri
        assert jwks_uri is not None
        try:
            with httpx.Client(verify=self.ssl_context) as client:
                # get keys
                response = client.get(jwks_uri)
                response.raise_for_status()
                response_dict = response.json()
        except Exception as exception:
            if self.logger:
                self.logger.warning(
                    self._log_item_class(
                        code="edab2e97",
                        msg=f"Unable to load new signing keys from {jwks_uri}",
                        scheme_name=self.scheme_name,
                        exception=exception,
                    ).dumps()
                )
            raise exc.ServiceUnavailableError() from exception

        # verify keys
        self._signing_keys = {}
        for key_data in response_dict["keys"]:
            if (
                key_data.get("use") != "sig"
                or key_data.get("kty") != "RSA"
                or key_data.get("alg") not in self._allowed_signing_algorithms
            ):
                if self.logger:
                    self.logger.warning(
                        self._log_item_class(
                            code="d4e5f6a7",
                            msg="Skipping loading of signing key due to use/alg mismatch",
                            scheme_name=self.scheme_name,
                            key_id=key_data.get("kid"),
                            use=key_data.get("use"),
                            alg=key_data.get("alg"),
                        ).dumps()
                    )
                raise exc.UnauthorizedAuthError("Signing key use/alg mismatch")

            self._signing_keys[key_data["kid"]] = jwk.construct(
                key_data=key_data, algorithm=key_data["alg"]
            )

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
                    if self.logger:
                        self.logger.warning(
                            self._log_item_class(
                                code="ac521d94",
                                msg="Error retrieving claims from JWT",
                                scheme_name=self.scheme_name,
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
                            scheme_name=self.scheme_name,
                        ).dumps()
                    )
                return None
        if self.logger:
            self.logger.warning(
                self._log_item_class(
                    code="e1dad160",
                    msg="No authorisation information provided in header",
                    scheme_name=self.scheme_name,
                ).dumps()
            )
        return None

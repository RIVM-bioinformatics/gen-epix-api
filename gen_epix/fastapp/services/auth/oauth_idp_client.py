"""OAuth and OpenID Connect identity-provider client."""

import base64
import json
import logging
import ssl
import time
import urllib.parse
from typing import Any
from uuid import UUID

import httpx
import jwt
from fastapi import Request
from fastapi.openapi.models import OAuthFlowAuthorizationCode, OAuthFlows, SecurityBase
from fastapi.security import OAuth2

# from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from fastapi.security.open_id_connect_url import OpenIdConnect
from fastapi.security.utils import get_authorization_scheme_param

from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import AuthProtocol, OAuthFlow
from gen_epix.fastapp.log import BaseLogItem, LogItem
from gen_epix.fastapp.services.auth.idp_client import IdpClient
from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider, OidcServerCfg
from gen_epix.fastapp.services.auth.token_introspection_manager import (
    TokenIntrospectionManager,
)


class OauthIdpClient(IdpClient, OpenIdConnect):
    """Encapsulates OAuth identity-provider client that validates and obtains tokens."""

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
        """Initialize a OauthIdpClient instance."""
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
        self._signing_keys: dict[str, jwt.PyJWK] = {}
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

        if self.server_cfg.enable_introspection:
            self.token_introspection_manager: TokenIntrospectionManager = (
                TokenIntrospectionManager(
                    server_cfg=self.server_cfg,
                    discovery_url=discovery_url or self.server_cfg.discovery_url or "",
                    ssl_context=self.ssl_context,
                    introspect_token_request_headers=introspect_token_request_headers,
                    introspection_auth_method=self.server_cfg.introspection_auth_method,
                    introspection_timeout_seconds=self.server_cfg.introspection_timeout_seconds,
                    introspection_interval_seconds=self.server_cfg.introspection_interval_seconds,
                    log_item_class=self._log_item_class,
                    logger=self.logger,
                )
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
            scopes=(
                {x: x for x in self.server_cfg.scope.split()}
                if self.server_cfg.scope
                else {}
            ),
        )
        self.model: SecurityBase = OAuth2(flows=flows)

    @property
    def issuer(self) -> str:
        """Issuer the requested value."""
        assert self.server_cfg.issuer is not None
        return self.server_cfg.issuer

    @property
    def audience(self) -> str:
        """Audience the requested value."""
        return self.server_cfg.audience or self.server_cfg.client_id

    @property
    def scope(self) -> str:
        """Scope the requested value."""
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
                "109f98e6",
                "No discovery URL or document provided for OIDC configuration",
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
                response.raise_for_status()
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
                    "53851a9e",
                    f"OIDC configuration from discovery URL is not valid. Invalid fields: {invalid_fields}",
                )
        except Exception as exception:
            msg = "Error accessing discovery URL"
            # Add more specific error message for SSL certificate issues
            if self.logger:
                self.logger.error(
                    self._log_item_class(
                        code="cfe970aa",
                        msg=msg,
                        scheme_name=self.server_cfg.name,
                        exception=exception,
                    ).dumps()
                )
            raise exc.InitializationServiceError("66b9919e", msg) from exception

    async def get_jwk_from_jwt(self, jwt_token: str) -> jwt.PyJWK:
        """Return jwk from jwt."""
        key_id: str = self._validate_key_id(jwt_token, self._parse_kid(jwt_token))

        # Verify that the signing key in this session is outdated, fetch new one if so
        # TODO: verify if fetching new signing keys is ok

        key: jwt.PyJWK | None = self._signing_keys.get(key_id)
        if not key:
            self._refresh_signing_keys()
            key = self._signing_keys.get(key_id)
            if not key:
                self._log_keys_fetch_failure(key_id)
                raise exc.UnauthorizedAuthError("759a2688")
            self._log_keys_fetch_success()
        return key

    def _log_keys_fetch_success(self) -> None:
        """Log keys fetch success."""
        if self.logger and self.logger.level <= logging.DEBUG:
            self.logger.debug(
                self._log_item_class(
                    code="c448ead5",
                    msg="Key ID found among newly fetched signing keys",
                    scheme_name=self.scheme_name,
                ).dumps()
            )

    def _log_keys_fetch_failure(self, key_id: str) -> None:
        """Log keys fetch failure."""
        if self.logger:
            self.logger.warning(
                self._log_item_class(
                    code="2a5975ff",
                    msg="Key ID not found amoung newly fetched signing keys",
                    scheme_name=self.scheme_name,
                    key_id=key_id,
                ).dumps()
            )

    def _refresh_signing_keys(self) -> None:
        """Refresh signing keys."""
        if self.logger and self.logger.level <= logging.DEBUG:
            self.logger.debug(
                self._log_item_class(
                    code="e90dd1aa",
                    msg="Key ID not found among signing keys, fetching new ones",
                    scheme_name=self.scheme_name,
                ).dumps()
            )
        self._load_keys()

    def _validate_key_id(self, jwt_token: str, key_id: str | None) -> str:
        """Validate key id."""
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
            raise exc.UnauthorizedAuthError("d3d0bb67")
        return key_id

    def _parse_kid(self, jwt_token: str) -> str | None:
        """Parse kid."""
        try:
            return jwt.get_unverified_header(jwt_token).get("kid")
        except jwt.PyJWTError as e:
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
            raise exc.UnauthorizedAuthError("5bb8ffb6") from e

    async def get_claims_from_jwt(self, jwt_token: str) -> dict[str, Any] | None:
        """Return claims from jwt."""
        claims = self._decode_jwt_unverified(jwt_token)
        if not self._validate_issuer(claims):
            return None
        key = await self.get_jwk_from_jwt(jwt_token)

        claims = self._verify_token(jwt_token, key)
        self._check_required_claims(claims)

        # optionally apply token introspection
        if self.server_cfg.enable_introspection:
            self.token_introspection_manager.introspect_token(jwt_token, claims)

        if self.logger and self.logger.level <= logging.DEBUG:
            self.logger.debug(
                self._log_item_class(
                    code="8a7c4e92",
                    msg="JWT is valid",
                    scheme_name=self.scheme_name,
                    token_issuer=claims["iss"],
                ).dumps()
            )

        return self._map_claims(claims)

    def _map_claims(self, claims: dict[str, Any]) -> dict[str, Any]:
        """Map claims."""
        for new_claim_name, orig_claim_names in self.server_cfg.claim_map.items():
            for orig_claim_name in orig_claim_names:
                value = claims.get(orig_claim_name)
                if value is not None:
                    claims[new_claim_name] = value
                    break

        return claims

    def _check_required_claims(self, claims: dict[str, Any]) -> None:
        """Check required claims."""
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
                "4675ff0c", http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            )

    def _verify_token(self, jwt_token: str, key: jwt.PyJWK) -> dict[str, Any]:
        """Verify token."""
        try:
            claims: dict[str, Any] = jwt.decode(
                jwt_token,
                key=key,
                algorithms=self._allowed_signing_algorithms,
                audience=self.audience,
                issuer=self.server_cfg.issuer,
                options={
                    "require_iat": True,
                    "verify_iat": True,
                    "require_exp": True,
                    "verify_exp": True,
                },
            )
        except Exception as exception:
            msg = "Unable to decode JWT: "
            if isinstance(exception, jwt.ExpiredSignatureError):
                msg += "signature has expired"
            elif isinstance(exception, jwt.PyJWTError):
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
                "cde2a901", http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            ) from exception

        return claims

    def _validate_issuer(self, claims: dict[str, Any]) -> bool:
        """Validate issuer."""
        if claims["iss"] != self.server_cfg.issuer:
            if self.logger and self.logger.level <= logging.DEBUG:
                self.logger.debug(
                    self._log_item_class(
                        code="7e2a1c4d",
                        msg="JWT issuer does not match OIDC server configuration",
                        scheme_name=self.scheme_name,
                        token_issuer=claims["iss"],
                        token_subject=claims.get("sub"),
                        expected_issuer=self.server_cfg,
                    ).dumps()
                )
            return False
        return True

    def _decode_jwt_unverified(self, jwt_token: str) -> dict[str, Any]:
        """Decode jwt unverified."""
        return jwt.decode(jwt_token, options={"verify_signature": False})  # type: ignore[no-any-return]

    def retrieve_jwt_with_client_credentials_flow(
        self,
        scope: str,
        headers: dict[str, str] | None = None,
        max_retries: int | None = None,
        base_delay: float | None = None,
    ) -> str:
        """Call server to get token through OAuth Client Credentials flow."""
        # Parse input
        headers = dict(headers or self._client_credential_flow_request_headers)
        max_retries = max_retries or self._client_credential_flow_max_retries
        base_delay = base_delay or self._client_credential_flow_base_delay
        # Add basic auth header
        self._set_authorization_header(headers)
        # Get token endpoint URL
        url = self._get_token_endpoint()
        # Create request body
        token_data = self._generate_token_data(scope)
        # Call server with retries
        return self._request_token_with_retries(
            headers, max_retries, base_delay, url, token_data
        )

    def _request_token_with_retries(
        self,
        headers: dict[str, str],
        max_retries: int,
        base_delay: float,
        url: str,
        token_data: str,
    ) -> str:
        """Request token with retries."""
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
            if attempt < max_retries:
                time.sleep(base_delay)

        self._log_failed_token_retrieval_attempts(max_retries)
        raise exc.ServiceUnavailableError(
            "721b8f82",
            f"Token retrieval failed for server {self.server_cfg.name}: {last_exception}",
        )

    def _log_failed_token_retrieval_attempts(self, max_retries: int) -> None:
        """Log failed token retrieval attempts."""
        if self.logger:
            self.logger.error(
                self._log_item_class(
                    code="f8a3d7b2",
                    msg=f"OAuth Client Credentials flow token retrieval failed after {max_retries + 1} attempts for server {self.server_cfg.name}",
                    scheme_name=self.scheme_name,
                ).dumps()
            )

    def _generate_token_data(self, scope: str) -> str:
        """Helper method to build token data / request body for client credentials flow."""
        token_data: str = "&".join(
            (
                "grant_type=client_credentials",
                f"scope={urllib.parse.quote(scope)}",
            )
        )

        return token_data

    def _set_authorization_header(self, headers: dict[str, str]) -> None:
        """Set authorization header."""
        headers["Authorization"] = (
            "Basic "
            + base64.b64encode(
                f"{self.server_cfg.client_id}:{self.server_cfg.client_secret}".encode()
            ).decode()
        )

    def _get_token_endpoint(self) -> str:
        """Return token endpoint."""
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
            raise exc.ServiceUnavailableError(
                "3266c09e", "Token endpoint URL is not set"
            )
        return url

    def get_claims_from_userinfo(self, access_token: str) -> dict[str, Any]:
        """Return claims from userinfo."""
        userinfo_endpoint = self.server_cfg.userinfo_endpoint
        assert userinfo_endpoint is not None
        try:
            with httpx.Client(verify=self.ssl_context) as client:
                response = client.get(
                    userinfo_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                return self._validate_claims_from_userinfo(userinfo_endpoint, response)
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

    def _validate_claims_from_userinfo(
        self, userinfo_endpoint: str, response: httpx.Response
    ) -> dict[str, Any]:
        """Validate claims from userinfo."""
        claims: dict[str, Any] = json.loads(response.content)
        if (
            not isinstance(claims, dict) or "error" in claims  # type: ignore[unreachable]
        ):
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
            raise exc.ServiceUnavailableError("6053aea9")
        return claims

    def get_identity_provider(self) -> IdentityProvider:
        """Return identity provider."""
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
        """Load keys."""
        jwks_uri = self.server_cfg.jwks_uri
        assert jwks_uri is not None
        try:
            with httpx.Client(verify=self.ssl_context, timeout=30.0) as client:
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
            raise exc.ServiceUnavailableError("611dcc58") from exception

        # verify keys
        self._signing_keys = {}
        for key_data in response_dict["keys"]:
            if key_data.get("use") in ["sig"] and key_data.get("kty") == "RSA":
                self._signing_keys[key_data["kid"]] = jwt.PyJWK.from_dict(key_data)

    def _log_auth_error(self, exception: exc.AuthException) -> None:
        """Log auth error."""
        if self.logger:
            self.logger.warning(
                self._log_item_class(
                    code="ac521d94",
                    msg="Error retrieving claims from JWT",
                    scheme_name=self.scheme_name,
                    exception=exception,
                ).dumps()
            )

    def _log_unsupported_authorization_scheme(self, scheme: str) -> None:
        """Log unsupported authorization scheme."""
        if self.logger:
            self.logger.warning(
                self._log_item_class(
                    code="ecb88df4",
                    msg=f"Authorization scheme {scheme} not implemented",
                    scheme_name=self.scheme_name,
                ).dumps()
            )

    def _log_missing_authorization_header(self) -> None:
        """Log missing authorization header."""
        if self.logger:
            self.logger.warning(
                self._log_item_class(
                    code="e1dad160",
                    msg="No authorisation information provided in header",
                    scheme_name=self.scheme_name,
                ).dumps()
            )

    def _parse_authorization_header(self, request: Request) -> tuple[str, str] | None:
        """Parse authorization header."""
        if authorization := request.headers.get("authorization"):
            scheme, token = get_authorization_scheme_param(authorization)
            return (scheme, token)
        return None

    async def __call__(self, request: Request) -> Claims | None:  # type: ignore
        """Retrieve verified claims for the user based on the request."""
        authorization_header = self._parse_authorization_header(request)
        if not authorization_header:
            self._log_missing_authorization_header()
            return None
        scheme, token = authorization_header
        if scheme.upper() != "BEARER":
            self._log_unsupported_authorization_scheme(scheme)
            return None
        try:
            claims = await self.get_claims_from_jwt(token)
            return (
                Claims(claims=claims, scheme=scheme, token=token, idp_client_id=self.id)
                if claims
                else None
            )
        except exc.AuthException as exception:
            self._log_auth_error(exception)
            return None

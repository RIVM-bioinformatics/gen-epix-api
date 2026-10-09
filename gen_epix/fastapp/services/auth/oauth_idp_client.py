"""OAuth and OpenID Connect identity-provider client."""

import json
import logging
import ssl
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
from gen_epix.fastapp.services.auth.oauth_token_client import OauthTokenClient
from gen_epix.fastapp.services.auth.token_introspection_manager import (
    TokenIntrospectionManager,
)


class OauthIdpClient(OauthTokenClient, IdpClient, OpenIdConnect):
    """Encapsulates OAuth identity-provider client that validates and obtains tokens.

    Obtaining tokens is inherited from ``OauthTokenClient``; this class adds the
    server-side validation of incoming tokens as a FastAPI security scheme.
    """

    DEFAULT_INTROSPECTION_REQUEST_HEADERS: dict[str, str] = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    DEFAULT_INTROSPECTION_AUTH_METHOD: str = "client_secret_basic"
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
        # Initialize the bases explicitly: OauthTokenClient has its own standalone
        # initializer and OpenIdConnect is only used for its security scheme
        IdpClient.__init__(
            self,
            issuer,
            token_name=token_name or self.DEFAULT_TOKEN,
            id=id,
            ssl_context=ssl_context,
            **kwargs,
        )

        # Set input properties
        self._init_token_client(
            server_cfg,
            logger=logger,
            log_item_class=log_item_class,
            client_credential_flow_request_headers=client_credential_flow_request_headers,
            client_credential_flow_max_retries=client_credential_flow_max_retries,
            client_credential_flow_base_delay=client_credential_flow_base_delay,
        )
        self._signing_keys: dict[str, jwt.PyJWK] = {}
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

    async def get_jwk_from_jwt(self, jwt_token: str) -> jwt.PyJWK:
        """Return the signing key identified by a JWT.

        Raises:
            UnauthorizedAuthError: If the token has no key ID or its key is unknown.
            InitializationServiceError: If signing keys cannot be loaded.
        """
        key_id = self._parse_kid(jwt_token)
        if not key_id:
            if self.logger:
                self.logger.warning(
                    self._log_item_class(
                        code="0184bc35",
                        msg="No key ID found in token header",
                        scheme_name=self.scheme_name,
                    ).dumps()
                )
            raise exc.UnauthorizedAuthError("d3d0bb67")

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
                        exception=e,
                    ).dumps()
                )
            raise exc.UnauthorizedAuthError("5bb8ffb6") from e

    async def get_claims_from_jwt(self, jwt_token: str) -> dict[str, Any] | None:
        """Return validated claims from a JWT, or ``None`` for an untrusted issuer.

        Raises:
            CredentialsAuthError: If the JWT header is malformed.
            UnauthorizedAuthError: If the token cannot be verified or lacks required
                claims.
            InitializationServiceError: If signing keys cannot be loaded.
        """
        try:
            jwt.get_unverified_header(jwt_token)
        except jwt.PyJWTError as exception:
            raise exc.CredentialsAuthError(
                "f6ec5507", http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            ) from exception
        key = await self.get_jwk_from_jwt(jwt_token)

        claims = self._verify_token(jwt_token, key)
        if not self._validate_issuer(claims):
            return None
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
                options={
                    "require": ["iss"],
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

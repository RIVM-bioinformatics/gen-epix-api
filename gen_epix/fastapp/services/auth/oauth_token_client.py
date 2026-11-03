"""OAuth client for obtaining tokens from an identity provider."""

import base64
import logging
import math
import ssl
import time
import urllib.parse
from typing import Any

import httpx

from gen_epix.fastapp import exc
from gen_epix.fastapp.log import BaseLogItem, LogItem
from gen_epix.fastapp.services.auth.model import OidcServerCfg


class OauthTokenClient:
    """Encapsulates obtaining tokens from an OAuth identity provider.

    This is the outbound half of the OAuth integration: it resolves the provider
    configuration from its discovery document and retrieves tokens through the
    Client Credentials flow. It has no dependency on the web framework, so that
    it can be used by a client that only calls a remote application.
    ``OauthIdpClient`` extends it with the validation of incoming tokens.
    """

    DEFAULT_CLIENT_CREDENTIAL_FLOW_REQUEST_HEADERS: dict[str, str] = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    DEFAULT_CLIENT_CREDENTIAL_FLOW_MAX_RETRIES: int = 3
    DEFAULT_CLIENT_CREDENTIAL_FLOW_BASE_DELAY: float = 1.0  # in seconds

    # Name under which this provider appears in log messages
    scheme_name: str

    def __init__(
        self,
        server_cfg: OidcServerCfg,
        logger: logging.Logger | None = None,
        log_item_class: type[BaseLogItem] = LogItem,
        discovery_url: str | None = None,
        discovery_doc: dict[str, Any] | None = None,
        ssl_context: ssl.SSLContext | bool = True,
        client_credential_flow_request_headers: dict[str, str] | None = None,
        client_credential_flow_max_retries: int | None = None,
        client_credential_flow_base_delay: float | None = None,
    ):
        """Initialize a OauthTokenClient instance."""
        self.ssl_context = ssl_context
        self._init_token_client(
            server_cfg,
            logger=logger,
            log_item_class=log_item_class,
            client_credential_flow_request_headers=client_credential_flow_request_headers,
            client_credential_flow_max_retries=client_credential_flow_max_retries,
            client_credential_flow_base_delay=client_credential_flow_base_delay,
        )
        # The issuer may only become known from the discovery document
        self.scheme_name = self.server_cfg.issuer or ""
        self.update_server_config_from_discovery(url=discovery_url, doc=discovery_doc)
        if not self.scheme_name:
            self.scheme_name = self.server_cfg.issuer or ""

    def _init_token_client(
        self,
        server_cfg: OidcServerCfg,
        logger: logging.Logger | None,
        log_item_class: type[BaseLogItem],
        client_credential_flow_request_headers: dict[str, str] | None,
        client_credential_flow_max_retries: int | None,
        client_credential_flow_base_delay: float | None,
    ) -> None:
        """Set the properties needed for discovery and token retrieval.

        Shared with subclasses that have their own initializer. ``ssl_context`` and
        ``scheme_name`` are set by the caller.
        """
        self.server_cfg = server_cfg.model_copy()
        self.logger = logger
        self._log_item_class = log_item_class
        self._client_credential_flow_request_headers = (
            client_credential_flow_request_headers
            or self.DEFAULT_CLIENT_CREDENTIAL_FLOW_REQUEST_HEADERS
        )
        self._client_credential_flow_max_retries = (
            self.DEFAULT_CLIENT_CREDENTIAL_FLOW_MAX_RETRIES
            if client_credential_flow_max_retries is None
            else client_credential_flow_max_retries
        )
        self._client_credential_flow_base_delay = (
            self.DEFAULT_CLIENT_CREDENTIAL_FLOW_BASE_DELAY
            if client_credential_flow_base_delay is None
            else client_credential_flow_base_delay
        )

    def update_server_config_from_discovery(
        self,
        url: str | None = None,
        doc: dict[str, Any] | None = None,
    ) -> None:
        """Update OIDC configuration from a discovery URL or document.

        Raises:
            InitializationServiceError: If discovery data is missing, unavailable, or
                invalid.
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

    def retrieve_jwt_with_client_credentials_flow(
        self,
        scope: str,
        headers: dict[str, str] | None = None,
        max_retries: int | None = None,
        base_delay: float | None = None,
    ) -> str:
        """Call server to get token through OAuth Client Credentials flow."""
        token, _ = self.retrieve_jwt_with_client_credentials_flow_and_expiry(
            scope, headers, max_retries, base_delay
        )
        return token

    def retrieve_jwt_with_client_credentials_flow_and_expiry(
        self,
        scope: str,
        headers: dict[str, str] | None = None,
        max_retries: int | None = None,
        base_delay: float | None = None,
    ) -> tuple[str, float | None]:
        """Return an OAuth access token and its advertised lifetime in seconds."""
        # Parse input
        headers = dict(headers or self._client_credential_flow_request_headers)
        if max_retries is None:
            max_retries = self._client_credential_flow_max_retries
        if base_delay is None:
            base_delay = self._client_credential_flow_base_delay
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
    ) -> tuple[str, float | None]:
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
                    expires_in = token_response.get("expires_in")
                    if isinstance(expires_in, bool) or not isinstance(
                        expires_in, (int, float)
                    ):
                        expires_in = None
                    try:
                        expires_in = (
                            float(expires_in) if expires_in is not None else None
                        )
                    except OverflowError:
                        expires_in = None
                    if expires_in is not None and not math.isfinite(expires_in):
                        expires_in = None
                    return token, expires_in
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

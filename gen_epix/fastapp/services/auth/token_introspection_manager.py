"""Token introspection and validation support."""

import base64
import datetime
import logging
import ssl
import urllib.parse
from typing import Any, TypedDict

import httpx

from gen_epix.fastapp import exc
from gen_epix.fastapp.log import BaseLogItem, LogItem
from gen_epix.fastapp.services.auth.model import OidcServerCfg


class TokenIntrospectionManager:
    """Provide the token introspection manager framework abstraction."""

    DEFAULT_INTROSPECTION_REQUEST_HEADERS: dict[str, str] = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    DEFAULT_INTROSPECTION_AUTH_METHOD: str = "client_secret_basic"
    DEFAULT_INTROSPECTION_TIMEOUT_SECONDS: int = 2
    DEFAULT_INTROSPECTION_INTERVAL_SECONDS: int = 300
    INTROSPECTION_ENDPOINT_TTL: int = 30 * 60  # 30 minutes in seconds

    def __init__(
        self,
        server_cfg: OidcServerCfg,
        discovery_url: str,
        ssl_context: ssl.SSLContext | bool,
        introspect_token_request_headers: dict[str, str] | None = None,
        introspection_auth_method: str | None = None,
        introspection_timeout_seconds: int | None = None,
        introspection_interval_seconds: int | None = None,
        log_item_class: type[BaseLogItem] = LogItem,
        logger: logging.Logger | None = None,
    ):
        """Initialize the instance."""
        self.server_cfg = server_cfg.model_copy()
        self.discovery_url = discovery_url
        self.ssl_context = ssl_context
        self.logger = logger
        self._log_item_class = log_item_class
        self._introspect_token_request_headers = (
            introspect_token_request_headers
            or self.DEFAULT_INTROSPECTION_REQUEST_HEADERS
        )
        self._introspection_auth_method = (
            introspection_auth_method or self.DEFAULT_INTROSPECTION_AUTH_METHOD
        ).lower()
        self._introspection_timeout_seconds = (
            introspection_timeout_seconds or self.DEFAULT_INTROSPECTION_TIMEOUT_SECONDS
        )
        self._introspection_interval_seconds = (
            introspection_interval_seconds
            or self.DEFAULT_INTROSPECTION_INTERVAL_SECONDS
        )
        self._validate_introspection_interval()
        self._validate_discovery_url()

        class IntrospectionCacheEntry(TypedDict):
            """Provide the introspection cache entry framework abstraction."""

            active: bool | None
            last_checked: int
            exp: int

        class IntrospectionEndpointRetrievalCacheEntry(TypedDict):
            """Provide the introspection endpoint retrieval cache entry framework abstraction."""

            endpoint: str | None
            last_checked: int

        self._introspection_cache: dict[str, IntrospectionCacheEntry] = {}
        self._introspection_endpoint_cache: IntrospectionEndpointRetrievalCacheEntry = {
            "endpoint": None,
            "last_checked": 0,
        }

    def _validate_introspection_interval(self) -> None:
        """Perform the  validate introspection interval operation."""
        if self._introspection_interval_seconds > 1800:
            raise ValueError(
                "introspection_interval_seconds cannot be more than 1800 seconds (30 minutes)"
            )

    def _validate_discovery_url(self) -> None:
        """Perform the  validate discovery url operation."""
        if self.discovery_url.strip() == "":
            raise ValueError("discovery_url cannot be empty for token introspection")

    def _now(self) -> int:
        """Perform the  now operation."""
        return int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    def _fetch_introspection_endpoint(self) -> str:
        """Perform the  fetch introspection endpoint operation."""
        try:
            with httpx.Client(verify=self.ssl_context) as client:
                response = client.get(self.discovery_url)
                discovery_doc = response.json()
            introspection_endpoint: str = discovery_doc.get("introspection_endpoint")
            return introspection_endpoint
        except Exception as exception:
            if self.logger:
                self.logger.error(
                    self._log_item_class(
                        code="d1234abc",
                        msg="Error accessing discovery URL to determine introspection endpoint",
                        exception=exception,
                    ).dumps()
                )
            raise exc.UnauthorizedAuthError(
                "114cbc68", http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            ) from exception

    def _get_cached_introspection_endpoint(self) -> str:
        """Perform the  get cached introspection endpoint operation."""
        now = self._now()
        endpoint = self._introspection_endpoint_cache.get("endpoint")
        last_checked = self._introspection_endpoint_cache.get("last_checked", 0)
        if endpoint and (now - last_checked) < self.INTROSPECTION_ENDPOINT_TTL:
            return endpoint
        # fetch fresh and update cache; let exceptions propagate to caller
        endpoint = self._fetch_introspection_endpoint()
        self._introspection_endpoint_cache = {
            "endpoint": endpoint,
            "last_checked": now,
        }
        return endpoint

    def introspect_token(self, jwt_token: str, claims: dict[str, Any]) -> None:
        """Perform the introspect token operation."""
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
                "cd6f91e8", http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            )
        if self._is_recheck_introspection(jwt_token, now):
            if self.logger:
                self.logger.info(
                    self._log_item_class(
                        code="9deaa6b2", msg="Performing token introspection re-check"
                    ).dumps()
                )
            is_active = self._introspect_token_with_server(jwt_token)
            if is_active is None:
                raise exc.CredentialsAuthError(
                    "026ae562", http_props={"headers": {"WWW-Authenticate": "Bearer"}}
                )
            exp_val = int(claims.get("exp", now))
            if is_active:
                self._update_introspection_cache(jwt_token, True, exp_val, now)
            else:
                self._update_introspection_cache(jwt_token, False, exp_val, now)
                if self.logger:
                    self.logger.warning(
                        self._log_item_class(
                            code="b1c2d3e4",
                            msg="Token marked inactive by introspection; denying",
                        ).dumps()
                    )
                raise exc.CredentialsAuthError(
                    "e36c7738", http_props={"headers": {"WWW-Authenticate": "Bearer"}}
                )

    def _prune_expired_introspection_cache(self, now: int | None = None) -> None:
        """Perform the  prune expired introspection cache operation."""
        time_stamp = now or self._now()
        expired_keys = [
            x for x, y in self._introspection_cache.items() if y["exp"] <= time_stamp
        ]
        for x in expired_keys:
            self._introspection_cache.pop(x, None)

    def _is_cached_introspection_token_inactive(self, jwt_token: str) -> bool:
        """Perform the  is cached introspection token inactive operation."""
        introspection_token = self._introspection_cache.get(jwt_token)
        return bool(introspection_token and introspection_token.get("active") is False)

    def _is_recheck_introspection(self, jwt_token: str, now: int | None = None) -> bool:
        """Perform the  is recheck introspection operation."""
        introspection_token = self._introspection_cache.get(jwt_token)
        if not introspection_token:
            return True
        last = int(introspection_token.get("last_checked", 0))
        time_stamp = now or self._now()
        return (time_stamp - last) >= self._introspection_interval_seconds

    def _update_introspection_cache(
        self, jwt_token: str, active: bool | None, exp: int, now: int | None = None
    ) -> None:
        """Perform the  update introspection cache operation."""
        self._introspection_cache[jwt_token] = {
            "active": active,
            "last_checked": now or self._now(),
            "exp": exp,
        }

    def _introspect_token_with_server(self, jwt_token: str) -> bool | None:
        """Perform the  introspect token with server operation."""
        endpoint = self._get_cached_introspection_endpoint()
        if not endpoint:
            return None
        headers = dict(self._introspect_token_request_headers)
        data: str = "&".join(
            (f"token={urllib.parse.quote(jwt_token)}", f"token_type_hint=access_token")
        )
        if self._introspection_auth_method not in {
            "client_secret_basic",
            "client_secret_post",
        }:
            if self.logger:
                self.logger.warning(
                    self._log_item_class(
                        code="6f4a8e22",
                        msg="Unknown introspection auth method; defaulting to client_secret_basic",
                        method=self._introspection_auth_method,
                    ).dumps()
                )
            self._introspection_auth_method = "client_secret_basic"
        if self._introspection_auth_method == "client_secret_basic":
            headers["Authorization"] = (
                "Basic "
                + base64.b64encode(
                    f"{self.server_cfg.client_id}:{self.server_cfg.client_secret}".encode()
                ).decode()
            )
        try:
            with httpx.Client(
                verify=self.ssl_context, timeout=self._introspection_timeout_seconds
            ) as client:
                response = client.post(endpoint, data=data, headers=headers)
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
                    "e042bbc2", http_props={"headers": {"WWW-Authenticate": "Bearer"}}
                )
            payload = response.json()
            active = payload.get("active")
            if isinstance(active, bool):
                return active
            return None
        except Exception as exc_:
            if self.logger:
                self.logger.warning(
                    self._log_item_class(
                        code="f2b3c9aa",
                        msg=("Token introspection failed (timeout/network/parse)"),
                        exception=exc_,
                    ).dumps()
                )
            raise exc.UnauthorizedAuthError(
                "f73f7db5", http_props={"headers": {"WWW-Authenticate": "Bearer"}}
            ) from exc_

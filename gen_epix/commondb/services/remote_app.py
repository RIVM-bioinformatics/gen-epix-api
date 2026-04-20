import importlib
from datetime import datetime, timezone
from enum import Enum
from logging import Logger
from typing import Any

import jwt

from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain import enum, model
from gen_epix.fastapp import HttpProtocol, RemoteApp, exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import AuthProtocol, OAuthFlow
from gen_epix.fastapp.log import LogItem
from gen_epix.fastapp.model import Command
from gen_epix.fastapp.services.auth.model import OidcServerCfg
from gen_epix.fastapp.services.auth.oauth_idp_client import OauthIdpClient


class CommondbRemoteApp(RemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    ROUTE_MAP: dict[type[Command], str] = {}

    def __init__(
        self,
        domain: Domain,
        host: str,
        port: int | None,
        protocol: HttpProtocol = HttpProtocol.HTTPS,
        default_route_prefix: str | None = None,
        default_headers: dict[str, str] | None = None,
        ssl_cert_file: str | None = None,
        auth_protocol: AuthProtocol | str = AuthProtocol.NONE,
        oauth_flow: OAuthFlow | str | None = None,
        oauth_discovery_url: str | None = None,
        oauth_client_id: str | None = None,
        oauth_client_secret: str | None = None,
        oauth_scope: str | None = None,
        oauth_token_endpoint: str | None = None,
        oauth_token_refresh_margin: float | None = None,
        logger: Logger | None = None,
        log_item_class: type[LogItem] = LogItem,
        **kwargs: Any,
    ) -> None:
        if isinstance(auth_protocol, str):
            auth_protocol = AuthProtocol(auth_protocol)
        if isinstance(oauth_flow, str):
            oauth_flow = OAuthFlow(oauth_flow)
        default_route_prefix = default_route_prefix or self.DEFAULT_ROUTE_PREFIX
        oauth_token_refresh_margin = (
            oauth_token_refresh_margin or self.DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN
        )

        super().__init__(
            domain,
            host,
            port,
            protocol=protocol,
            default_route_prefix=default_route_prefix,
            default_headers=default_headers,
            add_generated_crud_route_handlers=True,
            ssl_cert_file=ssl_cert_file,
            **kwargs,
        )

        # Initialize IDP client if needed
        oauth_idp_client: OauthIdpClient | None = None
        if auth_protocol == AuthProtocol.NONE:
            pass
        elif auth_protocol == AuthProtocol.OAUTH2:
            if oauth_discovery_url is None:
                raise exc.InitializationServiceError(
                    "a1ad2a89",
                    "OAuth discovery endpoint must be provided for OAUTH2 auth protocol",
                )
            if oauth_client_id is None:
                raise exc.InitializationServiceError(
                    "47f9dfe6",
                    "OAuth client ID must be provided for OAUTH2 auth protocol",
                )
            if oauth_scope is None:
                raise exc.InitializationServiceError(
                    "683cf2a0", "OAuth scope must be provided for OAUTH2 auth protocol"
                )
            oauth_idp_client = OauthIdpClient(
                server_cfg=OidcServerCfg(
                    name="",
                    label="",
                    discovery_url=oauth_discovery_url,
                    client_id=oauth_client_id,
                    client_secret=oauth_client_secret,
                    token_endpoint=oauth_token_endpoint,
                    scope=oauth_scope,
                ),
                ssl_context=self.ssl_context,
                logger=logger,
                log_item_class=log_item_class,
            )
        else:
            raise exc.InitializationServiceError(
                "5a7ed32f", f"Auth protocol {auth_protocol} not supported"
            )
        self._auth_protocol = auth_protocol
        self._oauth_flow = oauth_flow
        self._oauth_idp_client = oauth_idp_client
        self._oauth_scope = oauth_scope
        self._oauth_token_refresh_margin = oauth_token_refresh_margin
        self._oauth_header_cache: tuple[int, dict[str, str]] | None = None

    def get_headers(self, cmd: Command) -> dict[str, str]:
        # Call identity provider to get JWT
        if self._auth_protocol == AuthProtocol.NONE:
            return self._default_headers
        if self._auth_protocol == AuthProtocol.OAUTH2:
            assert self._oauth_idp_client is not None
            assert self._oauth_scope is not None
            # Check if cached token is still valid
            if self._oauth_header_cache and self._oauth_header_cache[0] > (
                datetime.now(timezone.utc).timestamp()
                - self._oauth_token_refresh_margin
            ):
                # Return cached header
                return self._oauth_header_cache[1]
            # Retrieve new token

            jwt_token = (
                self._oauth_idp_client.retrieve_jwt_with_client_credentials_flow(
                    scope=self._oauth_scope
                )
            )
            # Create headers
            headers = dict(self._default_headers)
            headers["Authorization"] = f"Bearer {jwt_token}"
            # Put header in cache together with its expiry time
            claims = jwt.decode(jwt_token, options={"verify_signature": False})
            exp: int | None = claims.get("exp")
            if exp is None:
                # No expiration claim, valid forever
                self._oauth_header_cache = (int(datetime.max.timestamp()), headers)
            else:
                self._oauth_header_cache = (exp, headers)
            return headers
        raise exc.InitializationServiceError(
            "7bf9fe04",
            f"Auth protocol {self._auth_protocol.value} not supported for token retrieval",
        )

    @staticmethod
    def create_local_or_remote_app(
        app_type: enum.AppType,
        app_setup_type: str,  # "LOCAL" or "REMOTE"
        local_app_props: dict[str, Any] | None = None,
        remote_app_props: dict[str, Any] | None = None,
        app_composer_class: type | None = None,
        user_class: type[model.User] | None = None,
        service_type_enum: type[Enum] | None = None,
        repository_type_enum: type[Enum] | None = None,
        logger: Logger | None = None,
    ) -> tuple[App, model.User | None]:
        # Parse input
        app_setup_type = app_setup_type.upper()
        if app_setup_type not in ("LOCAL", "REMOTE"):
            raise exc.InitializationServiceError(
                "2ceb9c7c",
                f"Invalid app_setup_type: {app_setup_type}. Must be 'LOCAL' or 'REMOTE'.",
            )
        # Create local or remote app
        app: App
        user: user_class | None  # pyright: ignore[reportInvalidTypeForm]
        if app_setup_type == "LOCAL":
            # Parse local app props
            app, user = CommondbRemoteApp._create_local_app(
                app_type,
                local_app_props,
                app_composer_class,
                user_class,
                service_type_enum,
                repository_type_enum,
                logger,
            )
        elif app_setup_type == "REMOTE":
            # Parse remote app props
            app, user = CommondbRemoteApp._create_remote_app(remote_app_props)
        else:
            raise exc.InitializationServiceError(
                "84a87605",
                f"Invalid app_setup_type: {app_setup_type}. Must be 'LOCAL' or 'REMOTE'.",
            )
        return app, user

    @staticmethod
    def _create_local_app(
        app_type: enum.AppType,
        local_app_props: dict[str, Any] | None,
        app_composer_class: type | None,
        user_class: type[model.User] | None,
        service_type_enum: type[Enum] | None,
        repository_type_enum: type[Enum] | None,
        logger: Logger | None = None,
    ) -> tuple[App, model.User]:
        if (
            local_app_props is None
            or app_composer_class is None
            or user_class is None
            or service_type_enum is None
            or repository_type_enum is None
        ):
            raise exc.InitializationServiceError(
                "6451025d",
                "local_app_props, app_composer_class, user_class, service_type_enum, and repository_type_enum must be provided for LOCAL app setup.",
            )
        if "user" not in local_app_props:
            raise exc.InitializationServiceError(
                "80bc4360",
                "local_app_props must contain 'user' key for LOCAL app setup.",
            )
            # Get app config
        if "app_cfg" in local_app_props:
            app_cfg = local_app_props.pop("app_cfg")
        else:
            app_cfg = AppCfg(app_type, service_type_enum, repository_type_enum)
        log_setup = local_app_props.get("log_setup", logger is not None)
        # Create local app and user
        app_composer = app_composer_class(app_cfg, log_setup=log_setup)
        app = app_composer.app
        user = user_class(**local_app_props["user"])

        return app, user

    @staticmethod
    def _create_remote_app(remote_app_props: dict[str, Any] | None) -> tuple[App, None]:
        if remote_app_props is None:
            raise exc.InitializationServiceError(
                "4007b438", "remote_app_props must be provided for REMOTE app setup."
            )
        if "module" not in remote_app_props or "class_name" not in remote_app_props:
            raise exc.InitializationServiceError(
                "0c268454",
                "remote_app_props must contain 'module' and 'class_name' keys for REMOTE app setup.",
            )
            # Create remote app
        remote_app_module = remote_app_props.pop("module")
        remote_app_class_name = remote_app_props.pop("class_name")
        remote_app_class = getattr(
            importlib.import_module(remote_app_module), remote_app_class_name
        )
        app = remote_app_class(**remote_app_props)
        # No user for remote app, this is handled via authentication to the actual remote service
        user = None
        return app, user

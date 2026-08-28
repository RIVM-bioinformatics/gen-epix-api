import importlib
from datetime import datetime, timezone
from enum import Enum
from logging import Logger
from typing import Any, Literal

import jwt

from gen_epix.commondb import api
from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain import command, enum, model
from gen_epix.fastapp import HttpProtocol, RemoteApp, exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import AuthProtocol, HttpMethod, OAuthFlow
from gen_epix.fastapp.log import LogItem
from gen_epix.fastapp.model import Command, Permission
from gen_epix.fastapp.services.auth.model import OidcServerCfg
from gen_epix.fastapp.services.auth.oauth_idp_client import OauthIdpClient


class CommondbRemoteApp(RemoteApp):
    """Remote app client for the commondb service with OAuth2/NONE authentication."""

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    DEFAULT_HTTP_TIMEOUTS: dict[type[Command], float] = {}

    ROUTE_MAP: dict[type[Command], str] = {
        command.GetIdentityProvidersCommand: "/identity_providers",
        command.InviteUserCommand: "/invite_user",
        command.RetrieveInviteUserConstraintsCommand: "/invite_user/constraints",
        command.RegisterInvitedUserCommand: "/user_registrations",
        command.OrganizationSetOrganizationUpdateAssociationCommand: "/organization_sets",
        command.DataCollectionSetDataCollectionUpdateAssociationCommand: (
            "/data_collection_sets"
        ),
        command.RetrieveOwnPermissionsCommand: "/user_me/permissions",
        command.AnonymizeUserCommand: "/user",
        command.UpdateUserCommand: "/update_user",
        command.UpdateUserOwnOrganizationCommand: "/update_user_own_organization",
        command.OrganizationIdentifierIssuerUpdateAssociationCommand: (
            "/organizations"
        ),
        command.RetrieveOrganizationContactsCommand: "/retrieve/organization_contacts",
        command.RetrieveOrganizationAdminNameEmailsCommand: (
            "/retrieve_organization_admin_name_emails"
        ),
        command.RetrieveFeatureFlagsCommand: "/retrieve/feature_flags",
        command.RetrieveLicensesCommand: "/retrieve/licenses",
        command.RetrieveOutagesCommand: "/retrieve/outages",
    }

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
        jwks_uri: str | None = None,
        oauth_client_id: str | None = None,
        oauth_client_secret: str | None = None,
        oauth_scope: str | None = None,
        oauth_token_endpoint: str | None = None,
        oauth_token_refresh_margin: float | None = None,
        logger: Logger | None = None,
        log_item_class: type[LogItem] = LogItem,
        **kwargs: Any,
    ) -> None:
        """Initialize with connection and authentication settings; register all commondb handlers."""
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

        # Register routes. CommondbRemoteApp.ROUTE_MAP is referenced explicitly
        # (not self.ROUTE_MAP) because subclasses override ROUTE_MAP with their
        # own dict rather than merging it, so self.ROUTE_MAP would resolve to the
        # subclass's dict here and cause double registration in its own __init__.
        for cmd_class, route in CommondbRemoteApp.ROUTE_MAP.items():
            self.register_route(cmd_class, route)
        # Register handlers
        self.register_handler(
            command.GetIdentityProvidersCommand, self.get_identity_providers
        )
        self.register_handler(command.InviteUserCommand, self.invite_user)
        self.register_handler(
            command.RetrieveInviteUserConstraintsCommand,
            self.retrieve_invite_user_constraints,
        )
        self.register_handler(
            command.RegisterInvitedUserCommand, self.register_invited_user
        )
        self.register_handler(
            command.OrganizationSetOrganizationUpdateAssociationCommand,
            self.organization_set_organization_update_association,
        )
        self.register_handler(
            command.DataCollectionSetDataCollectionUpdateAssociationCommand,
            self.data_collection_set_data_collection_update_association,
        )
        self.register_handler(
            command.RetrieveOwnPermissionsCommand, self.retrieve_own_permissions
        )
        self.register_handler(command.AnonymizeUserCommand, self.anonymize_user)
        self.register_handler(command.UpdateUserCommand, self.update_user)
        self.register_handler(
            command.UpdateUserOwnOrganizationCommand,
            self.update_user_own_organization,
        )
        self.register_handler(
            command.OrganizationIdentifierIssuerUpdateAssociationCommand,
            self.organization_identifier_issuer_link_update_association,
        )
        self.register_handler(
            command.RetrieveOrganizationContactsCommand,
            self.retrieve_organization_contacts,
        )
        self.register_handler(
            command.RetrieveOrganizationAdminNameEmailsCommand,
            self.retrieve_organization_admin_name_emails,
        )
        self.register_handler(
            command.RetrieveFeatureFlagsCommand, self.retrieve_feature_flags
        )
        self.register_handler(command.RetrieveLicensesCommand, self.retrieve_licenses)
        self.register_handler(command.RetrieveOutagesCommand, self.retrieve_outages)

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
                    jwks_uri=jwks_uri,
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
        """Return auth headers, retrieving a fresh OAuth token when needed."""
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

    # --- Non-CRUD command handlers ---

    def get_identity_providers(
        self, cmd: command.GetIdentityProvidersCommand
    ) -> list[model.IdentityProvider]:
        """Retrieve the list of configured identity providers."""
        response_body: list[dict[str, Any]] = self.request(cmd, HttpMethod.GET)  # type: ignore[assignment]
        return [model.IdentityProvider(**x) for x in response_body]

    def invite_user(self, cmd: command.InviteUserCommand) -> model.UserInvitation:
        """Send a user invitation request."""
        request_body = api.InviteUserRequestBody(
            key=cmd.key,
            description=cmd.description,
            roles=cmd.roles,
            organization_id=cmd.organization_id,
        )
        response_body: dict[str, Any] = self.request(
            cmd, HttpMethod.POST, model=request_body
        )  # type: ignore[assignment]
        return model.UserInvitation(**response_body)

    def retrieve_invite_user_constraints(
        self, cmd: command.RetrieveInviteUserConstraintsCommand
    ) -> model.UserInvitationConstraints:
        """Retrieve constraints that govern user invitations."""
        response_body: dict[str, Any] = self.request(cmd, HttpMethod.GET)  # type: ignore[assignment]
        return model.UserInvitationConstraints(**response_body)

    def register_invited_user(
        self, cmd: command.RegisterInvitedUserCommand
    ) -> model.User:
        """Register an invited user using their invitation token."""
        response_body: dict[str, Any] = self.request(
            cmd, HttpMethod.POST, route=f"{self.get_route(cmd)}/{cmd.token}"
        )  # type: ignore[assignment]
        return model.User(**response_body)

    def organization_set_organization_update_association(
        self, cmd: command.OrganizationSetOrganizationUpdateAssociationCommand
    ) -> list[model.OrganizationSetMember]:
        """Update the set of organizations associated with an organization set."""
        request_body = api.OrganizationSetOrganizationUpdateAssociationRequestBody(
            organization_set_members=cmd.association_objs
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.PUT,
            route=f"{self.get_route(cmd)}/{cmd.obj_id1}/organizations",
            model=request_body,
        )
        return [model.OrganizationSetMember(**x) for x in response_body]

    def data_collection_set_data_collection_update_association(
        self, cmd: command.DataCollectionSetDataCollectionUpdateAssociationCommand
    ) -> list[model.DataCollectionSetMember]:
        """Update the set of data collections associated with a data collection set."""
        request_body = api.DataCollectionSetDataCollectionUpdateAssociationRequestBody(
            data_collection_set_members=cmd.association_objs
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.PUT,
            route=f"{self.get_route(cmd)}/{cmd.obj_id1}/data_collections",
            model=request_body,
        )
        return [model.DataCollectionSetMember(**x) for x in response_body]

    def retrieve_own_permissions(
        self, cmd: command.RetrieveOwnPermissionsCommand
    ) -> set[Permission]:
        """Retrieve the set of permissions for the authenticated user."""
        response_body: list[dict[str, Any]] = self.request(cmd, HttpMethod.GET)  # type: ignore[assignment]
        return {Permission(**x) for x in response_body}

    def anonymize_user(self, cmd: command.AnonymizeUserCommand) -> None:
        """Anonymize a user's personal data."""
        self.request(
            cmd,
            HttpMethod.POST,
            route=f"{self.get_route(cmd)}/{cmd.tgt_user_id}/anonymize",
        )

    def update_user(self, cmd: command.UpdateUserCommand) -> model.User:
        """Update a user's active status, roles, or organization."""
        request_body = api.UpdateUserRequestBody(
            is_active=cmd.is_active,
            roles=cmd.roles,
            organization_id=cmd.organization_id,
        )
        response_body: dict[str, Any] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.PUT,
            route=f"{self.get_route(cmd)}/{cmd.tgt_user_id}",
            model=request_body,
        )
        return model.User(**response_body)

    def update_user_own_organization(
        self, cmd: command.UpdateUserOwnOrganizationCommand
    ) -> model.User:
        """Update the authenticated user's own organization."""
        request_body = api.UpdateUserOwnOrganizationRequestBody(
            organization_id=cmd.organization_id
        )
        response_body: dict[str, Any] = self.request(cmd, HttpMethod.PUT, model=request_body)  # type: ignore[assignment]
        return model.User(**response_body)

    def organization_identifier_issuer_link_update_association(
        self, cmd: command.OrganizationIdentifierIssuerUpdateAssociationCommand
    ) -> list[model.OrganizationIdentifierIssuerLink]:
        """Update identifier issuer links for an organization."""
        request_body = api.OrganizationIdentifierIssuerUpdateAssociationRequestBody(
            organization_identifier_issuer_links=cmd.association_objs
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.PUT,
            route=f"{self.get_route(cmd)}/{cmd.obj_id1}/identifier_issuers",
            model=request_body,
        )
        return [model.OrganizationIdentifierIssuerLink(**x) for x in response_body]

    def retrieve_organization_contacts(
        self, cmd: command.RetrieveOrganizationContactsCommand
    ) -> model.OrganizationContacts:
        """Retrieve contact information for an organization."""
        request_body = api.RetrieveOrganizationContactsRequestBody(
            organization_id=cmd.organization_id
        )
        response_body: dict[str, Any] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=request_body,
        )
        return model.OrganizationContacts(**response_body)

    def retrieve_organization_admin_name_emails(
        self, cmd: command.RetrieveOrganizationAdminNameEmailsCommand
    ) -> list[model.UserNameEmail]:
        """Retrieve name and email for organization admins."""
        response_body: list[dict[str, Any]] = self.request(cmd, HttpMethod.GET)  # type: ignore[assignment]
        return [model.UserNameEmail(**x) for x in response_body]

    def retrieve_feature_flags(
        self, cmd: command.RetrieveFeatureFlagsCommand
    ) -> dict[str, bool]:
        """Retrieve the current feature flag settings."""
        response_body: dict[Literal["feature_flags"], dict[str, bool]] = self.request(cmd, HttpMethod.GET)  # type: ignore[assignment]
        return response_body["feature_flags"]

    def retrieve_licenses(
        self, cmd: command.RetrieveLicensesCommand
    ) -> list[model.PackageMetadata]:
        """Retrieve metadata for installed packages."""
        response_body: list[dict[str, Any]] = self.request(cmd, HttpMethod.POST)  # type: ignore[assignment]
        return [model.PackageMetadata(**x) for x in response_body]

    def retrieve_outages(
        self, cmd: command.RetrieveOutagesCommand
    ) -> list[model.Outage]:
        """Retrieve current outage announcements."""
        response_body: list[dict[str, Any]] = self.request(cmd, HttpMethod.GET)  # type: ignore[assignment]
        return [model.Outage(**x) for x in response_body]

    @classmethod
    def create_local_or_remote_app(
        cls,
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
        """Create either a local or remote app instance based on setup type."""
        # Parse input
        app_setup_type = app_setup_type.upper()
        if app_setup_type not in ("LOCAL", "REMOTE"):
            raise exc.InitializationServiceError(
                "2ceb9c7c",
                f"Invalid app_setup_type: {app_setup_type}. Must be 'LOCAL' or 'REMOTE'.",
            )
        # Create local or remote app
        app: App
        user: user_class | None  # type: ignore[valid-type]
        if app_setup_type == "LOCAL":
            # Parse local app props
            app, user = cls._create_local_app(
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

    @classmethod
    def _create_local_app(
        cls,
        app_type: enum.AppType,
        local_app_props: dict[str, Any] | None,
        app_composer_class: type | None,
        user_class: type[model.User] | None,
        service_type_enum: type[Enum] | None,
        repository_type_enum: type[Enum] | None,
        logger: Logger | None = None,
    ) -> tuple[App, model.User]:
        """Instantiate a local app from configuration and a user definition."""
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

    @classmethod
    def _create_remote_app(
        cls, remote_app_props: dict[str, Any] | None
    ) -> tuple[App, None]:
        """Instantiate a remote app from a module path and class name."""
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
        remote_app_class: type[RemoteApp] = getattr(
            importlib.import_module(remote_app_module), remote_app_class_name
        )
        app = remote_app_class(**remote_app_props)
        for command_class, timeout in cls.DEFAULT_HTTP_TIMEOUTS.items():
            app.set_timeout(command_class, timeout)
        # No user for remote app, this is handled via authentication to the actual remote service
        user = None
        return app, user

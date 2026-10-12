"""Provide an HTTP command client for remote commondb applications.

The client dispatches mapped commondb commands under ``/v1`` and supports either
NONE-mode default headers or OAuth2 client-credentials authentication.
"""

import importlib
import math
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from logging import Logger
from typing import Any, ClassVar, Literal

import jwt

from gen_epix import fastapp
from gen_epix.commondb import api
from gen_epix.commondb.domain import command, enum, model, util
from gen_epix.fastapp import Client, HttpProtocol, exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import AuthProtocol, HttpMethod, OAuthFlow
from gen_epix.fastapp.log import LogItem
from gen_epix.fastapp.model import Command, Permission
from gen_epix.fastapp.services.auth.model import OidcServerCfg
from gen_epix.fastapp.services.auth.oauth_idp_client import OauthIdpClient

# Decode options for reading the ``exp`` claim of a token without verifying it
_UNVERIFIED_OPTIONS = {"verify_signature": False}


class CommondbClient(Client):
    """Encapsulates a remote app client for the commondb service with OAuth2/NONE authentication."""

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    DEFAULT_HTTP_TIMEOUTS: ClassVar[dict[type[Command], float]] = {}

    ROUTE_MAP: ClassVar[dict[type[Command], str]] = {
        command.DeleteAllOperationalDataCommand: "/operational_data",
        command.DeleteAllRefDataCommand: "/ref_data",
        command.GetIdentityProvidersCommand: "/identity_providers",
        command.InviteUserCommand: "/invite_user",
        command.RetrieveInviteUserConstraintsCommand: "/invite_user/constraints",
        command.RegisterInvitedUserCommand: "/user_registrations",
        command.OrganizationSetOrganizationUpdateAssociationCommand: "/organization_sets",
        command.DataCollectionSetDataCollectionUpdateAssociationCommand: (
            "/data_collection_sets"
        ),
        command.RetrieveOwnPermissionsCommand: "/user_me/permissions",
        command.RetrieveOwnUserCommand: "/user_me",
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
        token_provider: Callable[[], str] | None = None,
        logger: Logger | None = None,
        log_item_class: type[LogItem] = LogItem,
        **kwargs: Any,
    ) -> None:
        """Initialize remote commondb routes with connection and authentication settings.

        Args:
            domain: Domain defining supported remote command routes.
            host: Remote application host.
            port: Optional remote application port.
            protocol: HTTP protocol used for requests.
            default_route_prefix: Optional API route prefix.
            default_headers: Optional headers included with every request.
            ssl_cert_file: Optional CA certificate path.
            auth_protocol: None or OAuth2 authentication protocol.
            oauth_flow: Optional OAuth2 flow configuration.
            oauth_discovery_url: OAuth2 discovery endpoint.
            jwks_uri: Optional JSON Web Key Set endpoint.
            oauth_client_id: OAuth2 client identifier.
            oauth_client_secret: Optional OAuth2 client secret.
            oauth_scope: OAuth2 scope requested for client credentials.
            oauth_token_endpoint: Optional OAuth2 token endpoint override.
            oauth_token_refresh_margin: Seconds before expiry to refresh a token.
            token_provider: Optional callable returning a bearer token, used instead
                of the OAuth2 client-credentials flow, e.g. for a token of a human
                user. Must be combined with ``auth_protocol=NONE``. The token is
                cached until shortly before its ``exp`` claim; on a 401 response the
                cache is dropped, the provider is called again and the command is
                retried once.
            logger: Optional logger for identity-provider requests.
            log_item_class: Structured log item implementation.
            **kwargs: Additional remote application configuration.

        Raises:
            InitializationServiceError: If authentication settings are unsupported,
                required OAuth2 settings are missing, or ``token_provider`` conflicts
                with the OAuth2 settings or an ``Authorization`` default header.
        """
        self._check_token_provider(token_provider, auth_protocol, default_headers)
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

        # Register routes. CommondbClient.ROUTE_MAP is referenced explicitly
        # (not self.ROUTE_MAP) because subclasses override ROUTE_MAP with their
        # own dict rather than merging it, so self.ROUTE_MAP would resolve to the
        # subclass's dict here and cause double registration in its own __init__.
        for cmd_class, route in CommondbClient.ROUTE_MAP.items():
            self.register_route(cmd_class, route)
        # Register handlers
        self.register_handler(
            command.DeleteAllOperationalDataCommand, self.delete_all_operational_data
        )
        self.register_handler(command.DeleteAllRefDataCommand, self.delete_all_ref_data)
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
        self.register_handler(command.RetrieveOwnUserCommand, self.retrieve_own_user)
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
        self._token_provider = token_provider
        self._oauth_header_cache: tuple[float, dict[str, str]] | None = None

    @staticmethod
    def _check_token_provider(
        token_provider: Callable[[], str] | None,
        auth_protocol: AuthProtocol | str,
        default_headers: dict[str, str] | None,
    ) -> None:
        """Reject token provider combinations that conflict with other auth settings.

        Raises:
            InitializationServiceError: If a token provider is combined with the
                OAUTH2 auth protocol or with an ``Authorization`` default header.
        """
        if token_provider is None:
            return
        if auth_protocol not in (AuthProtocol.NONE, AuthProtocol.NONE.value):
            raise exc.InitializationServiceError(
                "b4a99708",
                "token_provider cannot be combined with the OAUTH2 auth protocol; use auth_protocol NONE",
            )
        if default_headers and any(
            key.lower() == "authorization" for key in default_headers
        ):
            raise exc.InitializationServiceError(
                "82dd3da9",
                "token_provider cannot be combined with an Authorization default header",
            )

    def get_headers(self, cmd: Command) -> dict[str, str]:
        """Return request headers, refreshing an OAuth token when needed.

        Args:
            cmd: Command for which headers are requested.

        Returns:
            Default headers or headers containing a client-credentials bearer token.

        Raises:
            InitializationServiceError: If the configured authentication protocol cannot
                provide request headers.
        """
        if self._token_provider is not None:
            return self._get_cached_bearer_headers(self._retrieve_provided_token)
        if self._auth_protocol == AuthProtocol.NONE:
            return self._default_headers
        if self._auth_protocol == AuthProtocol.OAUTH2:
            assert self._oauth_idp_client is not None
            assert self._oauth_scope is not None
            return self._get_cached_bearer_headers(
                self._retrieve_client_credentials_token
            )
        raise exc.InitializationServiceError(
            "7bf9fe04",
            f"Auth protocol {self._auth_protocol.value} not supported for token retrieval",
        )

    def get_access_token(self) -> str:
        """Return a valid bearer token from the configured token source.

        Raises:
            InitializationServiceError: If no token source is configured.
        """
        authorization = self.get_headers(Command()).get("Authorization", "")
        if not authorization.startswith("Bearer "):
            raise exc.InitializationServiceError(
                "b9ebc5bf", "Client is not configured to retrieve an access token"
            )
        return authorization.removeprefix("Bearer ")

    def _retrieve_client_credentials_token(self) -> tuple[str, float | None]:
        """Retrieve a token and its advertised lifetime via client credentials."""
        assert self._oauth_idp_client is not None
        assert self._oauth_scope is not None
        return (
            self._oauth_idp_client.retrieve_jwt_with_client_credentials_flow_and_expiry(
                scope=self._oauth_scope
            )
        )

    def _retrieve_provided_token(self) -> str:
        """Retrieve a new token from the token provider, wrapping its failures."""
        assert self._token_provider is not None
        try:
            return self._token_provider()
        except Exception as e:
            raise exc.AuthException(
                "f2bf14f1", f"Token provider failed to supply a token: {e}"
            ) from e

    def _get_cached_bearer_headers(
        self, retrieve_token: Callable[[], str | tuple[str, float | None]]
    ) -> dict[str, str]:
        """Return headers with a bearer token, calling ``retrieve_token`` only near expiry."""
        now = datetime.now(UTC).timestamp()
        if self._oauth_header_cache and self._oauth_header_cache[0] > (
            now + self._oauth_token_refresh_margin
        ):
            return self._oauth_header_cache[1]

        token_result = retrieve_token()
        if isinstance(token_result, tuple):
            jwt_token, expires_in = token_result
            expires_at = now + expires_in if expires_in is not None else None
        else:
            jwt_token = token_result
            try:
                # Only the unverified ``exp`` claim is read, to schedule renewal of
                # the cached token; the service verifies the signature per request.
                claims = jwt.decode(jwt_token, options=_UNVERIFIED_OPTIONS)  # NOSONAR
                exp = claims.get("exp")
            except jwt.DecodeError:
                # Opaque (non-JWT) token, expiry unknown
                exp = None
            # Provider tokens without an exp claim are cached until a 401 forces refresh.
            expires_at = exp if exp is not None else math.inf

        headers = dict(self._default_headers)
        headers["Authorization"] = f"Bearer {jwt_token}"
        self._oauth_header_cache = (
            (expires_at, headers) if expires_at is not None else None
        )
        return headers

    def _handle_once(self, cmd: Command) -> Any:
        """Handle a command; on a 401 with a token provider, refresh the token and retry once."""
        if self._token_provider is None:
            return super()._handle_once(cmd)
        try:
            return super()._handle_once(cmd)
        except exc.ServiceException as e:
            if fastapp.RetryPolicy.get_remote_http_status(e) != 401:
                raise
        self._oauth_header_cache = None
        return super()._handle_once(cmd)

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

    def retrieve_own_user(self, cmd: command.RetrieveOwnUserCommand) -> model.User:
        """Retrieve the user the client is authenticated as."""
        response_body: dict[str, Any] = self.request(cmd, HttpMethod.GET)  # type: ignore[assignment]
        return model.User(**response_body)

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

    def delete_all_operational_data(
        self, cmd: command.DeleteAllOperationalDataCommand
    ) -> model.DeleteAllOperationalDataResult:
        """Delete all the operational data.

        Returns a specific subclass of `model.DeleteAllOperationalDataResult`
        containing the result of the deletion operation.
        """
        response_body: dict[str, Any] = self.request(cmd, HttpMethod.DELETE)  # type: ignore[assignment]
        return model.DeleteAllOperationalDataResult(**response_body)

    def delete_all_ref_data(
        self, cmd: command.DeleteAllRefDataCommand
    ) -> model.DeleteAllRefDataResult:
        """Delete all reference data after operational data has been deleted."""
        response_body: dict[str, Any] = self.request(cmd, HttpMethod.DELETE)  # type: ignore[assignment]
        return model.DeleteAllRefDataResult(**response_body)

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
    def create_local_or_remote(
        cls,
        app_type: enum.AppType,
        app_setup_type: Literal["LOCAL", "REMOTE", "NONE"],
        local_client_props: dict[str, Any] | None = None,
        remote_client_props: dict[str, Any] | None = None,
        no_client_props: dict[str, Any] | None = None,
        app_composer_class: type | None = None,
        user_class: type[model.User] | None = None,
        service_type_enum: type[Enum] | None = None,
        repository_type_enum: type[Enum] | None = None,
        logger: Logger | None = None,
    ) -> tuple[App, model.User | None]:
        """Create a local or remote application instance for the requested setup type.

        Args:
            app_type: Application type to create locally.
            app_setup_type: Setup mode, either ``LOCAL``, ``REMOTE``, or ``NONE``.
            local_client_props: Properties for local client (app) construction.
            remote_client_props: Properties for remote client construction.
            no_client_props: Properties for no-client construction.
            app_composer_class: Composer class for local setup.
            user_class: User model class for local setup.
            service_type_enum: Service-type enum for local setup.
            repository_type_enum: Repository-type enum for local setup.
            logger: Optional logger for local setup.

        Returns:
            Created application and local user when applicable.

        Raises:
            InitializationServiceError: If the setup mode is invalid or incomplete.
        """
        # Parse input
        app_setup_type = app_setup_type.upper()  # type: ignore[assignment]
        if app_setup_type not in ("LOCAL", "REMOTE", "NONE"):
            raise exc.InitializationServiceError(
                "2ceb9c7c",
                f"Invalid app_setup_type: {app_setup_type}. Must be 'LOCAL', 'REMOTE', or 'NONE'.",
            )
        # Create local or remote app
        app: App
        user: user_class | None  # type: ignore[valid-type]
        if app_setup_type == "LOCAL":
            # Parse local app props
            app, user = cls._create_local_client(
                app_type,
                local_client_props,
                app_composer_class,
                user_class,
                service_type_enum,
                repository_type_enum,
                logger,
            )
        elif app_setup_type == "REMOTE":
            # Parse remote app props
            app, user = CommondbClient._create_client(remote_client_props)
        elif app_setup_type == "NONE":
            # Parse no-client props
            app = cls._create_no_client(
                app_type,
                no_client_props,
                app_composer_class,
                user_class,
                service_type_enum,
                repository_type_enum,
                logger,
            )
            user = None
        else:
            raise exc.InitializationServiceError(
                "84a87605",
                f"Invalid app_setup_type: {app_setup_type}. Must be 'LOCAL', 'REMOTE', or 'NONE'.",
            )
        return app, user

    @classmethod
    def _create_local_client(
        cls,
        app_type: enum.AppType,
        local_client_props: dict[str, Any] | None,
        app_composer_class: type | None,
        user_class: type[model.User] | None,
        service_type_enum: type[Enum] | None,
        repository_type_enum: type[Enum] | None,
        logger: Logger | None = None,
    ) -> tuple[App, model.User]:
        """Instantiate a local application from configuration and a user definition.

        Args:
            app_type: Application type to configure.
            local_client_props: Local configuration containing user properties.
            app_composer_class: Composer used to construct the local application.
            user_class: User model used to construct the local user.
            service_type_enum: Application service-type enum.
            repository_type_enum: Application repository-type enum.
            logger: Optional logger used to determine setup logging.

        Returns:
            Local application and constructed user.

        Raises:
            InitializationServiceError: If required local setup properties are missing.
        """
        if (
            local_client_props is None
            or app_composer_class is None
            or user_class is None
            or service_type_enum is None
            or repository_type_enum is None
        ):
            raise exc.InitializationServiceError(
                "6451025d",
                "local_client_props, app_composer_class, user_class, service_type_enum, and repository_type_enum must be provided for LOCAL app setup.",
            )
        if "user" not in local_client_props:
            raise exc.InitializationServiceError(
                "80bc4360",
                "local_client_props must contain 'user' key for LOCAL app setup.",
            )
            # Get app config
        if "app_cfg" in local_client_props:
            app_cfg = local_client_props.pop("app_cfg")
        else:
            app_cfg = util.get_app_cfg_class(app_type)(
                app_type, service_type_enum, repository_type_enum
            )
        log_setup = local_client_props.get("log_setup", logger is not None)
        # Create local app and user
        app_composer = app_composer_class(app_cfg, log_setup=log_setup)
        app = app_composer.app
        user = user_class(**local_client_props["user"])

        return app, user

    @classmethod
    def _create_no_client(
        cls,
        app_type: enum.AppType,
        no_client_props: dict[str, Any] | None,
        app_composer_class: type | None,
        user_class: type[model.User] | None,
        service_type_enum: type[Enum] | None,
        repository_type_enum: type[Enum] | None,
        logger: Logger | None = None,
    ) -> App:
        """Instantiate a no-client application from configuration and a user definition.

        Args:
            app_type: Application type to configure.
            no_client_props: No-client configuration containing user properties.
            app_composer_class: Composer used to construct the local application.
            user_class: User model used to construct the local user.
            service_type_enum: Application service-type enum.
            repository_type_enum: Application repository-type enum.
            logger: Optional logger used to determine setup logging.

        Returns:
            Local application that raises an exception on use.

        Raises:
            InitializationServiceError: If required local setup properties are missing.
        """
        if (
            no_client_props is None
            or app_composer_class is None
            or user_class is None
            or service_type_enum is None
            or repository_type_enum is None
        ):
            raise exc.InitializationServiceError(
                "2f572747",
                "no_client_props, app_composer_class, user_class, service_type_enum, and repository_type_enum must be provided for NO_CLIENT app setup.",
            )
        # Get app config
        if "app_cfg" in no_client_props:
            app_cfg = no_client_props.pop("app_cfg")
        else:
            app_cfg = util.get_app_cfg_class(app_type)(
                app_type, service_type_enum, repository_type_enum
            )
        log_setup = no_client_props.get("log_setup", logger is not None)
        # Create local app and user
        app_composer = app_composer_class(app_cfg, log_setup=log_setup)
        app = app_composer.app

        return app

    @classmethod
    def _create_client(cls, client_props: dict[str, Any] | None) -> tuple[App, None]:
        """Instantiate a remote application from configured module and class names.

        Args:
            client_props: Remote configuration including module and class names.

        Returns:
            Constructed remote application and no local user.

        Raises:
            InitializationServiceError: If remote properties or required keys are absent.
        """
        if client_props is None:
            raise exc.InitializationServiceError(
                "4007b438", "client_props must be provided for REMOTE app setup."
            )
        if "module" not in client_props or "class_name" not in client_props:
            raise exc.InitializationServiceError(
                "0c268454",
                "client_props must contain 'module' and 'class_name' keys for REMOTE app setup.",
            )
            # Create remote app
        client_module = client_props.pop("module")
        client_class_name = client_props.pop("class_name")
        client_class: type[Client] = getattr(
            importlib.import_module(client_module), client_class_name
        )
        app = client_class(**client_props)
        for command_class, timeout in cls.DEFAULT_HTTP_TIMEOUTS.items():
            app.set_timeout(command_class, timeout)
        # No user for remote app, this is handled via authentication to the actual remote service
        user = None
        return app, user

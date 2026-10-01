"""Create authenticated clients for running Gen-EpiX services.

``create_client`` returns a client for a deployed CASEDB, SEQDB, OMOPDB or COMMONDB
service. It is configured from environment variables, authenticates for you, and
optionally retries transient failures. This module documents how that works.

Quick start
-----------
Set the connection settings for the service as ``<APP>_*`` environment variables
(or in a ``.env`` file in the working directory), where ``<APP>`` is ``CASEDB``,
``SEQDB``, ``OMOPDB`` or ``COMMONDB``::

    SEQDB_HOST=api.seqdb.example.org
    SEQDB_PORT=443
    SEQDB_OAUTH_DISCOVERY_URL=https://idp.example.org/.well-known/openid-configuration
    SEQDB_OAUTH_CLIENT_ID=<functional user client id>
    SEQDB_OAUTH_CLIENT_SECRET=<functional user client secret>
    SEQDB_OAUTH_SCOPE=<scope to request>

Then create the client and send commands::

    from gen_epix import AppType, create_client, seqdb_command
    from gen_epix.fastapp import CrudOperation

    client = create_client(AppType.SEQDB)  # or "seqdb"
    loci = client.handle(
        seqdb_command.LocusCrudCommand(operation=CrudOperation.READ_ALL)
    )

Creating the client makes no network call. The first command triggers the
authentication described below.

Settings
--------
Required: ``<APP>_PORT``, and for the default flow ``<APP>_OAUTH_CLIENT_ID``,
``<APP>_OAUTH_CLIENT_SECRET``, ``<APP>_OAUTH_SCOPE`` plus one of the two token
location settings. Missing required variables raise a ``ValueError`` that names
them. Environment variables take precedence over the ``.env`` file. Optional
settings, with defaults:

- ``<APP>_HOST`` (``localhost``), ``<APP>_PROTOCOL`` (``HTTPS``)
- ``<APP>_OAUTH_DISCOVERY_URL``: OpenID Connect discovery document, from which the
  token endpoint is taken.
- ``<APP>_OAUTH_TOKEN_ENDPOINT`` with ``<APP>_OAUTH_DISCOVER_FROM_REMOTE=false``:
  use a token endpoint directly and skip discovery.
- ``<APP>_SSL_CERT_FILE``: CA certificate file to trust.
- ``<APP>_DISABLE_SSL_VERIFICATION`` (``false``)
- ``<APP>_DEFAULT_REQUEST_TIMEOUT`` (``5`` seconds)

The TLS settings apply to API calls and to token requests alike. For hosts
``localhost``, ``127.0.0.1`` and ``0.0.0.0`` TLS verification is always off.

How authentication works
------------------------
The default is the OAuth2 *client-credentials* flow, meant for machines. A
*functional user* is an account at the identity provider with a client id and a
client secret, which act as its username and password. It also has to exist as a
user in the target service, with a role that allows the command (for example
``ORG_USER`` or higher to read reference data).

1. When a command first needs a token, the client finds the token endpoint (from
   the discovery document, or ``<APP>_OAUTH_TOKEN_ENDPOINT``) and sends
   ``POST grant_type=client_credentials&scope=...`` with the client id and secret
   as HTTP Basic credentials.
2. The identity provider returns an access token, a signed JWT whose ``exp`` claim
   is its expiry time. The client reads ``exp`` (without verifying the signature,
   which is the service's job) and caches the token.
3. The command is sent with ``Authorization: Bearer <token>``. The service checks
   the signature, issuer, audience and expiry, finds the user, and checks the
   user's role against the command.
4. Later commands reuse the cached token. When fewer than 60 seconds remain before
   ``exp``, the next command first fetches a new token the same way. There is no
   separate refresh token in this flow; the client simply authenticates again.

Using another kind of token
---------------------------
To act as another user, for example a human user whose token you obtained
elsewhere, skip client credentials::

    client = create_client("seqdb", token="eyJ...")  # fixed token
    client = create_client("seqdb", token_provider=my_function)  # called when needed

``token_provider`` is a function returning a bearer token. The token is cached like
above. If the service answers a command with ``401``, the cached token is dropped,
the provider is called once more, and the command is retried once; a second 401 is
raised. A fixed ``token`` therefore cannot renew itself. The ``<APP>_OAUTH_*``
credentials are not used in these modes. This 401 retry does not apply to the
client-credentials flow, which renews tokens by expiry time only.

Retrying transient failures
---------------------------
By default a failing command is raised immediately. Pass a ``RemoteRetryPolicy`` to
repeat it::

    from gen_epix import RemoteRetryPolicy

    policy = RemoteRetryPolicy(
        retryable_status_codes=frozenset({502, 503, 504}),
        wait_schedule=(10, 20, 30),  # seconds to wait before each retry
    )
    client = create_client("seqdb", retry_policy=policy)

Network errors (timeouts, connection failures) are always retried. HTTP errors are
retried only for the listed status codes; 401 and 403 can never be listed, because
they are authentication problems that waiting does not fix. The command is
attempted ``len(wait_schedule) + 1`` times, then the last error is raised. Every
attempt gets fresh headers, so a token that expired while waiting is renewed.

Troubleshooting
---------------
- ``ValueError: Missing required environment variable(s) ...``: set the named
  variables, or run from the directory holding your ``.env``.
- ``ServiceException: Error when handling remote command ...: Token retrieval
  failed ...``: the identity provider refused or could not be reached (the client
  tries three times). Check the client id and secret, the scope, and the discovery
  URL or token endpoint.
- ``HTTP status 401``: the service did not accept the token. Typical causes are an
  audience or issuer that does not match the service's identity provider settings,
  or a functional user that is not registered (or not active) in the service.
- ``HTTP status 403``: the token is fine but the user's role does not allow the
  command.
- ``HTTP request error ... Name or service not known`` (or a connection error): the
  service host cannot be reached from where you run, for example an internal-only
  environment.
- TLS errors: set ``<APP>_SSL_CERT_FILE`` to the CA that signed the service
  certificate. Use ``<APP>_DISABLE_SSL_VERIFICATION`` only for testing.

Never print or log tokens or the client secret.
"""

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from gen_epix.casedb.services.client import CasedbClient
from gen_epix.commondb.domain import DOMAIN as COMMONDB_DOMAIN
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.services.client import CommondbClient
from gen_epix.fastapp.client import RemoteRetryPolicy
from gen_epix.fastapp.enum import AuthProtocol
from gen_epix.omopdb.services.client import OmopdbClient
from gen_epix.seqdb.services.client import SeqdbClient

if TYPE_CHECKING:
    from typing import Self


class ClientSettings(BaseSettings):
    """Base connection settings for a remote-app client.

    Subclasses declare no fields of their own; they only set ``env_prefix``, so the
    same field set is read under ``CASEDB_*``, ``SEQDB_*``, ``OMOPDB_*`` or
    ``COMMONDB_*`` environment variables respectively.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="localhost", description="Remote app host.")
    port: int = Field(description="Remote app port.")
    protocol: str = Field(
        default="HTTPS", description="Remote app connection protocol."
    )
    ssl_cert_file: Path | str | None = Field(
        default=None,
        description="Path to a custom CA/SSL certificate for the connection.",
    )
    disable_ssl_verification: bool = Field(
        default=False,
        description="Disable TLS certificate verification for the connection.",
    )
    auth_protocol: AuthProtocol = Field(
        default=AuthProtocol.OAUTH2,
        description="Authentication protocol used against the remote app.",
    )
    oauth_discover_from_remote: bool = Field(
        default=True,
        description="Discover OAuth2 endpoints via the discovery URL instead of oauth_token_endpoint.",
    )
    oauth_discovery_url: str | None = Field(
        default=None,
        description="OAuth2 discovery URL, used when oauth_discover_from_remote is True.",
    )
    oauth_token_endpoint: str | None = Field(
        default=None,
        description="OAuth2 token endpoint, used when oauth_discover_from_remote is False.",
    )
    oauth_client_id: str | None = Field(default=None, description="OAuth2 client id.")
    oauth_client_secret: SecretStr | None = Field(
        default=None, description="OAuth2 client secret."
    )
    oauth_scope: str | None = Field(
        default=None,
        description="OAuth2 scope requested for the client-credentials token.",
    )
    default_request_timeout: float = Field(
        default=5.0,
        description="Default HTTP request timeout in seconds for calls to the remote app.",
    )

    @classmethod
    def load(cls) -> "Self":
        """Load settings from the environment, with a friendly error for missing variables.

        Raises:
            ValueError: If required environment variables are missing or invalid.
        """
        try:
            return cls()  # type: ignore[call-arg]
        except ValidationError as e:
            prefix = cls.model_config.get("env_prefix", "")
            missing_vars = [
                f"{prefix}{err['loc'][0]}".upper()
                for err in e.errors()
                if err["type"] == "missing" and err["loc"]
            ]
            if missing_vars:
                raise ValueError(
                    f"Missing required environment variable(s): {', '.join(missing_vars)}. "
                    "Check your .env file."
                ) from None
            raise ValueError(str(e)) from None


class CasedbClientSettings(ClientSettings):
    """ClientSettings read from CASEDB_* env vars."""

    model_config = SettingsConfigDict(env_prefix="CASEDB_")


class OmopdbClientSettings(ClientSettings):
    """ClientSettings read from OMOPDB_* env vars."""

    model_config = SettingsConfigDict(env_prefix="OMOPDB_")


class SeqdbClientSettings(ClientSettings):
    """ClientSettings read from SEQDB_* env vars."""

    model_config = SettingsConfigDict(env_prefix="SEQDB_")


class CommondbClientSettings(ClientSettings):
    """ClientSettings read from COMMONDB_* env vars."""

    model_config = SettingsConfigDict(env_prefix="COMMONDB_")


_CLIENT_CONFIG: dict[
    AppType, tuple[Callable[..., CommondbClient], type[ClientSettings]]
] = {
    AppType.CASEDB: (CasedbClient, CasedbClientSettings),
    AppType.OMOPDB: (OmopdbClient, OmopdbClientSettings),
    AppType.SEQDB: (SeqdbClient, SeqdbClientSettings),
    AppType.COMMONDB: (
        lambda **kwargs: CommondbClient(COMMONDB_DOMAIN, **kwargs),
        CommondbClientSettings,
    ),
}


def _parse_app_type(app: AppType | str) -> AppType:
    """Convert an app type or its (case-insensitive) name to a supported AppType."""
    try:
        app_type = app if isinstance(app, AppType) else AppType(app.upper())
    except ValueError:
        app_type = AppType.ALL
    if app_type not in _CLIENT_CONFIG:
        raise ValueError(
            f"Unsupported app: {app!r}. Must be one of "
            f"{[x.value.lower() for x in _CLIENT_CONFIG]}"
        )
    return app_type


def default_token_file(app: AppType | str) -> Path:
    """Return the default token file path (``.token.<app>``) for an app."""
    return Path(f".token.{_parse_app_type(app).value.lower()}")


def read_token_file(token_file: Path | str) -> str:
    """Read a bearer token from a file, stripping surrounding whitespace.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty.
    """
    token = Path(token_file).read_text(encoding="utf-8").strip()
    if not token:
        raise ValueError(f"Token file is empty: {token_file}")
    return token


def resolve_token(
    token: str | None, token_file: Path | str | None, app: AppType | str
) -> str | None:
    """Resolve a bearer token: explicit token, else explicit file, else ``.token.<app>``.

    Returns:
        The token, or None if none was given and the default token file is absent.
    """
    if token:
        return token
    if token_file is not None:
        return read_token_file(token_file)
    default_file = default_token_file(app)
    if default_file.is_file():
        return read_token_file(default_file)
    return None


def create_client(
    app: AppType | Literal["casedb", "omopdb", "seqdb", "commondb"] | str,
    *,
    token: str | None = None,
    token_provider: Callable[[], str] | None = None,
    retry_policy: RemoteRetryPolicy | None = None,
    settings: ClientSettings | None = None,
) -> CommondbClient:
    """Create a client for a running Gen-EpiX service.

    By default the client authenticates with the OAuth2 client-credentials flow,
    using the ``<APP>_*`` environment variables. Pass ``token`` or ``token_provider``
    to authenticate as another (e.g. human) user instead. See the module
    documentation for setup, settings, token renewal, retries and troubleshooting.

    Example:
        >>> client = create_client("seqdb")  # doctest: +SKIP
        >>> client.handle(command)  # doctest: +SKIP

    Args:
        app: Service to connect to, as an ``AppType`` or its name (any case).
        token: Static bearer token. Shorthand for ``token_provider=lambda: token``.
        token_provider: Callable returning a bearer token, called when a token is
            needed or after a 401 response.
        retry_policy: Optional policy for retrying transient failures. No retries
            if None.
        settings: Connection settings. Loaded from the ``<APP>_*`` environment
            variables if None.

    Returns:
        The configured client.

    Raises:
        ValueError: If ``app`` is unsupported, both ``token`` and ``token_provider``
            are given, or settings cannot be loaded.
    """
    app_type = _parse_app_type(app)
    if token is not None and token_provider is not None:
        raise ValueError("Provide either token or token_provider, not both")
    if token is not None:
        static_token = token
        token_provider = lambda: static_token  # noqa: E731

    client_factory, settings_class = _CLIENT_CONFIG[app_type]
    if settings is None:
        settings = settings_class.load()
    oauth_client_secret = (
        settings.oauth_client_secret.get_secret_value()
        if settings.oauth_client_secret is not None
        else None
    )
    client_kwargs = settings.model_dump(
        exclude={
            "oauth_client_secret",
            "oauth_discover_from_remote",
            "auth_protocol",
        }
    )
    if not settings.oauth_discover_from_remote:
        # Keep explicit endpoints from env and skip OIDC discovery fetch.
        client_kwargs["oauth_discovery_url"] = ""
    if token_provider is not None:
        auth_protocol = AuthProtocol.NONE
        oauth_client_secret = None
    else:
        auth_protocol = settings.auth_protocol
    client = client_factory(
        **client_kwargs,
        oauth_client_secret=oauth_client_secret,
        auth_protocol=auth_protocol,
        token_provider=token_provider,
        retry_policy=retry_policy,
        log_cmd_object_on_error=False,
    )
    for command_class, timeout in client.DEFAULT_HTTP_TIMEOUTS.items():
        client.set_timeout(command_class, timeout)
    return client

"""Create authenticated clients for running Gen-EpiX services from environment settings.

The client authenticates with the OAuth2 client-credentials flow using a functional
user's client id and secret, all read from ``<APP>_*`` environment variables (or a
``.env`` file), where ``<APP>`` is one of ``CASEDB``, ``SEQDB``, ``OMOPDB`` or
``COMMONDB``.
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

    By default the client authenticates with the OAuth2 client-credentials flow.
    Pass ``token`` or ``token_provider`` to authenticate as another (e.g. human)
    user instead, bypassing the client-credentials flow.

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

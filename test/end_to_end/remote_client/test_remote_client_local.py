"""End-to-end test of the environment-driven remote client against a local stack.

Starts the same local components as ``casedb_seqdb_connection`` (a mock OAuth server
and a real SEQDB server using it as identity provider), registers a functional user
(mapped to the SEQDB root user) at the mock server, and then talks to SEQDB
exclusively through ``gen_epix.create_client`` with settings taken from ``SEQDB_*``
environment variables, as a production caller would. The root user may read
everything, so this test checks authentication and transport, not role permissions.

Requires the local TLS certificates in ``cert/``.
"""

from __future__ import annotations

import logging
import socket
from collections.abc import Generator
from pathlib import Path
from test.end_to_end.casedb_seqdb_connection.envvar import set_envvar
from test.test_client.enum import ServerType
from test.test_client.oauth.server import LOGGER as OAUTH_LOGGER
from test.test_client.server_manager import ServerManager

import pytest

from gen_epix import create_client, seqdb_command
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.services.client import CommondbClient
from gen_epix.fastapp import exc
from gen_epix.fastapp.client import RemoteRetryPolicy, get_remote_http_status
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.api.router import create_routers as seqdb_create_routers
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.env import AppComposer as SeqdbAppComposer

pytestmark = pytest.mark.e2e

CERT_FILE = Path("cert/cert.pem").absolute()
KEY_FILE = Path("cert/key.pem").absolute()
SEQDB_PORT = 8003
# The local SEQDB does not auto-create users and its repositories are in-memory, so
# the functional user is registered under the configured root user key: the first
# request creates the root user from the token claims (key claim = sub = client id).
CLIENT_ID = "root@dummy.org"
CLIENT_SECRET = "REMOTE_CLIENT_TEST_SECRET"
SCOPE = "openid profile aud"
# The local SEQDB expects the client id of its identity provider config as audience
AUDIENCE = "mock"

# The reference-data reads juno-seqdb-etl performs
READ_ALL_COMMANDS: list[type] = [
    seqdb_command.SeqCategoryCrudCommand,
    seqdb_command.LocusCrudCommand,
    seqdb_command.ProtocolCrudCommand,
]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


# The servers are started once for the whole module; the tests stay independent
# because each builds its own client from the environment settings.


@pytest.fixture(scope="module")
def oauth_server() -> Generator[ServerManager, None, None]:
    """Start the mock OAuth server and register the functional user."""
    if not (CERT_FILE.is_file() and KEY_FILE.is_file()):
        pytest.skip("Local TLS certificates in cert/ are required")
    orig_level = OAUTH_LOGGER.level
    OAUTH_LOGGER.setLevel(logging.FATAL)
    try:
        with ServerManager(
            service=ServerType.OAUTH,
            port=_free_port(),
            ssl_keyfile=KEY_FILE.as_posix(),
            ssl_certfile=CERT_FILE.as_posix(),
        ) as server:
            if not server.start():
                pytest.fail("Failed to start OAuth server")
            if not server.add_client(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                audience=AUDIENCE,
                scopes=SCOPE.split(),
            ):
                pytest.fail("Failed to register the functional user")
            yield server
    finally:
        OAUTH_LOGGER.setLevel(orig_level)


@pytest.fixture(scope="module")
def seqdb_server(
    oauth_server: ServerManager, tmp_path_factory: pytest.TempPathFactory
) -> Generator[ServerManager, None, None]:
    """Start a local SEQDB server that uses the mock OAuth server as IDP."""
    identity_provider_file = (
        Path(__file__).parents[1] / "casedb_seqdb_connection" / "identity_provider.toml"
    )
    settings_file = tmp_path_factory.mktemp("remote_client") / "oauth-discovery.toml"
    settings_file.write_text(
        identity_provider_file.read_text(encoding="utf-8").replace(
            "https://127.0.0.1:5443", f"https://127.0.0.1:{oauth_server.port}"
        ),
        encoding="utf-8",
    )
    with pytest.MonkeyPatch.context() as env, _logging_disabled():
        for key, value in _envvars(settings_file).items():
            env.setenv(key, value)
        app_cfg = AppCfg(
            AppType.SEQDB, seqdb_enum.ServiceType, seqdb_enum.RepositoryType
        )
        composer = SeqdbAppComposer(app_cfg, log_setup=False)
        fastapi_app = create_fast_api(
            app=composer.app,
            create_routers_fn=seqdb_create_routers,
            app_id=composer.app.generate_id(),
            setup_logger=None,
            api_logger=None,
            debug=False,
        )
        with ServerManager(
            service=ServerType.SEQDB,
            app=fastapi_app,
            host="127.0.0.1",
            port=SEQDB_PORT,
            ssl_certfile=CERT_FILE.as_posix(),
            ssl_keyfile=KEY_FILE.as_posix(),
        ) as server:
            if not server.start():
                pytest.fail("Failed to start seqdb server")
            yield server


def _envvars(identity_provider_file: Path) -> dict[str, str]:
    """Return the app settings env vars set by the shared e2e helper."""
    import os

    before = dict(os.environ)
    try:
        set_envvar(identity_provider_file)
        return {k: v for k, v in os.environ.items() if before.get(k) != v}
    finally:
        os.environ.clear()
        os.environ.update(before)


class _logging_disabled:  # pylint: disable=invalid-name
    """Context manager silencing logging while the servers start."""

    def __enter__(self) -> None:
        self._previous = logging.root.manager.disable
        logging.disable(logging.CRITICAL)

    def __exit__(self, *args: object) -> None:
        logging.disable(self._previous)


@pytest.fixture(autouse=True)
def seqdb_client_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    oauth_server: ServerManager,
    seqdb_server: ServerManager,
) -> None:
    """Point the SEQDB_* client settings at the local stack, per test."""
    # Run from an empty dir so no developer .env is read, and clear leftovers
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SEQDB_DISABLE_SSL_VERIFICATION", raising=False)
    monkeypatch.delenv("SEQDB_OAUTH_TOKEN_ENDPOINT", raising=False)
    for key, value in {
        "SEQDB_HOST": "127.0.0.1",
        "SEQDB_PORT": str(seqdb_server.port),
        "SEQDB_OAUTH_DISCOVERY_URL": f"https://127.0.0.1:{oauth_server.port}/.well-known/openid-configuration",
        "SEQDB_OAUTH_CLIENT_ID": CLIENT_ID,
        "SEQDB_OAUTH_CLIENT_SECRET": CLIENT_SECRET,
        "SEQDB_OAUTH_SCOPE": SCOPE,
        "SEQDB_SSL_CERT_FILE": CERT_FILE.as_posix(),
    }.items():
        monkeypatch.setenv(key, value)


def _read_all(client: CommondbClient, command_class: type) -> list:
    result = client.handle(command_class(operation=CrudOperation.READ_ALL))
    assert isinstance(result, list)
    return result


@pytest.mark.parametrize("command_class", READ_ALL_COMMANDS, ids=lambda x: x.__name__)
def test_client_credentials_read_all(command_class: type) -> None:
    """The client authenticates with client credentials and reads reference data."""
    client = create_client("seqdb")
    _read_all(client, command_class)
    # Token is cached, so a second call needs no new token request
    token = client.get_access_token()
    _read_all(client, command_class)
    assert client.get_access_token() == token


def test_retry_policy_does_not_disturb_successful_calls() -> None:
    """A client with a retry policy behaves normally when nothing fails."""
    policy = RemoteRetryPolicy(frozenset({502, 503, 504}), (0.1, 0.1))
    client = create_client("seqdb", retry_policy=policy)
    _read_all(client, seqdb_command.LocusCrudCommand)


def test_invalid_token_is_rejected() -> None:
    """A garbage bearer token is refused by the server with 401/403."""
    client = create_client("seqdb", token="not-a-valid-token")
    with pytest.raises(exc.ServiceException) as info:
        _read_all(client, seqdb_command.LocusCrudCommand)
    assert get_remote_http_status(info.value) in (401, 403)


def test_stale_token_from_provider_is_refreshed_once() -> None:
    """On a 401 the token provider is called again and the command retried once."""
    valid_token = create_client("seqdb").get_access_token()
    tokens = ["not-a-valid-token", valid_token]
    calls: list[int] = []

    def provider() -> str:
        calls.append(1)
        return tokens[min(len(calls), len(tokens)) - 1]

    client = create_client("seqdb", token_provider=provider)
    _read_all(client, seqdb_command.LocusCrudCommand)
    assert len(calls) == 2

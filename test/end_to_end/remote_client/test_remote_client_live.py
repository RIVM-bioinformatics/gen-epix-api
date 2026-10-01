"""Live test of the environment-driven remote client against deployed services.

Calls real services with real credentials, so it is skipped unless run explicitly
with the ``live`` marker (which gates this module; see ``test/conftest.py``):

    python -m pytest test/end_to_end/remote_client -m live

Configuration
-------------
Settings are read per app from ``<APP>_*`` environment variables, or from a ``.env``
file in the directory pytest is started from (normally the repository root, where
``.env`` is gitignored). ``<APP>`` is ``SEQDB``, ``CASEDB`` or ``OMOPDB``; use the
variables below for each app you want to test::

    <APP>_HOST=api.<app>.<environment>.example.org
    <APP>_PORT=443
    <APP>_OAUTH_DISCOVERY_URL=https://idp.example.org/.well-known/openid-configuration
    <APP>_OAUTH_CLIENT_ID=<functional user client id>
    <APP>_OAUTH_CLIENT_SECRET=<functional user client secret>
    <APP>_OAUTH_SCOPE=<scope requested for the token, e.g. api://<app>/.default>

Required: ``HOST`` has a default (``localhost``) but should be set, ``PORT`` is
required by the settings, and the three ``OAUTH_*`` credentials/scope are needed for
the default client-credentials flow. Optional (defaults in parentheses):

    <APP>_PROTOCOL (HTTPS)
    <APP>_OAUTH_DISCOVER_FROM_REMOTE (true; set false together with
        <APP>_OAUTH_TOKEN_ENDPOINT to skip discovery)
    <APP>_OAUTH_TOKEN_ENDPOINT
    <APP>_SSL_CERT_FILE (custom CA file)
    <APP>_DISABLE_SSL_VERIFICATION (false)
    <APP>_DEFAULT_REQUEST_TIMEOUT (5 seconds)

Skipping
--------
An app is skipped, not failed, when its settings are missing or when its host cannot
be reached (e.g. an internal-only environment): the test cannot verify it then. The
configured user must be allowed to read the reference data below (e.g. APP_ADMIN).
Only non-destructive reads are made and no token or secret is printed.
"""

from __future__ import annotations

import socket
from typing import Any

import pytest

from gen_epix import (
    CommondbClient,
    casedb_command,
    create_client,
    omopdb_command,
    seqdb_command,
)
from gen_epix.fastapp import exc
from gen_epix.fastapp.client import get_remote_http_status
from gen_epix.fastapp.enum import CrudOperation

pytestmark = [pytest.mark.e2e, pytest.mark.live]

# One authenticated reference-data read per service
APP_COMMANDS: list[tuple[str, type]] = [
    ("seqdb", seqdb_command.SeqCategoryCrudCommand),
    ("seqdb", seqdb_command.LocusCrudCommand),
    ("seqdb", seqdb_command.ProtocolCrudCommand),
    ("casedb", casedb_command.CaseTypeCrudCommand),
    ("omopdb", omopdb_command.VocabularyCrudCommand),
]


def _create_client(app: str, **kwargs: Any) -> CommondbClient:
    try:
        client = create_client(app, **kwargs)
    except ValueError as e:
        pytest.skip(f"No client settings for {app}: {e}")
    try:
        socket.create_connection((client.host, client.port or 443), timeout=5).close()
    except OSError as e:
        pytest.skip(f"{app} at {client.host}:{client.port} is not reachable: {e}")
    return client


@pytest.mark.parametrize(
    "app,command_class", APP_COMMANDS, ids=lambda x: getattr(x, "__name__", x)
)
def test_authenticated_read_all(app: str, command_class: Any) -> None:
    """Authenticate with client credentials and read a reference-data table."""
    client = _create_client(app)
    result = client.handle(command_class(operation=CrudOperation.READ_ALL))
    assert isinstance(result, list)
    assert all(isinstance(x, command_class.MODEL_CLASS) for x in result)


@pytest.mark.parametrize("app", ["seqdb", "casedb", "omopdb"])
def test_client_credentials_token_is_cached(app: str) -> None:
    """A second token request is served from the cache."""
    client = _create_client(app)
    first = client.get_access_token()
    second = client.get_access_token()
    assert second == first


@pytest.mark.parametrize("app", ["seqdb"])
def test_invalid_token_is_rejected(app: str) -> None:
    """A garbage bearer token is refused with an authentication error."""
    client = _create_client(app, token="not-a-valid-token")
    cmd = seqdb_command.SeqCategoryCrudCommand(operation=CrudOperation.READ_ALL)
    with pytest.raises(exc.ServiceException) as info:
        client.handle(cmd)
    assert get_remote_http_status(info.value) in (401, 403)

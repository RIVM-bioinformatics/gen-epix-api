"""Verify application remote clients expose reference-data reset routes."""

from typing import Any

import pytest

from gen_epix.casedb.domain import command as casedb_command
from gen_epix.casedb.services.client import CasedbClient
from gen_epix.omopdb.domain import command as omopdb_command
from gen_epix.omopdb.services.client import OmopdbClient
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.services.client import SeqdbClient


@pytest.mark.parametrize(
    ("client_class", "command_class"),
    [
        (CasedbClient, casedb_command.DeleteAllRefDataCommand),
        (SeqdbClient, seqdb_command.DeleteAllRefDataCommand),
        (OmopdbClient, omopdb_command.DeleteAllRefDataCommand),
    ],
)
def test_ref_data_route_and_timeout_are_registered(
    client_class: type[Any], command_class: type[Any]
) -> None:
    """Route concrete application commands to the long-running reset endpoint."""
    assert client_class.ROUTE_MAP[command_class] == "/ref_data"
    assert client_class.DEFAULT_HTTP_TIMEOUTS[command_class] == 300.0


@pytest.mark.parametrize(
    ("client_class", "command_class"),
    [
        (CasedbClient, casedb_command.DeleteAllOperationalDataCommand),
        (SeqdbClient, seqdb_command.DeleteAllOperationalDataCommand),
        (OmopdbClient, omopdb_command.DeleteAllOperationalDataCommand),
    ],
)
def test_operational_data_route_and_timeout_are_registered(
    client_class: type[Any], command_class: type[Any]
) -> None:
    """Route concrete application commands to the long-running reset endpoint."""
    assert client_class.ROUTE_MAP[command_class] == "/operational_data"
    assert client_class.DEFAULT_HTTP_TIMEOUTS[command_class] == 300.0


@pytest.mark.parametrize(
    ("client_class", "command_module"),
    [
        (CasedbClient, casedb_command),
        (SeqdbClient, seqdb_command),
        (OmopdbClient, omopdb_command),
    ],
)
@pytest.mark.parametrize(
    ("command_name", "route"),
    [
        ("DeleteAllOperationalDataCommand", "/v1/operational_data"),
        ("DeleteAllRefDataCommand", "/v1/ref_data"),
    ],
)
def test_a_client_can_route_and_handle_the_reset_commands_of_its_app(
    client_class: type[Any], command_module: Any, command_name: str, route: str
) -> None:
    """A constructed client knows both the route and the handler; no request is made."""
    client = client_class("localhost", 8000)
    command_class = getattr(command_module, command_name)

    assert client.get_route(command_class()).endswith(route)
    assert client.get_handler(command_class) is not None

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

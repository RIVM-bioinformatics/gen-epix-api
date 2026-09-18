"""Verify application remote clients expose reference-data reset routes."""

from typing import Any

import pytest

from gen_epix.casedb.domain import command as casedb_command
from gen_epix.casedb.services.remote_app import CasedbRemoteApp
from gen_epix.omopdb.domain import command as omopdb_command
from gen_epix.omopdb.services.remote_app import OmopdbRemoteApp
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.services.remote_app import SeqdbRemoteApp


@pytest.mark.parametrize(
    ("remote_app_class", "command_class"),
    [
        (CasedbRemoteApp, casedb_command.DeleteAllRefDataCommand),
        (SeqdbRemoteApp, seqdb_command.DeleteAllRefDataCommand),
        (OmopdbRemoteApp, omopdb_command.DeleteAllRefDataCommand),
    ],
)
def test_ref_data_route_and_timeout_are_registered(
    remote_app_class: type[Any], command_class: type[Any]
) -> None:
    """Route concrete application commands to the long-running reset endpoint."""
    assert remote_app_class.ROUTE_MAP[command_class] == "/ref_data"
    assert remote_app_class.DEFAULT_HTTP_TIMEOUTS[command_class] == 300.0

"""Unit tests for casedb's seqdb service composition."""

from test.util.mock_compat import Mock, patch
from uuid import uuid4

import pytest

from gen_epix.casedb.services.seqdb import service
from gen_epix.casedb.services.seqdb.service import SeqdbService
from gen_epix.fastapp import exc
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model


def test_lowercase_client_type_is_rejected() -> None:
    """Reject lowercase setup values before constructing dependencies."""
    with pytest.raises(exc.InitializationServiceError, match="in uppercase"):
        SeqdbService(Mock(), "none")


def test_none_client_type_uses_no_app_composer() -> None:
    """Use the exception-raising composer for the NONE setup mode."""
    with (
        patch.object(service.BaseSeqdbService, "__init__", return_value=None),
        patch.object(
            service.SeqdbClient,
            "create_local_or_remote",
            return_value=(Mock(), None),
        ) as create_client,
    ):
        SeqdbService(Mock(), "NONE")

    assert (
        create_client.call_args.kwargs["app_composer_class"]
        is service.SeqdbNoAppComposer
    )


def test_retrieve_seq_distances_uses_functional_user() -> None:
    functional_user = seqdb_model.User(
        id=uuid4(),
        key="seqdb-test@example.com",
        email="seqdb-test@example.com",
        name="Seqdb Test User",
        organization_id=uuid4(),
        roles={seqdb_enum.Role.APP_ADMIN},
    )
    distance = Mock(spec=seqdb_model.SeqDistance)
    seqdb_service = Mock(spec=SeqdbService)
    seqdb_service.seqdb_user = functional_user
    seqdb_service.seqdb_app.handle.return_value = [distance]
    cmd = seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand(
        user=None,
        seq_profile_ids=[uuid4()],
        protocol_id=uuid4(),
    )

    result = SeqdbService.retrieve_seq_distances_by_seq_profiles(seqdb_service, cmd)

    assert result == [distance]
    forwarded_cmd = seqdb_service.seqdb_app.handle.call_args.args[0]
    assert forwarded_cmd.user is functional_user
    assert forwarded_cmd.seq_profile_ids == cmd.seq_profile_ids
    assert forwarded_cmd.protocol_id == cmd.protocol_id

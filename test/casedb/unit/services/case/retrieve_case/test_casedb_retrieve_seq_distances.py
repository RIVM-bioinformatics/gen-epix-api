import json
from test.util.mock_compat import MagicMock, Mock, patch
from types import SimpleNamespace
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.domain.service.abac import BaseAbacService
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.retrieve_seq_distances_by_cases import (
    case_service_retrieve_seq_distances_by_cases,
)
from gen_epix.casedb.services.seqdb.service import SeqdbService
from gen_epix.fastapp.app import App
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model


def test_retrieve_seq_distances_is_registered_for_case_abac() -> None:
    assert (
        command.RetrieveSeqDistancesByCasesCommand in BaseAbacService.CASE_ABAC_COMMANDS
    )


def test_seqdb_bridge_forwards_profile_distance_command_with_functional_user() -> None:
    """Forward the Seqdb command through the configured functional user."""
    functional_user = seqdb_model.User(
        id=uuid4(),
        key="seqdb-test@example.com",
        email="seqdb-test@example.com",
        name="Seqdb Test User",
        organization_id=uuid4(),
        roles={seqdb_enum.Role.APP_ADMIN},
    )
    distance = Mock(spec=seqdb_model.SeqDistance)
    service = Mock(spec=SeqdbService)
    service.seqdb_user = functional_user
    service.seqdb_app.handle.return_value = [distance]
    cmd = seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand(
        user=None,
        seq_profile_ids=[uuid4()],
        protocol_id=uuid4(),
    )

    result = SeqdbService.retrieve_seq_distances_by_seq_profiles(service, cmd)

    assert result == [distance]
    forwarded_cmd = service.seqdb_app.handle.call_args.args[0]
    assert forwarded_cmd.user is functional_user
    assert forwarded_cmd.seq_profile_ids == cmd.seq_profile_ids
    assert forwarded_cmd.protocol_id == cmd.protocol_id


@pytest.mark.parametrize("filter_other_cases", [True, False])
def test_retrieve_seq_distances_maps_case_ids_and_filters_other_profiles(
    filter_other_cases: bool,
) -> None:
    user = model.User(
        id=uuid4(),
        key="test@example.com",
        email="test@example.com",
        roles={"CASEDB_APP_ADMIN"},
        organization_id=uuid4(),
        is_active=True,
    )
    case_type_id = uuid4()
    distance_col_id = uuid4()
    ref_col_id = uuid4()
    protocol_id = uuid4()
    case_id = uuid4()
    other_case_id = uuid4()
    profile_id = uuid4()
    other_profile_id = uuid4()
    outside_profile_id = uuid4()
    repository = Mock()
    uow = MagicMock()
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    repository.uow.return_value = uow
    service: BaseCaseService = Mock(spec=BaseCaseService)
    service.repository = repository
    service.app = Mock(spec=App)
    service._get_user_and_repository.return_value = (user, repository)
    service._retrieve_cases_with_content_right.return_value = (
        [
            SimpleNamespace(
                id=case_id,
                content={distance_col_id: str(profile_id)},
            ),
            SimpleNamespace(
                id=other_case_id,
                content={distance_col_id: str(other_profile_id)},
            ),
        ],
        False,
    )

    distance = Mock(spec=seqdb_model.SeqDistance)
    distance.seq_profile_id = profile_id
    distance.get_profile_distance_map.return_value = {
        other_profile_id: 1.5,
        outside_profile_id: 9.0,
    }
    distance.content = json.dumps(
        {
            str(other_profile_id): 1.5,
            str(outside_profile_id): 9.0,
        }
    )
    service.app.handle.return_value = [distance]
    repository.crud.side_effect = [
        SimpleNamespace(
            case_type_id=case_type_id,
            ref_col_id=ref_col_id,
        ),
        SimpleNamespace(
            col_type=enum.ColType.GENETIC_DISTANCE,
            genetic_distance_protocol_id=uuid4(),
        ),
        SimpleNamespace(seqdb_seq_distance_protocol_id=protocol_id),
    ]
    cmd = command.RetrieveSeqDistancesByCasesCommand(
        user=user,
        case_type_id=case_type_id,
        case_ids=[case_id, other_case_id],
        genetic_distance_col_id=distance_col_id,
        filter_other_cases=filter_other_cases,
    )

    with patch.object(
        BaseCaseAbacPolicy,
        "get_case_abac_from_command",
        return_value=Mock(),
    ):
        result = case_service_retrieve_seq_distances_by_cases(service, cmd)

    assert result == [distance]
    assert distance.id == case_id
    expected_content = (
        {str(other_profile_id): 1.5}
        if filter_other_cases
        else {str(other_profile_id): 1.5, str(outside_profile_id): 9.0}
    )
    assert json.loads(distance.content) == expected_content
    seqdb_cmd = service.app.handle.call_args.args[0]
    assert isinstance(seqdb_cmd, seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand)
    assert seqdb_cmd.seq_profile_ids == [profile_id, other_profile_id]
    assert seqdb_cmd.protocol_id == protocol_id

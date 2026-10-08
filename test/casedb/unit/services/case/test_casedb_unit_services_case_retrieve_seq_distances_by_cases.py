"""Unit tests for case-linked sequence-distance retrieval."""

import json
from test.util.mock_compat import MagicMock, Mock, patch
from types import SimpleNamespace
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case import (
    retrieve_seq_distances_by_cases as target_module,
)
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.retrieve_seq_distances_by_cases import (
    case_service_retrieve_seq_distances_by_cases,
)
from gen_epix.fastapp.app import App
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import model as seqdb_model


def _create_service_and_command(
    filter_other_cases: bool = True,
) -> tuple[BaseCaseService, command.RetrieveSeqDistancesByCasesCommand]:
    user = model.User(
        id=uuid4(),
        key="test@example.com",
        email="test@example.com",
        roles={"CASEDB_APP_ADMIN"},
        organization_id=uuid4(),
        is_active=True,
    )
    repository = Mock()
    uow = MagicMock()
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    repository.uow.return_value = uow
    service: BaseCaseService = Mock(spec=BaseCaseService)
    service.repository = repository
    service.app = Mock(spec=App)
    service._get_user_and_repository.return_value = (user, repository)
    cmd = command.RetrieveSeqDistancesByCasesCommand(
        user=user,
        case_type_id=uuid4(),
        case_ids=[uuid4()],
        genetic_distance_col_id=uuid4(),
        filter_other_cases=filter_other_cases,
    )
    return service, cmd


def test_empty_case_profile_map_returns_no_distances() -> None:
    service, cmd = _create_service_and_command()
    protocol = SimpleNamespace(seqdb_seq_distance_protocol_id=uuid4())

    with patch.object(
        target_module,
        "_retrieve_case_profile_map",
        return_value=(protocol, {}, Mock()),
    ):
        result = case_service_retrieve_seq_distances_by_cases(service, cmd)

    assert result == []
    service.app.handle.assert_not_called()


def test_empty_seqdb_results_returns_no_distances() -> None:
    service, cmd = _create_service_and_command()
    protocol = SimpleNamespace(seqdb_seq_distance_protocol_id=uuid4())
    case_id = uuid4()
    profile_id = uuid4()
    service.app.handle.return_value = []

    with patch.object(
        target_module,
        "_retrieve_case_profile_map",
        return_value=(protocol, {case_id: profile_id}, Mock()),
    ):
        result = case_service_retrieve_seq_distances_by_cases(service, cmd)

    assert result == []


@pytest.mark.parametrize("filter_other_cases", [True, False])
def test_retrieves_mapped_distances_and_filters_unmapped_profiles(
    filter_other_cases: bool,
) -> None:
    service, cmd = _create_service_and_command(filter_other_cases)
    case_type_id = cmd.case_type_id
    distance_col_id = cmd.genetic_distance_col_id
    ref_col_id = uuid4()
    protocol_id = uuid4()
    case_id = cmd.case_ids[0]
    other_case_id = uuid4()
    profile_id = uuid4()
    other_profile_id = uuid4()
    outside_profile_id = uuid4()
    service._retrieve_cases_with_content_right.return_value = (
        [
            SimpleNamespace(id=case_id, content={distance_col_id: str(profile_id)}),
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
        {str(other_profile_id): 1.5, str(outside_profile_id): 9.0}
    )
    unmapped_distance = Mock(spec=seqdb_model.SeqDistance)
    unmapped_distance.seq_profile_id = outside_profile_id
    service.app.handle.return_value = [distance, unmapped_distance]
    service.repository.crud.side_effect = [
        SimpleNamespace(case_type_id=case_type_id, ref_col_id=ref_col_id),
        SimpleNamespace(
            col_type=enum.ColType.GENETIC_DISTANCE,
            genetic_distance_protocol_id=uuid4(),
        ),
        SimpleNamespace(seqdb_seq_distance_protocol_id=protocol_id),
    ]

    with patch.object(
        BaseCaseAbacPolicy, "get_case_abac_from_command", return_value=Mock()
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

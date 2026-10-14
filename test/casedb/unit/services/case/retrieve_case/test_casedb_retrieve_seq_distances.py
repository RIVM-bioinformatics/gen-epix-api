import json
from contextlib import nullcontext
from test.util.mock_compat import Mock, patch
from types import SimpleNamespace
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.domain.policy.permission import RoleGenerator
from gen_epix.casedb.domain.service.abac import BaseAbacService
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.retrieve_seq_distances_by_cases import (
    case_service_retrieve_seq_distances_by_cases,
)
from gen_epix.casedb.services.seqdb.service import SeqdbService
from gen_epix.fastapp import PermissionType, PermissionTypeSet
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model


@pytest.fixture
def setup() -> SimpleNamespace:
    user = model.User(
        id=uuid4(),
        key="u",
        email="u@example.com",
        name="u",
        organization_id=uuid4(),
        roles={enum.Role.ORG_USER.value},
    )
    dist, seq, case_type, profile, other = [uuid4() for _ in range(5)]
    case = model.Case(
        id=uuid4(),
        case_type_id=case_type,
        created_in_data_collection_id=uuid4(),
        content={dist: str(profile)},
    )
    external = model.Case(
        id=uuid4(),
        case_type_id=case_type,
        created_in_data_collection_id=uuid4(),
        content={dist: str(other)},
    )
    assert case.id is not None
    row = seqdb_model.SeqDistance(  # type: ignore[call-arg]
        id=uuid4(),
        sample_id=uuid4(),
        protocol_id=uuid4(),
        seq_profile_id=profile,
        format=seqdb_enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
        content=json.dumps({str(profile): 0.0, str(other): 2.0, str(uuid4()): 9.0}),
    )
    service = Mock(spec=BaseCaseService)
    repo = Mock()
    repo.uow.return_value = nullcontext()
    service._get_user_and_repository.return_value = (user, repo)
    service._retrieve_cases_with_content_right.return_value = ([case], False)
    service._retrieve_case_data_collections_map.return_value = {}
    col = SimpleNamespace(
        case_type_id=case_type, ref_col_id=uuid4(), genetic_sequence_col_id=seq
    )
    protocol = SimpleNamespace(
        seqdb_seq_distance_protocol_id=row.protocol_id, seqdb_max_stored_distance=2.0
    )
    repo.crud.side_effect = [
        col,
        SimpleNamespace(
            col_type=enum.ColType.GENETIC_DISTANCE, genetic_distance_protocol_id=uuid4()
        ),
        protocol,
        [external],
    ]
    result = [row]
    service.app.handle.return_value = result
    abac = Mock(is_full_access=False)
    rights = {case.id: {dist}, external.id: {dist, seq}}
    abac.get_case_rights.side_effect = lambda cid, *args: SimpleNamespace(
        is_full_access=False, read_col_ids=rights[cid]
    )
    cmd = command.RetrieveSeqDistancesByCasesCommand(
        user=user,
        case_type_id=case_type,
        case_ids=[case.id],
        genetic_distance_col_id=dist,
        filter_other_cases=False,
    )
    return SimpleNamespace(
        service=service,
        repo=repo,
        cmd=cmd,
        abac=abac,
        rights=rights,
        case=case,
        external=external,
        row=row,
        result=result,
        protocol=protocol,
        dist=dist,
        seq=seq,
        col=col,
        profile=profile,
        other=other,
    )


def retrieve(s: SimpleNamespace) -> list[seqdb_model.SeqDistance]:
    with patch.object(
        BaseCaseAbacPolicy, "get_case_abac_from_command", return_value=s.abac
    ):
        return case_service_retrieve_seq_distances_by_cases(s.service, s.cmd)


def test_permission_and_abac_registration() -> None:
    permission = (command.RetrieveSeqDistancesByCasesCommand, PermissionTypeSet.E)
    assert permission in RoleGenerator.ROLE_PERMISSION_SETS[enum.Role.ORG_USER]
    assert permission not in RoleGenerator.ROLE_PERMISSION_SETS[enum.Role.APP_ADMIN]
    assert (
        command.RetrieveSeqDistancesByCasesCommand in BaseAbacService.CASE_ABAC_COMMANDS
    )


@pytest.mark.parametrize("filter_other", [False, True])
def test_threshold_mutual_and_copy(setup: SimpleNamespace, filter_other: bool) -> None:
    s = setup
    s.cmd.filter_other_cases = filter_other
    original = s.row.model_dump()
    rows = retrieve(s)
    assert rows[0].id == s.case.id
    expected = {s.profile: 0.0}
    if not filter_other:
        expected[s.other] = 2.0
    assert rows[0].get_profile_distance_map() == expected
    assert s.row.model_dump() == original
    assert s.repo.crud.call_count == (3 if filter_other else 4)


@pytest.mark.parametrize("column", ["distance", "sequence"])
def test_external_column_access(setup: SimpleNamespace, column: str) -> None:
    s = setup
    s.rights[s.external.id].remove(s.dist if column == "distance" else s.seq)
    if column == "distance":
        with pytest.raises(exc.UnauthorizedAuthError):
            retrieve(s)
    else:
        assert retrieve(s)[0].get_profile_distance_map() == {s.profile: 0.0}


@pytest.mark.parametrize("missing_value", [False, True])
def test_requested_content_required(
    setup: SimpleNamespace, missing_value: bool
) -> None:
    s = setup
    if missing_value:
        s.case.content = {}
    else:
        s.rights[s.case.id] = set()
    with pytest.raises(exc.UnauthorizedAuthError):
        retrieve(s)
    s.service.app.handle.assert_not_called()


def test_missing_sequence_link(setup: SimpleNamespace) -> None:
    s = setup
    s.col.genetic_sequence_col_id = None
    with pytest.raises(
        exc.InitializationServiceError, match="no linked genetic-sequence column"
    ):
        retrieve(s)


def test_no_maximum_and_unknown_profiles(setup: SimpleNamespace) -> None:
    s = setup
    s.protocol.seqdb_max_stored_distance = None
    s.row.content = json.dumps({str(s.other): 100.0, str(uuid4()): 0.0})
    assert retrieve(s)[0].get_profile_distance_map() == {s.other: 100.0}


def test_shared_requested_profile(setup: SimpleNamespace) -> None:
    s = setup
    second = s.case.model_copy(deep=True, update={"id": uuid4()})
    s.cmd.case_ids.append(second.id)
    s.rights[second.id] = {s.dist}
    s.service._retrieve_cases_with_content_right.return_value = (
        [s.case, second],
        False,
    )
    rows = retrieve(s)
    assert [row.id for row in rows] == [s.case.id, second.id]
    assert rows[0] is not rows[1]
    assert s.service.app.handle.call_args.args[0].seq_profile_ids == [s.profile]


def test_shared_external_profile(setup: SimpleNamespace) -> None:
    s = setup
    denied = s.external.model_copy(deep=True, update={"id": uuid4()})
    unrelated = s.external.model_copy(deep=True, update={"id": uuid4(), "content": {}})
    s.rights[denied.id] = set()
    s.repo.crud.side_effect = [
        s.col,
        SimpleNamespace(
            col_type=enum.ColType.GENETIC_DISTANCE, genetic_distance_protocol_id=uuid4()
        ),
        s.protocol,
        [denied, unrelated, s.external],
    ]
    assert s.other in retrieve(s)[0].get_profile_distance_map()


def test_full_access(setup: SimpleNamespace) -> None:
    s = setup
    s.abac.is_full_access = True
    s.rights.clear()
    assert s.other in retrieve(s)[0].get_profile_distance_map()
    s.abac.get_case_rights.assert_not_called()


def test_empty_filtered_map(setup: SimpleNamespace) -> None:
    s = setup
    s.row.content = json.dumps({str(s.other): 3.0})
    assert retrieve(s)[0].get_profile_distance_map() == {}


def test_empty_request(setup: SimpleNamespace) -> None:
    s = setup
    s.cmd.case_ids = []
    assert retrieve(s) == []
    s.service.app.handle.assert_not_called()


@pytest.mark.parametrize(
    "error", [exc.UnauthorizedAuthError, exc.RequestLimitExceededAuthError]
)
def test_shared_helper_errors_propagate(
    setup: SimpleNamespace, error: type[Exception]
) -> None:
    s = setup
    s.service._retrieve_cases_with_content_right.side_effect = error("test")
    with pytest.raises(error):
        retrieve(s)


def test_bridge_forwards_result(setup: SimpleNamespace) -> None:
    s = setup
    service = Mock(spec=SeqdbService)
    service.seqdb_user = seqdb_model.User(
        id=uuid4(),
        key="functional",
        email="functional@example.com",
        name="functional",
        organization_id=uuid4(),
        roles={seqdb_enum.Role.ORG_USER.value},
    )
    service.seqdb_app.handle.return_value = s.result
    cmd = seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand(
        user=s.cmd.user, seq_profile_ids=[s.profile], protocol_id=s.row.protocol_id
    )
    assert SeqdbService.retrieve_seq_distances_by_seq_profiles(service, cmd) is s.result
    assert service.seqdb_app.handle.call_args.args[0].user is service.seqdb_user


def test_none_maximum_still_checks_access(setup: SimpleNamespace) -> None:
    setup.protocol.seqdb_max_stored_distance = None
    setup.rights[setup.external.id] = set()
    with pytest.raises(exc.UnauthorizedAuthError):
        retrieve(setup)


def test_requested_result_limit_is_not_silent(setup: SimpleNamespace) -> None:
    setup.service._retrieve_cases_with_content_right.return_value = ([setup.case], True)
    with pytest.raises(exc.RequestLimitExceededAuthError):
        retrieve(setup)


def test_no_pair_does_not_create_candidate(setup: SimpleNamespace) -> None:
    setup.row.content = json.dumps({str(setup.profile): 0.0})
    setup.rights[setup.external.id] = set()
    assert retrieve(setup)[0].get_profile_distance_map() == {setup.profile: 0.0}
    assert setup.repo.crud.call_count == 3


def test_split_shared_case_rights_do_not_grant_sequence(setup: SimpleNamespace) -> None:
    s = setup
    second = s.external.model_copy(deep=True, update={"id": uuid4()})
    s.rights[s.external.id] = {s.dist}
    s.rights[second.id] = {s.seq}
    s.repo.crud.side_effect = [
        s.col,
        SimpleNamespace(
            col_type=enum.ColType.GENETIC_DISTANCE, genetic_distance_protocol_id=uuid4()
        ),
        s.protocol,
        [s.external, second],
    ]
    assert retrieve(s)[0].get_profile_distance_map() == {s.profile: 0.0}


@pytest.mark.parametrize("wrong_type", [False, True])
def test_invalid_column_metadata(setup: SimpleNamespace, wrong_type: bool) -> None:
    s = setup
    if wrong_type:
        s.repo.crud.side_effect = [
            s.col,
            SimpleNamespace(col_type=enum.ColType.GENETIC_SEQUENCE),
        ]
    else:
        s.col.case_type_id = uuid4()
    with pytest.raises(exc.InvalidArgumentsError):
        retrieve(s)

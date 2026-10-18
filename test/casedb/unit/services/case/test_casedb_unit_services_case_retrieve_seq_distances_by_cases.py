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
from gen_epix.casedb.services.case import (
    retrieve_seq_distances_by_cases as service_module,
)
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.retrieve_seq_distances_by_cases import (
    case_service_retrieve_seq_distances_by_cases,
)
from gen_epix.fastapp import PermissionTypeSet
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
    dist_col_id, case_type_id, profile_id, external_profile_id = [
        uuid4() for _ in range(4)
    ]
    case_id = uuid4()
    case = model.Case(
        id=case_id,
        case_type_id=case_type_id,
        created_in_data_collection_id=uuid4(),
        content={dist_col_id: str(profile_id)},
    )
    external_case = model.Case(
        id=uuid4(),
        case_type_id=case_type_id,
        created_in_data_collection_id=uuid4(),
        content={dist_col_id: str(external_profile_id)},
    )
    assert case.id is not None
    row = seqdb_model.SeqDistance(  # type: ignore[call-arg]
        id=uuid4(),
        sample_id=uuid4(),
        protocol_id=uuid4(),
        seq_profile_id=profile_id,
        format=seqdb_enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
        content=json.dumps(
            {
                str(profile_id): 0.0,
                str(external_profile_id): 2.0,
                str(uuid4()): 9.0,
                str(uuid4()): None,
            }
        ),
    )
    repository = Mock()
    repository.uow.return_value = nullcontext()
    service = Mock(spec=BaseCaseService)
    service._get_user_and_repository.return_value = (user, repository)
    service.repository = repository
    service.app.handle.return_value = [row]
    protocol = SimpleNamespace(
        id=uuid4(),
        seqdb_seq_distance_protocol_id=row.protocol_id,
        seqdb_max_stored_distance=2.0,
    )
    distance_col = SimpleNamespace(id=dist_col_id)
    case_profile_map = {case_id: profile_id}
    case_abac = SimpleNamespace(is_full_access=True)
    cmd = command.RetrieveSeqDistancesByCasesCommand(
        user=user,
        case_type_id=case_type_id,
        case_ids=[case_id],
        genetic_distance_col_id=dist_col_id,
        filter_other_cases=True,
    )
    return SimpleNamespace(
        service=service,
        repository=repository,
        cmd=cmd,
        case_abac=case_abac,
        case=case,
        external_case=external_case,
        row=row,
        protocol=protocol,
        distance_col=distance_col,
        case_profile_map=case_profile_map,
        profile_id=profile_id,
        external_profile_id=external_profile_id,
        dist_col_id=dist_col_id,
        case_type_id=case_type_id,
        user=user,
    )


def retrieve(s: SimpleNamespace) -> list[model.CaseSeqDistance]:
    with (
        patch.object(
            service_module,
            "_retrieve_case_profile_map",
            return_value=(s.protocol, s.case_profile_map, s.distance_col),
        ),
        patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=s.case_abac,
        ),
    ):
        return case_service_retrieve_seq_distances_by_cases(s.service, s.cmd)


def test_permission_and_abac_registration() -> None:
    permission = (command.RetrieveSeqDistancesByCasesCommand, PermissionTypeSet.E)
    assert permission in RoleGenerator.ROLE_PERMISSION_SETS[enum.Role.ORG_USER]
    assert permission not in RoleGenerator.ROLE_PERMISSION_SETS[enum.Role.APP_ADMIN]
    assert (
        command.RetrieveSeqDistancesByCasesCommand in BaseAbacService.CASE_ABAC_COMMANDS
    )


def test_filters_threshold_and_maps_target_profiles_to_case_ids(
    setup: SimpleNamespace,
) -> None:
    s = setup
    original = s.row.model_dump()

    rows = retrieve(s)

    assert rows == [
        model.CaseSeqDistance(
            id=s.case.id,
            distances={s.case.id: 0.0},
        )
    ]
    assert s.row.model_dump() == original
    s.service.app.handle.assert_called_once()
    assert s.service.app.handle.call_args.args[0].seq_profile_ids == [s.profile_id]


@pytest.mark.parametrize("filter_other_cases", [True, False])
def test_external_case_targets_require_readable_case(
    setup: SimpleNamespace, filter_other_cases: bool
) -> None:
    s = setup
    s.cmd.filter_other_cases = filter_other_cases
    s.case_abac.is_full_access = False
    second_external_case = model.Case(
        id=uuid4(),
        case_type_id=s.case_type_id,
        created_in_data_collection_id=uuid4(),
        content={s.dist_col_id: str(s.external_profile_id)},
    )
    s.service._retrieve_cases_with_content_right.return_value = (
        [s.external_case, second_external_case],
        False,
    )

    rows = retrieve(s)

    expected = {s.case.id: 0.0}
    if not filter_other_cases:
        expected[s.external_case.id] = 2.0
        expected[second_external_case.id] = 2.0
        s.service._retrieve_cases_with_content_right.assert_called_once()
    else:
        s.service._retrieve_cases_with_content_right.assert_not_called()
    assert rows[0].distances == expected


def test_full_access_reads_external_case_fields(setup: SimpleNamespace) -> None:
    s = setup
    s.cmd.filter_other_cases = False
    second_external_case_id = uuid4()
    s.repository.read_fields.return_value = [
        (
            str(s.external_case.id),
            json.dumps({str(s.dist_col_id): str(s.external_profile_id)}),
        ),
        (
            str(second_external_case_id),
            json.dumps({str(s.dist_col_id): str(s.external_profile_id)}),
        ),
    ]

    rows = retrieve(s)

    assert rows[0].distances == {
        s.case.id: 0.0,
        s.external_case.id: 2.0,
        second_external_case_id: 2.0,
    }
    s.repository.read_fields.assert_called_once()


def test_unbounded_protocol_includes_large_external_distances(
    setup: SimpleNamespace,
) -> None:
    s = setup
    s.cmd.filter_other_cases = False
    s.protocol.seqdb_max_stored_distance = None
    s.row.content = json.dumps(
        {str(s.profile_id): 0.0, str(s.external_profile_id): 100.0}
    )
    s.repository.read_fields.return_value = [
        (
            str(s.external_case.id),
            json.dumps({str(s.dist_col_id): str(s.external_profile_id)}),
        )
    ]

    rows = retrieve(s)

    assert rows[0].distances == {
        s.case.id: 0.0,
        s.external_case.id: 100.0,
    }


def test_shared_requested_profile_returns_results_for_each_case(
    setup: SimpleNamespace,
) -> None:
    s = setup
    s.cmd.case_ids = [s.case.id, s.external_case.id]
    s.case_profile_map = {
        s.case.id: s.profile_id,
        s.external_case.id: s.profile_id,
    }

    rows = retrieve(s)

    assert [row.id for row in rows] == s.cmd.case_ids
    assert all(
        row.distances == {s.case.id: 0.0, s.external_case.id: 0.0} for row in rows
    )
    sent_command = s.service.app.handle.call_args.args[0]
    assert sent_command.seq_profile_ids == [s.profile_id]


def test_no_mapped_profiles_returns_empty_distances_without_seqdb_call(
    setup: SimpleNamespace,
) -> None:
    s = setup
    second_case_id = uuid4()
    s.cmd.case_ids = [s.case.id, second_case_id]
    s.case_profile_map = {}

    rows = retrieve(s)

    assert rows == [
        model.CaseSeqDistance(id=case_id, distances={}) for case_id in s.cmd.case_ids
    ]
    s.service.app.handle.assert_not_called()


def test_empty_request_still_runs_profile_validation(setup: SimpleNamespace) -> None:
    s = setup
    s.cmd.case_ids = []

    with patch.object(
        service_module,
        "_retrieve_case_profile_map",
        return_value=(s.protocol, {}, s.distance_col),
    ) as retrieve_profile_map:
        assert case_service_retrieve_seq_distances_by_cases(s.service, s.cmd) == []

    retrieve_profile_map.assert_called_once()
    s.service.app.handle.assert_not_called()


def test_profile_validation_errors_propagate(setup: SimpleNamespace) -> None:
    s = setup
    with patch.object(
        service_module,
        "_retrieve_case_profile_map",
        side_effect=exc.InvalidArgumentsError("test", "invalid column"),
    ):
        with pytest.raises(exc.InvalidArgumentsError, match="invalid column"):
            case_service_retrieve_seq_distances_by_cases(s.service, s.cmd)


def test_missing_stored_distance_row_is_an_invariant_failure(
    setup: SimpleNamespace,
) -> None:
    s = setup
    s.service.app.handle.return_value = []

    with pytest.raises(AssertionError):
        retrieve(s)


def test_unexpected_distance_format_is_rejected(setup: SimpleNamespace) -> None:
    s = setup
    s.service.app.handle.return_value = [SimpleNamespace(format="unexpected")]

    with pytest.raises(AssertionError, match="Unexpected SeqDistance format"):
        retrieve(s)


def test_missing_requested_profile_gets_empty_result(setup: SimpleNamespace) -> None:
    s = setup
    second_case_id = uuid4()
    s.cmd.case_ids.append(second_case_id)

    rows = retrieve(s)

    assert [row.id for row in rows] == [s.case.id, second_case_id]
    assert rows[1].distances == {}

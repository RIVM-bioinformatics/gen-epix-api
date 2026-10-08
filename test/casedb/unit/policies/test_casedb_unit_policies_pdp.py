from test.util.mock_compat import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, enum
from gen_epix.casedb.policies.pdp import PolicyDecisionPoint
from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import OnException


@pytest.fixture
def abac_service() -> Mock:
    return Mock()


@pytest.fixture
def pdp(abac_service: Mock) -> PolicyDecisionPoint:
    return PolicyDecisionPoint(abac_service)


def test_is_allowed_returns_false_without_user(pdp: PolicyDecisionPoint) -> None:
    cmd = Mock(spec=command.Command)
    cmd.user = None

    assert pdp.is_allowed(cmd) is False


def test_is_allowed_delegates_case_set_creation(
    pdp: PolicyDecisionPoint, abac_service: Mock
) -> None:
    cmd = Mock(spec=command.CreateCaseSetCommand)
    case_type_id = uuid4()
    data_collection_id = uuid4()
    cmd.user = Mock()
    cmd.case_set = Mock()
    cmd.case_set.case_type_id = case_type_id
    cmd.case_set.created_in_data_collection_id = data_collection_id
    cmd.data_collection_ids = {data_collection_id}
    case_abac = abac_service.get_case_abac.return_value
    case_abac.is_allowed.return_value = True

    assert pdp.is_allowed(cmd) is True

    abac_service.get_case_abac.assert_called_once_with(cmd)
    case_abac.is_allowed.assert_called_once_with(
        case_type_id,
        data_collection_id,
        enum.CaseRight.ADD_CASE_SET,
        True,
        tgt_data_collection_ids=cmd.data_collection_ids,
    )


def test_is_allowed_rejects_unsupported_command(pdp: PolicyDecisionPoint) -> None:
    cmd = Mock(spec=command.Command)
    cmd.user = Mock()

    with pytest.raises(NotImplementedError):
        pdp.is_allowed(cmd)


@pytest.mark.parametrize(
    ("data_collection_ids", "col_ids", "expected"),
    [
        (frozenset(), frozenset(), False),
        (frozenset({uuid4()}), frozenset(), True),
    ],
    ids=["no-data-collections", "no-columns"],
)
def test_is_readable_columns_empty_inputs(
    pdp: PolicyDecisionPoint,
    data_collection_ids: frozenset,
    col_ids: frozenset,
    expected: bool,
) -> None:
    complete_case_type = Mock()

    assert (
        pdp.is_readable_columns_for_data_collections(
            complete_case_type, data_collection_ids, col_ids
        )
        is expected
    )


def test_is_readable_columns_uses_union_of_collection_rights(
    pdp: PolicyDecisionPoint,
) -> None:
    first_collection_id = uuid4()
    second_collection_id = uuid4()
    first_col_id = uuid4()
    second_col_id = uuid4()
    complete_case_type = Mock()
    complete_case_type.case_type_access_abacs = {
        first_collection_id: Mock(read_col_ids={first_col_id}),
        second_collection_id: Mock(read_col_ids={second_col_id}),
    }

    assert pdp.is_readable_columns_for_data_collections(
        complete_case_type,
        frozenset({first_collection_id, second_collection_id}),
        frozenset({first_col_id, second_col_id}),
    )
    assert not pdp.is_readable_columns_for_data_collections(
        complete_case_type,
        frozenset({first_collection_id}),
        frozenset({first_col_id, second_col_id}),
    )


def _case_set_row(
    case_set_id: UUID,
    case_type_id: UUID,
    data_collection_ids: frozenset[UUID],
) -> tuple[UUID, UUID, frozenset[UUID]]:
    return case_set_id, case_type_id, data_collection_ids


def _case_set_command() -> Mock:
    cmd = Mock(spec=command.CaseSetCrudCommand)
    cmd.user = Mock(id=uuid4())
    return cmd


def test_filter_case_set_ids_rejects_invalid_right(
    pdp: PolicyDecisionPoint,
) -> None:
    with pytest.raises(ValueError, match="Invalid case right for case set"):
        list(pdp.filter_case_set_ids(_case_set_command(), [], enum.CaseRight.READ_CASE))


def test_filter_case_set_ids_yields_every_id_with_full_access(
    pdp: PolicyDecisionPoint, abac_service: Mock
) -> None:
    case_abac = abac_service.get_case_abac.return_value
    case_abac.is_full_access = True
    rows = [
        _case_set_row(uuid4(), uuid4(), frozenset({uuid4()})),
        _case_set_row(uuid4(), uuid4(), frozenset()),
    ]

    assert list(
        pdp.filter_case_set_ids(_case_set_command(), rows, enum.CaseRight.READ_CASE_SET)
    ) == [row[0] for row in rows]


def test_filter_case_set_ids_skips_case_type_without_access_when_requested(
    pdp: PolicyDecisionPoint, abac_service: Mock
) -> None:
    case_abac = abac_service.get_case_abac.return_value
    case_abac.is_full_access = False
    case_abac.case_type_access_abacs = {}
    row = _case_set_row(uuid4(), uuid4(), frozenset())

    assert (
        list(
            pdp.filter_case_set_ids(
                _case_set_command(),
                [row],
                enum.CaseRight.READ_CASE_SET,
                on_filtered=OnException.SKIP,
            )
        )
        == []
    )


def test_filter_case_set_ids_raises_for_case_type_without_access(
    pdp: PolicyDecisionPoint, abac_service: Mock
) -> None:
    case_abac = abac_service.get_case_abac.return_value
    case_abac.is_full_access = False
    case_abac.case_type_access_abacs = {}
    row = _case_set_row(uuid4(), uuid4(), frozenset())

    with pytest.raises(exc.UnauthorizedAuthError):
        list(
            pdp.filter_case_set_ids(
                _case_set_command(), [row], enum.CaseRight.READ_CASE_SET
            )
        )


def test_filter_case_set_ids_allows_any_accessible_collection_and_caches(
    pdp: PolicyDecisionPoint, abac_service: Mock
) -> None:
    case_type_id = uuid4()
    first_collection_id = uuid4()
    second_collection_id = uuid4()
    access = Mock()
    access.is_allowed.return_value = True
    case_abac = abac_service.get_case_abac.return_value
    case_abac.is_full_access = False
    case_abac.case_type_access_abacs = {case_type_id: {second_collection_id: access}}
    rows = [
        _case_set_row(
            uuid4(),
            case_type_id,
            frozenset({first_collection_id, second_collection_id}),
        ),
        _case_set_row(
            uuid4(),
            case_type_id,
            frozenset({first_collection_id, second_collection_id}),
        ),
    ]

    assert list(
        pdp.filter_case_set_ids(_case_set_command(), rows, enum.CaseRight.READ_CASE_SET)
    ) == [row[0] for row in rows]
    access.is_allowed.assert_called_once_with(enum.CaseRight.READ_CASE_SET)


def test_filter_case_set_ids_skips_when_collection_lacks_right(
    pdp: PolicyDecisionPoint, abac_service: Mock
) -> None:
    case_type_id = uuid4()
    data_collection_id = uuid4()
    access = Mock()
    access.is_allowed.return_value = False
    case_abac = abac_service.get_case_abac.return_value
    case_abac.is_full_access = False
    case_abac.case_type_access_abacs = {case_type_id: {data_collection_id: access}}
    row = _case_set_row(uuid4(), case_type_id, frozenset({data_collection_id}))

    assert (
        list(
            pdp.filter_case_set_ids(
                _case_set_command(),
                [row],
                enum.CaseRight.READ_CASE_SET,
                on_filtered=OnException.SKIP,
            )
        )
        == []
    )

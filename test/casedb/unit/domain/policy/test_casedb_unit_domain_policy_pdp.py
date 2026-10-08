from collections.abc import Iterable
from test.util.mock_compat import Mock
from typing import Literal
from uuid import UUID

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.policy.pdp import BasePolicyDecisionPoint
from gen_epix.fastapp import OnException


class _ConcretePolicyDecisionPoint(BasePolicyDecisionPoint):
    def is_exempted(self, cmd: command.Command) -> bool:
        return bool(getattr(cmd, "exempted", False))

    def is_allowed(self, cmd: command.Command) -> bool:
        return False

    def is_readable_columns_for_data_collections(
        self,
        complete_case_type: model.CompleteCaseType,
        data_collection_ids: frozenset[UUID],
        col_ids: frozenset[UUID],
    ) -> bool:
        return True

    def is_writable_columns_for_data_collections(
        self,
        complete_case_type: model.CompleteCaseType,
        data_collection_ids: frozenset[UUID],
        col_ids: frozenset[UUID],
    ) -> bool:
        return True

    def filter_case_set_ids(
        self,
        cmd: command.CaseSetCrudCommand,
        case_set_data_collection_ids: Iterable[tuple[UUID, UUID, frozenset[UUID]]],
        right: enum.CaseRight,
        on_filtered: Literal[OnException.SKIP, OnException.RAISE] = OnException.RAISE,
    ) -> Iterable[UUID]:
        return ()


@pytest.fixture
def abac_service() -> Mock:
    return Mock()


@pytest.fixture
def pdp(abac_service: Mock) -> _ConcretePolicyDecisionPoint:
    return _ConcretePolicyDecisionPoint(abac_service)


@pytest.mark.parametrize(
    ("filter_method", "access_method", "field_argument", "field_name"),
    [
        (
            "get_case_type_id_filter",
            "get_case_type_filter",
            "case_type_id_field_name",
            "case_type_key",
        ),
        ("get_col_id_filter", "get_col_filter", "col_id_field_name", "col_key"),
        (
            "get_col_set_id_filter",
            "get_col_set_filter",
            "col_set_id_field_name",
            "col_set_key",
        ),
        ("get_dim_id_filter", "get_dim_filter", "dim_id_field_name", "dim_key"),
        (
            "get_ref_col_id_filter",
            "get_ref_col_filter",
            "ref_col_id_field_name",
            "ref_col_key",
        ),
        (
            "get_ref_dim_id_filter",
            "get_ref_dim_filter",
            "ref_dim_id_field_name",
            "ref_dim_key",
        ),
    ],
    ids=["case-type", "column", "column-set", "dimension", "ref-column", "ref-dim"],
)
def test_filter_helpers_forward_field_names(
    pdp: _ConcretePolicyDecisionPoint,
    abac_service: Mock,
    filter_method: str,
    access_method: str,
    field_argument: str,
    field_name: str,
) -> None:
    cmd = Mock(exempted=False)
    access = abac_service.get_ref_data_access.return_value
    expected_filter = object()
    getattr(access, access_method).return_value = expected_filter

    result = getattr(pdp, filter_method)(cmd, **{field_argument: field_name})

    assert result is expected_filter
    abac_service.get_ref_data_access.assert_called_once_with(cmd)
    getattr(access, access_method).assert_called_once_with(field_name)


def test_filter_helpers_return_none_for_exempt_command(
    pdp: _ConcretePolicyDecisionPoint, abac_service: Mock
) -> None:
    cmd = Mock(exempted=True)

    assert pdp.get_dim_id_filter(cmd) is None
    abac_service.get_ref_data_access.assert_not_called()


def test_filter_helper_preserves_none_result(
    pdp: _ConcretePolicyDecisionPoint, abac_service: Mock
) -> None:
    cmd = Mock(exempted=False)
    abac_service.get_ref_data_access.return_value.get_dim_filter.return_value = None

    assert pdp.get_dim_id_filter(cmd) is None


def test_case_abac_and_ref_data_access_delegate_to_service(
    pdp: _ConcretePolicyDecisionPoint, abac_service: Mock
) -> None:
    cmd = Mock()

    assert pdp.get_case_abac(cmd) is abac_service.get_case_abac.return_value
    assert pdp.get_ref_data_access(cmd) is abac_service.get_ref_data_access.return_value
    abac_service.get_case_abac.assert_called_once_with(cmd)
    abac_service.get_ref_data_access.assert_called_once_with(cmd)

"""Regression tests for case-set association selection in CaseService."""

from test.util.mock_compat import Mock
from types import MethodType
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import model
from gen_epix.casedb.services.case.service import CaseService


@pytest.fixture
def association_service():
    service = Mock()
    service._retrieve_association_map = MethodType(
        CaseService._retrieve_association_map, service
    )
    service.repository.read_fields.return_value = [(uuid4(), uuid4())]
    return service


@pytest.mark.parametrize("empty_endpoint", ["case_set_ids", "data_collection_ids"])
@pytest.mark.parametrize("empty_kind", ["list", "generator"])
def test_empty_case_set_association_selection_does_not_read_links(
    association_service, empty_endpoint, empty_kind
):
    selection = [] if empty_kind == "list" else iter(())
    result = CaseService._retrieve_case_set_data_collections_map(
        association_service, Mock(), uuid4(), **{empty_endpoint: selection}
    )

    assert result == {}
    association_service.repository.read_fields.assert_not_called()


def test_none_case_set_selection_remains_unrestricted(association_service):
    case_set_id, collection_id = (
        association_service.repository.read_fields.return_value[0]
    )

    result = CaseService._retrieve_case_set_data_collections_map(
        association_service, Mock(), uuid4()
    )

    assert result == {case_set_id: {collection_id}}
    assert association_service.repository.read_fields.call_args.kwargs["filter"] is None


def test_nonempty_case_set_selection_keeps_both_endpoint_filters(association_service):
    case_set_id, collection_id = (
        association_service.repository.read_fields.return_value[0]
    )

    result = CaseService._retrieve_case_set_data_collections_map(
        association_service,
        Mock(),
        uuid4(),
        case_set_ids=[case_set_id],
        data_collection_ids=[collection_id],
    )

    assert result == {case_set_id: {collection_id}}
    kwargs = association_service.repository.read_fields.call_args.kwargs
    assert kwargs["model_class"] is model.CaseSetDataCollectionLink
    filters = kwargs["filter"].filters
    assert {item.key: item.members for item in filters} == {
        "case_set_id": frozenset({case_set_id}),
        "data_collection_id": frozenset({collection_id}),
    }

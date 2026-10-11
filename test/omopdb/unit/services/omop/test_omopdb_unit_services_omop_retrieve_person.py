from datetime import UTC, datetime
from test.util.mock_compat import MagicMock, Mock
from uuid import UUID

import pytest

from gen_epix.omopdb.domain.command import (
    RetrievePersonsByIdCommand,
    RetrievePersonsByQueryCommand,
)
from gen_epix.omopdb.domain.model import FullPerson, PersonQuery
from gen_epix.omopdb.services.omop.retrieve_person import (
    omop_service_retrieve_persons_by_id,
    omop_service_retrieve_persons_by_query,
)


@pytest.mark.parametrize(
    "person_ids",
    [
        pytest.param([], id="empty"),
        pytest.param([UUID("550e8400-e29b-41d4-a716-446655440001")], id="one-person"),
        pytest.param(
            [
                UUID("550e8400-e29b-41d4-a716-446655440001"),
                UUID("550e8400-e29b-41d4-a716-446655440002"),
            ],
            id="multiple-persons",
        ),
    ],
)
def test_retrieve_persons_by_id(person_ids: list[UUID]) -> None:
    service = Mock()
    service.repository = Mock()
    person_records = [Mock(spec=FullPerson)]
    service.repository.get_full_persons_by_person_ids.return_value = person_records
    command = RetrievePersonsByIdCommand(person_ids=person_ids)

    result = omop_service_retrieve_persons_by_id(service, command)

    if person_ids:
        service.repository.get_full_persons_by_person_ids.assert_called_once_with(
            person_ids
        )
        assert result is person_records
    else:
        service.repository.get_full_persons_by_person_ids.assert_not_called()
        assert result == []


@pytest.mark.parametrize(
    ("modified_since", "modified_until"),
    [
        pytest.param(datetime(2024, 1, 1, tzinfo=UTC), None, id="lower-bound"),
        pytest.param(None, datetime(2024, 2, 1, tzinfo=UTC), id="upper-bound"),
        pytest.param(
            datetime(2024, 1, 1, tzinfo=UTC),
            datetime(2024, 2, 1, tzinfo=UTC),
            id="both-bounds",
        ),
    ],
)
def test_retrieve_persons_by_query_forwards_bounds_and_returns_result(
    modified_since: datetime | None, modified_until: datetime | None
) -> None:
    service = Mock()
    service.repository = Mock()
    unit_of_work = MagicMock()
    context_manager = MagicMock()
    context_manager.__enter__.return_value = unit_of_work
    service.repository.uow.return_value = context_manager
    person_ids = [UUID("550e8400-e29b-41d4-a716-446655440001")]
    service.repository.get_person_ids_modified_in_range.return_value = person_ids
    person_query = PersonQuery(
        modified_since=modified_since,
        modified_until=modified_until,
    )
    command = RetrievePersonsByQueryCommand(person_query=person_query)

    result = omop_service_retrieve_persons_by_query(service, command)

    service.repository.uow.assert_called_once_with()
    service.repository.get_person_ids_modified_in_range.assert_called_once_with(
        uow=unit_of_work,
        modified_since=modified_since,
        modified_until=modified_until,
    )
    assert result.person_query == person_query
    assert result.person_ids == person_ids
    assert result.is_max_results_exceeded is False
    context_manager.__exit__.assert_called_once_with(None, None, None)

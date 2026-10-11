"""Test sample retrieval service functions."""

# ruff: noqa: I001

from datetime import UTC, datetime
from test.util.mock_compat import MagicMock
from types import SimpleNamespace
from uuid import uuid4

import pytest

from gen_epix.fastapp import CrudOperation
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.services.seq.retrieve_sample import (
    seq_service_retrieve_sample_identifiers_by_id,
    seq_service_retrieve_samples_by_id,
    seq_service_retrieve_samples_by_query,
)


@pytest.mark.parametrize("sample_ids", [None, []], ids=["none", "empty"])
def test_retrieve_samples_by_id_returns_empty_without_repository(sample_ids) -> None:
    """Return no samples for empty requests without querying persistence."""
    service = SimpleNamespace(repository=MagicMock())
    command = SimpleNamespace(sample_ids=sample_ids)

    assert seq_service_retrieve_samples_by_id(service, command) == []

    service.repository.get_full_samples_by_sample_ids.assert_not_called()


def test_retrieve_samples_by_id_delegates_requested_ids() -> None:
    """Return the repository's complete samples for the requested identifiers."""
    sample_ids = [uuid4(), uuid4()]
    samples = [object(), object()]
    repository = MagicMock()
    repository.get_full_samples_by_sample_ids.return_value = samples
    service = SimpleNamespace(repository=repository)
    command = SimpleNamespace(sample_ids=sample_ids)

    assert seq_service_retrieve_samples_by_id(service, command) is samples

    repository.get_full_samples_by_sample_ids.assert_called_once_with(sample_ids)


@pytest.mark.parametrize("sample_ids", [None, []], ids=["none", "empty"])
def test_retrieve_sample_identifiers_by_id_returns_empty_without_repository(
    sample_ids,
) -> None:
    """Return no identifiers for empty requests without opening a unit of work."""
    repository = MagicMock()
    service = SimpleNamespace(repository=repository)
    command = SimpleNamespace(sample_ids=sample_ids, user=None)

    assert seq_service_retrieve_sample_identifiers_by_id(service, command) == []

    repository.uow.assert_not_called()


@pytest.mark.parametrize("user_id", [None, uuid4()], ids=["anonymous", "identified"])
def test_retrieve_sample_identifiers_by_id_filters_internal_ids(user_id) -> None:
    """Read identifiers by the requested sample IDs and pass the current user."""
    sample_ids = [uuid4(), uuid4()]
    user = SimpleNamespace(id=user_id) if user_id is not None else None
    repository = MagicMock()
    uow = repository.uow.return_value.__enter__.return_value
    identifiers = [object()]
    repository.crud.return_value = identifiers
    service = SimpleNamespace(repository=repository)
    command = SimpleNamespace(sample_ids=sample_ids, user=user)
    expected_filter = UuidSetFilter(key="internal_id", members=frozenset(sample_ids))

    assert (
        seq_service_retrieve_sample_identifiers_by_id(service, command) is identifiers
    )

    repository.crud.assert_called_once_with(
        uow,
        user_id,
        model.SampleIdentifier,
        CrudOperation.READ_ALL,
        filter=expected_filter,
    )


@pytest.mark.parametrize(
    ("modified_since", "modified_until"),
    [
        (datetime(2024, 1, 1, tzinfo=UTC), datetime(2024, 2, 1, tzinfo=UTC)),
        (datetime(2024, 1, 1, tzinfo=UTC), None),
        (None, datetime(2024, 2, 1, tzinfo=UTC)),
    ],
    ids=["bounded", "since-only", "until-only"],
)
def test_retrieve_samples_by_query_forwards_range_and_reports_all_results(
    modified_since, modified_until
) -> None:
    """Forward optional time bounds and return all matching IDs as untruncated."""
    sample_query = model.SampleQuery(
        modified_since=modified_since,
        modified_until=modified_until,
    )
    sample_ids = [uuid4(), uuid4()]
    repository = MagicMock()
    uow = repository.uow.return_value.__enter__.return_value
    repository.get_sample_ids_modified_in_range.return_value = sample_ids
    service = SimpleNamespace(repository=repository)
    command = SimpleNamespace(sample_query=sample_query)

    result = seq_service_retrieve_samples_by_query(service, command)

    assert result == model.SampleQueryResult(
        sample_query=sample_query,
        sample_ids=sample_ids,
        is_max_results_exceeded=False,
    )
    repository.get_sample_ids_modified_in_range.assert_called_once_with(
        uow=uow,
        modified_since=modified_since,
        modified_until=modified_until,
    )

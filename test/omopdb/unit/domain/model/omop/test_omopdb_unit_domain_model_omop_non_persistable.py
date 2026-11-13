from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.omopdb.domain.model.omop.clinical_data import Person
from gen_epix.omopdb.domain.model.omop.non_persistable import (
    FullPerson,
    PersonQuery,
    PersonQueryResult,
    SpecimenIdsByCohortResult,
)


def test_specimen_ids_by_cohort_result_accepts_empty_and_populated_mappings():
    """Retain empty cohort results and supplied specimen identifiers."""
    cohort_id = uuid4()
    specimen_id = uuid4()

    assert (
        SpecimenIdsByCohortResult(
            specimen_ids_by_cohort_id={}
        ).specimen_ids_by_cohort_id
        == {}
    )
    assert SpecimenIdsByCohortResult(
        specimen_ids_by_cohort_id={cohort_id: [specimen_id]}
    ).specimen_ids_by_cohort_id == {cohort_id: [specimen_id]}


@pytest.mark.parametrize(
    ("query_values", "is_valid"),
    [
        pytest.param({}, False, id="no-time-bounds"),
        pytest.param({"label": "label only"}, False, id="label-is-not-a-bound"),
        pytest.param(
            {"modified_since": datetime(2025, 1, 1, tzinfo=timezone.utc)},
            True,
            id="lower-bound-only",
        ),
        pytest.param(
            {"modified_until": datetime(2025, 1, 2, tzinfo=timezone.utc)},
            True,
            id="upper-bound-only",
        ),
        pytest.param(
            {
                "modified_since": datetime(2025, 1, 1, tzinfo=timezone.utc),
                "modified_until": datetime(2025, 1, 2, tzinfo=timezone.utc),
            },
            True,
            id="both-bounds",
        ),
    ],
)
def test_person_query_requires_at_least_one_time_bound(query_values, is_valid):
    """Reject unbounded queries and accept either or both time bounds."""
    if is_valid:
        assert PersonQuery(**query_values)
    else:
        with pytest.raises(
            ValidationError, match="At least one criterion must be provided"
        ):
            PersonQuery(**query_values)


@pytest.mark.parametrize("is_max_results_exceeded", [False, True])
def test_person_query_result_preserves_query_ids_and_limit_flag(
    is_max_results_exceeded,
):
    """Preserve the query, matching identifiers, and limit status."""
    query = PersonQuery(modified_since=datetime(2025, 1, 1, tzinfo=timezone.utc))
    person_ids = [uuid4(), uuid4()]

    result = PersonQueryResult(
        person_query=query,
        person_ids=person_ids,
        is_max_results_exceeded=is_max_results_exceeded,
    )

    assert result.person_query is query
    assert result.person_ids == person_ids
    assert result.is_max_results_exceeded is is_max_results_exceeded


def test_full_person_maps_all_related_fields_and_uses_independent_list_defaults():
    """Keep the repository maps complete and list defaults independent."""
    data_classes = set(FullPerson.DATA_CLASSES)
    identifier_classes = set(FullPerson.IDENTIFIER_CLASSES)
    related_field_names = (
        set(FullPerson.DATA_CLASS_FIELD_MAP.values())
        | set(FullPerson.IDENTIFIER_FIELD_MAP.values())
        | {"person_identifiers"}
    )

    assert data_classes == set(FullPerson.DATA_CLASS_FIELD_MAP)
    assert data_classes == set(FullPerson.DATA_IDENTIFIER_CLASS_MAP)
    assert identifier_classes == set(FullPerson.IDENTIFIER_FIELD_MAP)
    assert set(FullPerson.DATA_IDENTIFIER_CLASS_MAP.values()) == identifier_classes
    assert related_field_names <= set(FullPerson.model_fields) - {"id", "person"}

    first = FullPerson(person=Person.model_construct())
    second = FullPerson(person=Person.model_construct())
    for field_name in related_field_names:
        first_value = getattr(first, field_name)
        second_value = getattr(second, field_name)
        assert first_value == []
        assert second_value == []
        assert first_value is not second_value

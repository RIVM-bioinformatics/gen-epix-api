"""Check OMOP person upload result discriminator registration."""

from uuid import uuid4

import pytest

from gen_epix.commondb.domain.model.upload import (
    UploadResult,
    UploadResultWithIdentifiers,
)
from gen_epix.etl.model import Result
from gen_epix.omopdb.domain.model.omop.upload import (
    PersonBatchForUpload,
    PersonBatchUploadResult,
    PersonForUpload,
    PersonUploadResult,
)


@pytest.mark.parametrize(
    ("result_class", "expected_result_id"),
    [
        (PersonUploadResult, "c6dd271e"),
        (PersonBatchUploadResult, "3d81faf1"),
    ],
    ids=["person", "person-batch"],
)
def test_result_id_is_registered_for_polymorphic_deserialization(
    result_class: type[Result], expected_result_id: str
) -> None:
    assert result_class.RESULT_ID == expected_result_id
    assert Result._SUBCLASS_REGISTRY[expected_result_id] is result_class
    assert "RESULT_ID" not in result_class.model_fields


def test_person_batch_merge_concatenates_persons_in_order() -> None:
    first, second, third = PersonForUpload(), PersonForUpload(), PersonForUpload()
    batch_a = PersonBatchForUpload(persons=[first, second])
    batch_b = PersonBatchForUpload(persons=[third])

    result = PersonBatchForUpload.merge([batch_a, batch_b])

    assert result.persons == [first, second, third]
    assert result.id not in (batch_a.id, batch_b.id)


def test_person_batch_merge_rejects_empty_sequence() -> None:
    with pytest.raises(ValueError, match="empty"):
        PersonBatchForUpload.merge([])


def test_person_batch_merge_rejects_duplicate_person_ids() -> None:
    shared_id = uuid4()
    batch_a = PersonBatchForUpload(persons=[PersonForUpload(id=shared_id)])
    batch_b = PersonBatchForUpload(persons=[PersonForUpload(id=shared_id)])

    with pytest.raises(ValueError, match="Duplicate parent IDs"):
        PersonBatchForUpload.merge([batch_a, batch_b])


def test_person_batch_subset_keeps_matching_persons() -> None:
    first, second = PersonForUpload(), PersonForUpload()
    batch = PersonBatchForUpload(persons=[first, second])

    result = batch.subset(lambda person: person is first)

    assert result.persons == [first]


def test_person_batch_summarizes_child_counts_and_distributions() -> None:
    first = PersonForUpload.model_construct(
        specimens=[object(), object()],
        observations=None,
        measurements=[object()],
    )
    second = PersonForUpload.model_construct(
        specimens=[],
        observations=[object(), object(), object()],
        measurements=None,
    )
    third = PersonForUpload.model_construct()
    batch = PersonBatchForUpload.model_construct(persons=[first, second, third])

    assert batch.has_specimens is True
    assert batch.has_observations is True
    assert batch.has_measurements is True
    assert batch.total_persons() == 3
    assert batch.total_specimens() == 2
    assert batch.total_observations() == 3
    assert batch.total_measurements() == 1
    assert batch.specimen_distribution() == {2: 1, 0: 2}
    assert batch.observation_distribution() == {0: 2, 3: 1}
    assert batch.measurement_distribution() == {1: 1, 0: 2}
    assert batch.upload_summary() == {
        "totals": {
            "persons": 3,
            "specimens": 2,
            "observations": 3,
            "measurements": 1,
        },
        "distributions": {
            "specimens": {2: 1, 0: 2},
            "observations": {0: 2, 3: 1},
            "measurements": {1: 1, 0: 2},
        },
    }


def test_empty_person_batch_has_no_child_counts_or_distributions() -> None:
    batch = PersonBatchForUpload.model_construct(persons=[])

    assert batch.has_specimens is False
    assert batch.has_observations is False
    assert batch.has_measurements is False
    assert batch.total_persons() == 0
    assert batch.specimen_distribution() == {}
    assert batch.observation_distribution() == {}
    assert batch.measurement_distribution() == {}
    assert batch.upload_summary() == {
        "totals": {
            "persons": 0,
            "specimens": 0,
            "observations": 0,
            "measurements": 0,
        },
        "distributions": {
            "specimens": {},
            "observations": {},
            "measurements": {},
        },
    }


def test_person_upload_result_aggregates_errors_from_all_result_categories() -> None:
    identifier_result = UploadResult()
    identifier_result.add_error("identifier-error", "Identifier failed")
    child_results = [UploadResultWithIdentifiers() for _ in range(4)]
    for index, child_result in enumerate(child_results):
        child_result.add_error(f"child-error-{index}", "Child failed")
    result = PersonUploadResult(
        identifiers=[identifier_result],
        specimens=[child_results[0]],
        observations=[child_results[1]],
        measurements=[child_results[2]],
        measurement_relations=[child_results[3]],
    )
    result.add_error("person-error", "Person failed")

    errors = result.get_errors()

    assert [error.code for error in errors] == [
        "person-error",
        "identifier-error",
        "child-error-0",
        "child-error-1",
        "child-error-2",
        "child-error-3",
    ]


def test_person_upload_result_without_nested_results_returns_only_own_errors() -> None:
    result = PersonUploadResult()

    assert result.get_errors() == []

    result.add_error("person-error", "Person failed")

    assert [error.code for error in result.get_errors()] == ["person-error"]

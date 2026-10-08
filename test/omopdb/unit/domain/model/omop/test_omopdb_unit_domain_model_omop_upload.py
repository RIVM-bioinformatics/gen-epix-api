"""Check OMOP person upload result discriminator registration."""

from uuid import uuid4

import pytest

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

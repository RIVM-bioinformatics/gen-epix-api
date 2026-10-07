"""Unit tests for PersonBatchForUpload.merge (inherited from BaseBatchForUpload).

PersonBatchForUpload carries no allele-like extra state, so unlike
SampleBatchForUpload it needs no override at all -- these tests exist to
confirm the base-class merge/subset contract (see
test/commondb/unit/upload/test_batch_subset_merge.py) actually works through
a second, independent subclass rather than only the minimal test harness.
"""

from uuid import uuid4

import pytest

from gen_epix.omopdb.domain.model.omop import PersonBatchForUpload, PersonForUpload


def make_batch(persons: list[PersonForUpload]) -> PersonBatchForUpload:
    return PersonBatchForUpload(persons=persons)


class TestPersonBatchForUploadMerge:
    def test_merge_concatenates_persons_in_order(self) -> None:
        p1, p2, p3 = PersonForUpload(), PersonForUpload(), PersonForUpload()
        batch_a = make_batch([p1, p2])
        batch_b = make_batch([p3])

        result = PersonBatchForUpload.merge([batch_a, batch_b])

        assert result.persons == [p1, p2, p3]
        assert result.id not in (batch_a.id, batch_b.id)

    def test_merge_empty_sequence_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            PersonBatchForUpload.merge([])

    def test_merge_duplicate_person_id_raises(self) -> None:
        shared_id = uuid4()
        batch_a = make_batch([PersonForUpload(id=shared_id)])
        batch_b = make_batch([PersonForUpload(id=shared_id)])

        with pytest.raises(ValueError, match="Duplicate parent IDs"):
            PersonBatchForUpload.merge([batch_a, batch_b])

    def test_subset_keeps_whole_persons(self) -> None:
        p1, p2 = PersonForUpload(), PersonForUpload()
        batch = make_batch([p1, p2])

        result = batch.subset(lambda p: p is p1)

        assert result.persons == [p1]

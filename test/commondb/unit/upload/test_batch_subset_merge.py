"""Unit tests for ``BaseBatchForUpload.subset`` / ``subset_by_index`` / ``merge``.

Reuses the Parent/Child1/Child2 harness in ``model.py`` -- a minimal,
non-seqdb-specific domain that exercises exactly the base-class contract
(whole-parent granularity, symmetric merge, full re-validation) without any
allele-specific handling (covered separately for ``SampleBatchForUpload``).
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import IdentifierForUpload
from test.commondb.unit.upload.model import (
    Child1ForUpload,
    Child2ForUpload,
    Parent,
    ParentBatchForUpload,
)
from test.commondb.unit.upload.model import ParentForUpload as FixtureParentForUpload


def make_parent(
    parent_id: UUID | None = None,
    identifiers: list[IdentifierForUpload] | None = None,
    children1: list[Child1ForUpload] | None = None,
    children2: list[Child2ForUpload] | None = None,
) -> FixtureParentForUpload:
    return FixtureParentForUpload(
        id=parent_id,
        identifiers=identifiers,
        children1=children1,
        children2=children2,
        parent=Parent(a="a"),
    )


def make_batch(parents: list[FixtureParentForUpload]) -> ParentBatchForUpload:
    return ParentBatchForUpload(parents=parents)


class TestSubset:
    def test_keeps_whole_parents_matching_predicate(self) -> None:
        p1 = make_parent()
        p2 = make_parent()
        batch = make_batch([p1, p2])

        result = batch.subset(lambda p: p is p1)

        assert result.parents == [p1]

    def test_preserves_order(self) -> None:
        p1, p2, p3 = make_parent(), make_parent(), make_parent()
        batch = make_batch([p1, p2, p3])

        result = batch.subset(lambda p: p is not p2)

        assert result.parents == [p1, p3]

    def test_subset_to_zero(self) -> None:
        batch = make_batch([make_parent(), make_parent()])

        result = batch.subset(lambda p: False)

        assert result.parents == []

    def test_by_index_selects_and_preserves_given_order(self) -> None:
        p1, p2, p3 = make_parent(), make_parent(), make_parent()
        batch = make_batch([p1, p2, p3])

        result = batch.subset_by_index([2, 0])

        assert result.parents == [p3, p1]

    def test_default_id_and_created_at_are_fresh(self) -> None:
        batch = make_batch([make_parent()])

        result = batch.subset(lambda p: True)

        assert result.id != batch.id
        assert result.created_at != batch.created_at

    def test_explicit_id_and_created_at_are_used(self) -> None:
        batch = make_batch([make_parent()])
        new_id = uuid4()
        new_created_at = datetime(2020, 1, 1, tzinfo=UTC)

        result = batch.subset(lambda p: True, id=new_id, created_at=new_created_at)

        assert result.id == new_id
        assert result.created_at == new_created_at


class TestMerge:
    def test_concatenates_parents_in_order(self) -> None:
        p1, p2, p3 = make_parent(), make_parent(), make_parent()
        batch_a = make_batch([p1, p2])
        batch_b = make_batch([p3])

        result = ParentBatchForUpload.merge([batch_a, batch_b])

        assert result.parents == [p1, p2, p3]

    def test_empty_sequence_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            ParentBatchForUpload.merge([])

    def test_foreign_class_raises(self) -> None:
        class OtherBatch(ParentBatchForUpload):
            pass

        batch_a = make_batch([make_parent()])
        batch_b = OtherBatch(parents=[make_parent()])

        with pytest.raises(ValueError, match="type"):
            ParentBatchForUpload.merge([batch_a, batch_b])

    def test_duplicate_parent_id_raises(self) -> None:
        shared_id = uuid4()
        batch_a = make_batch([make_parent(parent_id=shared_id)])
        batch_b = make_batch([make_parent(parent_id=shared_id)])

        with pytest.raises(ValueError, match="Duplicate parent IDs"):
            ParentBatchForUpload.merge([batch_a, batch_b])

    def test_duplicate_identifier_raises(self) -> None:
        identifier = IdentifierForUpload(
            identifier_issuer_id=uuid4(), external_id="shared"
        )
        batch_a = make_batch([make_parent(identifiers=[identifier])])
        batch_b = make_batch([make_parent(identifiers=[identifier])])

        with pytest.raises(ValueError, match="Duplicate parent identifiers"):
            ParentBatchForUpload.merge([batch_a, batch_b])

    def test_cross_parent_intra_parent_link_raises(self) -> None:
        # Child1 X lives under parent 1 in batch A; Child2 links to X but lives
        # under parent 2 in batch B. Neither source batch violates the
        # intra-parent-link rule on its own (X isn't present in batch B, so
        # it's assumed to point at an already-stored child) - only the merge,
        # which brings both into the same batch, does.
        shared_child1_id = uuid4()
        parent1 = make_parent(
            children1=[Child1ForUpload(child1_id=shared_child1_id, ref1_code="r1")]
        )
        parent2 = make_parent(
            children2=[
                Child2ForUpload(child1_id=shared_child1_id, ref2_id=NULL_ID)
            ]
        )
        batch_a = make_batch([parent1])
        batch_b = make_batch([parent2])

        with pytest.raises(ValueError, match="Inconsistent intra-parent link"):
            ParentBatchForUpload.merge([batch_a, batch_b])

    def test_default_id_and_created_at_are_fresh(self) -> None:
        batch_a = make_batch([make_parent()])
        batch_b = make_batch([make_parent()])

        result = ParentBatchForUpload.merge([batch_a, batch_b])

        assert result.id not in (batch_a.id, batch_b.id)

    def test_explicit_id_and_created_at_are_used(self) -> None:
        batch_a = make_batch([make_parent()])
        batch_b = make_batch([make_parent()])
        new_id = uuid4()
        new_created_at = datetime(2020, 1, 1, tzinfo=UTC)

        result = ParentBatchForUpload.merge(
            [batch_a, batch_b], id=new_id, created_at=new_created_at
        )

        assert result.id == new_id
        assert result.created_at == new_created_at

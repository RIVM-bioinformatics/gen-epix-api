"""Check upload result identifiers and model fields."""

from datetime import UTC, datetime
from test.commondb.unit.upload.model import (
    Child1,
    Child1ForUpload,
    Child2,
    Child2ForUpload,
    Parent,
    ParentBatchForUpload,
)
from test.commondb.unit.upload.model import ParentForUpload as FixtureParentForUpload
from typing import ClassVar
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import IdentifierForUpload
from gen_epix.commondb.domain.model.upload import (
    BaseBatchUploadResult,
    ParentForUpload,
    ParentUploadResult,
    UploadResult,
    UploadResultWithIdentifiers,
)
from gen_epix.etl.enum import EtlStatus
from gen_epix.etl.model import LogItem, Result
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.fastapp.enum import LogLevel


@pytest.mark.parametrize(
    ("result_class", "expected_result_id"),
    [
        (UploadResult, "c4f1a9e2"),
        (UploadResultWithIdentifiers, "06e14d51"),
        (ParentUploadResult, "f354e913"),
        (BaseBatchUploadResult, "6d64fbc3"),
    ],
    ids=["upload", "with-identifiers", "parent", "batch"],
)
def test_result_id_is_registered_and_object_id_remains_a_field(
    result_class: type[Result], expected_result_id: str
) -> None:
    assert result_class.RESULT_ID == expected_result_id
    assert Result._SUBCLASS_REGISTRY[expected_result_id] is result_class
    assert "id" in result_class.model_fields
    assert "RESULT_ID" not in result_class.model_fields


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
        parent1 = make_parent()
        parent2 = make_parent()
        batch = make_batch([parent1, parent2])

        result = batch.subset(lambda parent: parent is parent1)

        assert result.parents == [parent1]

    def test_preserves_order(self) -> None:
        parent1, parent2, parent3 = make_parent(), make_parent(), make_parent()
        batch = make_batch([parent1, parent2, parent3])

        result = batch.subset(lambda parent: parent is not parent2)

        assert result.parents == [parent1, parent3]

    def test_subset_to_zero(self) -> None:
        batch = make_batch([make_parent(), make_parent()])

        result = batch.subset(lambda parent: False)

        assert result.parents == []

    def test_by_index_selects_and_preserves_given_order(self) -> None:
        parent1, parent2, parent3 = make_parent(), make_parent(), make_parent()
        batch = make_batch([parent1, parent2, parent3])

        result = batch.subset_by_index([2, 0])

        assert result.parents == [parent3, parent1]

    def test_default_id_and_created_at_are_fresh(self) -> None:
        batch = make_batch([make_parent()])

        result = batch.subset(lambda parent: True)

        assert result.id != batch.id
        assert result.created_at != batch.created_at

    def test_explicit_id_and_created_at_are_used(self) -> None:
        batch = make_batch([make_parent()])
        new_id = uuid4()
        new_created_at = datetime(2020, 1, 1, tzinfo=UTC)

        result = batch.subset(lambda parent: True, id=new_id, created_at=new_created_at)

        assert result.id == new_id
        assert result.created_at == new_created_at


class TestMerge:
    def test_concatenates_parents_in_order(self) -> None:
        parent1, parent2, parent3 = make_parent(), make_parent(), make_parent()
        batch_a = make_batch([parent1, parent2])
        batch_b = make_batch([parent3])

        result = ParentBatchForUpload.merge([batch_a, batch_b])

        assert result.parents == [parent1, parent2, parent3]

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
        shared_child1_id = uuid4()
        parent1 = make_parent(
            children1=[Child1ForUpload(child1_id=shared_child1_id, ref1_code="r1")]
        )
        parent2 = make_parent(
            children2=[Child2ForUpload(child1_id=shared_child1_id, ref2_id=NULL_ID)]
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


class TestChildOrderDerivation:
    """Verify ParentForUpload derives a valid foreign-key dependency order."""

    def test_base_class_has_no_children(self) -> None:
        assert ParentForUpload.get_child_order() == []

    def test_derived_from_entity_link(self) -> None:
        assert FixtureParentForUpload.get_child_order() == [Child1, Child2]
        assert FixtureParentForUpload.__dict__.get("CHILD_ORDER") == [Child1, Child2]

    def test_reordering_is_derived_not_coincidental(self) -> None:
        class ReversedParentForUpload(FixtureParentForUpload):
            NAME: ClassVar = "ReversedParentForUpload"
            CHILDREN_FIELD_NAME_MAP: ClassVar = {
                Child2: "children2",
                Child1: "children1",
            }
            CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar = {
                Child2: Child2ForUpload,
                Child1: Child1ForUpload,
            }

        assert ReversedParentForUpload.get_child_order() == [Child1, Child2]

    def test_unconstrained_children_keep_relative_order_within_a_layer(self) -> None:
        from gen_epix.commondb.domain.model import Model

        class A(Model):
            ENTITY: ClassVar = Entity(persistable=True, id_field_name="a_id")
            NAME: ClassVar = "ChildOrderA"
            a_id: UUID | None = None

        class B(Model):
            ENTITY: ClassVar = Entity(persistable=True, id_field_name="b_id")
            NAME: ClassVar = "ChildOrderB"
            b_id: UUID | None = None

        class C(Model):
            ENTITY: ClassVar = Entity(persistable=True, id_field_name="c_id")
            NAME: ClassVar = "ChildOrderC"
            c_id: UUID | None = None

        class D(Model):
            ENTITY: ClassVar = Entity(
                persistable=True,
                id_field_name="d_id",
                links=create_links({1: ("b_id", B, None)}),
            )
            NAME: ClassVar = "ChildOrderD"
            d_id: UUID | None = None
            b_id: UUID | None = None

        class P(ParentForUpload):
            NAME: ClassVar = "ChildOrderLayerParent"
            CHILDREN_FIELD_NAME_MAP: ClassVar = {A: "aa", D: "dd", B: "bb", C: "cc"}
            CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar = {A: A, D: D, B: B, C: C}

        assert P.get_child_order() == [A, B, C, D]

    def test_explicit_override_is_returned_verbatim(self) -> None:
        class OverriddenParentForUpload(FixtureParentForUpload):
            NAME: ClassVar = "OverriddenParentForUpload"
            CHILD_ORDER: ClassVar = [Child2, Child1]

        assert OverriddenParentForUpload.get_child_order() == [Child2, Child1]

    def test_incomplete_override_raises(self) -> None:
        class MissingChildParentForUpload(FixtureParentForUpload):
            NAME: ClassVar = "MissingChildParentForUpload"
            CHILD_ORDER: ClassVar = [Child1]

        with pytest.raises(ValueError, match="permutation"):
            MissingChildParentForUpload.get_child_order()

    def test_override_with_duplicate_child_raises(self) -> None:
        class DuplicateChildParentForUpload(FixtureParentForUpload):
            NAME: ClassVar = "DuplicateChildParentForUpload"
            CHILD_ORDER: ClassVar = [Child1, Child1, Child2]

        with pytest.raises(ValueError, match="duplicates"):
            DuplicateChildParentForUpload.get_child_order()

    def test_cycle_falls_back_to_declaration_order_with_warning(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        from gen_epix.commondb.domain.model import Model

        class CycA(Model):
            ENTITY: ClassVar = Entity(persistable=True, id_field_name="a_id")
            NAME: ClassVar = "ChildOrderCycA"
            a_id: UUID | None = None
            b_id: UUID | None = None

        class CycB(Model):
            ENTITY: ClassVar = Entity(persistable=True, id_field_name="b_id")
            NAME: ClassVar = "ChildOrderCycB"
            b_id: UUID | None = None
            a_id: UUID | None = None

        CycA.ENTITY.links.update(create_links({1: ("b_id", CycB, None)}))
        CycB.ENTITY.links.update(create_links({1: ("a_id", CycA, None)}))

        class CycParent(ParentForUpload):
            NAME: ClassVar = "ChildOrderCycParent"
            CHILDREN_FIELD_NAME_MAP: ClassVar = {CycA: "aa", CycB: "bb"}
            CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar = {CycA: CycA, CycB: CycB}

        with caplog.at_level("WARNING"):
            order = CycParent.get_child_order()
        assert order == [CycA, CycB]
        assert "cyclic foreign keys" in caplog.text


class TestUploadResultLogs:
    def setup_method(self) -> None:
        self.result = UploadResult.model_construct(
            id=None,
            status=EtlStatus.PENDING,
            is_new=False,
            logs=[],
        )

    def test_upload_log_item_is_shared_etl_log_item(self) -> None:
        from gen_epix.commondb.domain.model.upload import UploadLogItem

        assert UploadLogItem is LogItem

    def test_add_error_sets_failed_and_is_queryable(self) -> None:
        self.result.add_error("E001", "upload broke")
        assert self.result.status is EtlStatus.FAILED
        assert self.result.has_errors()

    @pytest.mark.parametrize(
        ("method", "severity", "code"),
        [
            ("add_warning", LogLevel.WARN, "W001"),
            ("add_info", LogLevel.INFO, "I001"),
        ],
    )
    def test_non_error_log_does_not_change_status(
        self, method: str, severity: LogLevel, code: str
    ) -> None:
        getattr(self.result, method)(code, "message")
        assert self.result.status is EtlStatus.PENDING
        assert self.result.logs[0].severity is severity

    def test_add_logs_list_with_error_sets_failed(self) -> None:
        self.result.add_logs(
            [
                LogItem(code="W001", message="warn", severity=LogLevel.WARN),
                LogItem(code="E001", message="err", severity=LogLevel.ERROR),
            ]
        )
        assert self.result.status is EtlStatus.FAILED
        assert len(self.result.logs) == 2

    def test_add_logs_list_without_error_keeps_status(self) -> None:
        self.result.add_logs(
            [
                LogItem(code="I001", message="info", severity=LogLevel.INFO),
                LogItem(code="W001", message="warn", severity=LogLevel.WARN),
            ]
        )
        assert self.result.status is EtlStatus.PENDING

    def test_add_logs_single_error_sets_failed(self) -> None:
        item = LogItem(code="E001", message="err", severity=LogLevel.ERROR)
        self.result.add_logs(item)
        assert self.result.status is EtlStatus.FAILED

    def test_add_logs_single_non_error_keeps_status(self) -> None:
        item = LogItem(code="W001", message="warn", severity=LogLevel.WARN)
        self.result.add_logs(item)
        assert self.result.status is EtlStatus.PENDING

    def test_log_code_query_works_on_upload_result(self) -> None:
        self.result.add_warning("SPECIFIC_CODE", "msg")
        assert self.result.has_log_code("SPECIFIC_CODE")
        assert not self.result.has_log_code("OTHER_CODE")

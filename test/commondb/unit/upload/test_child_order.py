"""Unit tests for ``ParentForUpload.CHILD_ORDER`` / ``get_child_order``.

These cover the foreign-key dependency ordering of children that
``BatchUploader`` relies on so a child that links to a sibling child is never
created before that sibling (which would raise a DB foreign-key error).
"""

from test.commondb.unit.upload.model import (
    Child1,
    Child1ForUpload,
    Child2,
    Child2ForUpload,
)
from test.commondb.unit.upload.model import ParentForUpload as FixtureParentForUpload
from test.commondb.unit.upload.test_commondb_upload import BaseUploadTestCase
from typing import ClassVar
from uuid import UUID

import pytest

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.upload import ParentForUpload
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.fastapp.enum import CrudOperation


class TestChildOrderDerivation:
    """The order is derived from the child models' relations, not hand-set."""

    def test_base_class_has_no_children(self) -> None:
        assert ParentForUpload.get_child_order() == []

    def test_derived_from_entity_link(self) -> None:
        # model.py declares Child1 before Child2 and Child2.child1_id -> Child1.
        assert FixtureParentForUpload.get_child_order() == [Child1, Child2]
        # __pydantic_init_subclass__ materialised it as a real class attribute.
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

        # Declared Child2-first, but the FK forces Child1 first.
        assert ReversedParentForUpload.get_child_order() == [Child1, Child2]

    def test_independent_children_keep_declaration_order(self) -> None:
        class A(Model):
            ENTITY: ClassVar = Entity(persistable=True, id_field_name="a_id")
            NAME: ClassVar = "ChildOrderA"
            a_id: UUID | None = None

        class B(Model):
            ENTITY: ClassVar = Entity(persistable=True, id_field_name="b_id")
            NAME: ClassVar = "ChildOrderB"
            b_id: UUID | None = None

        class C(Model):
            ENTITY: ClassVar = Entity(
                persistable=True,
                id_field_name="c_id",
                links=create_links({1: ("a_id", A, None)}),
            )
            NAME: ClassVar = "ChildOrderC"
            c_id: UUID | None = None
            a_id: UUID | None = None

        class P(ParentForUpload):
            NAME: ClassVar = "ChildOrderIndependentParent"
            CHILDREN_FIELD_NAME_MAP: ClassVar = {A: "aa", B: "bb", C: "cc"}
            CHILD_FOR_UPLOAD_CLASS_MAP: ClassVar = {A: A, B: B, C: C}

        # Only C -> A is constrained; B keeps its declared slot.
        assert P.get_child_order() == [A, B, C]

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


class TestChildOrderCreateOrdering(BaseUploadTestCase):
    """The uploader creates children in the derived order end-to-end."""

    def test_children_are_created_in_child_order(self) -> None:
        # Child2 links to sibling Child1 (see model.py), so CHILD_ORDER puts
        # Child1 first; the uploader must create Child1 before Child2 regardless
        # of the order the payload happens to list them in.
        existing_ref1 = self.create_ref1(self.ref1_id, "test_ref1_code")
        existing_ref2 = self.create_ref2(self.ref2_id, "test_ref2_code")
        child1_for_upload = self.create_child1_for_upload(ref1_code=existing_ref1.code)
        child2_for_upload = self.create_child2_for_upload(ref2_code=existing_ref2.code)
        parent_for_upload = self.create_parent_for_upload(
            children1=[child1_for_upload], children2=[child2_for_upload]
        )

        created_parent_id = self.random_ids[0]
        created_child1_id = self.random_ids[1]
        created_child2_id = self.random_ids[2]
        self.service.generate_id.side_effect = [
            created_parent_id,
            created_child1_id,
            created_child2_id,
        ]
        self.service.repository.crud.side_effect = [
            [created_parent_id],  # create parents
            [created_child1_id],  # create children1
            [created_child2_id],  # create children2
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_ref1.id, existing_ref1.code)],
        ]
        self.service.app.handle.side_effect = [
            [existing_ref2],
        ]

        batch_result = self.upload_batch(parent_for_upload)
        self.expectBatchProcessed(batch_result)

        created_model_classes = [
            call.args[2]
            for call in self.service.repository.crud.call_args_list
            if len(call.args) > 3 and call.args[3] == CrudOperation.CREATE_SOME
        ]
        assert created_model_classes.index(Child1) < created_model_classes.index(Child2)

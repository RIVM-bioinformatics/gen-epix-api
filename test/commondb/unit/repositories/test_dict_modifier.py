"""
Unit tests for CommondbDictModelModifier.

Verifies that:
- on_create stamps created_at, modified_at with the timestamp-factory result
  and sets modified_by to the user_id.
- on_update preserves created_at from the stored object, stamps modified_at
  with the timestamp-factory result, and sets modified_by to the user_id.
- Both methods work when user_id is None.
- The default timestamp_factory produces UTC-aware datetimes.
"""

import datetime
from test.commondb.unit.conftest import DEFAULT_CREATED_AT, DEFAULT_MODIFIED_AT
from unittest import TestCase
from uuid import uuid4

from gen_epix.commondb.domain.model.base import ModelNoId
from gen_epix.commondb.repositories.dict_modifier import CommondbDictModelModifier


_FIXED_NOW = datetime.datetime(2024, 6, 15, 12, 0, 0, tzinfo=datetime.timezone.utc)


def _fixed_factory() -> datetime.datetime:
    return _FIXED_NOW


def _make_obj(
    created_at: datetime.datetime | None = DEFAULT_CREATED_AT,
    modified_at: datetime.datetime | None = DEFAULT_MODIFIED_AT,
    modified_by: object = None,
) -> ModelNoId:
    return ModelNoId(created_at=created_at, modified_at=modified_at, modified_by=modified_by)


class TestCommondbDictModelModifier(TestCase):

    def setUp(self) -> None:
        self.user_id = uuid4()
        self.modifier = CommondbDictModelModifier(timestamp_factory=_fixed_factory)

    # ------------------------------------------------------------------ on_create

    def test_on_create_sets_created_at(self) -> None:
        # 1. Input
        obj = _make_obj(created_at=None, modified_at=None)

        # 2. Mocks (none)

        # 3. Execute
        self.modifier.on_create(self.user_id, obj)

        # 4. Verify
        assert obj.created_at == _FIXED_NOW

    def test_on_create_sets_modified_at(self) -> None:
        # 1. Input
        obj = _make_obj(created_at=None, modified_at=None)

        # 2. Mocks (none)

        # 3. Execute
        self.modifier.on_create(self.user_id, obj)

        # 4. Verify
        assert obj.modified_at == _FIXED_NOW

    def test_on_create_created_at_and_modified_at_are_equal(self) -> None:
        # 1. Input
        obj = _make_obj(created_at=None, modified_at=None)

        # 2. Mocks (none)

        # 3. Execute
        self.modifier.on_create(self.user_id, obj)

        # 4. Verify — both come from a single factory call
        assert obj.created_at == obj.modified_at

    def test_on_create_sets_modified_by(self) -> None:
        # 1. Input
        obj = _make_obj()

        # 2. Mocks (none)

        # 3. Execute
        self.modifier.on_create(self.user_id, obj)

        # 4. Verify
        assert obj.modified_by == self.user_id

    def test_on_create_with_none_user_id(self) -> None:
        # 1. Input
        obj = _make_obj()

        # 2. Mocks (none)

        # 3. Execute
        self.modifier.on_create(None, obj)

        # 4. Verify
        assert obj.modified_by is None
        assert obj.created_at == _FIXED_NOW

    # ------------------------------------------------------------------ on_update

    def test_on_update_preserves_created_at_from_stored_obj(self) -> None:
        # 1. Input
        original_created_at = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
        obj = _make_obj(created_at=datetime.datetime(2099, 1, 1, tzinfo=datetime.timezone.utc))
        stored_obj = _make_obj(created_at=original_created_at)

        # 2. Mocks (none)

        # 3. Execute
        self.modifier.on_update(self.user_id, obj, stored_obj)

        # 4. Verify — incoming obj's created_at overwritten with stored value
        assert obj.created_at == original_created_at

    def test_on_update_sets_modified_at_to_now(self) -> None:
        # 1. Input
        obj = _make_obj()
        stored_obj = _make_obj()

        # 2. Mocks (none)

        # 3. Execute
        self.modifier.on_update(self.user_id, obj, stored_obj)

        # 4. Verify
        assert obj.modified_at == _FIXED_NOW

    def test_on_update_sets_modified_by(self) -> None:
        # 1. Input
        obj = _make_obj()
        stored_obj = _make_obj()

        # 2. Mocks (none)

        # 3. Execute
        self.modifier.on_update(self.user_id, obj, stored_obj)

        # 4. Verify
        assert obj.modified_by == self.user_id

    def test_on_update_does_not_touch_stored_obj(self) -> None:
        # 1. Input
        obj = _make_obj()
        stored_created_at = stored_obj_created_at = DEFAULT_CREATED_AT
        stored_obj = _make_obj(created_at=stored_created_at)

        # 2. Mocks (none)

        # 3. Execute
        self.modifier.on_update(self.user_id, obj, stored_obj)

        # 4. Verify — stored_obj is only read, never mutated
        assert stored_obj.created_at == stored_obj_created_at

    def test_on_update_with_none_user_id(self) -> None:
        # 1. Input
        obj = _make_obj()
        stored_obj = _make_obj()

        # 2. Mocks (none)

        # 3. Execute
        self.modifier.on_update(None, obj, stored_obj)

        # 4. Verify
        assert obj.modified_by is None
        assert obj.modified_at == _FIXED_NOW

    # ------------------------------------------------------------------ default factory

    def test_default_factory_produces_utc_aware_datetime(self) -> None:
        # 1. Input
        modifier = CommondbDictModelModifier()  # default factory
        obj = _make_obj(created_at=None, modified_at=None)

        # 2. Mocks (none)

        # 3. Execute
        modifier.on_create(self.user_id, obj)

        # 4. Verify
        assert obj.created_at is not None
        assert obj.created_at.tzinfo == datetime.timezone.utc

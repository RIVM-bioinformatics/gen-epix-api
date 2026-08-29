"""
Unit tests for ModelNoId.set_modified and ModelNoId.set_created.

Test coverage:
- set_modified: always sets fields, leaves created_at untouched, timestamps are UTC-aware
- set_created: always sets all three fields atomically, timestamps are UTC-aware

"""

from uuid import uuid4

import pytest

from gen_epix.commondb.domain.model.base import ModelNoId


# TODO: check scenario ids, how are they determined?
@pytest.mark.scenario_ids("TC-MODEL-01")
class TestSetModified:

    def setup_method(self) -> None:
        self.user_id = uuid4()
        self.model = ModelNoId()

    def test_sets_modified_at_and_modified_by_when_unset(self) -> None:
        self.model.set_modified(self.user_id)

        assert self.model.modified_at is not None
        assert self.model.modified_by == self.user_id

    def test_does_not_touch_created_at(self) -> None:
        self.model.set_modified(self.user_id)

        assert self.model.created_at is None

    def test_modified_at_is_utc_aware(self) -> None:
        self.model.set_modified(self.user_id)

        assert self.model.modified_at is not None
        assert self.model.modified_at.tzinfo is not None


@pytest.mark.scenario_ids("TC-MODEL-02")
class TestSetCreated:

    def setup_method(self) -> None:
        self.user_id = uuid4()
        self.model = ModelNoId()

    def test_sets_all_three_fields(self) -> None:
        self.model.set_created(self.user_id)

        assert self.model.created_at is not None
        assert self.model.modified_at is not None
        assert self.model.modified_by == self.user_id

    def test_created_at_and_modified_at_are_equal(self) -> None:
        self.model.set_created(self.user_id)

        assert self.model.created_at == self.model.modified_at

    def test_timestamps_are_utc_aware(self) -> None:
        self.model.set_created(self.user_id)

        assert self.model.created_at is not None
        assert self.model.modified_at is not None
        assert self.model.created_at.tzinfo is not None
        assert self.model.modified_at.tzinfo is not None

"""
Unit tests for ModelNoId.set_modified and ModelNoId.set_created.

Test coverage:
- set_modified: sets fields when unset, is no-op when already set, override flag, leaves created_at untouched
- set_created: sets all three fields atomically, is no-op when already set, override flag, timestamps are UTC-aware


# TODO RG: The model does not test the one in omopdb, but they are identical.
# We should deduplicate the code and test the shared implementation directly.

"""

from unittest import TestCase
from uuid import uuid4

import pytest

from gen_epix.commondb.domain.model.base import ModelNoId


# TODO: check scenario ids, how are they determined?
@pytest.mark.scenario_ids("TC-MODEL-01")
class TestSetModified(TestCase):

    def setUp(self) -> None:
        self.user_id = uuid4()
        self.model = ModelNoId()

    def test_sets_modified_at_and_modified_by_when_unset(self) -> None:
        self.model.set_modified(self.user_id)

        assert self.model.modified_at is not None
        assert self.model.modified_by == self.user_id

    def test_is_noop_when_modified_at_already_set(self) -> None:
        self.model.set_modified(self.user_id)
        first_ts = self.model.modified_at
        second_user = uuid4()

        self.model.set_modified(second_user)

        assert self.model.modified_at == first_ts
        assert self.model.modified_by == self.user_id

    def test_override_replaces_fields(self) -> None:
        self.model.set_modified(self.user_id)
        second_user = uuid4()

        self.model.set_modified(second_user, override=True)

        assert self.model.modified_by == second_user

    def test_does_not_touch_created_at(self) -> None:
        self.model.set_modified(self.user_id)

        assert self.model.created_at is None

    def test_modified_at_is_utc_aware(self) -> None:
        self.model.set_modified(self.user_id)

        assert self.model.modified_at is not None
        assert self.model.modified_at.tzinfo is not None


@pytest.mark.scenario_ids("TC-MODEL-02")
class TestSetCreated(TestCase):

    def setUp(self) -> None:
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

    def test_is_noop_when_created_at_already_set(self) -> None:
        self.model.set_created(self.user_id)
        first_ts = self.model.created_at
        second_user = uuid4()

        self.model.set_created(second_user)

        assert self.model.created_at == first_ts
        assert self.model.modified_by == self.user_id

    def test_override_replaces_fields(self) -> None:
        self.model.set_created(self.user_id)
        second_user = uuid4()

        self.model.set_created(second_user, override=True)

        assert self.model.modified_by == second_user

    def test_timestamps_are_utc_aware(self) -> None:
        self.model.set_created(self.user_id)

        assert self.model.created_at is not None
        assert self.model.modified_at is not None
        assert self.model.created_at.tzinfo is not None
        assert self.model.modified_at.tzinfo is not None

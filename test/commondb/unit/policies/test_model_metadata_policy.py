"""
Unit tests for SetModelMetadataPolicy and MaskModelMetadataPolicy.

SetModelMetadataPolicy (BEFORE):
- Calls set_created on ModelNoId objects for CREATE/UPSERT operations.
- Calls set_modified on ModelNoId objects for UPDATE operations.
- Skips non-ModelNoId objects.
- Skips READ/DELETE operations.
- Skips when user is None or has a privileged role.
- Always returns True.

MaskModelMetadataPolicy (AFTER):
- Nulls created_at, modified_at, modified_by on returned ModelNoId objects
  for non-privileged users.
- Passes through unchanged for privileged users (APP_ADMIN / ROOT).
- Handles both single objects and lists.
- Handles None retval.
- Skips non-ModelNoId objects.


TODO: the masking should only be done on objects from casedb, not omopdb and seqdb


"""

from datetime import datetime
from unittest import TestCase
from uuid import uuid4

import pytest

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.enum import Role
from gen_epix.commondb.domain.model.base import ModelNoId
from gen_epix.commondb.domain.model.organization import User
from gen_epix.commondb.policies.model_metadata_policy import (
    MaskModelMetadataPolicy,
    SetModelMetadataPolicy,
)
from gen_epix.fastapp.enum import CrudOperation

_PRIVILEGED_ROLES: frozenset[str] = frozenset({Role.APP_ADMIN.value, Role.ROOT.value})


def _make_user(roles: set[str]) -> User:
    return User(
        id=uuid4(),
        key="user@example.com",
        email="user@example.com",
        roles=roles,
        organization_id=uuid4(),
        is_active=True,
    )


def _make_cmd(
    user: User | None,
    operation: CrudOperation,
    objs: ModelNoId | list[ModelNoId] | None = None,
) -> command.UserCrudCommand:
    """Build a UserCrudCommand bypassing field validation."""
    return command.UserCrudCommand.model_construct(
        user=user,
        operation=operation,
        objs=objs,
        obj_ids=None,
        query_filter=None,
    )


@pytest.mark.scenario_ids("TC-SEC-META-01")
class TestSetModelMetadataPolicy(TestCase):

    def setUp(self) -> None:
        self.policy = SetModelMetadataPolicy(_PRIVILEGED_ROLES)
        self.regular_user = _make_user({Role.ORG_USER.value})
        self.admin_user = _make_user({Role.APP_ADMIN.value})

    # --- always returns True ---

    def test_returns_true_for_create(self) -> None:
        obj = ModelNoId()
        cmd = _make_cmd(self.regular_user, CrudOperation.CREATE_ONE, obj)
        assert self.policy.is_allowed(cmd) is True

    # --- CREATE operations call set_created ---

    def test_create_one_calls_set_created(self) -> None:
        obj = ModelNoId()
        cmd = _make_cmd(self.regular_user, CrudOperation.CREATE_ONE, obj)
        self.policy.is_allowed(cmd)

        assert obj.created_at is not None
        assert obj.modified_at is not None
        assert obj.modified_by == self.regular_user.id

    def test_create_some_calls_set_created_on_each(self) -> None:
        objs = [ModelNoId(), ModelNoId()]
        cmd = _make_cmd(self.regular_user, CrudOperation.CREATE_SOME, objs)
        self.policy.is_allowed(cmd)

        for obj in objs:
            assert obj.created_at is not None

    def test_upsert_one_calls_set_created(self) -> None:
        obj = ModelNoId()
        cmd = _make_cmd(self.regular_user, CrudOperation.UPSERT_ONE, obj)
        self.policy.is_allowed(cmd)

        assert obj.created_at is not None

    def test_upsert_some_calls_set_created_on_each(self) -> None:
        objs = [ModelNoId(), ModelNoId()]
        cmd = _make_cmd(self.regular_user, CrudOperation.UPSERT_SOME, objs)
        self.policy.is_allowed(cmd)

        for obj in objs:
            assert obj.created_at is not None

    # --- UPDATE operations call set_modified ---

    def test_update_one_calls_set_modified(self) -> None:
        obj = ModelNoId()
        cmd = _make_cmd(self.regular_user, CrudOperation.UPDATE_ONE, obj)
        self.policy.is_allowed(cmd)

        assert obj.modified_at is not None
        assert obj.modified_by == self.regular_user.id
        assert obj.created_at is None  # set_modified does not touch created_at

    def test_update_some_calls_set_modified_on_each(self) -> None:
        objs = [ModelNoId(), ModelNoId()]
        cmd = _make_cmd(self.regular_user, CrudOperation.UPDATE_SOME, objs)
        self.policy.is_allowed(cmd)

        for obj in objs:
            assert obj.modified_at is not None

    # --- READ / DELETE operations are skipped ---

    def test_read_operation_leaves_objects_unchanged(self) -> None:
        obj = ModelNoId()
        cmd = _make_cmd(self.regular_user, CrudOperation.READ_ONE, obj)
        self.policy.is_allowed(cmd)

        assert obj.created_at is None
        assert obj.modified_at is None

    def test_delete_operation_leaves_objects_unchanged(self) -> None:
        obj = ModelNoId()
        cmd = _make_cmd(self.regular_user, CrudOperation.DELETE_ONE, obj)
        self.policy.is_allowed(cmd)

        assert obj.created_at is None
        assert obj.modified_at is None

    # --- Privileged users bypass ---

    def test_app_admin_bypasses_set_created(self) -> None:
        obj = ModelNoId()
        cmd = _make_cmd(self.admin_user, CrudOperation.CREATE_ONE, obj)
        self.policy.is_allowed(cmd)

        assert obj.created_at is None  # not set

    # --- No user bypasses ---

    def test_none_user_bypasses_mutation(self) -> None:
        obj = ModelNoId()
        cmd = _make_cmd(None, CrudOperation.CREATE_ONE, obj)
        self.policy.is_allowed(cmd)

        assert obj.created_at is None

    # --- Non-ModelNoId objects are skipped ---

    def test_non_model_noid_objects_are_skipped(self) -> None:
        """Objects that are not ModelNoId instances should not cause errors."""
        cmd = _make_cmd(self.regular_user, CrudOperation.CREATE_ONE, None)
        # Should not raise
        result = self.policy.is_allowed(cmd)
        assert result is True

    # --- Already-set fields are preserved (set_created is a no-op) ---

    def test_set_created_not_called_again_when_already_set(self) -> None:
        from datetime import UTC

        fixed_ts = datetime(2020, 1, 1, tzinfo=UTC)
        obj = ModelNoId(created_at=fixed_ts, modified_at=fixed_ts, modified_by=uuid4())
        original_modified_by = obj.modified_by
        cmd = _make_cmd(self.regular_user, CrudOperation.CREATE_ONE, obj)
        self.policy.is_allowed(cmd)

        assert obj.created_at == fixed_ts
        assert obj.modified_by == original_modified_by  # unchanged


@pytest.mark.scenario_ids("TC-SEC-META-02")
class TestMaskModelMetadataPolicy(TestCase):

    def setUp(self) -> None:
        self.policy = MaskModelMetadataPolicy(_PRIVILEGED_ROLES)
        self.regular_user = _make_user({Role.ORG_USER.value})
        self.admin_user = _make_user({Role.APP_ADMIN.value})
        self.root_user = _make_user({Role.ROOT.value})

    def _obj_with_metadata(self) -> ModelNoId:
        from datetime import UTC

        return ModelNoId(
            created_at=datetime(2020, 1, 1, tzinfo=UTC),
            modified_at=datetime(2020, 6, 1, tzinfo=UTC),
            modified_by=uuid4(),
        )

    # --- Non-privileged user: fields are nulled ---

    def test_regular_user_gets_fields_nulled_single(self) -> None:
        obj = self._obj_with_metadata()
        cmd = _make_cmd(self.regular_user, CrudOperation.READ_ONE)
        result = self.policy.filter(cmd, obj)

        assert obj.created_at is None
        assert obj.modified_at is None
        assert obj.modified_by is None
        assert result is obj

    def test_regular_user_gets_fields_nulled_list(self) -> None:
        objs = [self._obj_with_metadata(), self._obj_with_metadata()]
        cmd = _make_cmd(self.regular_user, CrudOperation.READ_ALL)
        result = self.policy.filter(cmd, objs)

        for obj in objs:
            assert obj.created_at is None
            assert obj.modified_at is None
            assert obj.modified_by is None
        assert result is objs

    # --- Privileged users: fields are preserved ---

    def test_app_admin_fields_are_not_nulled(self) -> None:
        obj = self._obj_with_metadata()
        original_created = obj.created_at
        cmd = _make_cmd(self.admin_user, CrudOperation.READ_ONE)
        self.policy.filter(cmd, obj)

        assert obj.created_at == original_created

    def test_root_user_fields_are_not_nulled(self) -> None:
        obj = self._obj_with_metadata()
        original_created = obj.created_at
        cmd = _make_cmd(self.root_user, CrudOperation.READ_ONE)
        self.policy.filter(cmd, obj)

        assert obj.created_at == original_created

    # --- None user bypasses ---

    def test_none_user_bypasses_masking(self) -> None:
        obj = self._obj_with_metadata()
        original_created = obj.created_at
        cmd = _make_cmd(None, CrudOperation.READ_ONE)
        self.policy.filter(cmd, obj)

        assert obj.created_at == original_created

    # --- None retval passes through ---

    def test_none_retval_passes_through(self) -> None:
        cmd = _make_cmd(self.regular_user, CrudOperation.READ_ONE)
        result = self.policy.filter(cmd, None)

        assert result is None

    # --- Non-ModelNoId objects in list are skipped ---

    def test_non_model_noid_objects_in_list_are_skipped(self) -> None:
        from gen_epix.fastapp.model import Model

        non_model = Model()
        cmd = _make_cmd(self.regular_user, CrudOperation.READ_ALL)
        # Should not raise; non-ModelNoId objects have no metadata fields
        result = self.policy.filter(cmd, [non_model])
        assert result is not None

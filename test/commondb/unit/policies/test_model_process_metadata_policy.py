"""
Unit tests for SetModelProcessMetadataPolicy and MaskModelProcessMetadataPolicy.

SetModelProcessMetadataPolicy (BEFORE):
- Calls set_created on ModelNoId objects for CREATE/UPSERT operations.
- Calls set_modified on ModelNoId objects for UPDATE operations; also backfills
  created_at if it is None (handles objects whose creation bypassed BEFORE policies).
- Skips non-ModelNoId objects.
- Skips READ/DELETE operations.
- Skips when user is None or has a privileged role (ROOT only).
- Always returns True.

MaskModelProcessMetadataPolicy (AFTER):
- Nulls created_at, modified_at, modified_by on returned ModelNoId objects
  for non-privileged users.
- Passes through unchanged for privileged users (APP_ADMIN / ROOT).
- Handles both single objects and lists.
- Handles None retval.
- Skips non-ModelNoId objects.


TODO: the masking should only be done on objects from casedb, not omopdb and seqdb


"""

from test.commondb.unit.conftest import DEFAULT_CREATED_AT, DEFAULT_MODIFIED_AT
from unittest import TestCase
from uuid import uuid4

import pytest

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.enum import Role
from gen_epix.commondb.domain.model.base import ModelNoId
from gen_epix.commondb.domain.model.organization import User
from gen_epix.commondb.policies.model_metadata_policy import (
    MaskModelProcessMetadataPolicy,
    SetModelProcessMetadataPolicy,
)
from gen_epix.fastapp.enum import CrudOperation

# _PRIVILEGED_ROLES: frozenset[str] = frozenset({Role.APP_ADMIN.value, Role.ROOT.value})
_PRIVILEGED_ROLES_READ: frozenset[str] = frozenset(
    {Role.APP_ADMIN.value, Role.ROOT.value}
)
_PRIVILEGED_ROLES_CREATE_UPDATE: frozenset[str] = frozenset({Role.ROOT.value})


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
class TestSetModelProcessMetadataPolicy(TestCase):

    def setUp(self) -> None:
        self.policy = SetModelProcessMetadataPolicy(_PRIVILEGED_ROLES_CREATE_UPDATE)
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
        # created_at was None → backfilled to match modified_at
        assert obj.created_at == obj.modified_at

    def test_update_one_preserves_existing_created_at(self) -> None:
        obj = ModelNoId(created_at=DEFAULT_CREATED_AT)
        cmd = _make_cmd(self.regular_user, CrudOperation.UPDATE_ONE, obj)
        self.policy.is_allowed(cmd)

        # created_at was already set → must not be overwritten
        assert obj.created_at == DEFAULT_CREATED_AT

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

    def test_app_admin_does_not_bypasses_set_created(self) -> None:
        obj = ModelNoId()

        obj.created_at = DEFAULT_CREATED_AT
        cmd = _make_cmd(self.admin_user, CrudOperation.CREATE_ONE, obj)
        self.policy.is_allowed(cmd)

        assert obj.created_at != DEFAULT_CREATED_AT  # not overwritten

    # --- No user bypasses ---

    """
    The if not cmd.user guard in SetModelProcessMetadataPolicy and MaskModelProcessMetadataPolicy 
    is a safety check: if there's no user, there's no user.id to set as modified_by, 
    and no roles to check — so the policy skips rather than crashing.
    Whether this is a realistic scenario for the current codebase is a valid question. 
    If commands always have a user by the time they reach the policies, 
    the guard is defensive dead code. 
    The test exists because the guard exists, but if you remove the guard, the test goes away too. 
    What does your system actually do — are there commands dispatched without a user?
    """

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

    # --- Pre-set fields are overwritten for non-privileged users ---

    def test_pre_set_metadata_is_overwritten_for_regular_user(self) -> None:
        from datetime import UTC

        fixed_ts = DEFAULT_CREATED_AT
        original_modified_by = uuid4()
        obj = ModelNoId(
            created_at=fixed_ts, modified_at=fixed_ts, modified_by=original_modified_by
        )
        cmd = _make_cmd(self.regular_user, CrudOperation.CREATE_ONE, obj)
        self.policy.is_allowed(cmd)

        assert obj.created_at != fixed_ts  # overwritten with current time
        assert obj.modified_by == self.regular_user.id  # overwritten with actual user


@pytest.mark.scenario_ids("TC-SEC-META-02")
class TestMaskModelProcessMetadataPolicy(TestCase):

    def setUp(self) -> None:
        self.policy = MaskModelProcessMetadataPolicy(_PRIVILEGED_ROLES_READ)
        self.regular_user = _make_user({Role.ORG_USER.value})
        self.admin_user = _make_user({Role.APP_ADMIN.value})
        self.root_user = _make_user({Role.ROOT.value})

    def _obj_with_metadata(self) -> ModelNoId:
        from datetime import UTC

        return ModelNoId(
            created_at=DEFAULT_CREATED_AT,
            modified_at=DEFAULT_MODIFIED_AT,
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

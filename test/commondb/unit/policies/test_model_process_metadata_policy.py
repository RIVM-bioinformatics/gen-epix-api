"""
Unit tests for MaskModelProcessMetadataPolicy.

MaskModelProcessMetadataPolicy (AFTER):
- Nulls created_at, modified_at, modified_by on returned ModelNoId objects
  for non-privileged users.
- Passes through unchanged for privileged users (APP_ADMIN / ROOT).
- Handles both single objects and lists.
- Handles None retval.
- Skips non-ModelNoId objects.

"""

from enum import Enum
from test.commondb.unit.conftest import DEFAULT_CREATED_AT, DEFAULT_MODIFIED_AT
from unittest import TestCase
from uuid import uuid4

import pytest

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.enum import Role, RoleSet
from gen_epix.commondb.domain.model.base import ModelNoId
from gen_epix.commondb.domain.model.organization import User
from gen_epix.commondb.policies.model_metadata_policy import (
    ModelMetadataPolicy,
)
from gen_epix.fastapp.enum import CrudOperation

# _PRIVILEGED_ROLES: frozenset[str] = frozenset({Role.APP_ADMIN.value, Role.ROOT.value})
# _PRIVILEGED_ROLES_READ: frozenset[str] = frozenset(
#     {Role.APP_ADMIN.value, Role.ROOT.value}
# )
_PRIVILEGED_ROLES_READ: dict[RoleSet | Enum, frozenset[str]] = {
    RoleSet.GE_APP_ADMIN: frozenset({x.value for x in RoleSet.GE_APP_ADMIN.value}),
}


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


@pytest.mark.scenario_ids("TC-SEC-META-02", "TC-SEC-30-02")
class TestModelMetadataPolicy(TestCase):

    def setUp(self) -> None:
        self.policy = ModelMetadataPolicy(_PRIVILEGED_ROLES_READ)
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

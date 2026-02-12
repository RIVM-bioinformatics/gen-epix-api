"""
Unit tests for ReadUserPolicy.filter.

The tests cover all branches in ReadUserPolicy.filter:
- Unsupported command type
- Non-read operations
- Unauthenticated user
- APP_ADMIN bypass
- Organization admin and regular user paths for READ_ALL, READ_SOME, and READ_ONE

Each test verifies the return values, exceptions, and interactions with app.handle and get_mapped_class.
"""

from types import SimpleNamespace
from typing import Any, Iterable, List, Tuple
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain import command, exc
from gen_epix.commondb.enum import Role, RoleSet
from gen_epix.commondb.domain.model.organization import User
from gen_epix.commondb.policies.read_user_policy import ReadUserPolicy
from gen_epix.fastapp.enum import CrudOperation


class BaseReadUserPolicyTestCase(TestCase):
    """Base test case with common fixtures and utilities."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Mock ABAC service and app impl
        self.abac_service = Mock()
        self.abac_service.app = Mock()
        self.abac_service.app.impl = Mock()
        self.abac_service.app.impl.get_mapped_class = Mock(
            return_value=command.OrganizationAdminPolicyCrudCommand
        )
        self.abac_service.app.impl.role_map = {}
        self.abac_service.app.impl.role_set_map = {
            RoleSet.GE_APP_ADMIN: {Role.APP_ADMIN.value},
            RoleSet.GE_ORG_ADMIN: {Role.ORG_ADMIN.value},
        }

        # Policy under test
        self.policy = ReadUserPolicy(self.abac_service)

        # Common orgs and users
        self.org_id_1: UUID = uuid4()
        self.org_id_2: UUID = uuid4()
        self.org_admin_user: User = self._make_user(
            organization_id=self.org_id_1, roles={Role.ORG_ADMIN.value}, is_active=True
        )
        self.app_admin_user: User = self._make_user(
            organization_id=self.org_id_1, roles={Role.APP_ADMIN.value}, is_active=True
        )
        self.regular_user: User = self._make_user(
            organization_id=self.org_id_1, roles={Role.ORG_USER.value}, is_active=True
        )

    def _make_user(
        self,
        organization_id: UUID,
        roles: set[str],
        is_active: bool,
        id: UUID | None = None,
        email: str = "user@example.com",
    ) -> User:
        """Create a domain User."""
        return User(
            id=id or uuid4(),
            key=email,
            email=email,
            roles=roles,
            organization_id=organization_id,
            is_active=is_active,
        )

    def _make_user_cmd(
        self, user: User | None, operation: CrudOperation
    ) -> command.UserCrudCommand:
        """Create a UserCrudCommand without validation."""
        return command.UserCrudCommand.model_construct(
            user=user,
            operation=operation,
            query_filter=None,
        )

    def _make_org_admin_policy(self, organization_id: UUID, user_id: UUID) -> Any:
        """Create a minimal OrganizationAdminPolicy-like object."""
        return SimpleNamespace(organization_id=organization_id, user_id=user_id)

    def _users(self, specs: Iterable[Tuple[UUID, UUID, set[str], bool]]) -> List[User]:
        """Create a list of Users from tuples: (id, org_id, roles, is_active)."""
        return [
            self._make_user(
                organization_id=org_id, roles=roles, is_active=is_active, id=user_id
            )
            for user_id, org_id, roles, is_active in specs
        ]


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestUnsupportedAndNonReadPaths(BaseReadUserPolicyTestCase):
    """Test unsupported command types and non-read operations."""

    def test_unsupported_command_type_raises(self) -> None:
        """Unsupported command type should raise NotImplementedError."""
        # Create inputs
        cmd = Mock()  # Not a UserCrudCommand
        results: list[User] = []

        # Execute and verify
        with pytest.raises(NotImplementedError):
            self.policy.filter(cmd, results)
        self.abac_service.app.handle.assert_not_called()

    def test_operation_not_read_returns_unmodified(self) -> None:
        """Non-read operations should return results unchanged."""
        # Create inputs
        cmd = self._make_user_cmd(self.regular_user, CrudOperation.CREATE_ONE)
        results = self._users(
            [
                (uuid4(), self.org_id_1, {Role.ORG_USER.value}, True),
                (uuid4(), self.org_id_2, {Role.ORG_USER.value}, False),
            ]
        )

        # Execute and verify
        retval = self.policy.filter(cmd, results)
        assert retval is results
        self.abac_service.app.handle.assert_not_called()


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestUnauthenticated(BaseReadUserPolicyTestCase):
    """Test unauthenticated user conditions."""

    def test_none_user_raises_assertion(self) -> None:
        """None user should assert."""
        # Create inputs
        cmd = self._make_user_cmd(None, CrudOperation.READ_ALL)
        results: list[User] = []

        # Execute and verify
        with pytest.raises(AssertionError):
            self.policy.filter(cmd, results)
        self.abac_service.app.handle.assert_not_called()

    def test_none_user_id_raises_assertion(self) -> None:
        """User without id should assert."""
        # Create inputs
        bad_user = self._make_user(
            organization_id=self.org_id_1,
            roles={Role.ORG_USER.value},
            is_active=True,
            id=None,
        )
        bad_user.id = None
        cmd = self._make_user_cmd(bad_user, CrudOperation.READ_ALL)
        results: list[User] = []

        # Execute and verify
        with pytest.raises(AssertionError):
            self.policy.filter(cmd, results)
        self.abac_service.app.handle.assert_not_called()


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestAppAdminBypass(BaseReadUserPolicyTestCase):
    """Test APP_ADMIN users bypass ABAC filtering."""

    def test_app_admin_returns_unmodified(self) -> None:
        """APP_ADMIN should receive unmodified results for READ operations."""
        # Create inputs
        cmd = self._make_user_cmd(self.app_admin_user, CrudOperation.READ_ALL)
        results = self._users(
            [
                (uuid4(), self.org_id_1, {Role.ORG_USER.value}, True),
                (uuid4(), self.org_id_2, {Role.ORG_USER.value}, False),
            ]
        )

        # Execute and verify
        retval = self.policy.filter(cmd, results)
        assert retval == results
        self.abac_service.app.handle.assert_not_called()
        self.abac_service.app.impl.get_mapped_class.assert_called_once_with(
            command.OrganizationAdminPolicyCrudCommand
        )


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestOrgAdminReads(BaseReadUserPolicyTestCase):
    """Test organization admin read behavior."""

    def test_read_all_org_admin_filters_and_allows_inactive(self) -> None:
        """READ_ALL for org admin should include users in admin orgs and admins, including inactive."""
        # Create inputs
        cmd = self._make_user_cmd(self.org_admin_user, CrudOperation.READ_ALL)
        # Policies: org admin user is admin of org_id_1
        policies = [
            self._make_org_admin_policy(self.org_id_1, self.org_admin_user.id),  # type: ignore[arg-type]
            self._make_org_admin_policy(self.org_id_1, uuid4()),  # another admin
        ]
        other_org_user = self._make_user(
            organization_id=self.org_id_2, roles={Role.ORG_USER.value}, is_active=True
        )
        same_org_active = self._make_user(
            organization_id=self.org_id_1, roles={Role.ORG_USER.value}, is_active=True
        )
        same_org_inactive = self._make_user(
            organization_id=self.org_id_1, roles={Role.ORG_USER.value}, is_active=False
        )
        another_admin_user = self._make_user(
            organization_id=self.org_id_1,
            roles={Role.ORG_ADMIN.value},
            is_active=False,
            id=policies[1].user_id,
        )
        results = [
            other_org_user,
            same_org_active,
            same_org_inactive,
            another_admin_user,
        ]

        # Set up mocks
        self.abac_service.app.handle.side_effect = [
            policies,
        ]

        # Execute and verify
        retval = self.policy.filter(cmd, results)
        assert same_org_active in retval
        assert same_org_inactive in retval  # allowed because org admin
        assert another_admin_user in retval
        assert other_org_user not in retval

        # Verify interactions
        self.abac_service.app.handle.assert_called_once()
        org_admin_cmd = self.abac_service.app.handle.call_args[0][0]
        assert isinstance(org_admin_cmd, command.OrganizationAdminPolicyCrudCommand)
        assert org_admin_cmd.operation == CrudOperation.READ_ALL
        assert org_admin_cmd.user == self.org_admin_user
        from gen_epix.filter.equals_boolean import EqualsBooleanFilter

        assert isinstance(org_admin_cmd.query_filter, EqualsBooleanFilter)

    def test_read_some_org_admin_authorizes_subset(self) -> None:
        """READ_SOME for org admin should authorize when all users are within admin orgs."""
        # Create inputs
        cmd = self._make_user_cmd(self.org_admin_user, CrudOperation.READ_SOME)
        policies = [self._make_org_admin_policy(self.org_id_1, self.org_admin_user.id)]  # type: ignore[arg-type]
        target1 = self._make_user(
            organization_id=self.org_id_1, roles={Role.ORG_USER.value}, is_active=False
        )  # allowed despite inactive
        target2 = self._make_user(
            organization_id=self.org_id_1, roles={Role.ORG_USER.value}, is_active=True
        )
        results = [target1, target2]

        # Set up mocks
        self.abac_service.app.handle.side_effect = [
            policies,
        ]

        # Execute and verify
        retval = self.policy.filter(cmd, results)
        assert retval == results
        self.abac_service.app.handle.assert_called_once()

    def test_read_some_org_admin_denies_outside_org(self) -> None:
        """READ_SOME should raise when any user is outside admin orgs."""
        # Create inputs
        cmd = self._make_user_cmd(self.org_admin_user, CrudOperation.READ_SOME)
        policies = [self._make_org_admin_policy(self.org_id_1, self.org_admin_user.id)]  # type: ignore[arg-type]
        allowed = self._make_user(
            organization_id=self.org_id_1, roles={Role.ORG_USER.value}, is_active=True
        )
        denied = self._make_user(
            organization_id=self.org_id_2, roles={Role.ORG_USER.value}, is_active=True
        )
        results = [allowed, denied]

        # Set up mocks
        self.abac_service.app.handle.side_effect = [
            policies,
        ]

        # Execute and verify
        with pytest.raises(exc.UnauthorizedAuthError):
            self.policy.filter(cmd, results)
        self.abac_service.app.handle.assert_called_once()

    def test_read_one_org_admin_allows_inactive(self) -> None:
        """READ_ONE for org admin allows inactive user in admin orgs."""
        # Create inputs
        cmd = self._make_user_cmd(self.org_admin_user, CrudOperation.READ_ONE)
        policies = [self._make_org_admin_policy(self.org_id_1, self.org_admin_user.id)]  # type: ignore[arg-type]
        target = self._make_user(
            organization_id=self.org_id_1, roles={Role.ORG_USER.value}, is_active=False
        )

        # Set up mocks
        self.abac_service.app.handle.side_effect = [
            policies,
        ]

        # Execute and verify
        retval = self.policy.filter(cmd, target)
        assert retval == target
        self.abac_service.app.handle.assert_called_once()


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestRegularUserReads(BaseReadUserPolicyTestCase):
    """Test regular user read behavior."""

    def test_read_all_regular_user_filters_only_self_and_active_admins(self) -> None:
        """READ_ALL for regular user should include self and active admins of own org."""
        # Create inputs
        cmd = self._make_user_cmd(self.regular_user, CrudOperation.READ_ALL)
        active_admin_id = uuid4()
        inactive_admin_id = uuid4()
        policies = [
            self._make_org_admin_policy(self.org_id_1, active_admin_id),
            self._make_org_admin_policy(self.org_id_1, inactive_admin_id),
        ]
        # Results set
        self_user = self.regular_user
        active_admin_user = self._make_user(
            organization_id=self.org_id_1,
            roles={Role.ORG_ADMIN.value},
            is_active=True,
            id=active_admin_id,
        )
        inactive_admin_user = self._make_user(
            organization_id=self.org_id_1,
            roles={Role.ORG_ADMIN.value},
            is_active=False,
            id=inactive_admin_id,
        )
        other_org_user = self._make_user(
            organization_id=self.org_id_2, roles={Role.ORG_USER.value}, is_active=True
        )
        results = [self_user, active_admin_user, inactive_admin_user, other_org_user]

        # Set up mocks
        self.abac_service.app.handle.side_effect = [
            policies,
        ]

        # Execute and verify
        retval = self.policy.filter(cmd, results)
        assert self_user in retval
        assert active_admin_user in retval
        assert inactive_admin_user not in retval  # inactive admin excluded
        assert other_org_user not in retval

        # Verify interactions
        self.abac_service.app.handle.assert_called_once()
        org_admin_cmd = self.abac_service.app.handle.call_args[0][0]
        assert isinstance(org_admin_cmd, command.OrganizationAdminPolicyCrudCommand)
        from gen_epix.filter.composite import CompositeFilter
        from gen_epix.filter.enum import LogicalOperator
        from gen_epix.filter.equals_boolean import EqualsBooleanFilter
        from gen_epix.filter.equals_uuid import EqualsUuidFilter

        assert isinstance(org_admin_cmd.query_filter, CompositeFilter)
        assert org_admin_cmd.query_filter.operator == LogicalOperator.AND
        keys = {f.key for f in org_admin_cmd.query_filter.filters}
        assert keys == {"organization_id", "is_active"}
        assert any(
            isinstance(f, EqualsUuidFilter) for f in org_admin_cmd.query_filter.filters
        )
        assert any(
            isinstance(f, EqualsBooleanFilter)
            for f in org_admin_cmd.query_filter.filters
        )

    def test_read_some_regular_user_allows_self_and_active_admins(self) -> None:
        """READ_SOME for regular user should allow self and active admins only."""
        # Create inputs
        cmd = self._make_user_cmd(self.regular_user, CrudOperation.READ_SOME)
        active_admin_id = uuid4()
        policies = [self._make_org_admin_policy(self.org_id_1, active_admin_id)]
        self_user = self.regular_user
        active_admin_user = self._make_user(
            organization_id=self.org_id_1,
            roles={Role.ORG_ADMIN.value},
            is_active=True,
            id=active_admin_id,
        )
        results = [self_user, active_admin_user]

        # Set up mocks
        self.abac_service.app.handle.side_effect = [
            policies,
        ]

        # Execute and verify
        retval = self.policy.filter(cmd, results)
        assert retval == results
        self.abac_service.app.handle.assert_called_once()

    def test_read_some_regular_user_denies_other_org(self) -> None:
        """READ_SOME should raise when includes users outside allowed set."""
        # Create inputs
        cmd = self._make_user_cmd(self.regular_user, CrudOperation.READ_SOME)
        active_admin_id = uuid4()
        policies = [self._make_org_admin_policy(self.org_id_1, active_admin_id)]
        allowed_self = self.regular_user
        denied_user = self._make_user(
            organization_id=self.org_id_2, roles={Role.ORG_USER.value}, is_active=True
        )
        results = [allowed_self, denied_user]

        # Set up mocks
        self.abac_service.app.handle.side_effect = [
            policies,
        ]

        # Execute and verify
        with pytest.raises(exc.UnauthorizedAuthError):
            self.policy.filter(cmd, results)
        self.abac_service.app.handle.assert_called_once()

    def test_read_one_regular_user_allows_self(self) -> None:
        """READ_ONE for regular user should allow self if active."""
        # Create inputs
        cmd = self._make_user_cmd(self.regular_user, CrudOperation.READ_ONE)
        target = self.regular_user  # active self

        # Set up mocks
        self.abac_service.app.handle.side_effect = [
            [self._make_org_admin_policy(self.org_id_1, uuid4())],
        ]

        # Execute and verify
        retval = self.policy.filter(cmd, target)
        assert retval == target
        self.abac_service.app.handle.assert_called_once()

    def test_read_one_regular_user_denies_other_org_or_inactive(self) -> None:
        """READ_ONE should raise for other org users or inactive non-admins."""
        # Create inputs
        cmd = self._make_user_cmd(self.regular_user, CrudOperation.READ_ONE)
        target = self._make_user(
            organization_id=self.org_id_2, roles={Role.ORG_USER.value}, is_active=True
        )

        # Set up mocks
        self.abac_service.app.handle.side_effect = [
            [self._make_org_admin_policy(self.org_id_1, uuid4())],
        ]

        # Execute and verify
        with pytest.raises(exc.UnauthorizedAuthError):
            self.policy.filter(cmd, target)
        self.abac_service.app.handle.assert_called_once()

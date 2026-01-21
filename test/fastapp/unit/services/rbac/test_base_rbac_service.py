"""
Unit tests for BaseRbacService.

The tests cover all public methods and properties of the BaseRbacService class,
focusing on verifying RBAC functionality including role registration, permission
management, user authorization, and policy registration.

The tests handle all of the following scenarios:
1. Service initialization and basic properties
2. Permission registration (with and without RBAC)
3. Role registration and management
4. Role hierarchy and sub-role calculations
5. User permission retrieval and authorization checks
6. RBAC policy registration
7. Hierarchical role permission expansion
8. Error conditions and edge cases
"""

from collections.abc import Hashable
from enum import Enum
from typing import Any
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4
import pytest

from gen_epix.fastapp import (
    App,
    EventTiming,
    Permission,
    PermissionType,
    PermissionTypeSet,
    exc,
)
from gen_epix.fastapp.model import Command, User
from gen_epix.fastapp.services.rbac.policy import RbacPolicy
from gen_epix.fastapp.services.rbac.service import BaseRbacService


class TestRole(Enum):
    """Test roles for testing."""

    ROOT = "ROOT"
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"


class TestCommand(Command):
    """Test command for testing."""

    def __init__(self, user: User):
        super().__init__(user=user)


class TestCommand2(Command):
    """Another test command for testing."""

    def __init__(self, user: User):
        super().__init__(user=user)


class ConcreteRbacService(BaseRbacService):
    """Concrete implementation of BaseRbacService for testing."""

    def __init__(
        self, app: App, user_roles: dict[UUID, set[Hashable]] = None, **kwargs: Any
    ):
        super().__init__(app, **kwargs)
        self._user_roles = user_roles or {}
        self._root_users: set[UUID] = set()
        self._non_rbac_authorized_users: set[UUID] = set()

    def retrieve_user_roles(self, user: User) -> set[Hashable]:
        """Retrieve roles for a user."""
        return self._user_roles.get(user.id, set())

    def set_user_roles(self, user_id: UUID, roles: set[Hashable]) -> None:
        """Helper method to set user roles for testing."""
        self._user_roles[user_id] = roles

    def set_root_user(self, user_id: UUID, is_root: bool = True) -> None:
        """Helper method to set root user status for testing."""
        if is_root:
            self._root_users.add(user_id)
        else:
            self._root_users.discard(user_id)

    def set_non_rbac_authorized(
        self, user_id: UUID, is_authorized: bool = True
    ) -> None:
        """Helper method to set non-RBAC authorization for testing."""
        if is_authorized:
            self._non_rbac_authorized_users.add(user_id)
        else:
            self._non_rbac_authorized_users.discard(user_id)

    def retrieve_user_is_root(self, user: User) -> bool:
        """Check if user is root."""
        return user.id in self._root_users

    def retrieve_user_is_non_rbac_authorized(self, cmd: Command) -> bool:
        """Check if user is authorized via non-RBAC mechanism."""
        return cmd.user.id in self._non_rbac_authorized_users


class BaseRbacServiceTestCase(TestCase):
    """Base test case with common fixtures and utilities."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Test user
        self.user_id = uuid4()
        self.user = User(
            id=self.user_id,
            # key="test@example.com",
            # email="test@example.com",
            # roles={TestRole.USER.value},
            # organization_id=uuid4(),
            # is_active=True,
        )

        # Another test user
        self.admin_user_id = uuid4()
        self.admin_user = User(
            id=self.admin_user_id,
            # key="admin@example.com",
            # email="admin@example.com",
            # roles={TestRole.ADMIN.value},
            # organization_id=uuid4(),
            # is_active=True,
        )

        # Mock app and domain
        self.mock_app = Mock(spec=App)
        self.mock_domain = Mock()
        self.mock_app.domain = self.mock_domain

        TestCommand.__name__ = "TestCommand"
        TestCommand2.__name__ = "TestCommand2"

        # Create test permissions
        self.permission1 = Permission(
            command_name=TestCommand.__name__,
            permission_type=PermissionType.READ,
        )
        self.permission2 = Permission(
            command_name=TestCommand.__name__,
            permission_type=PermissionType.UPDATE,
        )
        self.permission3 = Permission(
            command_name=TestCommand2.__name__,
            permission_type=PermissionType.READ,
        )
        self.permission4 = Permission(
            command_name=TestCommand2.__name__,
            permission_type=PermissionType.UPDATE,
        )

        all_permissions = {
            self.permission1,
            self.permission2,
            self.permission3,
            self.permission4,
        }

        # Create command name to class mapping for mocks
        command_name_to_class = {
            TestCommand.__name__: TestCommand,
            TestCommand2.__name__: TestCommand2,
        }

        self.mock_domain.permissions = all_permissions
        self.mock_domain.get_permission.side_effect = lambda cmd_class, perm_type: next(
            (
                p
                for p in all_permissions
                if p.command_name
                == (
                    cmd_class.__name__
                    if hasattr(cmd_class, "__name__")
                    else str(cmd_class)
                )
                and p.permission_type == perm_type
            ),
            None,
        )
        self.mock_domain.get_permissions_for_command.side_effect = lambda cmd_class: {
            p for p in all_permissions if p.command_name == cmd_class.__name__
        }
        self.mock_domain.get_command_for_permission.side_effect = (
            lambda perm: command_name_to_class.get(perm.command_name)
        )
        self.mock_domain.get_permission_for_command_instance.side_effect = (
            lambda cmd: next(
                (p for p in all_permissions if p.command_name == type(cmd).__name__),
                None,
            )
        )
        self.mock_domain.get_permissions_for_domain.return_value = all_permissions

        # Create service
        self.service = ConcreteRbacService(self.mock_app)

    def create_test_command(self, user: User = None) -> TestCommand:
        """Create a test command."""
        return TestCommand(user=user or self.user)

    def create_test_command2(self, user: User = None) -> TestCommand2:
        """Create another test command."""
        return TestCommand2(user=user or self.user)


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestServiceInitialization(BaseRbacServiceTestCase):
    """Test service initialization and basic properties."""

    def test_init_creates_empty_collections(self) -> None:
        """Test that service initialization creates empty collections."""
        # Execute
        service = ConcreteRbacService(self.mock_app)

        # Verify
        self.assertEqual(len(service.permissions_without_rbac), 0)
        self.assertEqual(len(service.permissions_by_role), 0)
        self.assertEqual(
            len(service.roles_by_permission), 4
        )  # One entry per domain permission
        for permission in self.mock_domain.permissions:
            self.assertEqual(len(service.roles_by_permission[permission]), 0)

    def test_properties_return_correct_collections(self) -> None:
        """Test that properties return the correct internal collections."""
        # Setup
        self.service._permissions_without_rbac.add(self.permission1)
        self.service._permissions_by_role[TestRole.USER] = {self.permission2}
        self.service._roles_by_permission[self.permission2] = {TestRole.USER}

        # Execute & Verify
        self.assertIs(
            self.service.permissions_without_rbac,
            self.service._permissions_without_rbac,
        )
        self.assertIs(
            self.service.permissions_by_role, self.service._permissions_by_role
        )
        self.assertIs(
            self.service.roles_by_permission, self.service._roles_by_permission
        )

    def test_register_handlers_does_nothing_in_base_implementation(self) -> None:
        """Test that register_handlers does nothing in base implementation."""
        # Execute (should not raise any exceptions)
        self.service.register_handlers()

        # Verify (no assertions needed, just ensuring no exceptions)
        pass


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestPermissionRegistration(BaseRbacServiceTestCase):
    """Test permission registration functionality."""

    def test_register_permission_without_rbac_succeeds(self) -> None:
        """Test registering a permission without RBAC."""
        # Execute
        self.service.register_permission_without_rbac(self.permission1)

        # Verify
        self.assertIn(self.permission1, self.service.permissions_without_rbac)

    def test_register_permission_without_rbac_with_existing_roles_fails(self) -> None:
        """Test registering permission without RBAC fails when roles exist."""
        # Setup
        self.service._roles_by_permission[self.permission1].add(TestRole.USER)

        # Execute & Verify
        with self.assertRaises(exc.ServiceException) as cm:
            self.service.register_permission_without_rbac(self.permission1)
        self.assertIn("has some roles registered", str(cm.exception))

    def test_unregister_permission_without_rbac_succeeds(self) -> None:
        """Test unregistering a permission without RBAC."""
        # Setup
        self.service._permissions_without_rbac.add(self.permission1)

        # Execute
        self.service.unregister_permission_without_rbac(self.permission1)

        # Verify
        self.assertNotIn(self.permission1, self.service.permissions_without_rbac)

    def test_unregister_permission_without_rbac_not_registered_fails(self) -> None:
        """Test unregistering non-registered permission fails."""
        # Execute & Verify
        with self.assertRaises(exc.ServiceException) as cm:
            self.service.unregister_permission_without_rbac(self.permission1)
        self.assertIn("is not registered", str(cm.exception))


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestRoleRegistration(BaseRbacServiceTestCase):
    """Test role registration and management."""

    def test_register_role_new_role_succeeds(self) -> None:
        """Test registering a new role with permissions."""
        # Setup
        permissions = {self.permission1, self.permission2}

        # Execute
        self.service.register_role(TestRole.USER, permissions)

        # Verify
        self.assertEqual(self.service.permissions_by_role[TestRole.USER], permissions)
        for permission in permissions:
            self.assertIn(TestRole.USER, self.service.roles_by_permission[permission])

    def test_register_role_invalid_permissions_fails(self) -> None:
        """Test registering role with invalid permissions fails."""
        # Setup
        invalid_permission = Permission(
            command_name="TestCommand", permission_type=PermissionType.DELETE
        )  # Not in domain
        permissions = {self.permission1, invalid_permission}

        # Execute & Verify
        with self.assertRaises(exc.ServiceException) as cm:
            self.service.register_role(TestRole.USER, permissions)
        self.assertIn("are not registered", str(cm.exception))

    def test_register_role_existing_role_without_update_fails(self) -> None:
        """Test registering existing role without update fails."""
        # Setup
        permissions = {self.permission1}
        self.service.register_role(TestRole.USER, permissions)

        # Execute & Verify
        with self.assertRaises(exc.ServiceException) as cm:
            self.service.register_role(TestRole.USER, permissions, update_role=False)
        self.assertIn("is already registered", str(cm.exception))

    def test_register_role_existing_role_with_update_succeeds(self) -> None:
        """Test updating existing role succeeds."""
        # Setup
        old_permissions = {self.permission1, self.permission2}
        new_permissions = {self.permission2, self.permission3}
        self.service.register_role(TestRole.USER, old_permissions)

        # Execute
        self.service.register_role(TestRole.USER, new_permissions, update_role=True)

        # Verify
        self.assertEqual(
            self.service.permissions_by_role[TestRole.USER], new_permissions
        )
        self.assertNotIn(
            TestRole.USER, self.service.roles_by_permission[self.permission1]
        )
        self.assertIn(TestRole.USER, self.service.roles_by_permission[self.permission2])
        self.assertIn(TestRole.USER, self.service.roles_by_permission[self.permission3])

    def test_register_roles_multiple_roles_succeeds(self) -> None:
        """Test registering multiple roles at once."""
        # Setup
        role_permissions = {
            TestRole.USER: {(TestCommand, PermissionType.READ)},
            TestRole.ADMIN: {
                (TestCommand, PermissionType.READ),
                (TestCommand, PermissionType.UPDATE),
            },
        }

        # Execute
        self.service.register_roles(role_permissions)

        # Verify
        self.assertEqual(
            self.service.permissions_by_role[TestRole.USER], {self.permission1}
        )
        self.assertEqual(
            self.service.permissions_by_role[TestRole.ADMIN],
            {self.permission1, self.permission2},
        )

    def test_register_roles_with_root_role_adds_missing_permissions(self) -> None:
        """Test registering roles with root role adds all missing permissions."""
        # Setup
        role_permissions = {
            TestRole.ROOT: {(TestCommand, PermissionType.READ)},
            TestRole.USER: {(TestCommand, PermissionType.READ)},
        }

        # Execute
        self.service.register_roles(role_permissions, root_role=TestRole.ROOT)

        # Verify
        self.assertEqual(
            self.service.permissions_by_role[TestRole.ROOT],
            self.mock_domain.permissions,
        )

    def test_register_roles_with_root_role_missing_permissions_raises(self) -> None:
        """Test registering roles with root role and missing permissions raises error."""
        # Setup
        role_permissions = {
            TestRole.ROOT: {(TestCommand, PermissionType.READ)},
        }

        # Execute & Verify
        with self.assertRaises(exc.InitializationServiceError) as cm:
            self.service.register_roles(
                role_permissions,
                root_role=TestRole.ROOT,
                on_missing_root_permissions="raise",
            )
        self.assertIn("is missing permissions", str(cm.exception))

    def test_unregister_role_existing_role_succeeds(self) -> None:
        """Test unregistering existing role succeeds."""
        # Setup
        permissions = {self.permission1, self.permission2}
        self.service.register_role(TestRole.USER, permissions)

        # Execute
        self.service.unregister_role(TestRole.USER)

        # Verify
        self.assertNotIn(TestRole.USER, self.service.permissions_by_role)
        for permission in permissions:
            self.assertNotIn(
                TestRole.USER, self.service.roles_by_permission[permission]
            )

    def test_unregister_role_non_existing_role_fails(self) -> None:
        """Test unregistering non-existing role fails."""
        # Execute & Verify
        with self.assertRaises(exc.ServiceException) as cm:
            self.service.unregister_role(TestRole.USER)
        self.assertIn("is not registered", str(cm.exception))

    def test_verify_roles_exist_for_all_permission_succeeds_when_all_covered(
        self,
    ) -> None:
        """Test verification succeeds when all permissions have roles."""
        # Setup
        self.service.register_role(TestRole.USER, {self.permission1, self.permission2})
        self.service.register_role(TestRole.ADMIN, {self.permission3, self.permission4})

        # Execute (should not raise)
        self.service.verify_roles_exist_for_all_permission()

    def test_verify_roles_exist_for_all_permission_fails_when_missing_roles(
        self,
    ) -> None:
        """Test verification fails when some permissions have no roles."""
        # Setup
        self.service.register_role(TestRole.USER, {self.permission1, self.permission2})
        # permission3 and permission4 have no roles

        # Execute & Verify
        with self.assertRaises(exc.ServiceException) as cm:
            self.service.verify_roles_exist_for_all_permission()
        self.assertIn("No roles for permission(s)", str(cm.exception))


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestRoleHierarchy(BaseRbacServiceTestCase):
    """Test role hierarchy and sub-role calculations."""

    def test_get_sub_roles_calculates_hierarchy_correctly(self) -> None:
        """Test that sub-roles are calculated correctly based on permission subsets."""
        # Setup
        self.service.register_role(
            TestRole.ROOT,
            {self.permission1, self.permission2, self.permission3, self.permission4},
        )
        self.service.register_role(
            TestRole.ADMIN, {self.permission1, self.permission2, self.permission3}
        )
        self.service.register_role(TestRole.USER, {self.permission1, self.permission2})
        self.service.register_role(TestRole.GUEST, {self.permission1})

        # Execute
        root_sub_roles = self.service.get_sub_roles(TestRole.ROOT)
        admin_sub_roles = self.service.get_sub_roles(TestRole.ADMIN)
        user_sub_roles = self.service.get_sub_roles(TestRole.USER)
        guest_sub_roles = self.service.get_sub_roles(TestRole.GUEST)

        # Verify
        self.assertEqual(
            root_sub_roles, {TestRole.ADMIN, TestRole.USER, TestRole.GUEST}
        )
        self.assertEqual(admin_sub_roles, {TestRole.USER, TestRole.GUEST})
        self.assertEqual(user_sub_roles, {TestRole.GUEST})
        self.assertEqual(guest_sub_roles, set())

    def test_get_sub_roles_caches_results(self) -> None:
        """Test that sub-role calculations are cached."""
        # Setup
        self.service.register_role(TestRole.ADMIN, {self.permission1, self.permission2})
        self.service.register_role(TestRole.USER, {self.permission1})

        # Execute - first call
        sub_roles1 = self.service.get_sub_roles(TestRole.ADMIN)
        # Execute - second call
        sub_roles2 = self.service.get_sub_roles(TestRole.ADMIN)

        # Verify
        self.assertIs(sub_roles1, sub_roles2)  # Same object reference (cached)

    def test_get_sub_roles_cache_cleared_on_role_update(self) -> None:
        """Test that sub-role cache is cleared when roles are updated."""
        # Setup
        self.service.register_role(TestRole.ADMIN, {self.permission1, self.permission2})
        self.service.register_role(TestRole.USER, {self.permission1})
        self.service.get_sub_roles(TestRole.ADMIN)  # Cache it

        # Execute - update a role
        self.service.register_role(TestRole.ADMIN, {self.permission1}, update_role=True)

        # Verify cache was cleared by checking internal state
        self.assertNotIn(TestRole.ADMIN, self.service._sub_roles_by_role)


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestUserPermissions(BaseRbacServiceTestCase):
    """Test user permission retrieval and authorization checks."""

    def test_retrieve_user_permissions_returns_union_of_role_permissions(self) -> None:
        """Test that user permissions are union of all their role permissions."""
        # Setup
        self.service.register_role(TestRole.USER, {self.permission1, self.permission2})
        self.service.register_role(TestRole.GUEST, {self.permission3})
        self.service.set_user_roles(self.user.id, {TestRole.USER, TestRole.GUEST})

        # Execute
        permissions = self.service.retrieve_user_permissions(self.user)

        # Verify
        self.assertEqual(
            permissions, {self.permission1, self.permission2, self.permission3}
        )

    def test_retrieve_user_permissions_empty_roles_returns_empty_set(self) -> None:
        """Test that user with no roles has no permissions."""
        # Setup
        self.service.set_user_roles(self.user.id, set())

        # Execute
        permissions = self.service.retrieve_user_permissions(self.user)

        # Verify
        self.assertEqual(permissions, set())

    def test_retrieve_user_has_all_rbac_permissions_true_when_has_all(self) -> None:
        """Test that user has all RBAC permissions when they actually do."""
        # Setup
        self.service.register_permission_without_rbac(
            self.permission4
        )  # Exclude from RBAC
        self.service.register_role(
            TestRole.ROOT, {self.permission1, self.permission2, self.permission3}
        )
        self.service.set_user_roles(self.user.id, {TestRole.ROOT})

        # Execute
        has_all = self.service.retrieve_user_has_all_rbac_permissions(self.user)

        # Verify
        self.assertTrue(has_all)

    def test_retrieve_user_has_all_rbac_permissions_false_when_missing(self) -> None:
        """Test that user doesn't have all RBAC permissions when missing some."""
        # Setup
        self.service.register_role(TestRole.USER, {self.permission1, self.permission2})
        self.service.set_user_roles(self.user.id, {TestRole.USER})
        # User is missing permission3 and permission4

        # Execute
        has_all = self.service.retrieve_user_has_all_rbac_permissions(self.user)

        # Verify
        self.assertFalse(has_all)

    def test_retrieve_user_has_more_permissions_with_user_target(self) -> None:
        """Test checking if user has more permissions than another user."""
        # Setup
        self.service.register_role(
            TestRole.ADMIN, {self.permission1, self.permission2, self.permission3}
        )
        self.service.register_role(TestRole.USER, {self.permission1, self.permission2})
        self.service.set_user_roles(self.user.id, {TestRole.ADMIN})
        self.service.set_user_roles(self.admin_user.id, {TestRole.USER})

        # Execute
        has_more = self.service.retrieve_user_has_more_permissions(
            self.user, self.admin_user
        )

        # Verify
        self.assertTrue(has_more)

    def test_retrieve_user_has_more_permissions_with_roles_target(self) -> None:
        """Test checking if user has more permissions than a set of roles."""
        # Setup
        self.service.register_role(
            TestRole.ADMIN, {self.permission1, self.permission2, self.permission3}
        )
        self.service.register_role(TestRole.USER, {self.permission1, self.permission2})
        self.service.set_user_roles(self.user.id, {TestRole.ADMIN})

        # Execute
        has_more = self.service.retrieve_user_has_more_permissions(
            self.user, {TestRole.USER}
        )

        # Verify
        self.assertTrue(has_more)

    def test_retrieve_user_has_more_permissions_false_when_subset(self) -> None:
        """Test that user doesn't have more permissions when they're a subset."""
        # Setup
        self.service.register_role(
            TestRole.ADMIN, {self.permission1, self.permission2, self.permission3}
        )
        self.service.register_role(TestRole.USER, {self.permission1, self.permission2})
        self.service.set_user_roles(self.user.id, {TestRole.USER})

        # Execute
        has_more = self.service.retrieve_user_has_more_permissions(
            self.user, {TestRole.ADMIN}
        )

        # Verify
        self.assertFalse(has_more)


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestCommandPermissions(BaseRbacServiceTestCase):
    """Test command-related permission functionality."""

    def test_get_rbac_permissions_for_command_class_excludes_non_rbac(self) -> None:
        """Test getting RBAC permissions for a command class excludes non-RBAC permissions."""
        # Setup
        self.service.register_permission_without_rbac(self.permission2)

        # Execute
        rbac_permissions = self.service.get_rbac_permissions_for_command_class(
            TestCommand
        )

        # Verify
        self.assertEqual(rbac_permissions, {self.permission1})  # permission2 excluded

    def test_get_command_classes_with_rbac_returns_correct_classes(self) -> None:
        """Test getting command classes that have RBAC permissions."""
        # Setup
        self.service.register_permission_without_rbac(self.permission3)
        self.service.register_permission_without_rbac(self.permission4)

        # Execute
        command_classes = self.service.get_command_classes_with_rbac()

        # Verify
        self.assertEqual(command_classes, {TestCommand})  # TestCommand2 excluded

    def test_get_root_permissions_returns_all_domain_permissions(self) -> None:
        """Test that get_root_permissions returns all domain permissions."""
        # Execute
        root_permissions = self.service.get_root_permissions()

        # Verify
        self.assertEqual(root_permissions, self.mock_domain.permissions)


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestRbacPolicyRegistration(BaseRbacServiceTestCase):
    """Test RBAC policy registration."""

    def test_register_rbac_policies_registers_for_all_rbac_commands(self) -> None:
        """Test that RBAC policies are registered for all RBAC command classes."""
        # Setup
        self.service.register_permission_without_rbac(self.permission3)
        self.service.register_permission_without_rbac(self.permission4)

        # Execute
        self.service.register_rbac_policies()

        # Verify
        self.mock_app.register_policy.assert_called_once()
        call_args = self.mock_app.register_policy.call_args
        self.assertEqual(call_args[0][0], TestCommand)  # Command class
        self.assertIsInstance(call_args[0][1], RbacPolicy)  # Policy instance
        self.assertEqual(call_args[0][2], EventTiming.BEFORE)  # Timing

    def test_register_rbac_policies_with_custom_functions(self) -> None:
        """Test registering RBAC policies with custom override functions."""
        # Setup
        custom_get_permission = Mock()
        custom_functions = {
            "get_permission_for_command": custom_get_permission,
        }

        # Execute
        self.service.register_rbac_policies(**custom_functions)

        # Verify policy was registered (exact testing of RbacPolicy internals would require more complex setup)
        self.mock_app.register_policy.assert_called()


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestHierarchicalRolePermissions(BaseRbacServiceTestCase):
    """Test hierarchical role permission expansion."""

    def test_expand_hierarchical_role_permissions_expands_correctly(self) -> None:
        """Test that hierarchical role permissions are expanded correctly."""
        # Setup
        role_hierarchy = {
            TestRole.ROOT: {TestRole.ADMIN, TestRole.USER, TestRole.GUEST},
            TestRole.ADMIN: {TestRole.USER, TestRole.GUEST},
            TestRole.USER: {TestRole.GUEST},
            TestRole.GUEST: set(),
        }
        role_permission_sets = {
            TestRole.GUEST: {(TestCommand, PermissionTypeSet({PermissionType.READ}))},
            TestRole.USER: {(TestCommand, PermissionTypeSet({PermissionType.UPDATE}))},
            TestRole.ADMIN: {(TestCommand2, PermissionTypeSet({PermissionType.READ}))},
        }

        # Execute
        expanded = BaseRbacService.expand_hierarchical_role_permissions(
            role_hierarchy, role_permission_sets
        )

        # Verify
        self.assertEqual(expanded[TestRole.GUEST], {(TestCommand, PermissionType.READ)})
        self.assertEqual(
            expanded[TestRole.USER],
            {
                (TestCommand, PermissionType.READ),
                (TestCommand, PermissionType.UPDATE),
            },
        )
        self.assertEqual(
            expanded[TestRole.ADMIN],
            {
                (TestCommand, PermissionType.READ),
                (TestCommand, PermissionType.UPDATE),
                (TestCommand2, PermissionType.READ),
            },
        )
        self.assertEqual(
            expanded[TestRole.ROOT],
            {
                (TestCommand, PermissionType.READ),
                (TestCommand, PermissionType.UPDATE),
                (TestCommand2, PermissionType.READ),
            },
        )

    def test_expand_hierarchical_role_permissions_detects_redundant_permissions(
        self,
    ) -> None:
        """Test that redundant permissions in hierarchy are detected."""
        # Setup
        role_hierarchy = {
            TestRole.ADMIN: {TestRole.USER},
            TestRole.USER: set(),
        }
        role_permission_sets = {
            TestRole.USER: {(TestCommand, PermissionTypeSet({PermissionType.READ}))},
            TestRole.ADMIN: {
                (TestCommand, PermissionTypeSet({PermissionType.READ}))
            },  # Redundant!
        }

        # Execute & Verify
        with self.assertRaises(exc.InitializationServiceError) as cm:
            BaseRbacService.expand_hierarchical_role_permissions(
                role_hierarchy, role_permission_sets, verify_redundant_permissions=True
            )
        self.assertIn("Duplicate permissions", str(cm.exception))

    def test_expand_hierarchical_role_permissions_allows_redundant_when_disabled(
        self,
    ) -> None:
        """Test that redundant permissions are allowed when verification is disabled."""
        # Setup
        role_hierarchy = {
            TestRole.ADMIN: {TestRole.USER},
            TestRole.USER: set(),
        }
        role_permission_sets = {
            TestRole.USER: {(TestCommand, PermissionTypeSet({PermissionType.READ}))},
            TestRole.ADMIN: {
                (TestCommand, PermissionTypeSet({PermissionType.READ}))
            },  # Redundant but allowed
        }

        # Execute (should not raise)
        expanded = BaseRbacService.expand_hierarchical_role_permissions(
            role_hierarchy, role_permission_sets, verify_redundant_permissions=False
        )

        # Verify
        self.assertEqual(expanded[TestRole.ADMIN], {(TestCommand, PermissionType.READ)})

    def test_expand_hierarchical_role_permissions_handles_permission_type_sets(
        self,
    ) -> None:
        """Test that PermissionTypeSet is properly expanded to individual PermissionTypes."""
        # Setup
        role_hierarchy = {
            TestRole.USER: set(),
        }
        role_permission_sets = {
            TestRole.USER: {
                (
                    TestCommand,
                    PermissionTypeSet({PermissionType.READ, PermissionType.UPDATE}),
                )
            },
        }

        # Execute
        expanded = BaseRbacService.expand_hierarchical_role_permissions(
            role_hierarchy, role_permission_sets
        )

        # Verify
        self.assertEqual(
            expanded[TestRole.USER],
            {
                (TestCommand, PermissionType.READ),
                (TestCommand, PermissionType.UPDATE),
            },
        )


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestUserAuthorizationBehavior(BaseRbacServiceTestCase):
    """Test user authorization behavior methods."""

    def test_retrieve_user_is_root_returns_false_by_default(self) -> None:
        """Test that retrieve_user_is_root returns False by default."""
        # Execute
        is_root = self.service.retrieve_user_is_root(self.user)

        # Verify
        self.assertFalse(is_root)

    def test_retrieve_user_is_root_can_be_overridden(self) -> None:
        """Test that retrieve_user_is_root can be overridden in concrete implementation."""
        # Setup
        self.service.set_root_user(self.user.id)

        # Execute
        is_root = self.service.retrieve_user_is_root(self.user)

        # Verify
        self.assertTrue(is_root)

    def test_retrieve_user_is_non_rbac_authorized_returns_false_by_default(
        self,
    ) -> None:
        """Test that retrieve_user_is_non_rbac_authorized returns False by default in concrete implementation."""
        # Setup
        cmd = self.create_test_command()

        # Execute
        is_authorized = self.service.retrieve_user_is_non_rbac_authorized(cmd)

        # Verify
        self.assertFalse(is_authorized)

    def test_retrieve_user_is_non_rbac_authorized_can_be_overridden(self) -> None:
        """Test that retrieve_user_is_non_rbac_authorized can be overridden."""
        # Setup
        self.service.set_non_rbac_authorized(self.user.id, False)
        cmd = self.create_test_command()

        # Execute
        is_authorized = self.service.retrieve_user_is_non_rbac_authorized(cmd)

        # Verify
        self.assertFalse(is_authorized)


@pytest.mark.scenario_ids("TC-SEC-28-05")
class TestEdgeCasesAndErrorConditions(BaseRbacServiceTestCase):
    """Test edge cases and error conditions."""

    def test_register_roles_with_invalid_on_missing_root_permissions_raises(
        self,
    ) -> None:
        """Test that invalid on_missing_root_permissions value raises error."""
        # Setup
        role_permissions = {TestRole.ROOT: set()}

        # Execute & Verify
        with self.assertRaises(ValueError) as cm:
            self.service.register_roles(
                role_permissions,
                root_role=TestRole.ROOT,
                on_missing_root_permissions="invalid",
            )
        self.assertIn(
            "Invalid value for on_missing_root_permissions", str(cm.exception)
        )

    def test_register_roles_creates_root_role_when_missing(self) -> None:
        """Test that root role is created when missing from role_permissions."""
        # Setup
        role_permissions = {TestRole.USER: {(TestCommand, PermissionType.READ)}}

        # Execute
        self.service.register_roles(role_permissions, root_role=TestRole.ROOT)

        # Verify
        self.assertEqual(
            self.service.permissions_by_role[TestRole.ROOT],
            self.mock_domain.permissions,
        )

    def test_empty_role_hierarchy_handled_gracefully(self) -> None:
        """Test that empty role hierarchy is handled gracefully."""
        # Execute
        expanded = BaseRbacService.expand_hierarchical_role_permissions({}, {})

        # Verify
        self.assertEqual(expanded, {})

    def test_role_with_no_sub_roles_returns_empty_set(self) -> None:
        """Test that role with no sub-roles returns empty set."""
        # Setup
        self.service.register_role(TestRole.USER, {self.permission1})

        # Execute
        sub_roles = self.service.get_sub_roles(TestRole.USER)

        # Verify
        self.assertEqual(sub_roles, set())

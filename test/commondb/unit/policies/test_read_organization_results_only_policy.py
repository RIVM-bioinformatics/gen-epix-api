from typing import Any, cast
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb import enum
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, model
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.commondb.policies.read_organization_results_only_policy import (
    ReadOrganizationResultsOnlyPolicy,
)
from gen_epix.fastapp import CrudOperation, exc
from gen_epix.fastapp.services.rbac.service import (
    BaseRbacService as FastBaseRbacService,
)
from gen_epix.fastapp.user_manager import BaseUserManager as FastBaseUserManager


class BasePolicyTestCase(TestCase):
    """Base test case with common fixtures and utilities for policy tests."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # User and organizations
        self.org_id: UUID = uuid4()
        self.other_org_id: UUID = uuid4()
        self.user: model.User = model.User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={enum.Role.ORG_USER.value},
            organization_id=self.org_id,
            is_active=True,
        )

        # App implementation details (role maps sufficient for tests)
        class DummyRbacService(FastBaseRbacService):
            pass

        class DummyUserManager(FastBaseUserManager):
            def get_user_instance_from_claims(self, claims: dict[str, Any]) -> model.User | None:  # type: ignore[override]
                return None

            def create_root_user_from_claims(self, claims: dict[str, Any]) -> model.User:  # type: ignore[override]
                return model.User(
                    id=uuid4(),
                    key=claims.get("email", "root@example.com"),
                    email=claims.get("email", "root@example.com"),
                    roles={enum.Role.APP_ADMIN.value},
                    organization_id=uuid4(),
                    is_active=True,
                )

            def is_root_user_claims(self, claims: dict[str, Any]) -> bool:  # type: ignore[override]
                return False

            def is_root_user(self, user: model.User) -> bool:  # type: ignore[override]
                return False

            def create_user_from_claims(self, claims: dict[str, Any]) -> model.User | None:  # type: ignore[override]
                return None

            def create_new_user_from_token(self, user: model.User, token: str, **kwargs: Any) -> model.User:  # type: ignore[override]
                return user

            def is_existing_user_by_key(self, user_key: str | None, uow: Any) -> bool:  # type: ignore[override]
                return False

        self.app_impl: AppImplDetails = AppImplDetails(
            sorted_service_types=[enum.ServiceType.ABAC],
            services={},
            repositories={},
            registered_user_dependency_or_none=None,
            new_user_dependency_or_none=None,
            idp_user_dependency_or_none=None,
            model_class_map={},
            command_class_map={},
            policy_class_map={},
            rbac_service_class=DummyRbacService,  # type: ignore[type-abstract]
            user_manager_class=DummyUserManager,  # type: ignore[type-abstract]
            role_map=enum.Role,  # type: ignore[arg-type]
            role_set_map=enum.RoleSet,  # type: ignore[arg-type]
            role_permissions_map={},
        )

        # Mock abac service and app
        self.app_mock = Mock()
        self.app_mock.impl = self.app_impl
        self.app_mock.handle = Mock(return_value=[])

        self.abac_service: BaseAbacService = cast(
            BaseAbacService, Mock(spec=BaseAbacService)
        )
        self.abac_service.app = self.app_mock  # type: ignore[misc]
        self.abac_service.retrieve_organizations_under_admin = Mock(return_value=set())  # type: ignore[method-assign]

        # Policy under test
        self.policy = ReadOrganizationResultsOnlyPolicy(self.abac_service)

    # Helpers
    def create_user(
        self, roles: set[str] | None = None, organization_id: UUID | None = None
    ) -> model.User:
        """Create a user with optional roles and organization."""
        return model.User(
            id=uuid4(),
            key="user@example.com",
            email="user@example.com",
            roles=roles or {enum.Role.ORG_USER.value},
            organization_id=organization_id or self.org_id,
            is_active=True,
        )

    def create_org_admin_policy(
        self, organization_id: UUID, user_id: UUID | None = None, is_active: bool = True
    ) -> model.OrganizationAdminPolicy:
        """Create an OrganizationAdminPolicy object for filtering assertions."""
        return model.OrganizationAdminPolicy(
            organization_id=organization_id,
            user_id=user_id or uuid4(),
            is_active=is_active,
        )

    def create_crud_cmd(
        self,
        cmd_class: type[command.CrudCommand],
        operation: CrudOperation,
        user: model.User | None,
        obj_ids: UUID | list[UUID] | None = None,
        objs: model.Model | list[model.Model] | None = None,
    ) -> command.CrudCommand:
        """Create a CRUD command instance with minimal valid fields."""
        # Provide defaults consistent with CRUD validator
        if obj_ids is None:
            if operation == CrudOperation.READ_ONE:
                obj_ids = uuid4()
            elif operation == CrudOperation.READ_SOME:
                obj_ids = [uuid4(), uuid4()]
            elif operation == CrudOperation.DELETE_ONE:
                obj_ids = uuid4()
            elif operation == CrudOperation.DELETE_SOME:
                obj_ids = [uuid4()]
        if objs is None:
            if operation in {CrudOperation.CREATE_ONE, CrudOperation.UPDATE_ONE}:
                # Minimal model instance for write operations
                objs = model.OrganizationAdminPolicy(
                    organization_id=self.org_id, user_id=uuid4(), is_active=True
                )
            elif operation in {CrudOperation.CREATE_SOME, CrudOperation.UPDATE_SOME}:
                objs = [
                    model.OrganizationAdminPolicy(
                        organization_id=self.org_id, user_id=uuid4(), is_active=True
                    )
                ]
        return cmd_class(operation=operation, obj_ids=obj_ids, objs=objs, user=user)  # type: ignore[arg-type]


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestPassThroughAndErrors(BasePolicyTestCase):
    """Test scenarios for early returns and error branches."""

    def test_no_user_raises_service_exception(self) -> None:
        # 1) Input
        cmd: command.CrudCommand = self.create_crud_cmd(
            command.OrganizationAdminPolicyCrudCommand,
            CrudOperation.READ_ALL,
            user=None,
        )
        retval: list[model.OrganizationAdminPolicy] = []

        # 2) Mocks already set in setUp

        # 3) Execute
        with pytest.raises(exc.ServiceException) as e:
            self.policy.filter(cmd, retval)

        # 4) Verify
        assert "Command has no user" in str(e.value.message)

    def test_retrieve_invite_constraints_passthrough(self) -> None:
        # 1) Input
        cmd: command.RetrieveInviteUserConstraintsCommand = (
            command.RetrieveInviteUserConstraintsCommand(user=self.user)
        )
        retval: list[int] = [1, 2, 3]

        # 2) Mocks: none specific

        # 3) Execute
        out = self.policy.filter(cmd, retval)

        # 4) Verify
        assert out is retval

    def test_non_crud_command_raises_not_implemented(self) -> None:
        # 1) Input
        cmd: command.RetrieveOrganizationsUnderAdminCommand = (
            command.RetrieveOrganizationsUnderAdminCommand(user=self.user)
        )
        retval: list[Any] = []

        # 2) Mocks: none specific

        # 3) Execute
        with pytest.raises(NotImplementedError):
            self.policy.filter(cmd, retval)

    def test_non_read_operation_passthrough(self) -> None:
        # 1) Input
        cmd: command.CrudCommand = self.create_crud_cmd(
            command.OrganizationAdminPolicyCrudCommand,
            CrudOperation.DELETE_ONE,
            user=self.user,
        )
        retval: list[model.OrganizationAdminPolicy] = [
            self.create_org_admin_policy(self.org_id),
            self.create_org_admin_policy(self.other_org_id),
        ]

        # 2) Mocks: none specific

        # 3) Execute
        out = self.policy.filter(cmd, retval)

        # 4) Verify
        assert out is retval
        assert self.abac_service.retrieve_organizations_under_admin.call_count == 0  # type: ignore[attr-defined]

    def test_exempt_roles_passthrough(self) -> None:
        # 1) Input
        exempt_user: model.User = self.create_user(roles={enum.Role.APP_ADMIN.value})
        cmd: command.CrudCommand = self.create_crud_cmd(
            command.OrganizationAdminPolicyCrudCommand,
            CrudOperation.READ_ALL,
            user=exempt_user,
        )
        retval: list[model.OrganizationAdminPolicy] = [
            self.create_org_admin_policy(self.org_id),
            self.create_org_admin_policy(self.other_org_id),
        ]

        # 2) Mocks: none specific

        # 3) Execute
        out = self.policy.filter(cmd, retval)

        # 4) Verify
        assert out is retval
        assert self.abac_service.retrieve_organizations_under_admin.call_count == 0  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestOrganizationIdFiltering(BasePolicyTestCase):
    """Test scenarios related to organization_id attribute filtering."""

    def test_read_all_filters_with_abac_orgs_and_user_org(self) -> None:
        # 1) Input
        cmd: command.CrudCommand = self.create_crud_cmd(
            command.OrganizationAdminPolicyCrudCommand,
            CrudOperation.READ_ALL,
            user=self.user,
        )
        retval: list[model.OrganizationAdminPolicy] = [
            self.create_org_admin_policy(self.org_id),
            self.create_org_admin_policy(self.other_org_id),
            self.create_org_admin_policy(uuid4()),
        ]

        # 2) Mocks
        self.abac_service.retrieve_organizations_under_admin.return_value = {  # type: ignore[attr-defined]
            self.other_org_id
        }

        # 3) Execute
        out = self.policy.filter(cmd, retval)

        # 4) Verify
        assert isinstance(out, list)
        ids = {x.organization_id for x in out}
        assert ids == {self.org_id, self.other_org_id}
        self.abac_service.retrieve_organizations_under_admin.assert_called_once()  # type: ignore[attr-defined]
        call_cmd = self.abac_service.retrieve_organizations_under_admin.call_args[0][0]  # type: ignore[attr-defined]
        assert isinstance(call_cmd, command.RetrieveOrganizationsUnderAdminCommand)
        assert call_cmd.user == self.user

    def test_read_all_filters_with_no_abac_orgs_uses_user_org_only(self) -> None:
        # 1) Input
        cmd: command.CrudCommand = self.create_crud_cmd(
            command.OrganizationAdminPolicyCrudCommand,
            CrudOperation.READ_ALL,
            user=self.user,
        )
        retval: list[model.OrganizationAdminPolicy] = [
            self.create_org_admin_policy(self.org_id),
            self.create_org_admin_policy(self.other_org_id),
        ]

        # 2) Mocks
        self.abac_service.retrieve_organizations_under_admin.return_value = set()  # type: ignore[attr-defined]

        # 3) Execute
        out = self.policy.filter(cmd, retval)

        # 4) Verify
        assert len(out) == 1
        assert out[0].organization_id == self.user.organization_id

    def test_read_one_not_in_org_raises_unauthorized(self) -> None:
        # 1) Input
        cmd: command.CrudCommand = self.create_crud_cmd(
            command.OrganizationAdminPolicyCrudCommand,
            CrudOperation.READ_ONE,
            user=self.user,
        )
        retval: model.OrganizationAdminPolicy = self.create_org_admin_policy(uuid4())

        # 2) Mocks
        self.abac_service.retrieve_organizations_under_admin.return_value = set()  # type: ignore[attr-defined]

        # 3) Execute
        with pytest.raises(exc.UnauthorizedAuthError) as e:
            self.policy.filter(cmd, retval)

        # 4) Verify
        assert "User is not an admin for the organization" in str(e.value.message)

    def test_read_some_mixed_orgs_raises_unauthorized(self) -> None:
        # 1) Input
        cmd: command.CrudCommand = self.create_crud_cmd(
            command.OrganizationAdminPolicyCrudCommand,
            CrudOperation.READ_SOME,
            user=self.user,
        )
        retval: list[model.OrganizationAdminPolicy] = [
            self.create_org_admin_policy(self.org_id),
            self.create_org_admin_policy(uuid4()),
        ]

        # 2) Mocks
        self.abac_service.retrieve_organizations_under_admin.return_value = set()  # type: ignore[attr-defined]

        # 3) Execute
        with pytest.raises(exc.UnauthorizedAuthError) as e:
            self.policy.filter(cmd, retval)

        # 4) Verify
        assert "User is not an admin for some of the organizations" in str(
            e.value.message
        )

    def test_unrecognized_crud_command_raises_not_implemented(self) -> None:
        # 1) Input
        cmd: command.CrudCommand = self.create_crud_cmd(
            command.SiteCrudCommand,
            CrudOperation.READ_ALL,
            user=self.user,
        )
        retval: list[Any] = []

        # 2) Mocks: none specific

        # 3) Execute
        with pytest.raises(NotImplementedError):
            self.policy.filter(cmd, retval)


@pytest.mark.scenario_ids("TC-SEC-30-02")
class TestUserIdFiltering(BasePolicyTestCase):
    """Test scenarios related to user_id attribute filtering (monkeypatched)."""

    def setUp(self) -> None:
        super().setUp()
        # Monkeypatch policy to drive execution into user_id branch
        self.policy.has_organization_id_attr_command_classes = set()
        self.policy.has_user_id_attr_command_classes = {command.UserCrudCommand}

        # Provide a subclass with get_objs() to satisfy policy expectations
        class UserCrudCommandWithGetObjs(command.UserCrudCommand):
            def get_objs(self) -> list:
                return []

        self.user_crud_cmd_with_get_objs = UserCrudCommandWithGetObjs

    def test_user_id_read_all_filters_and_app_handle_called(self) -> None:
        # 1) Input
        cmd: command.CrudCommand = self.create_crud_cmd(
            self.user_crud_cmd_with_get_objs,
            CrudOperation.READ_ALL,
            user=self.user,
        )
        # Retval with user_id attrs
        allowed_user_id: UUID = uuid4()
        denied_user_id: UUID = uuid4()
        retval: list[model.OrganizationAdminPolicy] = [
            self.create_org_admin_policy(self.org_id, user_id=allowed_user_id),
            self.create_org_admin_policy(self.other_org_id, user_id=denied_user_id),
        ]

        # 2) Mocks
        # abac returns user's own org only
        self.abac_service.retrieve_organizations_under_admin.return_value = set()  # type: ignore[attr-defined]
        # app.handle returns users in the caller's org (only allowed_user_id present)
        users: list[model.User] = [
            model.User(
                id=allowed_user_id,
                key="allowed@example.com",
                email="allowed@example.com",
                roles={enum.Role.ORG_USER.value},
                organization_id=self.org_id,
                is_active=True,
            )
        ]
        self.app_mock.handle.return_value = users

        # 3) Execute
        out = self.policy.filter(cmd, retval)

        # 4) Verify
        assert len(out) == 1
        assert out[0].user_id == allowed_user_id
        # app.handle invoked with READ_ALL and obj_ids None
        handle_cmd = self.app_mock.handle.call_args[0][0]
        assert isinstance(handle_cmd, command.UserCrudCommand)
        assert handle_cmd.operation == CrudOperation.READ_ALL
        assert handle_cmd.obj_ids is None

    def test_user_id_read_one_not_allowed_raises(self) -> None:
        # 1) Input
        cmd: command.CrudCommand = self.create_crud_cmd(
            self.user_crud_cmd_with_get_objs,
            CrudOperation.READ_ONE,
            user=self.user,
        )
        denied_user_id: UUID = uuid4()
        retval: model.OrganizationAdminPolicy = self.create_org_admin_policy(
            self.other_org_id, user_id=denied_user_id
        )

        # 2) Mocks
        self.abac_service.retrieve_organizations_under_admin.return_value = {  # type: ignore[attr-defined]
            self.other_org_id
        }
        # Only allow different user id
        users: list[model.User] = [
            model.User(
                id=uuid4(),
                key="other@example.com",
                email="other@example.com",
                roles={enum.Role.ORG_USER.value},
                organization_id=self.other_org_id,
                is_active=True,
            )
        ]
        self.app_mock.handle.return_value = users
        # get_objs provided by subclass; policy will derive empty obj_ids

        # 3) Execute
        with pytest.raises(exc.UnauthorizedAuthError) as e:
            self.policy.filter(cmd, retval)

        # 4) Verify
        assert "User is not an admin for the organization" in str(e.value.message)

    def test_user_id_read_some_not_subset_raises(self) -> None:
        # 1) Input
        cmd: command.CrudCommand = self.create_crud_cmd(
            self.user_crud_cmd_with_get_objs,
            CrudOperation.READ_SOME,
            user=self.user,
        )
        allowed_user_id: UUID = uuid4()
        denied_user_id: UUID = uuid4()
        retval: list[model.OrganizationAdminPolicy] = [
            self.create_org_admin_policy(self.org_id, user_id=allowed_user_id),
            self.create_org_admin_policy(self.org_id, user_id=denied_user_id),
        ]

        # 2) Mocks
        self.abac_service.retrieve_organizations_under_admin.return_value = {  # type: ignore[attr-defined]
            self.org_id
        }
        users: list[model.User] = [
            model.User(
                id=allowed_user_id,
                key="allowed@example.com",
                email="allowed@example.com",
                roles={enum.Role.ORG_USER.value},
                organization_id=self.org_id,
                is_active=True,
            )
        ]
        self.app_mock.handle.return_value = users
        # get_objs provided by subclass; policy will derive empty obj_ids

        # 3) Execute
        with pytest.raises(exc.UnauthorizedAuthError) as e:
            self.policy.filter(cmd, retval)

        # 4) Verify
        assert "User is not an admin for some of the organizations" in str(
            e.value.message
        )
        self.app_mock.handle.assert_called()

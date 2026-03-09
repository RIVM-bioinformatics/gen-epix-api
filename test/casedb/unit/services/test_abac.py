"""
Unit tests for AbacService.

The tests focus on verifying the behavior of the AbacService class, including policy
registration, ABAC (Attribute-Based Access Control) resolution for cases, and user
organization update logic.

The tests handle the following scenarios:
1. Policy registration for ABAC commands.
2. Retrieval of ABAC attributes for cases, including full access shortcuts and caching.
3. Temporary update of a user's organization and the associated policy transfers and
   deletions.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.service.abac import BaseAbacService
from gen_epix.casedb.policies.case_abac_policy import CaseAbacPolicy
from gen_epix.casedb.services.abac import AbacService
from gen_epix.commondb.domain.enum import RoleSet as CommonRoleSet
from gen_epix.commondb.domain.model.organization import User as OrgUser
from gen_epix.fastapp import EventTiming


class BaseAbacTestCase(TestCase):
    """Base test case with common fixtures and utilities."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.user_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        self.org_id = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
        self.new_org_id = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
        self.case_type_id = UUID("11111111-1111-1111-1111-111111111111")
        self.data_collection_id = UUID("22222222-2222-2222-2222-222222222222")
        self.case_type_set_id = UUID("33333333-3333-3333-3333-333333333333")
        self.read_col_set_id = UUID("44444444-4444-4444-4444-444444444444")
        self.write_col_set_id = UUID("55555555-5555-5555-5555-555555555555")
        self.col_id_1 = UUID("66666666-6666-6666-6666-666666666661")
        self.col_id_2 = UUID("66666666-6666-6666-6666-666666666662")
        self.col_id_3 = UUID("66666666-6666-6666-6666-666666666663")
        self.from_data_collection_id = UUID("77777777-7777-7777-7777-777777777777")

        self.app = self._create_app_mock()
        self.repository = Mock()
        uow = Mock()
        uow.__enter__ = Mock(return_value=uow)
        uow.__exit__ = Mock(return_value=None)
        self.repository.uow.return_value = uow
        self.repository.crud = Mock()
        self.service: AbacService = AbacService(
            app=self.app, repository=self.repository
        )
        self.service.app.handle = Mock()  # type: ignore[method-assign]

        self.service.role_set_map = {
            CommonRoleSet.GE_APP_ADMIN: {"APP_ADMIN"},  # type: ignore[dict-item]
        }

    # Helpers

    def _create_app_mock(self) -> Any:
        """Create a minimal App mock compatible with AbacService __init__ and tests."""
        # Impl with identity mapper and empty role maps
        impl = SimpleNamespace(
            get_mapped_class=lambda cls: cls,
            role_map={},
            role_set_map={},
        )
        # Domain with required methods
        domain = SimpleNamespace(
            register_service_type=Mock(),
            get_crud_commands_for_service_type=Mock(return_value=[]),
            get_model_links=Mock(return_value={}),
        )
        app = SimpleNamespace(
            impl=impl,
            domain=domain,
            register_handler=Mock(),
            register_policy=Mock(),
            handle=Mock(),
            generate_id=Mock(return_value="svc-id"),
            generate_timestamp=Mock(return_value=0),
            create_log_message=Mock(return_value=""),
        )
        return app

    def create_cmd_with_user(self, user_id: UUID | None) -> Any:
        """Create a command-like object with a .user containing an id."""
        return SimpleNamespace(user=SimpleNamespace(id=user_id))

    def create_user_stub(self, id_: UUID, org_id: UUID, roles: set[str]) -> Any:
        """Create a user-like object for get_case_abac cached reads."""
        return OrgUser(
            id=id_,
            key="user@example.org",
            email="user@example.org",
            roles=roles,
            organization_id=org_id,
            is_active=True,
        )

    def create_update_user_cmd(
        self, user: Any, tgt_org_id: UUID, is_new_user: bool
    ) -> Any:
        """Create a command-like object for temp_update_user_own_organization."""
        return SimpleNamespace(
            user=user, organization_id=tgt_org_id, is_new_user=is_new_user
        )

    class UserModelStub:
        """User model stub supporting model_copy used by temp_update_user_own_organization."""

        def __init__(self, id_: UUID, org_id: UUID, roles: set[str]) -> None:
            self.id = id_
            self.organization_id = org_id
            self.roles = roles

        def model_copy(self) -> "BaseAbacTestCase.UserModelStub":
            return BaseAbacTestCase.UserModelStub(
                self.id, self.organization_id, set(self.roles)
            )

    class OrgPolicyDumpStub:
        """Organization policy stub exposing model_dump used to generate new user policies."""

        def __init__(
            self,
            *,
            case_type_set_id: UUID,
            data_collection_id: UUID,
            read_col_set_id: UUID | None,
            write_col_set_id: UUID | None,
            add_case: bool,
            remove_case: bool,
            add_case_set: bool,
            remove_case_set: bool,
            read_case_set: bool,
            write_case_set: bool,
            is_private: bool = True,
            is_active: bool = True,
            from_data_collection_id: UUID | None = None,
        ) -> None:
            self.case_type_set_id = case_type_set_id
            self.data_collection_id = data_collection_id
            self.read_col_set_id = read_col_set_id
            self.write_col_set_id = write_col_set_id
            self.add_case = add_case
            self.remove_case = remove_case
            self.add_case_set = add_case_set
            self.remove_case_set = remove_case_set
            self.read_case_set = read_case_set
            self.write_case_set = write_case_set
            self.is_private = is_private
            self.is_active = is_active
            self.from_data_collection_id = from_data_collection_id

        def model_dump(self, exclude: set[str] | None = None) -> dict[str, Any]:
            return {
                "case_type_set_id": self.case_type_set_id,
                "data_collection_id": self.data_collection_id,
                "read_col_set_id": self.read_col_set_id,
                "write_col_set_id": self.write_col_set_id,
                "add_case": self.add_case,
                "remove_case": self.remove_case,
                "add_case_set": self.add_case_set,
                "remove_case_set": self.remove_case_set,
                "read_case_set": self.read_case_set,
                "write_case_set": self.write_case_set,
                "is_private": self.is_private,
                "is_active": self.is_active,
                "from_data_collection_id": self.from_data_collection_id,
            }


@pytest.mark.scenario_ids("TC-SEC-29-02", "TC-RBAC-05-02")
class TestRegisterPolicies(BaseAbacTestCase):
    """Test registration of policies."""

    def test_register_policies_registers_case_abac_commands(self) -> None:
        """register_policies registers CaseAbacPolicy for all CASE_ABAC_COMMANDS with DURING timing."""
        self.service.app.register_policy = Mock()  # type: ignore[method-assign]
        self.service.register_policies()
        calls = self.service.app.register_policy.call_args_list

        case_abac_calls = [
            call
            for call in calls
            if isinstance(call[0][1], CaseAbacPolicy)
            and call[0][2] == EventTiming.DURING
        ]

        self.assertEqual(len(case_abac_calls), len(BaseAbacService.CASE_ABAC_COMMANDS))

        for call in case_abac_calls:
            args = call[0]
            self.assertIsNotNone(args[0])  # command_class
            self.assertIsNotNone(args[1])  # policy instance
            self.assertEqual(args[2], EventTiming.DURING)


@pytest.mark.scenario_ids("TC-SEC-29-02", "TC-RBAC-05-02")
class TestGetCaseAbac(BaseAbacTestCase):
    """Test get_case_abac behavior."""

    def test_get_case_abac_no_user_raises(self) -> None:
        """get_case_abac raises UnauthorizedAuthError when cmd.user is None."""
        cmd = SimpleNamespace(user=None)

        with self.assertRaises(exc.UnauthorizedAuthError):
            _ = self.service.get_case_abac(cmd)

        self.repository.uow.assert_not_called()

    def test_get_case_abac_none_user_id_raises(self) -> None:
        """get_case_abac raises UnauthorizedAuthError when cmd.user.id is None."""
        cmd = self.create_cmd_with_user(None)

        with self.assertRaises(exc.UnauthorizedAuthError):
            _ = self.service.get_case_abac(cmd)

        self.repository.uow.assert_not_called()

    def test_get_case_abac_full_access_short_circuits(self) -> None:
        """Full access users return is_full_access True and avoid repository calls."""
        cmd = self.create_cmd_with_user(self.user_id)

        user = self.create_user_stub(self.user_id, self.org_id, {"APP_ADMIN"})
        self.service._get_user_by_id_cached = Mock(return_value=user)

        abac = self.service.get_case_abac(cmd)
        self.assertTrue(abac.is_full_access)
        self.assertEqual(abac.case_type_access_abacs, {})
        self.assertEqual(abac.case_type_share_abacs, {})
        self.service._get_user_by_id_cached.assert_called_once_with(self.user_id)
        self.repository.uow.assert_not_called()
        self.service.app.handle.assert_not_called()  # type: ignore[attr-defined]

    def test_get_case_abac_caches_results(self) -> None:
        """Repeated calls with same user id are memoized."""
        cmd = self.create_cmd_with_user(self.user_id)

        user = self.create_user_stub(self.user_id, self.org_id, {"APP_ADMIN"})
        self.service._get_user_by_id_cached = Mock(return_value=user)

        _ = self.service.get_case_abac(cmd)
        _ = self.service.get_case_abac(cmd)

        self.service._get_user_by_id_cached.assert_called_once_with(self.user_id)

    def test_get_case_abac_no_policies_returns_empty(self) -> None:
        """Non-admin user with no policies yields empty ABAC mappings."""
        cmd = self.create_cmd_with_user(self.user_id)

        user = self.create_user_stub(self.user_id, self.org_id, {"ORG_USER"})
        self.service._get_user_by_id_cached = Mock(return_value=user)

        self.repository.crud.side_effect = [
            [],  # org access
            [],  # org share
            [],  # user access
            [],  # user share
        ]
        self.service.app.handle.side_effect = [  # type: ignore[attr-defined]
            [],  # ColCrudCommand
            [],  # CaseTypeSetMemberCrudCommand
            [],  # ColSetMemberCrudCommand
        ]

        abac = self.service.get_case_abac(cmd)

        self.assertFalse(abac.is_full_access)
        self.assertEqual(abac.case_type_access_abacs, {})
        self.assertEqual(abac.case_type_share_abacs, {})
        self.assertEqual(self.repository.crud.call_count, 4)
        self.assertEqual(self.service.app.handle.call_count, 3)  # type: ignore[attr-defined]

    def test_get_case_abac_with_policies_builds_intersection(self) -> None:
        """Intersection across org/user policies and ColSets is computed correctly."""

        cmd = self.create_cmd_with_user(self.user_id)

        user = self.create_user_stub(self.user_id, self.org_id, {"ORG_USER"})
        self.service._get_user_by_id_cached = Mock(return_value=user)

        org_access = SimpleNamespace(
            case_type_set_id=self.case_type_set_id,
            data_collection_id=self.data_collection_id,
            read_col_set_id=self.read_col_set_id,
            write_col_set_id=self.write_col_set_id,
            add_case=True,
            remove_case=True,
            add_case_set=False,
            remove_case_set=True,
            read_case_set=True,
            write_case_set=False,
            is_private=True,
        )
        user_access = SimpleNamespace(
            case_type_set_id=self.case_type_set_id,
            data_collection_id=self.data_collection_id,
            read_col_set_id=self.read_col_set_id,
            write_col_set_id=self.write_col_set_id,
            add_case=True,
            remove_case=False,
            add_case_set=True,
            remove_case_set=True,
            read_case_set=True,
            write_case_set=True,
            is_private=True,
        )

        org_share = SimpleNamespace(
            case_type_set_id=self.case_type_set_id,
            data_collection_id=self.data_collection_id,
            from_data_collection_id=self.from_data_collection_id,
            add_case=True,
            remove_case=True,
            add_case_set=False,
            remove_case_set=False,
        )
        user_share = SimpleNamespace(
            case_type_set_id=self.case_type_set_id,
            data_collection_id=self.data_collection_id,
            from_data_collection_id=self.from_data_collection_id,
            add_case=True,
            remove_case=False,
            add_case_set=True,
            remove_case_set=False,
        )

        self.repository.crud.side_effect = [
            [org_access],  # OrganizationAccessCasePolicy READ_ALL
            [org_share],  # OrganizationShareCasePolicy READ_ALL
            [user_access],  # UserAccessCasePolicy READ_ALL
            [user_share],  # UserShareCasePolicy READ_ALL
        ]

        # app.handle calls: ColCrud, CaseTypeSetMemberCrud, ColSetMemberCrud
        self.service.app.handle.side_effect = [  # type: ignore[attr-defined]
            # ColCrudCommand -> produces mapping case_type_id -> {Col ids}
            [
                SimpleNamespace(id=self.col_id_1, case_type_id=self.case_type_id),
                SimpleNamespace(id=self.col_id_2, case_type_id=self.case_type_id),
                SimpleNamespace(id=self.col_id_3, case_type_id=self.case_type_id),
            ],
            # CaseTypeSetMemberCrudCommand -> map case_type_set_id -> {case_type_id}
            [
                SimpleNamespace(
                    case_type_set_id=self.case_type_set_id,
                    case_type_id=self.case_type_id,
                ),
            ],
            # ColSetMemberCrudCommand -> memberships for read/write ColSets
            [
                SimpleNamespace(
                    col_set_id=self.read_col_set_id,
                    col_id=self.col_id_1,
                ),
                SimpleNamespace(
                    col_set_id=self.read_col_set_id,
                    col_id=self.col_id_2,
                ),
                SimpleNamespace(
                    col_set_id=self.write_col_set_id,
                    col_id=self.col_id_2,
                ),
                SimpleNamespace(
                    col_set_id=self.write_col_set_id,
                    col_id=self.col_id_3,
                ),
            ],
        ]

        abac = self.service.get_case_abac(cmd)

        self.assertFalse(abac.is_full_access)
        self.assertIn(self.case_type_id, abac.case_type_access_abacs)
        access_for_ct = abac.case_type_access_abacs[self.case_type_id]
        self.assertIn(self.data_collection_id, access_for_ct)
        access = access_for_ct[self.data_collection_id]
        self.assertTrue(access.add_case)
        self.assertFalse(access.remove_case)  # AND of True and False -> False
        # read/write Col ids are intersection across Col map and set members AND across org/user dicts
        self.assertSetEqual(
            access.read_col_ids,
            {self.col_id_1, self.col_id_2},
        )
        self.assertSetEqual(
            access.write_col_ids,
            {self.col_id_2, self.col_id_3},
        )
        self.assertTrue(access.read_case_set)
        self.assertFalse(access.write_case_set)
        # Share ABAC
        self.assertIn(self.case_type_id, abac.case_type_share_abacs)
        share_for_ct = abac.case_type_share_abacs[self.case_type_id]
        self.assertIn(self.data_collection_id, share_for_ct)
        share = share_for_ct[self.data_collection_id]
        self.assertSetEqual(
            share.add_case_from_data_collection_ids, {self.from_data_collection_id}
        )
        self.assertSetEqual(
            share.remove_case_from_data_collection_ids, set()
        )  # AND -> empty


@pytest.mark.scenario_ids("TC-SEC-29-02", "TC-RBAC-05-02")
class TestTempUpdateUserOrganization(BaseAbacTestCase):
    """Test temp_update_user_own_organization behavior."""

    def test_no_change_same_org_returns_early(self) -> None:
        """When target org is same and not new user, returns early without side effects."""
        user = self.UserModelStub(self.user_id, self.org_id, {"ORG_USER"})
        cmd = self.create_update_user_cmd(user, self.org_id, is_new_user=False)
        # Attach fake cache_clear targets to assert no calls
        self.service._get_user_by_id_cached = SimpleNamespace(cache_clear=Mock())  # type: ignore[assignment]
        self.service._get_case_abac_cached = SimpleNamespace(cache_clear=Mock())  # type: ignore[assignment]

        retval = self.service.temp_update_user_own_organization(cmd)

        self.assertIs(retval, user)
        self.repository.uow.assert_not_called()
        self.service.app.handle.assert_not_called()  # type: ignore[attr-defined]
        self.service._get_user_by_id_cached.cache_clear.assert_not_called()  # type: ignore[attr-defined]
        self.service._get_case_abac_cached.cache_clear.assert_not_called()  # type: ignore[attr-defined]

    def test_happy_path_transfers_policies_and_updates_user(self) -> None:
        """Transfers policies to new org, deletes old user policies, creates new, updates user, and clears caches."""
        user = self.create_user_stub(self.user_id, self.org_id, {"ORG_USER"})
        cmd = self.create_update_user_cmd(user, self.new_org_id, is_new_user=False)

        existing_uap_id = uuid4()
        existing_usp_id = uuid4()
        existing_user_access_policies = [SimpleNamespace(id=existing_uap_id)]
        existing_user_share_policies = [SimpleNamespace(id=existing_usp_id)]

        org_access_policies = [
            self.OrgPolicyDumpStub(
                case_type_set_id=self.case_type_set_id,
                data_collection_id=self.data_collection_id,
                read_col_set_id=self.read_col_set_id,
                write_col_set_id=self.write_col_set_id,
                add_case=True,
                remove_case=False,
                add_case_set=True,
                remove_case_set=False,
                read_case_set=True,
                write_case_set=False,
                is_private=True,
            )
        ]
        org_share_policies = [
            self.OrgPolicyDumpStub(
                case_type_set_id=self.case_type_set_id,
                data_collection_id=self.data_collection_id,
                read_col_set_id=None,
                write_col_set_id=None,
                add_case=True,
                remove_case=False,
                add_case_set=False,
                remove_case_set=False,
                read_case_set=False,
                write_case_set=False,
                is_private=True,
                from_data_collection_id=self.from_data_collection_id,
            )
        ]

        self.service.app.handle.side_effect = [  # type: ignore[attr-defined]
            existing_user_access_policies,
            existing_user_share_policies,
            org_access_policies,
            org_share_policies,
            None,  # delete user access
            None,  # delete user share
            [SimpleNamespace()],  # created user access policies
            [SimpleNamespace()],  # created user share policies
            OrgUser(  # updated user (real model)
                id=self.user_id,
                key="user@example.org",
                email="user@example.org",
                roles={"ORG_USER"},
                organization_id=self.new_org_id,
                is_active=True,
            ),
        ]

        self.service._get_user_by_id_cached = SimpleNamespace(cache_clear=Mock())  # type: ignore[assignment]
        self.service._get_case_abac_cached = SimpleNamespace(cache_clear=Mock())  # type: ignore[assignment]

        updated_user = self.service.temp_update_user_own_organization(cmd)

        self.assertEqual(updated_user.organization_id, self.new_org_id)
        self.assertEqual(self.service.app.handle.call_count, 9)  # type: ignore[attr-defined]
        delete_uap_call = self.service.app.handle.call_args_list[4][0][0]  # type: ignore[attr-defined]
        delete_usp_call = self.service.app.handle.call_args_list[5][0][0]  # type: ignore[attr-defined]
        self.assertIsNotNone(delete_uap_call)
        self.assertIsNotNone(delete_usp_call)
        self.service._get_user_by_id_cached.cache_clear.assert_called_once()  # type: ignore[attr-defined]
        self.service._get_case_abac_cached.cache_clear.assert_called_once()  # type: ignore[attr-defined]

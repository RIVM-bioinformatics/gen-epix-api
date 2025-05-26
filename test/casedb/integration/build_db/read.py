from test.casedb.casedb_service_test_client import CasedbServiceTestClient as Env
from test.casedb.integration.build_db.base import (
    ALL_USERS,
    DATA_USERS,
    GUEST_USERS,
    METADATA_ADMIN_OR_ABOVE_USERS,
    NO_DATA_USERS,
    NON_GUEST_USERS,
    ROOT,
    SKIP_CREATE_DATA,
    SKIP_RAISE,
)
from uuid import UUID

import pytest

from gen_epix.casedb.domain import exc, model


class TestRead:
    # READ tests

    def test_read_user(self, env: Env) -> None:
        # Read all users as root, app_admin
        all_users = list(env.db[model.User].values())
        all_user_ids = {x.id for x in all_users}
        env.verify_read_all("root1_1", model.User, all_user_ids)
        env.verify_read_all("root2_1", model.User, all_user_ids)
        env.verify_read_all("app_admin1_1", model.User, all_user_ids)
        # Read subset of users as org_admin, metadata_admin, org_user
        for i in range(0, 5):
            i += 1
            for j in range(0, 1):
                j += 1
                # Organization admins can only read users in their organization, as well as themselves
                org_admin_user = env._get_obj(model.User, f"org_admin{i}_{j}")
                env.verify_read_all(
                    org_admin_user,
                    model.User,
                    env.get_users_for_org_admin(org_admin_user),
                )
                # Organization and metadata admin users can only read themselves
                for user_type in ["org_user", "metadata_admin"]:
                    user = env._get_obj(
                        model.User, f"{user_type}{i}_{j}", on_missing="return_none"
                    )
                    if not user:
                        continue
                    env.verify_read_all(
                        user,
                        model.User,
                        {user.id},
                    )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_user_raise(self, env: Env) -> None:
        for exec_user in GUEST_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_all(exec_user, model.User)

    def test_read_organization_access_or_share_case_policy(self, env: Env) -> None:
        # Read all organization policies as root, app_admin, org_admin is restricted by rights
        for policy_class in [
            model.OrganizationAccessCasePolicy,
            model.OrganizationShareCasePolicy,
        ]:
            all_org_policies = env.read_all("root1_1", policy_class)
            all_org_policy_ids = {x.id for x in all_org_policies}
            env.verify_read_all("root1_1", policy_class, all_org_policy_ids)
            env.verify_read_all("root2_1", policy_class, all_org_policy_ids)
            env.verify_read_all("app_admin1_1", policy_class, all_org_policy_ids)
            for i in range(0, 5):
                i += 1
                for j in range(0, 1):
                    j += 1
                    org_ids = env.get_org_ids_for_org_admin(f"org_admin{i}_{j}")
                    org_policy_ids = {
                        x.id for x in all_org_policies if x.organization_id in org_ids
                    }
                    env.verify_read_all(
                        f"org_admin{i}_{j}", policy_class, org_policy_ids
                    )
                    try:
                        user: model.User = env._get_obj(model.User, f"org_user{i}_{j}")
                    except:
                        continue
                    own_org_policy_ids = {
                        x.id
                        for x in all_org_policies
                        if x.organization_id == user.organization_id
                    }
                    env.verify_read_all(user, policy_class, own_org_policy_ids)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_organization_access_or_share_case_policy_raise(
        self, env: Env
    ) -> None:
        for policy_class in [
            model.OrganizationAccessCasePolicy,
            model.OrganizationShareCasePolicy,
        ]:
            for exec_user in NO_DATA_USERS:
                with pytest.raises(exc.UnauthorizedAuthError):
                    env.read_all(exec_user, policy_class)

    def test_read_user_access_or_share_case_policy(self, env: Env) -> None:
        # Read all user policies as root, app_admin, org_admin is restricted by rights
        for policy_class in [model.UserAccessCasePolicy, model.UserShareCasePolicy]:
            all_user_policies = env.read_all("root1_1", policy_class)
            all_user_policy_ids = {x.id for x in all_user_policies}
            all_users = env.read_all("root1_1", model.User)
            all_user_org_ids = {x.id: x.organization_id for x in all_users}
            env.verify_read_all("root1_1", policy_class, all_user_policy_ids)
            env.verify_read_all("root2_1", policy_class, all_user_policy_ids)
            env.verify_read_all("app_admin1_1", policy_class, all_user_policy_ids)
            for i in range(0, 5):
                i += 1
                for j in range(0, 1):
                    j += 1
                    org_ids = env.get_org_ids_for_org_admin(f"org_admin{i}_{j}")
                    user_policy_ids = {
                        x.id
                        for x in all_user_policies
                        if all_user_org_ids[x.user_id] in org_ids
                    }
                    env.verify_read_all(
                        f"org_admin{i}_{j}", policy_class, user_policy_ids
                    )
                    try:
                        user: model.User = env._get_obj(model.User, f"org_user{i}_{j}")
                    except:
                        continue
                    own_user_policy_ids = {
                        x.id for x in all_user_policies if x.user_id == user.id
                    }
                    env.verify_read_all(user, policy_class, own_user_policy_ids)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_user_access_or_share_case_policy_raise(self, env: Env) -> None:
        for policy_class in [model.UserAccessCasePolicy, model.UserShareCasePolicy]:
            for exec_user in NO_DATA_USERS:
                with pytest.raises(exc.UnauthorizedAuthError):
                    env.read_all(exec_user, policy_class)

    # TODO: remove when ok. Replaced by case access integration test.
    # @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    # def test_read_case_access(self, env: Env) -> None:
    #     # TODO: add tests for when either/or org/user case policy is inactive
    #     # Verify case data access
    #     # Format: dict[tuple(org_user, case), list[col_content]]
    #     # Access to some data
    #     expected_access = {
    #         # org_user1_2 can access case1_4, dimension4 column1 and column2
    #         ("org_user1_1", "1_1"): ["1_1", "1_2", "1_3", "1_4", "1_5"],
    #         ("org_user1_1", "1_2"): ["2_1", "2_2", "2_3", "2_4", "2_5"],
    #         ("org_user1_1", "1_3"): ["3_1", "3_2", "3_3", "3_4", "3_5"],
    #         ("org_user2_1", "2_1"): ["1_1", "1_2", "1_3", "1_4", "1_5"],
    #         ("org_user2_1", "2_2"): ["2_1", "2_2", "2_3", "2_4", "2_5"],
    #         ("org_user2_1", "2_3"): ["3_1", "3_2", "3_3", "3_4", "3_5"],
    #         ("org_user3_1", "3_1"): ["1_1", "1_2", "1_3", "1_4", "1_5"],
    #         ("org_user3_1", "3_2"): ["2_1", "2_2", "2_3", "2_4", "2_5"],
    #         ("org_user3_1", "3_3"): ["3_1", "3_2", "3_3", "3_4", "3_5"],
    #         # Custom cases
    #         ("org_user1_2", "1_4"): ["4_1", "4_2"],
    #         ("org_user2_2", "2_4"): ["4_2", "4_3"],
    #         ("org_user2_2", "3_5"): ["5_2", "5_3"],
    #         ("org_user3_2", "1_4"): ["4_1", "4_2"],
    #         ("org_user3_2", "2_4"): ["4_2", "4_3"],
    #         ("org_user3_2", "3_5"): ["5_2", "5_3"],
    #     }
    #     env.verify_case_content_access(expected_access)
    #     # No access
    #     no_access = [
    #         # org_user1_1 has no access to case1_4
    #         ("org_user1_1", "2_1"),
    #         ("org_user1_1", "3_1"),
    #         ("org_user1_2", "1_1"),
    #         ("org_user1_2", "2_1"),
    #         ("org_user1_2", "3_1"),
    #         ("org_user2_1", "1_1"),
    #         ("org_user2_1", "3_1"),
    #         ("org_user2_2", "1_1"),
    #         ("org_user2_2", "2_1"),
    #         ("org_user2_2", "3_1"),
    #         ("org_user3_1", "1_1"),
    #         ("org_user3_1", "2_1"),
    #         ("org_user3_2", "1_1"),
    #         ("org_user3_2", "2_1"),
    #         ("org_user3_2", "3_1"),
    #     ]
    #     for tuple_ in no_access:
    #         if not SKIP_RAISE:
    #             with pytest.raises(exc.UnauthorizedAuthError):
    #                 try:
    #                     env.verify_case_content_access({tuple_: []})
    #                 except exc.UnauthorizedAuthError as exception:
    #                     raise exception
    #                 except Exception as exception:
    #                     if env.verbose:
    #                         print(f"Case access not denied: {tuple_}")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_read_case_type(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRU
        - metadata_admin: CRU
        - org_admin: R
        - org_user: R
        - guest: -

        org_admin has no ABAC permissions, so the result should be empty without raising an error
        """
        # Naming scheme: dict[user: list[case_type{case_type_id}]
        expected_access = {
            "root1_1": ["1", "2", "3", "4", "5"],
            "app_admin1_1": ["1", "2", "3", "4", "5"],
            "metadata_admin1_1": ["1", "2", "3", "4", "5"],
            "org_admin1_1": [],
            "org_user1_1": ["1"],
            "org_user1_2": ["1", "2"],
            "org_user1_3": ["1"],
            "org_user2_1": ["2"],
            "org_user2_2": ["2", "3"],
            "org_user2_3": ["2"],
            "org_user3_1": ["3"],
            "org_user3_2": ["1", "2", "3"],
            "org_user3_3": ["3"],
        }
        env.verify_case_type_access(expected_access)

    @pytest.mark.skip(reason="Test to be completed analogous to test_read_case_type")
    def test_read_case_type_set_member(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRU
        - metadata_admin: CRU
        - org_admin: R
        - org_user: R
        - guest: -
        """

        # Members have no name field so we have to use the ids
        all_case_type_set_members: list[model.CaseTypeSetMember] = env.read_all(
            ROOT, model.CaseTypeSetMember
        )
        all_case_type_set_members_ids = [x.id for x in all_case_type_set_members]

        # TODO: find a way to find which case_type_set_members are accessible by org_user1_1
        # They are generated randomly so we can't know them in advance, and they have no name field
        org_accessed_members: list[model.CaseTypeSetMember] = env.read_all(
            "org_user1_1", model.CaseTypeSetMember
        )
        org_accessed_members_ids = [x.id for x in org_accessed_members]
        abac_permissions: dict[str, list[str | UUID]] = {
            "root1_1": all_case_type_set_members_ids,
            "app_admin1_1": all_case_type_set_members_ids,
            "metadata_admin1_1": all_case_type_set_members_ids,
            "org_admin1_1": [],
            "org_user1_1": org_accessed_members_ids,
        }

        self._general_read_test(
            env, model.CaseTypeSetMember, NON_GUEST_USERS, abac_permissions
        )

    @pytest.mark.skip(reason="Test to be completed analogous to test_read_case_type")
    def test_read_case_type_col(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRU
        - metadata_admin: CRU
        - org_admin: -
        - org_user: -
        - guest: -

        No ABAC restrictions
        """
        self._general_read_test(env, model.CaseTypeCol, METADATA_ADMIN_OR_ABOVE_USERS)

    @pytest.mark.skip(reason="Test to be completed analogous to test_read_case_type")
    def test_read_case_type_col_set(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRU
        - metadata_admin: CRU
        - org_admin: R
        - org_user: R
        - guest: -

        No ABAC restrictions
        """
        self._general_read_test(env, model.CaseTypeColSet, NON_GUEST_USERS)

    @pytest.mark.skip(reason="Test to be completed analogous to test_read_case_type")
    def test_read_case_type_col_set_member(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - metadata_admin: CRUD
        - org_admin: -
        - org_user: -
        - guest: -

        No ABAC restrictions
        """
        self._general_read_test(
            env, model.CaseTypeColSetMember, METADATA_ADMIN_OR_ABOVE_USERS
        )

    @pytest.mark.skip(reason="Test to be completed analogous to test_read_case_type")
    def test_read_case_set(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - metadata_admin: -
        - org_admin: CRUD
        - org_user: CRUD
        - guest: -
        """

        abac_permissions: dict[str, list[str]] = {
            "root1_1": [],
            "app_admin1_1": [],
            "metadata_admin1_1": [],
            "org_admin1_1": [],
            "org_user1_1": [
                "case_set1_1",
                "case_set1_2",
                "case_set1_3",
                "case_set1_4",
                "case_set1_5",
            ],
            "guest1_1": [],
        }

        self._general_read_test(
            env, model.CaseSet, DATA_USERS, abac_permissions, root_not_full_access=True
        )

    def _general_read_test(
        self,
        env: Env,
        model_class: type,
        has_rbac_users: list[str],
        expected_abac_permissions: dict[str, list[str]] | None = None,
        root_not_full_access: bool = False,
    ) -> None:
        if not root_not_full_access:
            all_objects = env.read_all(ROOT, model_class)

        has_no_rbac_users = [x for x in ALL_USERS if x not in has_rbac_users]
        for exec_user in has_no_rbac_users:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_all(exec_user, model_class)

        if expected_abac_permissions:
            for exec_user in has_rbac_users:
                if root_not_full_access:
                    all_objects = env.read_all(exec_user, model_class)

                permissions = expected_abac_permissions[exec_user]
                if not permissions:
                    expected_ids = set()
                elif isinstance(permissions[0], UUID):
                    expected_ids = set(permissions)
                else:
                    expected_ids = {x.id for x in all_objects if x.name in permissions}
                env.verify_read_all(exec_user, model_class, expected_ids)

        else:
            expected_ids = {x.id for x in all_objects}
            for exec_user in has_rbac_users:
                env.verify_read_all(exec_user, model_class, expected_ids)

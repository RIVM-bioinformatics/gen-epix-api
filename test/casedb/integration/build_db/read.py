from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.build_db.base import (
    ALL_USERS,
    DATA_USERS,
    GUEST_USERS,
    NO_DATA_USERS,
    NON_GUEST_USERS,
    REFDATA_ADMIN_OR_ABOVE_USERS,
    SKIP_RAISE,
)
from uuid import UUID

import pytest

from gen_epix.casedb.domain import exc, model


class TestRead:

    def test_read_user(self, env: Env) -> None:
        # Read all users as root, app_admin
        all_users = list(env.db[model.User].values())
        all_user_ids = {x.id for x in all_users}
        env.verify_read_all("root1_1", model.User, all_user_ids)
        env.verify_read_all("root2_1", model.User, all_user_ids)
        env.verify_read_all("app_admin1_1", model.User, all_user_ids)
        # Read subset of users as org_admin, refdata_admin, org_user
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
                # Organization and refdata admin users can only read themselves
                for user_type in ["org_user", "refdata_admin"]:
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

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_type(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRU
        - refdata_admin: CRU
        - org_admin: R
        - org_user: R
        - guest: -

        org_admin has no ABAC permissions, so the result should be empty without raising an error
        """
        for user_name in ALL_USERS:
            expected_case_type_ids: set[UUID] = env.read_case_types_with_any_right(
                user_name
            )
            if user_name in NON_GUEST_USERS:
                # User is not a guest and should have read access to case types
                # verify that the expected case type IDs (ABAC) match
                env.verify_read_all(user_name, model.CaseType, expected_case_type_ids)
            else:
                # User is a guest and should not have access to any case types
                assert expected_case_type_ids == set()
                with pytest.raises(exc.UnauthorizedAuthError):
                    env.read_all(user_name, model.CaseType)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_type_set_member(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRU
        - refdata_admin: CRU
        - org_admin: R
        - org_user: R
        - guest: -
        """
        all_case_type_set_members: list[model.CaseTypeSetMember] = env.read_all(
            "root1_1", model.CaseTypeSetMember
        )
        for user_name in ALL_USERS:
            expected_case_type_ids: set[UUID] = env.read_case_types_with_any_right(
                user_name
            )
            if user_name in NON_GUEST_USERS:
                # User is not a guest and should have read access to case type set members
                expected_member_ids = {
                    x.id
                    for x in all_case_type_set_members
                    if x.case_type_id in expected_case_type_ids
                }
                env.verify_read_all(
                    user_name,
                    model.CaseTypeSetMember,
                    expected_member_ids,
                )
            else:
                # User is a guest and should not have access to any case type set members
                assert expected_case_type_ids == set()
                with pytest.raises(exc.UnauthorizedAuthError):
                    env.read_all(user_name, model.CaseTypeSetMember)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_type_col(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRU
        - refdata_admin: CRU
        - org_admin: -
        - org_user: -
        - guest: -

        No ABAC restrictions
        """
        all_case_type_cols: list[model.CaseTypeCol] = env.read_all(
            "root1_1", model.CaseTypeCol
        )
        for user_name in ALL_USERS:
            expected_case_type_ids: set[UUID] = env.read_case_types_with_any_right(
                user_name
            )
            if user_name in REFDATA_ADMIN_OR_ABOVE_USERS:
                # User is a refdata admin or above and should have read access to case type columns
                expected_member_ids = {
                    x.id
                    for x in all_case_type_cols
                    if x.case_type_id in expected_case_type_ids
                }
                env.verify_read_all(
                    user_name,
                    model.CaseTypeCol,
                    expected_member_ids,
                )
            else:
                continue
                # TODO: NEGATIVE CASES

    @pytest.mark.skip("CaseTypeColSet has commented out fields, see TODO comment")
    def test_read_case_type_col_set(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRU
        - refdata_admin: CRU
        - org_admin: R
        - org_user: R
        - guest: -

        No ABAC restrictions
        """
        # read all CaseTypeColSets to map case_type_id to CaseTypeColSet
        all_case_type_col_sets: list[model.CaseTypeColSet] = env.read_all(
            "root1_1", model.CaseTypeColSet
        )

        for user_name in ALL_USERS:
            expected_case_type_ids: set[UUID] = env.read_case_types_with_any_right(
                user_name
            )
            if user_name in NON_GUEST_USERS:
                # User is not a guest and should have read access to case type col sets
                # TODO: Fix model.CaseTypeColSet
                # Fields: case_type and case_type_id are commented out in CaseTypeColSet
                # therefore no mapping possible at the moment
                expected_member_ids = {
                    x.id
                    for x in all_case_type_col_sets
                    if x.case_type_id in expected_case_type_ids
                }
                env.verify_read_all(
                    user_name,
                    model.CaseTypeColSet,
                    expected_member_ids,
                )
            else:
                continue
                # TODO: NEGATIVE CASES

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_type_col_set_member(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - refdata_admin: CRUD
        - org_admin: -
        - org_user: -
        - guest: -

        No ABAC restrictions
        """
        # Create a mapping, to facilitate:
        # expected_case_type_ids -> case_type_col_ids -> case_type_col_set_member_ids
        all_case_type_col_set_members: list[model.CaseTypeColSetMember] = env.read_all(
            "root1_1", model.CaseTypeColSetMember
        )
        all_cols: list[model.CaseTypeCol] = env.read_all("root1_1", model.CaseTypeCol)
        col_case_type_map = {c.id: c.case_type_id for c in all_cols}
        for user_name in ALL_USERS:
            expected_case_type_ids: set[UUID] = env.read_case_types_with_any_right(
                user_name
            )
            if user_name in REFDATA_ADMIN_OR_ABOVE_USERS:
                # User is a refdata admin or above and should have read access to case type col set members
                expected_member_ids = {
                    m.id
                    for m in all_case_type_col_set_members
                    if col_case_type_map.get(m.case_type_col_id)
                    in expected_case_type_ids
                }
                env.verify_read_all(
                    user_name,
                    model.CaseTypeColSetMember,
                    expected_member_ids,
                )
            else:
                continue
                # TODO: NEGATIVE CASES

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_set(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - refdata_admin: -
        - org_admin: CRUD
        - org_user: CRUD
        - guest: -
        """
        all_case_sets: list[model.CaseSet] = env.read_all("root1_1", model.CaseSet)
        for user_name in NO_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_all(user_name, model.CaseSet)

        for user_name in ALL_USERS:
            expected_case_type_ids: set[UUID] = env.read_case_types_with_any_right(
                user_name
            )
            if user_name in DATA_USERS:
                # User is a data user and should have read access to case sets
                expected_member_ids = {
                    x.id
                    for x in all_case_sets
                    if x.case_type_id in expected_case_type_ids
                }
                env.verify_read_all(
                    user_name,
                    model.CaseSet,
                    expected_member_ids,
                )
            else:
                with pytest.raises(exc.UnauthorizedAuthError):
                    env.read_all(user_name, model.CaseSet)

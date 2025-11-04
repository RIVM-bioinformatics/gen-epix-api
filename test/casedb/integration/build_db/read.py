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

from gen_epix.casedb.domain import command, exc, model


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
                # Organization admins can only read users in their organization,
                # as well as themselves and other org admins that are admins of
                # some of their organizations
                org_admin_user = env._get_obj(model.User, f"org_admin{i}_{j}")
                env.verify_read_all(
                    org_admin_user,
                    model.User,
                    env.get_users_for_org_admin(
                        org_admin_user, include_self=True, include_other_org_admins=True
                    ),
                )
                # Organization and refdata admin users can only read themselves and organization admins of their organization
                for user_type in ["org_user", "refdata_admin"]:
                    user = env._get_obj(
                        model.User, f"{user_type}{i}_{j}", on_missing="return_none"
                    )
                    if not user:
                        continue
                    env.verify_read_all(
                        user,
                        model.User,
                        env.get_own_org_admin_users(user, include_self=True),
                    )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_user_raise(self, env: Env) -> None:
        for exec_user in GUEST_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_all(exec_user, model.User)

    def test_read_organization_admin_emails(self, env: Env) -> None:
        # Read all organization admin emails
        all_users: dict[UUID, model.User] = {
            x.id: x for x in env.read_all("root1_1", model.User)  # type:ignore[misc]
        }
        all_org_admin_policies: list[model.OrganizationAdminPolicy] = env.read_all(
            "root1_1", model.OrganizationAdminPolicy
        )  # type:ignore[assignment]
        org_admin_users_by_org: dict[UUID, set[UUID]] = {}
        for policy in all_org_admin_policies:
            org_admin_users_by_org.setdefault(policy.organization_id, set()).add(
                policy.user_id
            )
        for user_or_str in DATA_USERS:
            user: model.User = env._get_obj(
                model.User, user_or_str
            )  # type:ignore[assignment]
            user_name_emails = sorted(
                env.read_organization_admin_name_emails(user),
                key=lambda x: (x.name, x.email),
            )
            expected_users = sorted(
                [
                    all_users[x]
                    for x in org_admin_users_by_org.get(user.organization_id, set())
                ],
                key=lambda x: (x.name, x.email),
            )
            assert all(
                x.name == y.name and x.email == y.email
                for x, y in zip(user_name_emails, expected_users)
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_organization_admin_emails_raise(self, env: Env) -> None:
        for exec_user in NO_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_organization_admin_name_emails(exec_user)

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
                    x.id
                    for x in all_case_type_col_set_members
                    if col_case_type_map.get(x.case_type_col_id)
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

    def test_read_organization_contact_by_contact_ids(self, env: Env) -> None:
        root: model.User = env._get_obj(
            model.User, "root1_1"
        )  # type:ignore[assignment]
        all_contacts: list[model.Contact] = env.read_all(
            root, model.Contact
        )  # type:ignore[assignment]
        selected_contacts: list[model.Contact] = all_contacts[:3]
        selected_contact_ids: list[UUID] = [x.id for x in selected_contacts if x.id]

        organizations: list[model.Contact] = env.app.handle(
            command.RetrieveOrganizationContactCommand(
                user=root,
                organization_ids=None,
                site_ids=None,
                contact_ids=selected_contact_ids,
            )
        )

        result_ids = {x.id for x in organizations}
        assert result_ids == set(selected_contact_ids)
        assert all(x.site is None for x in organizations)

    def test_read_organization_contact_by_site_ids(self, env: Env) -> None:
        root: model.User = env._get_obj(
            model.User, "root1_1"
        )  # type:ignore[assignment]
        all_contacts: list[model.Contact] = env.read_all(
            root, model.Contact
        )  # type:ignore[assignment]
        all_sites: list[model.Site] = env.read_all(
            root, model.Site
        )  # type:ignore[assignment]

        contacts_by_site: dict[UUID, set[UUID]] = {}
        site_ids_with_contacts: list[UUID] = []
        for site in all_sites:
            site_contact_ids = {x.id for x in all_contacts if x.site_id == site.id}
            if site_contact_ids:
                contacts_by_site[site.id] = site_contact_ids  # type:ignore
                site_ids_with_contacts.append(site.id)  # type:ignore

        selected_site_ids: list[UUID] = site_ids_with_contacts[:2]
        expected_contact_ids: set[UUID] = set().union(
            *(contacts_by_site[sid] for sid in selected_site_ids)
        )

        organizations: list[model.Contact] = env.app.handle(
            command.RetrieveOrganizationContactCommand(
                user=root,
                organization_ids=None,
                site_ids=selected_site_ids,
                contact_ids=None,
            )
        )

        result_ids = {x.id for x in organizations}
        assert result_ids == expected_contact_ids
        assert all(x.site is None for x in organizations)
        assert all(x.site_id in set(selected_site_ids) for x in organizations)

    def test_read_organization_contact_by_organization_ids(self, env: Env) -> None:
        root: model.User = env._get_obj(
            model.User, "root1_1"
        )  # type:ignore[assignment]
        all_contacts: list[model.Contact] = env.read_all(
            root, model.Contact
        )  # type:ignore[assignment]
        all_sites: list[model.Site] = env.read_all(
            root, model.Site
        )  # type:ignore[assignment]

        sites_by_id: dict[UUID, model.Site] = {x.id: x for x in all_sites if x.id}
        contacts_by_org: dict[UUID, set[UUID]] = {}
        for x in all_contacts:
            site = sites_by_id.get(x.site_id)
            if not site:
                continue
            contacts_by_org.setdefault(site.organization_id, set()).add(x.id)

        selected_org_ids: list[UUID] = list(contacts_by_org.keys())[:2]
        expected_contact_ids: set[UUID] = set().union(
            *(contacts_by_org[org_id] for org_id in selected_org_ids)
        )

        organizations: list[model.Contact] = env.app.handle(
            command.RetrieveOrganizationContactCommand(
                user=root,
                organization_ids=selected_org_ids,
                site_ids=None,
                contact_ids=None,
            )
        )

        result_ids = {x.id for x in organizations}
        assert result_ids == expected_contact_ids
        assert all(x.site is None for x in organizations)
        for x in organizations:
            site = sites_by_id.get(x.site_id)
            assert site is not None and site.organization_id in set(selected_org_ids)

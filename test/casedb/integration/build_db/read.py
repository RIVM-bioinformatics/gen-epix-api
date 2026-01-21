from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.build_db.base import (
    DATA_USERS,
    GUEST_USERS,
    NO_DATA_USERS,
    NON_GUEST_USERS,
    ROOT,
    SKIP_RAISE,
)
from uuid import UUID

import pytest

from gen_epix.casedb.domain import command, exc, model


@pytest.mark.scenario_ids(
    "TC-RBAC-01-16",
    "TC-RBAC-01-17",
    "TC-RBAC-02-09",
    "TC-RBAC-02-10",
    "TC-RBAC-02-11",
    "TC-RBAC-02-12",
    "TC-RBAC-02-05",
    "TC-RBAC-02-06",
    "TC-RBAC-02-07",
    "TC-BIO-01-01",
    "TC-BIO-01-02",
    "TC-BIO-02-01",
    "TC-BIO-02-02",
    "TC-BIO-03-01",
    "TC-BIO-03-02",
    "TC-BIO-04-01",
    "TC-BIO-04-02",
    "TC-RBAC-04-22",
)
class TestRead:

    def test_read_user(self, env: Env) -> None:
        # Read all users as root, app_admin
        all_users: list[model.User] = list(
            env.db[model.User].values()
        )  # type:ignore[assignment]
        all_user_ids: set[UUID] = {x.id for x in all_users}  # type:ignore[assignment]
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
                org_admin_user: model.User = env._get_obj(
                    model.User, f"org_admin{i}_{j}"
                )  # type:ignore[assignment]
                expected_users = env.get_users_for_org_admin(
                    org_admin_user, include_self=True, include_other_org_admins=True
                )
                expected_user_ids: set[UUID] = {
                    x.id for x in expected_users
                }  # type:ignore[assignment]
                env.verify_read_all(
                    org_admin_user,
                    model.User,
                    expected_user_ids,
                )
                # Organization and refdata admin users can only read themselves and organization admins of their organization
                for user_type in ["org_user", "refdata_admin"]:
                    user: model.User | None = env._get_obj(  # type:ignore[assignment]
                        model.User, f"{user_type}{i}_{j}", on_missing="return_none"
                    )
                    if user is None:
                        continue
                    expected_users = env.get_own_org_admin_users(
                        user, include_self=True
                    )
                    expected_user_ids: set[UUID] = {
                        x.id for x in expected_users
                    }  # type:ignore[assignment]
                    env.verify_read_all(
                        user,
                        model.User,
                        expected_user_ids,
                    )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_user_raise(self, env: Env) -> None:
        for exec_user in GUEST_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_all(exec_user, model.User)

    def test_read_organization_admin_emails(self, env: Env) -> None:
        # Read all organization admin emails
        all_users: list[model.User] = env.read_all(
            ROOT, model.User
        )  # type:ignore[assignment]
        all_user_map = {x.id: x for x in all_users}
        all_org_admin_policies: list[model.OrganizationAdminPolicy] = env.read_all(
            ROOT, model.OrganizationAdminPolicy
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
                    all_user_map[x]
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
        policy_classes: list[type[model.Model]] = [
            model.OrganizationAccessCasePolicy,
            model.OrganizationShareCasePolicy,
        ]
        for policy_class in policy_classes:
            all_org_policies: list[
                model.OrganizationAccessCasePolicy | model.OrganizationShareCasePolicy
            ] = env.read_all(
                ROOT, policy_class
            )  # type:ignore[assignment]
            all_org_policy_ids: set[UUID] = {
                x.id for x in all_org_policies
            }  # type:ignore[assignment]
            env.verify_read_all("root1_1", policy_class, all_org_policy_ids)
            env.verify_read_all("root2_1", policy_class, all_org_policy_ids)
            env.verify_read_all("app_admin1_1", policy_class, all_org_policy_ids)
            for i in range(0, 5):
                i += 1
                for j in range(0, 1):
                    j += 1
                    org_ids = env.get_org_ids_for_org_admin(f"org_admin{i}_{j}")
                    expected_org_policy_ids: set[UUID] = {  # type:ignore[assignment]
                        x.id for x in all_org_policies if x.organization_id in org_ids
                    }
                    env.verify_read_all(
                        f"org_admin{i}_{j}", policy_class, expected_org_policy_ids
                    )
                    try:
                        user: model.User = env._get_obj(
                            model.User, f"org_user{i}_{j}"
                        )  # type:ignore[assignment]
                    except:
                        continue
                    expected_own_org_policy_ids: set[UUID] = (
                        {  # type:ignore[assignment]
                            x.id
                            for x in all_org_policies
                            if x.organization_id == user.organization_id
                        }
                    )
                    env.verify_read_all(user, policy_class, expected_own_org_policy_ids)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_organization_access_or_share_case_policy_raise(
        self, env: Env
    ) -> None:
        policy_classes: list[type[model.Model]] = [
            model.OrganizationAccessCasePolicy,
            model.OrganizationShareCasePolicy,
        ]
        for policy_class in policy_classes:
            for exec_user in NO_DATA_USERS:
                with pytest.raises(exc.UnauthorizedAuthError):
                    env.read_all(exec_user, policy_class)

    def test_read_user_access_or_share_case_policy(self, env: Env) -> None:
        # Read all user policies as root, app_admin, org_admin is restricted by rights
        policy_classes: list[type[model.Model]] = [
            model.UserAccessCasePolicy,
            model.UserShareCasePolicy,
        ]
        for policy_class in policy_classes:
            all_user_policies: list[
                model.UserAccessCasePolicy | model.UserShareCasePolicy
            ] = env.read_all(
                ROOT, policy_class
            )  # type:ignore[assignment]
            all_user_policy_ids: set[UUID] = {
                x.id for x in all_user_policies
            }  # type:ignore[assignment]
            all_users: list[model.User] = env.read_all(
                ROOT, model.User
            )  # type:ignore[assignment]
            all_user_org_ids = {x.id: x.organization_id for x in all_users}
            env.verify_read_all("root1_1", policy_class, all_user_policy_ids)
            env.verify_read_all("root2_1", policy_class, all_user_policy_ids)
            env.verify_read_all("app_admin1_1", policy_class, all_user_policy_ids)
            for i in range(0, 5):
                i += 1
                for j in range(0, 1):
                    j += 1
                    org_ids = env.get_org_ids_for_org_admin(f"org_admin{i}_{j}")
                    expected_user_policy_ids: set[UUID] = {  # type:ignore[assignment]
                        x.id  # type:ignore[misc]
                        for x in all_user_policies
                        if all_user_org_ids[x.user_id] in org_ids
                    }
                    env.verify_read_all(
                        f"org_admin{i}_{j}", policy_class, expected_user_policy_ids
                    )
                    try:
                        user: model.User = env._get_obj(
                            model.User, f"org_user{i}_{j}"
                        )  # type:ignore[assignment]
                    except:
                        continue
                    expected_own_user_policy_ids: set[UUID] = (
                        {  # type:ignore[assignment]
                            x.id for x in all_user_policies if x.user_id == user.id
                        }
                    )
                    env.verify_read_all(
                        user, policy_class, expected_own_user_policy_ids
                    )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_user_access_or_share_case_policy_raise(self, env: Env) -> None:
        policy_classes: list[type[model.Model]] = [
            model.UserAccessCasePolicy,
            model.UserShareCasePolicy,
        ]
        for policy_class in policy_classes:
            for exec_user in NO_DATA_USERS:
                with pytest.raises(exc.UnauthorizedAuthError):
                    env.read_all(exec_user, policy_class)

    def test_read_case_type(self, env: Env) -> None:
        for user in NON_GUEST_USERS:
            expected_case_type_ids: set[UUID] = env.read_case_types_with_any_right(user)
            env.verify_read_all(user, model.CaseType, expected_case_type_ids)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_type_raise(self, env: Env) -> None:
        for user in GUEST_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_all(user, model.CaseType)

    def test_read_case_type_set_member(self, env: Env) -> None:
        all_case_type_set_members: list[model.CaseTypeSetMember] = (
            env.read_all(  # type:ignore[assignment]
                ROOT, model.CaseTypeSetMember
            )
        )
        for user in NON_GUEST_USERS:
            expected_case_type_ids: set[UUID] = env.read_case_types_with_any_right(user)
            expected_case_type_set_member_ids: set[UUID] = {  # type:ignore[assignment]
                x.id
                for x in all_case_type_set_members
                if x.case_type_id in expected_case_type_ids
            }
            env.verify_read_all(
                user, model.CaseTypeSetMember, expected_case_type_set_member_ids
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_type_set_member_raise(self, env: Env) -> None:
        for user in GUEST_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_all(user, model.CaseTypeSetMember)

    def test_read_case_type_col(self, env: Env) -> None:
        for user in NON_GUEST_USERS:
            expected_case_type_col_ids = env.read_case_type_cols_with_any_right(user)
            env.verify_read_all(user, model.CaseTypeCol, expected_case_type_col_ids)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_type_col_raise(self, env: Env) -> None:
        for user in GUEST_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_all(user, model.CaseTypeCol)

    def test_read_case_type_col_set(self, env: Env) -> None:
        all_case_type_col_sets: list[model.CaseTypeColSet] = (
            env.read_all(  # type:ignore[assignment]
                ROOT, model.CaseTypeColSet
            )
        )
        all_case_type_col_set_members: list[model.CaseTypeColSetMember] = (
            env.read_all(  # type:ignore[assignment]
                ROOT, model.CaseTypeColSetMember
            )
        )
        empty_case_type_col_set_ids: set[UUID] = {  # type:ignore[assignment]
            x.id
            for x in all_case_type_col_sets
            if not any(
                y.case_type_col_set_id == x.id for y in all_case_type_col_set_members
            )
        }
        for user in NON_GUEST_USERS:
            expected_case_type_col_ids = env.read_case_type_cols_with_any_right(user)
            expected_case_type_col_set_ids = empty_case_type_col_set_ids | {
                x.case_type_col_set_id
                for x in all_case_type_col_set_members
                if x.case_type_col_id in expected_case_type_col_ids
            }
            env.verify_read_all(
                user,
                model.CaseTypeColSet,
                expected_case_type_col_set_ids,
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_type_col_set_raise(self, env: Env) -> None:
        for user in GUEST_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_all(user, model.CaseTypeColSet)

    def test_read_case_type_col_set_member(self, env: Env) -> None:
        all_case_type_col_set_members: list[model.CaseTypeColSetMember] = (
            env.read_all(  # type:ignore[assignment]
                ROOT, model.CaseTypeColSetMember
            )
        )
        for user in NON_GUEST_USERS:
            expected_case_type_col_ids: set[UUID] = (
                env.read_case_type_cols_with_any_right(user)
            )
            expected_case_type_col_set_member_ids: set[UUID] = (
                {  # type:ignore[assignment]
                    x.id
                    for x in all_case_type_col_set_members
                    if x.case_type_col_id in expected_case_type_col_ids
                }
            )
            env.verify_read_all(
                user,
                model.CaseTypeColSetMember,
                expected_case_type_col_set_member_ids,
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_type_col_set_member_raise(self, env: Env) -> None:
        for user in GUEST_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_all(user, model.CaseTypeColSetMember)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_set(self, env: Env) -> None:
        all_case_sets: list[model.CaseSet] = env.read_all(
            ROOT, model.CaseSet
        )  # type:ignore[assignment]
        for user in DATA_USERS:
            expected_case_type_ids: set[UUID] = env.read_case_types_with_any_right(user)
            expected_case_set_ids: set[UUID] = {  # type:ignore[assignment]
                x.id for x in all_case_sets if x.case_type_id in expected_case_type_ids
            }
            env.verify_read_all(
                user,
                model.CaseSet,
                expected_case_set_ids,
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_read_case_set_raise(self, env: Env) -> None:
        for user in NO_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.read_all(user, model.CaseSet)

    # TODO Refactor tests to the pattern used for all other tests: test_read_contact and test_read_contact_raise. The 3 ways to read a contact (by contact ids, by site ids, by organization ids) can be sub-tests within test_read_contact.
    def test_read_organization_contact_by_contact_ids(self, env: Env) -> None:
        root_user: model.User = env._get_obj(
            model.User, ROOT
        )  # type:ignore[assignment]
        all_contacts: list[model.Contact] = env.read_all(
            root_user, model.Contact
        )  # type:ignore[assignment]
        selected_contacts: list[model.Contact] = all_contacts[:3]
        selected_contact_ids: list[UUID] = [x.id for x in selected_contacts if x.id]

        organizations: list[model.Contact] = env.app.handle(
            command.RetrieveOrganizationContactCommand(
                user=root_user,
                organization_ids=None,
                site_ids=None,
                contact_ids=selected_contact_ids,
            )
        )

        result_ids = {x.id for x in organizations}
        assert result_ids == set(selected_contact_ids)
        assert all(x.site is None for x in organizations)

    def test_read_organization_contact_by_site_ids(self, env: Env) -> None:
        root_user: model.User = env._get_obj(
            model.User, ROOT
        )  # type:ignore[assignment]
        all_contacts: list[model.Contact] = env.read_all(
            root_user, model.Contact
        )  # type:ignore[assignment]
        all_sites: list[model.Site] = env.read_all(
            root_user, model.Site
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
                user=root_user,
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
        root_user: model.User = env._get_obj(
            model.User, ROOT
        )  # type:ignore[assignment]
        all_contacts: list[model.Contact] = env.read_all(
            root_user, model.Contact
        )  # type:ignore[assignment]
        all_sites: list[model.Site] = env.read_all(
            root_user, model.Site
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
                user=root_user,
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

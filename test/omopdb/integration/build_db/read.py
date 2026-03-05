from test.omopdb.integration.build_db.base import (
    DATA_USERS,
    GUEST_USERS,
    NO_DATA_USERS,
    SKIP_RAISE,
)
from uuid import UUID

import pytest

from gen_epix.commondb.test.test_client import TestClient as Env
from gen_epix.omopdb.domain import exc, model


@pytest.mark.scenario_ids("TC-SEC-31-02")
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
            x.id: x for x in env.read_all("root1_1", model.User)  # type: ignore[misc]
        }
        all_org_admin_policies: list[model.OrganizationAdminPolicy] = env.read_all(
            "root1_1", model.OrganizationAdminPolicy
        )  # type: ignore[assignment]
        org_admin_users_by_org: dict[UUID, set[UUID]] = {}
        for policy in all_org_admin_policies:
            org_admin_users_by_org.setdefault(policy.organization_id, set()).add(
                policy.user_id
            )
        for user_or_str in DATA_USERS:
            user: model.User = env._get_obj(
                model.User, user_or_str
            )  # type: ignore[assignment]
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

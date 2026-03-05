from test.seqdb.integration.build_db.base import (BELOW_ROOT_USERS, SKIP_RAISE,
                                                  USER_NAME_ROOTS)

import pytest

from gen_epix.commondb.test.test_client import TestClient as Env
from gen_epix.seqdb.domain import exc, model


@pytest.mark.scenario_ids("TC-11-09-03")
class TestDelete:

    def test_delete_organization(self, env: Env) -> None:
        # Root: delete any organization except own is allowed
        env.create_organization("root1_1", "org99")
        env.delete_object("root1_1", model.Organization, "org99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_organization_raise(self, env: Env) -> None:
        # Root: cannot delete own organization
        with pytest.raises(exc.UnauthorizedAuthError):
            env.delete_object("root1_1", model.Organization, "org1")
        # All others: cannot delete any
        env.create_organization("root1_1", "org99")
        for user in BELOW_ROOT_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.Organization, "org99")
        env.delete_object("root1_1", model.Organization, "org99")

    def test_delete_user(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: R
        - refdata_admin: R
        - org_admin: R
        - org_user: R
        - guest: -
        """
        # Root: delete any user except self is allowed
        for user_name_root in USER_NAME_ROOTS:
            for org_index in range(1, 3):
                user = env.invite_and_register_user(
                    "root1_1", f"{user_name_root}{org_index}_99"
                )
                env.delete_object("root1_1", model.User, user)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_user_raise(self, env: Env) -> None:
        # Root: cannot delete self
        with pytest.raises(exc.UnauthorizedAuthError):
            env.delete_object("root1_1", model.User, "root1_1")
        # All others: cannot delete any
        tgt_user = env.invite_and_register_user("root1_1", f"guest1_99")
        for user in BELOW_ROOT_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.User, tgt_user)
        env.delete_object("root1_1", model.User, tgt_user)

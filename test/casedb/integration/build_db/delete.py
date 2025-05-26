from test.casedb.casedb_service_test_client import CasedbServiceTestClient as Env
from test.casedb.integration.build_db.base import (
    APP_ADMIN_OR_ABOVE_USERS,
    BELOW_APP_ADMIN_DATA_USERS,
    BELOW_APP_ADMIN_METADATA_USERS,
    BELOW_ROOT_USERS,
    METADATA_ADMIN_OR_ABOVE_USERS,
    ROOT,
    SKIP_RAISE,
)

import pytest

from gen_epix.casedb.domain import exc, model


class TestDelete:

    def test_delete_case_type(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - metadata_admin: CRU
        - org_admin: -
        - org_user: -
        - guest: -
        """
        for user in APP_ADMIN_OR_ABOVE_USERS:
            case_type = env.create_case_type(
                ROOT, "case_type99", "disease1", "etiological_agent1"
            )
            assert case_type in env.read_all(
                ROOT, model.CaseType
            ), f"case_type: {case_type.id} not created in env"
            env.delete_object(user, model.CaseType, "case_type99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_case_type_raise(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - metadata_admin: CRU
        - org_admin: -
        - org_user: -
        - guest: -
        """
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        for user in BELOW_APP_ADMIN_METADATA_USERS + BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.CaseType, "case_type99")
        env.delete_object(ROOT, model.CaseType, "case_type99")

    def test_delete_case_type_set_member(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - metadata_admin: CRUD
        - org_admin: R
        - org_user: R
        - guest: -
        """
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        for user in METADATA_ADMIN_OR_ABOVE_USERS:
            case_type_set_member = env.create_case_type_set_member(
                ROOT,
                "case_type_set1",
                "case_type99",
            )
            assert case_type_set_member in env.read_all(
                ROOT, model.CaseTypeSetMember
            ), f"case_type_set_member: {case_type_set_member.id} not created in env"
            env.delete_object(user, model.CaseTypeSetMember, case_type_set_member)
        env.delete_object(ROOT, model.CaseType, "case_type99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_case_type_set_member_raise(self, env: Env) -> None:
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        case_type_set_member = env.create_case_type_set_member(
            ROOT,
            "case_type_set1",
            "case_type99",
        )
        for user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.CaseTypeSetMember, case_type_set_member)
        env.delete_object(ROOT, model.CaseType, "case_type99")

    def test_delete_case_type_col(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRU
        - metadata_admin: CRU
        - org_admin: -
        - org_user: -
        - guest: -
        """
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        case_type_col = env.create_case_type_col(ROOT, "case_type99_text1_8_time_year")
        assert case_type_col in env.read_all(
            ROOT, model.CaseTypeCol
        ), f"case_type: {case_type_col.id} not created in env"
        env.delete_object(ROOT, model.CaseTypeCol, case_type_col)
        env.delete_object(ROOT, model.CaseType, "case_type99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_case_type_col_raise(self, env: Env) -> None:
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        case_type_col = env.create_case_type_col(ROOT, "case_type99_text1_8_time_year")
        for user in BELOW_ROOT_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.CaseTypeCol, case_type_col)
        env.delete_object(ROOT, model.CaseTypeCol, case_type_col)
        env.delete_object(ROOT, model.CaseType, "case_type99")

    def test_delete_case_type_col_set(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRU
        - metadata_admin: CRU
        - org_admin: R
        - org_user: R
        - guest: -
        """
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        case_type_col = env.create_case_type_col(ROOT, "case_type99_text1_8_time_year")
        case_type_col_set = env.create_case_type_col_set(
            ROOT, "case_type_col_set99", {"case_type99_text1_8_time_year"}
        )
        assert case_type_col_set in env.read_all(
            ROOT, model.CaseTypeColSet
        ), f"case_type_col_set: {case_type_col_set.id} not created in env"
        env.delete_object(ROOT, model.CaseTypeColSet, case_type_col_set)
        env.delete_object(ROOT, model.CaseTypeCol, case_type_col)
        env.delete_object(ROOT, model.CaseType, "case_type99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_case_type_col_set_raise(self, env: Env) -> None:
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        case_type_col = env.create_case_type_col(ROOT, "case_type99_text1_8_time_year")
        case_type_col_set = env.create_case_type_col_set(
            ROOT, "case_type_col_set99", {"case_type99_text1_8_time_year"}
        )
        for user in BELOW_ROOT_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.CaseTypeColSet, case_type_col_set)
        env.delete_object(ROOT, model.CaseTypeColSet, case_type_col_set)
        env.delete_object(ROOT, model.CaseTypeCol, case_type_col)
        env.delete_object(ROOT, model.CaseType, "case_type99")

    def test_delete_case_type_col_set_member(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - metadata_admin: CRUD
        - org_admin: -
        - org_user: -
        - guest: -
        """
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        case_type_col_set = env.create_case_type_col_set(
            ROOT, "case_type_col_set99", set()
        )
        for user in METADATA_ADMIN_OR_ABOVE_USERS:
            case_type_col_set_member = env.create_case_type_col_set_member(
                ROOT,
                "case_type_col_set99",
                "case_type1_text1_6_text",
            )
            assert case_type_col_set_member in env.read_all(
                ROOT, model.CaseTypeColSetMember
            ), f"case_type_col_set_member: {case_type_col_set_member.id} not created in env"
            env.delete_object(
                user, model.CaseTypeColSetMember, case_type_col_set_member
            )
        env.delete_object(ROOT, model.CaseTypeColSet, case_type_col_set)
        env.delete_object(ROOT, model.CaseType, "case_type99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_case_type_col_set_member_raise(self, env: Env) -> None:
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        case_type_col_set = env.create_case_type_col_set(
            ROOT, "case_type_col_set99", set()
        )
        case_type_col_set_member = env.create_case_type_col_set_member(
            ROOT,
            "case_type_col_set99",
            "case_type1_text1_6_text",
        )
        for user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(
                    user, model.CaseTypeColSetMember, case_type_col_set_member
                )
        env.delete_object(ROOT, model.CaseTypeColSetMember, case_type_col_set_member)
        env.delete_object(ROOT, model.CaseTypeColSet, case_type_col_set)
        env.delete_object(ROOT, model.CaseType, "case_type99")

    def test_delete_case_set(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - metadata_admin: CRUD
        - org_admin: CRUD
        - org_user: CRUD
        - guest: -
        """
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        for user in APP_ADMIN_OR_ABOVE_USERS:
            case_type_set = env.create_case_type_set(
                ROOT,
                "case_type_set99",
                {"case_type99"},
                "case_type_set_category3",
            )
            assert case_type_set in env.read_all(
                ROOT, model.CaseTypeSet
            ), f"case_type_set: {case_type_set.id} not created in env"
            env.delete_object(user, model.CaseTypeSet, "case_type_set99")
        env.delete_object(ROOT, model.CaseType, "case_type99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_case_set_raise(self, env: Env) -> None:
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        env.create_case_type_set(
            ROOT,
            "case_type_set99",
            {"case_type99"},
            "case_type_set_category3",
        )
        for user in BELOW_APP_ADMIN_METADATA_USERS + BELOW_APP_ADMIN_DATA_USERS:

            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.CaseTypeSet, "case_type_set99")
        env.delete_object(ROOT, model.CaseTypeSet, "case_type_set99")
        env.delete_object(ROOT, model.CaseType, "case_type99")

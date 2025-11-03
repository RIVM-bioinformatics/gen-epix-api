from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.build_db.base import (
    APP_ADMIN_OR_ABOVE_USERS,
    BELOW_APP_ADMIN_DATA_USERS,
    BELOW_APP_ADMIN_METADATA_USERS,
    BELOW_ROOT_USERS,
    REFDATA_ADMIN_OR_ABOVE_USERS,
    ROOT,
    SKIP_RAISE,
    USER_NAME_ROOTS,
    ORG_ADMIN_OR_ABOVE_USERS,
    BELOW_ORG_ADMIN_USERS,
)

import pytest

from gen_epix.casedb.domain import exc, model


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

    def test_delete_case_type(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - refdata_admin: CRU
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
        - refdata_admin: CRU
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
        - refdata_admin: CRUD
        - org_admin: R
        - org_user: R
        - guest: -
        """
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        for user in REFDATA_ADMIN_OR_ABOVE_USERS:
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
        - refdata_admin: CRU
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
        - refdata_admin: CRU
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
        - refdata_admin: CRUD
        - org_admin: -
        - org_user: -
        - guest: -
        """
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        case_type_col_set = env.create_case_type_col_set(
            ROOT, "case_type_col_set99", set()
        )
        for user in REFDATA_ADMIN_OR_ABOVE_USERS:
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
        - refdata_admin: CRUD
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

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_link_constraint(self, env: Env) -> None:
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        # Create a case col for this case type
        env.create_case_type_col(ROOT, "case_type99_text1_8_time_year")
        # Delete the case type
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(ROOT, model.CaseType, "case_type99")

    def test_delete_site(self, env: Env) -> None:
        """
        RBAC permissions:
        root: CRUD
        app_admin: CUD
        refdata_admin:
        org_admin:
        org_user: R
        guest: -
        """
        for user in ORG_ADMIN_OR_ABOVE_USERS:
            site = env.create_site(ROOT, "site99_1", "org1")
            assert site in env.read_all(
                ROOT, model.Site
            ), f"site: {site.id} not created in env"
            env.delete_object(user, model.Site, "site99_1")

    def test_delete_contact(self, env: Env) -> None:
        """
        RBAC permissions:
        root: CRUD
        app_admin: CUD
        refdata_admin:
        org_admin:
        org_user: R
        guest: -
        """
        env.create_site(ROOT, "site99", "org1")
        for user in ORG_ADMIN_OR_ABOVE_USERS:
            contact: model.Contact = env.create_contact(ROOT, "contact99", "site99")
            assert contact in env.read_all(
                ROOT, model.Contact
            ), f"contact: {contact.id} not created in env"
            env.delete_object(user, model.Contact, "contact99")
        env.delete_object(ROOT, model.Site, "site99")

    def test_delete_site_raise(self, env: Env) -> None:
        """
        RBAC permissions:
        root: CRUD
        app_admin: CUD
        refdata_admin:
        org_admin:
        org_user: R
        guest: -
        """
        env.create_site(ROOT, "site99_1", "org1")
        for user in BELOW_ORG_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.Site, "site99_1")
        env.delete_object(ROOT, model.Site, "site99_1")

    def test_delete_contact_raise(self, env: Env) -> None:
        """
        RBAC permissions:
        root: CRUD
        app_admin: CUD
        refdata_admin:
        org_admin:
        org_user: R
        guest: -
        """
        env.create_site(ROOT, "site99", "org1")
        env.create_contact(ROOT, "contact99", "site99")
        for user in BELOW_ORG_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.Contact, "contact99")
        env.delete_object(ROOT, model.Contact, "contact99")
        env.delete_object(ROOT, model.Site, "site99")

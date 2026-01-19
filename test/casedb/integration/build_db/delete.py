from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.build_db.base import (
    APP_ADMIN_OR_ABOVE_USERS,
    BELOW_APP_ADMIN_DATA_USERS,
    BELOW_APP_ADMIN_METADATA_USERS,
    BELOW_APP_ADMIN_USERS,
    BELOW_ORG_ADMIN_USERS,
    BELOW_ROOT_USERS,
    ORG_ADMIN_OR_ABOVE_USERS,
    ROOT,
    SKIP_RAISE,
    USER_NAME_ROOTS,
)

import pytest

from gen_epix.casedb.domain import exc, model


@pytest.mark.scenario_ids(
    "TC-RBAC-01-18,TC-RBAC-01-19,TC-RBAC-01-03,TC-RBAC-02-09,TC-RBAC-02-10,TC-RBAC-02-11,TC-RBAC-02-12,TC-RBAC-02-05,TC-RBAC-02-06,TC-RBAC-02-07,TC-BIO-01-01,TC-BIO-01-02,TC-BIO-02-01,TC-BIO-02-02,TC-BIO-03-01,TC-BIO-03-02,TC-BIO-04-01,TC-BIO-04-02"
)
class TestDelete:

    def test_delete_organization(self, env: Env) -> None:
        # Root: delete any organization except own is allowed
        env.create_organization(ROOT, "org99")
        env.delete_object(ROOT, model.Organization, "org99", verify=True)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_organization_raise(self, env: Env) -> None:
        # Root: cannot delete own organization
        with pytest.raises(exc.UnauthorizedAuthError):
            env.delete_object(ROOT, model.Organization, "org1")
        # All others: cannot delete any
        for user in BELOW_ROOT_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.Organization, "org1")

    def test_delete_user(self, env: Env) -> None:
        # Root: delete any user except self is allowed
        for user_name_root in USER_NAME_ROOTS:
            for org_index in range(1, 3):
                user = env.invite_and_register_user(
                    ROOT, f"{user_name_root}{org_index}_99"
                )
                env.delete_object(ROOT, model.User, user, verify=True)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_user_raise(self, env: Env) -> None:
        # Root: cannot delete self
        with pytest.raises(exc.UnauthorizedAuthError):
            env.delete_object(ROOT, model.User, ROOT)
        # All others: cannot delete any
        tgt_user = env.invite_and_register_user(ROOT, f"guest1_99")
        for user in BELOW_ROOT_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.User, tgt_user)
        env.delete_object(ROOT, model.User, tgt_user)

    def test_delete_case_type(self, env: Env) -> None:
        for user in APP_ADMIN_OR_ABOVE_USERS:
            case_type = env.create_case_type(
                ROOT, "case_type99", "disease1", "etiological_agent1"
            )
            env.delete_object(user, model.CaseType, "case_type99", verify=True)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_case_type_raise(self, env: Env) -> None:
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        for user in BELOW_APP_ADMIN_METADATA_USERS + BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.CaseType, "case_type99")
        env.delete_object(ROOT, model.CaseType, "case_type99")

    def test_delete_case_type_set_member(self, env: Env) -> None:
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        for user in APP_ADMIN_OR_ABOVE_USERS:
            case_type_set_member = env.create_case_type_set_member(
                ROOT,
                "case_type_set1",
                "case_type99",
            )
            env.delete_object(
                user, model.CaseTypeSetMember, case_type_set_member, verify=True
            )
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
        env.delete_object(ROOT, model.CaseTypeSetMember, case_type_set_member)
        env.delete_object(ROOT, model.CaseType, "case_type99")

    def test_delete_case_type_col(self, env: Env) -> None:
        env.create_col(ROOT, "col1_99")
        for user in APP_ADMIN_OR_ABOVE_USERS:
            case_type_col = env.create_case_type_col(user, "case_type_col1_1_1_99")
            env.delete_object(ROOT, model.CaseTypeCol, case_type_col, verify=True)
        env.delete_object(ROOT, model.Col, "col1_99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_case_type_col_raise(self, env: Env) -> None:
        for user in BELOW_APP_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.CaseTypeCol, "case_type_col1_1_1_1")

    def test_delete_case_type_col_set(self, env: Env) -> None:
        for user in APP_ADMIN_OR_ABOVE_USERS:
            case_type_col_set = env.create_case_type_col_set(
                user, "case_type_col_set99", {"case_type_col1_1_1_1"}
            )
            env.delete_object(
                ROOT, model.CaseTypeColSet, case_type_col_set, verify=True
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_case_type_col_set_raise(self, env: Env) -> None:
        for user in BELOW_APP_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.CaseTypeColSet, "case_type_col_set1")

    def test_delete_case_type_col_set_member(self, env: Env) -> None:
        env.create_col(ROOT, "col1_99")
        env.create_case_type_col(ROOT, "case_type_col1_1_1_99")
        for user in APP_ADMIN_OR_ABOVE_USERS:
            case_type_col_set_member = env.create_case_type_col_set_member(
                ROOT,
                "case_type_col_set1",
                "case_type_col1_1_1_99",
            )
            env.delete_object(
                user, model.CaseTypeColSetMember, case_type_col_set_member, verify=True
            )
        env.delete_object(ROOT, model.CaseTypeCol, "case_type_col1_1_1_99")
        env.delete_object(ROOT, model.Col, "col1_99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_case_type_col_set_member_raise(self, env: Env) -> None:
        env.create_col(ROOT, "col1_99")
        env.create_case_type_col(ROOT, "case_type_col1_1_1_99")
        case_type_col_set_member = env.create_case_type_col_set_member(
            ROOT,
            "case_type_col_set1",
            "case_type_col1_1_1_99",
        )
        for user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(
                    user, model.CaseTypeColSetMember, case_type_col_set_member
                )
        env.delete_object(ROOT, model.CaseTypeColSetMember, case_type_col_set_member)
        env.delete_object(ROOT, model.CaseTypeCol, "case_type_col1_1_1_99")
        env.delete_object(ROOT, model.Col, "col1_99")

    def test_delete_case_set(self, env: Env) -> None:
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        for user in APP_ADMIN_OR_ABOVE_USERS:
            case_type_set = env.create_case_type_set(
                ROOT,
                "case_type_set99",
                {"case_type99"},
                "case_type_set_category1",
            )
            env.delete_object(user, model.CaseTypeSet, case_type_set, verify=True)
        env.delete_object(ROOT, model.CaseType, "case_type99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_case_set_raise(self, env: Env) -> None:
        env.create_case_type(ROOT, "case_type99", "disease1", "etiological_agent1")
        case_type_set = env.create_case_type_set(
            ROOT,
            "case_type_set99",
            {"case_type99"},
            "case_type_set_category1",
        )
        for user in BELOW_APP_ADMIN_METADATA_USERS + BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.CaseTypeSet, case_type_set)
        env.delete_object(ROOT, model.CaseTypeSet, case_type_set)
        env.delete_object(ROOT, model.CaseType, "case_type99")

    def test_delete_site(self, env: Env) -> None:
        for user in ORG_ADMIN_OR_ABOVE_USERS:
            site = env.create_site(ROOT, "site1_99")
            env.delete_object(user, model.Site, "site1_99", verify=True)

    def test_delete_site_raise(self, env: Env) -> None:
        for user in BELOW_ORG_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.Site, "site1_1")

    def test_delete_contact(self, env: Env) -> None:
        for user in ORG_ADMIN_OR_ABOVE_USERS:
            contact: model.Contact = env.create_contact(ROOT, "contact1_1_99")
            env.delete_object(user, model.Contact, "contact1_1_99")

    def test_delete_contact_raise(self, env: Env) -> None:
        for user in BELOW_ORG_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(user, model.Contact, "contact1_1_1")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_delete_link_constraint_raise(self, env: Env) -> None:
        # TODO Create rows that have a foreign key to the commented out tests, so that deletion of the latter raises LinkConstraintViolationError
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(ROOT, model.Organization, "org2")
        # with pytest.raises(exc.LinkConstraintViolationError):
        #     env.delete_object(ROOT, model.DataCollection, "data_collection1")
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(ROOT, model.Site, "site1_1")
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(ROOT, model.ConceptSet, "concept_set1_nominal")
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(ROOT, model.RegionSet, "region_set1")
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(ROOT, model.Dim, "dim1")
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(ROOT, model.Col, "col1_1")
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(ROOT, model.Disease, "disease1")
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(ROOT, model.EtiologicalAgent, "etiological_agent1")
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(
                ROOT, model.CaseTypeSetCategory, "case_type_set_category1"
            )
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(ROOT, model.CaseType, "case_type1")
        # with pytest.raises(exc.LinkConstraintViolationError):
        #     env.delete_object(ROOT, model.CaseTypeSet, "case_type_set1")
        with pytest.raises(exc.LinkConstraintViolationError):
            env.delete_object(ROOT, model.CaseTypeDim, "case_type_dim1_1_1")
        # with pytest.raises(exc.LinkConstraintViolationError):
        #     env.delete_object(ROOT, model.CaseTypeCol, "case_type_col1_1_1_1")
        # with pytest.raises(exc.LinkConstraintViolationError):
        #     env.delete_object(ROOT, model.CaseTypeColSet, "case_type_col_set1")
        # with pytest.raises(exc.LinkConstraintViolationError):
        #     env.delete_object(ROOT, model.CaseSetCategory, "case_set_category1")
        # with pytest.raises(exc.LinkConstraintViolationError):
        #     env.delete_object(ROOT, model.CaseSetStatus, "case_set_status1")

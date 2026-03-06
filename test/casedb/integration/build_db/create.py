from typing import Any

import pytest

from gen_epix.casedb.domain import enum, exc, model
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.build_db.base import (
    APP_ADMIN_OR_ABOVE_USERS,
    BELOW_APP_ADMIN_DATA_USERS,
    BELOW_APP_ADMIN_USERS,
    BELOW_ORG_ADMIN_USERS,
    ORG_ADMIN_OR_ABOVE_USERS,
    SKIP_CREATE_DATA,
    SKIP_RAISE,
)
from test.omopdb.integration.build_db.base import ROOT


@pytest.mark.scenario_ids(
    "TC-RBAC-01-12",
    "TC-RBAC-01-13",
    "TC-RBAC-03-01",
    "TC-RBAC-03-09",
    "TC-RBAC-02-08",
    "TC-RBAC-02-09",
    "TC-RBAC-02-10",
    "TC-RBAC-02-11",
    "TC-RBAC-02-12",
    "TC-RBAC-02-02",
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
)
class TestCreate:
    # CREATE tests

    def test_create_user_first_root(self, env: Env) -> None:
        # Create a first root user and organization
        user: model.User = env.retrieve_user_by_key("root1_1@org1.org")  # type: ignore[assignment]
        user.name = "root1_1"
        env._set_obj(user)  # type: ignore[arg-type]
        env._set_obj(
            env.read_one_by_property("root1_1", model.Organization, "name", "org1")
        )

    def test_create_user_additional_root(self, env: Env) -> None:
        # Create additional root user, including in a different organization
        assert (
            env.invite_and_register_user("root1_1", "root1_2").key == "root1_2@org1.org"
        )
        env.create_organization("root1_2", "org2")
        env.create_organization("root1_2", "org3")
        keyless_user = env.invite_and_register_user("root1_2", "root2_1", set_key=False)
        assert keyless_user.email == "root2_1@org2.org"
        if env.use_endpoints:
            assert keyless_user.key == "root2_1@org2.org"
        else:
            assert keyless_user.key is None
        env.invite_and_register_user("root1_2", "root2_2", set_key=False)

    def test_create_user_app_admin(self, env: Env) -> None:
        # Create invitations for app_admin as root
        env.invite_and_register_user("root1_1", "app_admin1_1")
        env.invite_and_register_user("root2_1", "app_admin1_2")
        env.invite_and_register_user("root1_2", "app_admin2_1")
        env.invite_and_register_user("root2_2", "app_admin2_2")
        env.invite_and_register_user("root1_2", "app_admin3_1")
        env.invite_and_register_user("root2_2", "app_admin3_2")

    def test_create_user_organization(self, env: Env) -> None:
        # Create organizations as root and app_admin
        env.create_organization("root1_2", "org4")
        env.create_organization("app_admin1_2", "org5")
        env.create_organization("app_admin2_1", "org6")
        if env.verbose:
            env.print_organizations()

    def test_create_user_refdata_admin(self, env: Env) -> None:
        # Create refdata_admin as root and app_admin
        env.invite_and_register_user("root2_1", "refdata_admin1_1")
        env.invite_and_register_user("app_admin2_1", "refdata_admin1_2")
        env.invite_and_register_user("app_admin1_1", "refdata_admin2_1")
        env.invite_and_register_user("app_admin1_2", "refdata_admin2_2")

    def test_create_user_org_admin(self, env: Env) -> None:
        # Create org_admin as root and app_admin
        env.invite_and_register_user("root2_1", "org_admin1_1")
        env.invite_and_register_user("app_admin2_1", "org_admin1_2")
        env.invite_and_register_user("app_admin1_1", "org_admin2_1")
        env.invite_and_register_user("app_admin1_2", "org_admin2_2")
        env.invite_and_register_user("app_admin1_1", "org_admin3_1")
        env.invite_and_register_user("app_admin1_2", "org_admin3_2")
        env.invite_and_register_user("app_admin2_1", "org_admin4_1")
        env.invite_and_register_user("app_admin2_2", "org_admin4_2")
        env.invite_and_register_user("app_admin3_1", "org_admin5_1")
        env.invite_and_register_user("app_admin3_2", "org_admin5_2")

    def test_create_org_admin_policy(self, env: Env) -> None:
        # Add org_admin policy
        env.create_org_admin_policy("root1_1", "app_admin1_1", "org5")
        env.create_org_admin_policy("root2_1", "org_admin1_1", "org1")
        env.create_org_admin_policy("app_admin1_1", "app_admin2_1", "org5")
        env.create_org_admin_policy("app_admin2_1", "org_admin2_1", "org2")
        env.create_org_admin_policy("app_admin3_1", "org_admin3_1", "org1")
        env.create_org_admin_policy("app_admin3_1", "org_admin3_1", "org2")
        env.create_org_admin_policy("app_admin3_1", "org_admin3_1", "org3")
        env.create_org_admin_policy("app_admin3_1", "org_admin4_1", "org3")
        env.create_org_admin_policy("app_admin3_1", "org_admin4_1", "org4")
        env.create_org_admin_policy("app_admin3_1", "org_admin4_1", "org5")
        env.create_org_admin_policy("app_admin3_1", "org_admin5_1", "org5")
        if env.verbose:
            env.print_org_admin_policies()

    def test_create_user_org_user(self, env: Env) -> None:
        # Create org_user as root, app_admin and org_admin
        env.invite_and_register_user("root1_1", "org_user1_1")
        env.invite_and_register_user("root1_1", "org_user1_2")
        env.invite_and_register_user("root2_1", "org_user1_3")
        env.invite_and_register_user("app_admin1_1", "org_user2_1")
        env.invite_and_register_user("org_admin3_1", "org_user2_2")
        env.invite_and_register_user("org_admin3_1", "org_user2_3")
        env.invite_and_register_user("org_admin3_1", "org_user3_1")
        env.invite_and_register_user("org_admin4_1", "org_user3_2")
        env.invite_and_register_user("org_admin4_1", "org_user3_3")
        env.invite_and_register_user("org_admin4_1", "org_user4_1")
        env.invite_and_register_user("org_admin4_1", "org_user4_2")
        env.invite_and_register_user("org_admin4_1", "org_user4_3")
        env.invite_and_register_user("org_admin4_1", "org_user5_1")
        env.invite_and_register_user("org_admin5_1", "org_user5_2")
        env.invite_and_register_user("org_admin5_1", "org_user5_3")

    def test_create_user_guest(self, env: Env) -> None:
        # Create guest as root, app_admin and org_admin
        env.invite_and_register_user("root1_1", "guest1_1")
        env.invite_and_register_user("root2_1", "guest1_2")
        env.invite_and_register_user("app_admin1_1", "guest2_1")
        env.invite_and_register_user("app_admin1_2", "guest2_2")
        env.invite_and_register_user("org_admin3_1", "guest3_1")
        env.invite_and_register_user("org_admin4_1", "guest3_2")
        if env.verbose:
            env.print_users()

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_user_raise(self, env: Env) -> None:
        # Invite user by admin
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("org_admin1_1", "root1_11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("org_admin1_1", "app_admin1_11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("org_admin1_1", "refdata_admin1_11")
        for exec_user in ["org_user1_1", "guest1_1"]:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "root1_11")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "app_admin1_11")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "refdata_admin1_11")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "org_admin1_11")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "org_user1_11")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "guest1_11")
        # Invite user by org admin
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("org_admin1_1", "app_admin1_1")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_organization_raise(self, env: Env) -> None:
        # Check if non-root, non-app_admin users cannot create an organization
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("org_admin1_1", "org11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("refdata_admin1_1", "org11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("org_user1_1", "org11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("guest1_1", "org11")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_org_admin_policy_raise(self, env: Env) -> None:
        for exec_user in [
            "org_admin1_1",
            "refdata_admin1_1",
            "org_user1_1",
            "guest1_1",
        ]:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "root2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "app_admin2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "refdata_admin2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "org_admin2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "org_user2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "guest2_1", "org1")

    def test_create_site(self, env: Env) -> None:
        for i in range(1, 6):
            for j, exec_user in enumerate(ORG_ADMIN_OR_ABOVE_USERS, start=1):
                env.create_site(exec_user, f"site{i}_{j}")

    def test_create_site_raise(self, env: Env) -> None:
        for exec_user in BELOW_ORG_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_site(exec_user, "site1_1")

    def test_create_contact(self, env: Env) -> None:
        for i, exec_user in enumerate(ORG_ADMIN_OR_ABOVE_USERS, start=1):
            for j in range(1, 3):
                env.create_contact(
                    exec_user, f"contact{i}_1_{j}", email=f"c{i}.{j}@example.com"
                )

    def test_create_contact_raise(self, env: Env) -> None:
        for exec_user in BELOW_ORG_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_contact(exec_user, "contact1_1_1")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_concept_set(self, env: Env) -> None:
        # Create concept_set as root, app_admin, refdata_admin
        env.create_concept_set(
            "root1_1",
            "concept_set1_nominal",
            enum.ConceptSetType.NOMINAL,
        )
        env.create_concept_set(
            "app_admin1_1",
            "concept_set2_ordinal",
            enum.ConceptSetType.ORDINAL,
        )
        env.create_concept_set(
            "refdata_admin1_1",
            "concept_set3_interval",
            enum.ConceptSetType.INTERVAL,
        )
        env.create_concept_set(
            "refdata_admin1_2",
            "concept_set4_regular_language",
            enum.ConceptSetType.REGULAR_LANGUAGE,
            regex=r"^ST(\d*)$",
        )
        env.create_concept_set(
            "refdata_admin2_1",
            "concept_set5_context_free_grammar_json",
            enum.ConceptSetType.CONTEXT_FREE_GRAMMAR_JSON,
            schema_definition="{}",
        )
        env.create_concept_set(
            "refdata_admin2_2",
            "concept_set6_context_free_grammar_xml",
            enum.ConceptSetType.CONTEXT_FREE_GRAMMAR_XML,
            schema_definition="<schema></schema>",
        )

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_concept_set_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_concept_set(
                    exec_user,
                    "concept_set1_nominal",
                    enum.ConceptSetType.NOMINAL,
                )

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_concept(self, env: Env) -> None:
        # Create concept as root, app_admin, refdata_admin
        env.create_concept("root1_1", "category1_1", "concept_set1_nominal")
        env.create_concept("app_admin1_1", "category1_2", "concept_set1_nominal")
        env.create_concept("refdata_admin1_1", "level2_1", "concept_set2_ordinal")
        env.create_concept("refdata_admin1_2", "level2_2", "concept_set2_ordinal")
        env.create_concept("refdata_admin2_1", "interval3_1", "concept_set3_interval")
        env.create_concept("refdata_admin2_2", "interval3_2", "concept_set3_interval")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_concept_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_concept(exec_user, "category1_1", "concept_set1_nominal")
        # TODO [LSP-2694]: add test for creating concept under regex or context free grammar concept set, which should not be allowed; alternatively regex and context free grammar Cols do not have a concept set but rather the regex/schema is part of the Col definition

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_region_set(self, env: Env) -> None:
        # Create region_set as root, app_admin, refdata_admin
        env.create_region_set("root1_1", "region_set1")
        env.create_region_set("app_admin1_1", "region_set2")
        env.create_region_set("refdata_admin1_1", "region_set3")
        env.create_region_set("refdata_admin1_2", "region_set4")
        env.create_region_set("refdata_admin2_1", "region_set5")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_region_set_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_region_set(exec_user, "region_set11")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_region_set_shape(self, env: Env) -> None:
        # Create region_set_shape as root, app_admin, refdata_admin
        env.create_region_set_shape("root1_1", "region_set1", 1)
        env.create_region_set_shape("app_admin1_1", "region_set2", 1)
        env.create_region_set_shape("refdata_admin1_1", "region_set3", 1)
        env.create_region_set_shape("refdata_admin1_2", "region_set4", 1)
        env.create_region_set_shape("refdata_admin2_1", "region_set5", 1)

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_region_set_shape_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_region_set_shape(exec_user, "region_set1", 1)

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_region(self, env: Env) -> None:
        # Create region as root, app_admin, refdata_admin
        env.create_region("root1_1", "region1_1", "region_set1")
        env.create_region("app_admin1_1", "region1_2", "region_set1")
        env.create_region("refdata_admin1_1", "region2_1", "region_set2")
        env.create_region("refdata_admin1_2", "region2_2", "region_set2")
        env.create_region("refdata_admin2_1", "region3_1", "region_set3")
        env.create_region("refdata_admin2_2", "region3_2", "region_set3")
        env.create_region("refdata_admin1_1", "region4_1", "region_set4")
        env.create_region("refdata_admin1_2", "region4_2", "region_set4")
        env.create_region("refdata_admin1_1", "region5_1", "region_set5")
        env.create_region("refdata_admin1_2", "region5_2", "region_set5")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_region_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_region(exec_user, "region11", "region_set1")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_genetic_distance_protocol(self, env: Env) -> None:
        # Create genetic_distance_protocol as root, app_admin, refdata_admin
        env.create_genetic_distance_protocol("root1_1", "genetic_distance_protocol1")
        env.create_genetic_distance_protocol(
            "app_admin1_1", "genetic_distance_protocol2"
        )
        env.create_genetic_distance_protocol(
            "refdata_admin1_1", "genetic_distance_protocol3"
        )
        env.create_genetic_distance_protocol(
            "refdata_admin1_2", "genetic_distance_protocol4"
        )
        env.create_genetic_distance_protocol(
            "refdata_admin2_1", "genetic_distance_protocol5"
        )

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_genetic_distance_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_genetic_distance_protocol(
                    exec_user, "genetic_distance_protocol11"
                )

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_dim(self, env: Env) -> None:
        # Create dim as root, app_admin, refdata_admin
        users: list[str] = ["root1_1", "app_admin1_1"] + ["refdata_admin1_1"] * len(
            enum.DimType
        )
        for i, dim_type in enumerate(enum.DimType, start=1):
            env.create_dim(users[i - 1], f"dim{i}", dim_type)

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_dim_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_dim(exec_user, "time11", enum.DimType.TIME)

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_col(self, env: Env) -> None:
        # Create col as root, app_admin, refdata_admin
        users: list[str] = ["root1_1", "app_admin1_1"] + ["refdata_admin1_1"] * len(
            enum.ColType
        )
        for i, dim_type in enumerate(enum.DimType, start=1):
            col_types = enum.DimColTypeSet[dim_type.name].value
            col_str = f"col{i}"
            for j, col_type in enumerate(col_types, start=1):
                concept_set: str | None = None
                region_set: str | None = None
                genetic_distance_protocol: str | None = None
                if col_type == enum.ColType.NOMINAL:
                    concept_set = "concept_set1_nominal"
                elif col_type == enum.ColType.ORDINAL:
                    concept_set = "concept_set2_ordinal"
                elif col_type == enum.ColType.INTERVAL:
                    concept_set = "concept_set3_interval"
                elif col_type == enum.ColType.REGULAR_LANGUAGE:
                    concept_set = "concept_set4_regular_language"
                elif col_type == enum.ColType.CONTEXT_FREE_GRAMMAR_JSON:
                    concept_set = "concept_set5_context_free_grammar_json"
                elif col_type == enum.ColType.CONTEXT_FREE_GRAMMAR_XML:
                    concept_set = "concept_set6_context_free_grammar_xml"
                elif col_type in enum.ColTypeSet.HAS_REGION_SET.value:
                    region_set = f"region_set{j}"
                elif col_type == enum.ColType.GENETIC_DISTANCE:
                    genetic_distance_protocol = f"genetic_distance_protocol1"
                env.create_col(
                    users[j - 1],
                    f"{col_str}_{j}",
                    col_type=col_type,
                    concept_set=concept_set,
                    region_set=region_set,
                    genetic_distance_protocol=genetic_distance_protocol,
                )

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_col_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_col(
                    exec_user,
                    "col1_99",
                    col_type=enum.ColType.NOMINAL,
                    concept_set="concept_set1_nominal",
                )
        # TODO [LSP-2691] create additional tests for casedb build_db create Col:
        #  invalid col type for dim type
        #  missing concept_set for nominal, ordinal, interval, regular_language,
        #    context_free_grammar_json, context_free_grammar_xml col types
        #  missing region_set for region col types
        #  missing genetic_sequence_case_type_col for genetic_distance col
        #  missing tree_algorithm_codes for genetic_distance col

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_disease(self, env: Env) -> None:
        # Create disease as root, app_admin, refdata_admin
        env.create_disease("root1_1", "disease1")
        env.create_disease("app_admin1_1", "disease2")
        env.create_disease("refdata_admin1_1", "disease3")
        env.create_disease("refdata_admin1_1", "disease4")
        env.create_disease("refdata_admin2_1", "disease5")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_disease_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_disease(exec_user, "disease11")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_etiological_agent(self, env: Env) -> None:
        # Create etiological_agent as root, app_admin, refdata_admin
        env.create_etiological_agent("root1_1", "etiological_agent1")
        env.create_etiological_agent("app_admin1_1", "etiological_agent2")
        env.create_etiological_agent("refdata_admin1_1", "etiological_agent3")
        env.create_etiological_agent("refdata_admin1_2", "etiological_agent4")
        env.create_etiological_agent("refdata_admin2_1", "etiological_agent5")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_etiological_agent_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_etiological_agent(exec_user, "etiological_agent11")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_etiology(self, env: Env) -> None:
        # Create etiology as root, app_admin, refdata_admin
        env.create_etiology("root1_1", "disease1", "etiological_agent1")
        env.create_etiology("app_admin1_1", "disease1", "etiological_agent2")
        env.create_etiology("refdata_admin1_1", "disease2", "etiological_agent3")
        env.create_etiology("refdata_admin1_2", "disease3", "etiological_agent3")
        env.create_etiology("refdata_admin2_1", "disease4", "etiological_agent4")
        env.create_etiology("refdata_admin2_1", "disease5", "etiological_agent5")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_etiology_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_etiology(exec_user, "disease1", "etiological_agent1")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_data_collection(self, env: Env) -> None:
        # Create data_collection as root, app_admin
        env.create_data_collection("root1_1", "data_collection1")
        env.create_data_collection("app_admin1_1", "data_collection2")
        env.create_data_collection("app_admin1_2", "data_collection3")
        env.create_data_collection("app_admin2_1", "data_collection4")
        env.create_data_collection("app_admin2_2", "data_collection5")
        if env.verbose:
            env.print_data_collections()

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_data_collection_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_data_collection(exec_user, "data_collection11")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_case_type(self, env: Env) -> None:
        # Create case_type as root, app_admin, refdata_admin
        env.create_case_type("root1_1", "case_type1", "disease1", "etiological_agent1")
        env.create_case_type(
            "app_admin1_1", "case_type2", "disease1", "etiological_agent2"
        )
        env.create_case_type(
            "refdata_admin1_1", "case_type3", "disease2", "etiological_agent3"
        )
        env.create_case_type(
            "refdata_admin1_2", "case_type4", "disease3", "etiological_agent3"
        )
        env.create_case_type(
            "refdata_admin2_1", "case_type5", "disease4", "etiological_agent4"
        )
        if env.verbose:
            env.print_case_types()

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_type_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_type(
                    exec_user, "case_type11", "disease1", "etiological_agent1"
                )

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_case_type_set_category(self, env: Env) -> None:
        # Create case_type_set_category as root, app_admin, refdata_admin
        env.create_case_type_set_category("root1_1", "case_type_set_category1")
        env.create_case_type_set_category("app_admin1_1", "case_type_set_category2")
        env.create_case_type_set_category("refdata_admin1_1", "case_type_set_category3")
        env.create_case_type_set_category("refdata_admin1_2", "case_type_set_category4")
        env.create_case_type_set_category("refdata_admin2_1", "case_type_set_category5")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_type_set_category_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_type_set_category(exec_user, "case_type_set_category11")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_case_type_set(self, env: Env) -> None:
        # Create case_type_set as root, app_admin, refdata_admin
        env.create_case_type_set(
            "root1_1", "case_type_set1", {"case_type1"}, "case_type_set_category1"
        )
        env.create_case_type_set(
            "app_admin1_1", "case_type_set2", {"case_type2"}, "case_type_set_category2"
        )
        env.create_case_type_set(
            "app_admin1_2", "case_type_set3", {"case_type3"}, "case_type_set_category3"
        )
        env.create_case_type_set(
            "app_admin1_1",
            "case_type_set4",
            {"case_type1", "case_type2"},
            "case_type_set_category4",
        )
        env.create_case_type_set(
            "app_admin1_1",
            "case_type_set5",
            {"case_type2", "case_type3"},
            "case_type_set_category5",
        )
        # Refdata admin creating empty case_type_set is allowed, not adding members (which is a separate operation) since this impacts ABAC
        env.create_case_type_set(
            "refdata_admin1_1",
            "case_type_set6",
            set(),
            "case_type_set_category5",
        )
        if env.verbose:
            env.print_case_type_sets()

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_type_set_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_type_set(
                    exec_user,
                    "case_type_set11",
                    {"case_type1"},
                    "case_type_set_category1",
                )

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_case_type_dim(self, env: Env) -> None:
        # Create case_type_dim as root, app_admin, refdata_admin
        for i in range(1, 6):
            for j in range(1, 3):
                env.create_case_type_dim("root1_1", f"case_type_dim{i}_1_{j}")
                env.create_case_type_dim("app_admin1_1", f"case_type_dim{i}_2_{j}")
                env.create_case_type_dim("refdata_admin1_1", f"case_type_dim{i}_3_{j}")
                env.create_case_type_dim("refdata_admin1_1", f"case_type_dim{i}_4_{j}")
                env.create_case_type_dim("refdata_admin1_1", f"case_type_dim{i}_5_{j}")
                env.create_case_type_dim("refdata_admin1_1", f"case_type_dim{i}_6_{j}")
                env.create_case_type_dim("refdata_admin1_1", f"case_type_dim{i}_7_{j}")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_type_dim_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_type_dim(exec_user, "case_type_dim1_1_11")
        # TODO [LSP-2616]: add test for creating case_type_dim for
        # non-existing dim
        # non-existing case_type
        # is_case_date_dim=True and dim.dim_type != TIME

    def test_create_case_type_dim_invalid_dim_type(self, env: Env) -> None:
        users: list[str] = ["root1_1", "app_admin1_1"] + ["refdata_admin1_1"] * len(
            enum.DimType
        )
        for i, dim_type in enumerate(enum.DimType, start=1):
            if dim_type != enum.DimType.TIME:
                with pytest.raises(exc.InvalidArgumentsError):
                    env.create_case_type_dim(
                        users[i - 1], f"case_type_dim1_{i}_1", is_case_date_dim=True
                    )

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_case_type_col(self, env: Env) -> None:
        # Create case_type_col as root, app_admin, refdata_admin
        cols: list[model.Col] = env.read_all(
            "root1_1", model.Col
        )  # type: ignore[assignment]
        case_type_dims: list[model.CaseTypeDim] = env.read_all(
            "root1_1", model.CaseTypeDim
        )  # type: ignore[assignment]
        users: list[str] = ["root1_1", "app_admin1_1"] + ["refdata_admin1_1"] * len(
            enum.ColType
        )
        for case_type_dim in case_type_dims:
            dim_id = case_type_dim.dim_id
            curr_cols = [x for x in cols if x.dim_id == dim_id]
            genetic_distance_case_type_col_kwargs: dict[str, Any] = {}
            genetic_distance_case_type_col_index: int | None = None
            genetic_sequence_case_type_col: model.CaseTypeCol | None = None
            for i, col in enumerate(curr_cols, start=1):
                kwargs: dict[str, Any] = {}
                is_genetic_distance_col = False
                if col.col_type == enum.ColType.GENETIC_DISTANCE:
                    is_genetic_distance_col = True
                    genetic_distance_case_type_col_index = i
                    genetic_distance_case_type_col_kwargs["tree_algorithm_codes"] = {
                        enum.TreeAlgorithmType.NJ,
                        enum.TreeAlgorithmType.SLINK,
                    }
                code = case_type_dim.code.replace("case_type_dim", "case_type_col")
                if not is_genetic_distance_col:
                    case_type_col = env.create_case_type_col(
                        users[i - 1], f"{code}_{i}", **kwargs
                    )
                if col.col_type == enum.ColType.GENETIC_SEQUENCE:
                    genetic_sequence_case_type_col = case_type_col
            # Handle genetic distance col case_type_col creation with extra args
            if genetic_sequence_case_type_col:
                genetic_distance_case_type_col_kwargs[
                    "genetic_sequence_case_type_col_id"
                ] = genetic_sequence_case_type_col.id
                case_type_col = env.create_case_type_col(
                    users[genetic_distance_case_type_col_index - 1],
                    f"{code}_{genetic_distance_case_type_col_index}",
                    **genetic_distance_case_type_col_kwargs,
                )

        if env.verbose:
            env.print_case_type_cols()

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_type_col_raise(self, env: Env) -> None:
        case_type_dims: list[model.CaseTypeDim] = env.read_all(
            "root1_1", model.CaseTypeDim
        )  # type: ignore[assignment]
        case_type_dim = case_type_dims[0]
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            code = case_type_dim.code.replace("case_type_dim", "case_type_col")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_type_col(exec_user, f"{code}_1")
        # TODO [LSP-2693] Add test for creating case_type_col for
        # non-existing case_type
        # non-existing case_type_dim
        # non-existing col
        # col is for different dim than case_type_dim

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_case_type_col_set(self, env: Env) -> None:
        # Create case_type_col_set as root, app_admin, refdata_admin
        env.create_case_type_col_set(
            "root1_1",
            "case_type_col_set1",
            {f"case_type_col1_{i+1}_1_1" for i in range(0, 5)},
        )
        env.create_case_type_col_set(
            "app_admin1_1",
            "case_type_col_set2",
            {f"case_type_col2_{i+1}_1_1" for i in range(0, 5)},
        )
        env.create_case_type_col_set(
            "app_admin1_2",
            "case_type_col_set3",
            {f"case_type_col3_{i+1}_1_1" for i in range(0, 5)},
        )
        env.create_case_type_col_set(
            "app_admin1_1",
            "case_type_col_set4",
            {
                "case_type_col1_1_1_1",
                "case_type_col1_2_1_1",
                "case_type_col2_1_1_1",
                "case_type_col2_2_1_1",
            },
        )
        env.create_case_type_col_set(
            "app_admin1_1",
            "case_type_col_set5",
            {
                "case_type_col2_2_1_1",
                "case_type_col2_3_1_1",
                "case_type_col3_2_1_1",
                "case_type_col3_3_1_1",
            },
        )
        # Refdata admin creating empty case_type_col_set is allowed, not adding members (which is a separate operation) since this impacts ABAC
        env.create_case_type_col_set(
            "refdata_admin1_1",
            "case_type_col_set6",
            set(),
        )
        if env.verbose:
            env.print_case_type_col_sets()

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_type_col_set_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_type_col_set(
                    exec_user,
                    "case_type_col_set11",
                    {
                        "case_type_col1_1_1_1",
                    },
                )

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_organization_access_case_policy(self, env: Env) -> None:
        # Create organization access case policy as root, app_admin
        # Naming scheme:
        # org_case_policy{organization_id}_{data_collection_id}
        # Create private org_case_policy{i}_{i}_1 for all organisations
        for i in range(1, 6):
            env.create_organization_access_case_policy(
                "app_admin1_1",
                f"org_case_policy{i}_{i}",
                f"case_type_set{i}",
                is_private=True,
                read_case_type_col_set=f"case_type_col_set{i}",
                write_case_type_col_set=f"case_type_col_set{i}",
            )
        # Create additional policies
        env.create_organization_access_case_policy(
            "root1_1",
            f"org_case_policy1_4",
            "case_type_set4",
            read_case_type_col_set="case_type_col_set4",
            write_case_type_col_set="case_type_col_set4",
        )
        env.create_organization_access_case_policy(
            "app_admin1_1",
            f"org_case_policy2_5",
            "case_type_set5",
            read_case_type_col_set="case_type_col_set5",
            write_case_type_col_set="case_type_col_set5",
        )
        env.create_organization_access_case_policy(
            "app_admin1_1",
            f"org_case_policy3_4",
            "case_type_set4",
            read_case_type_col_set="case_type_col_set4",
            write_case_type_col_set="case_type_col_set4",
        )
        env.create_organization_access_case_policy(
            "app_admin1_1",
            f"org_case_policy3_5",
            "case_type_set5",
            read_case_type_col_set="case_type_col_set5",
            write_case_type_col_set="case_type_col_set5",
        )
        if env.verbose:
            env.print_organization_access_case_policies()

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_user_access_case_policy(self, env: Env) -> None:
        # Create user case policy as org_admin
        data = [
            # User x[0] creates the policy
            # User x[1] has rights to data of data_collection x[2], case_type_set x[3], read_case_type_col_set x[4], write_case_type_col_set x[5]
            # Read rights, identical/analogous for 1, 2, 3
            ("1_1", "1_1", "1", "1", "1", None),
            ("2_1", "2_1", "2", "2", "2", None),
            ("3_1", "3_1", "3", "3", "3", None),
            # Read rights, custom additional rights
            ("1_1", "1_2", "4", "4", "4", None),
            ("2_1", "2_2", "5", "5", "5", None),
            ("3_1", "3_2", "4", "4", "4", None),
            ("3_1", "3_2", "5", "5", "5", None),
            # Read/write rights, identical/analogous for 1, 2, 3
            ("1_1", "1_3", "1", "1", "1", "1"),
            ("2_1", "2_3", "2", "2", "2", "2"),
            ("3_1", "3_3", "3", "3", "3", "3"),
        ]
        for x in data:
            env.create_user_access_case_policy(
                f"org_admin{x[0]}",
                f"org_user{x[1]}",
                f"data_collection{x[2]}",
                f"case_type_set{x[3]}",
                read_case_type_col_set=f"case_type_col_set{x[4]}" if x[4] else None,
                write_case_type_col_set=f"case_type_col_set{x[5]}" if x[5] else None,
            )
        if env.verbose:
            env.print_user_access_case_policies()

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_organization_share_case_policy(self, env: Env) -> None:
        # Create organization share case policy as root, app_admin
        # Naming scheme:
        # org_data_collection_policy{organization_id}_{data_collection_id}_{from_data_collection_id}
        # Create org_data_collection_policy4_5_{i} for all organisations to share data to data collection 5 from data collection 4
        # x[0] is the user creating the policy
        # x[1] is the name of the policy including the organisation, data collection and from_data_collection
        # x[2] is the case_type_set id
        data = [
            ("root1_1", "org_data_collection_policy4_5_4", "4"),
        ]
        for x in data:
            env.create_organization_share_case_policy(
                x[0], x[1], f"case_type_set{x[2]}"
            )
        if env.verbose:
            env.print_organization_share_case_policies()

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_user_share_case_policy(self, env: Env) -> None:
        # Create user case policy as org_admin
        rights = {
            "ADD": {
                "add_case": True,
                "remove_case": False,
                "add_case_set": True,
                "remove_case_set": False,
            },
            "FULL": {
                "add_case": True,
                "remove_case": True,
                "add_case_set": True,
                "remove_case_set": True,
            },
        }
        data = [
            # x[0] determines the type of rights
            # User x[1] creates the policy
            # User x[2] has rights to data of data_collection x[3] from data collection x[4] for case type set x[5]
            ("FULL", "1_1", "1_3", "5", "4", "4"),
            ("ADD", "2_1", "2_3", "5", "4", "4"),
            ("ADD", "3_1", "3_3", "5", "4", "4"),
        ]
        for x in data:
            env.create_user_share_case_policy(
                f"org_admin{x[1]}",
                f"org_user{x[2]}",
                f"data_collection{x[3]}",
                f"data_collection{x[4]}",
                f"case_type_set{x[5]}",
                **rights[x[0]],
            )
        if env.verbose:
            env.print_user_share_case_policies()

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_case_set_category(self, env: Env) -> None:
        # Create case_set_category as root, app_admin
        env.create_case_set_category("root1_1", "case_set_category1")
        env.create_case_set_category("app_admin1_1", "case_set_category2")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_set_category_raise(self, env: Env) -> None:
        for user in ["refdata_admin1_1"] + BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_set_category(user, "case_set_category11")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_case_set_status(self, env: Env) -> None:
        # Create case_set_status as root, app_admin
        env.create_case_set_status("root1_1", "case_set_status1")
        env.create_case_set_status("app_admin1_1", "case_set_status2")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_set_status_raise(self, env: Env) -> None:
        for user in ["refdata_admin1_1"] + BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_set_status(user, "case_set_status11")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_object_already_exists(self, env: Env) -> None:
        # Organization already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_organization(ROOT, "org2")
        # User already exists
        with pytest.raises(exc.UserAlreadyExistsAuthError):
            env.invite_and_register_user(ROOT, "root2_1")
        with pytest.raises(exc.UserAlreadyExistsAuthError):
            env.invite_and_register_user("app_admin1_1", "org_admin2_1")
        # Organization admin policy already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_org_admin_policy("app_admin1_1", "org_admin1_1", "org1")
        # Concept set already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_concept_set(
                    ROOT,
                    "concept_set1_nominal",
                    enum.ConceptSetType.NOMINAL,
                )
        # Concept already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_concept(ROOT, "category1_1", "concept_set1_nominal")
        # RegionSet already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_region_set(ROOT, "region_set1")
        # RegionSetShape already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_region_set_shape(ROOT, "region_set1", 1)
        # Region already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_region(ROOT, "region1_1", "region_set1")
        # GeneticDistanceProtocol already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_genetic_distance_protocol(ROOT, "genetic_distance_protocol1")
        # Dim already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_dim(ROOT, "dim1", enum.DimType.TIME)
        # Col already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_col(
                    ROOT,
                    "col1_1",
                    col_type=enum.ColType.NOMINAL,
                    concept_set="concept_set1_nominal",
                )
        # Disease already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_disease(ROOT, "disease1")
        # EtiologicalAgent already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_etiological_agent(ROOT, "etiological_agent1")
        # Etiology already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_etiology(ROOT, "disease1", "etiological_agent1")
        # DataCollection already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_data_collection(ROOT, "data_collection1")
        # CaseType already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_case_type(
                    ROOT, "case_type1", "disease1", "etiological_agent1"
                )
        # CaseTypeSetCategory already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_case_type_set_category(ROOT, "case_type_set_category1")
        # CaseTypeSet already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_case_type_set(
                    ROOT,
                    "case_type_set1",
                    {"case_type_col1_1_1_1"},
                    "case_type_set_category1",
                )
        # CaseTypeCol already exists
        if (
            not SKIP_CREATE_DATA
            # and DEV_REPOSITORY_CONFIG not in DevRepositoryConfigSet.SA_SQLITE.value
        ):
            # sqlite does not enforce unique constraints on nullable columns.
            # CaseTypeCol.occurrence, which is part of a unique constraint, is
            # nullable, so this this test will fail for sqlite and should therefore
            # not be executed for this type of repository.
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_case_type_col(ROOT, "case_type_col1_1_1_1")
        # CaseTypeColSet already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_case_type_col_set(
                    ROOT,
                    "case_type_col_set1",
                    set(),
                )
        # TODO: add OrganizationAccessCasePolicy and UserAccessCasePolicy already exist

    def test_create_case_type_set_member(self, env: Env) -> None:
        env.create_case_type_set(
            ROOT,
            "case_type_set99",
            set(),
            "case_type_set_category1",
        )
        for i, exec_user in enumerate(APP_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_case_type_set_member(
                exec_user, "case_type_set99", f"case_type{i}"
            )
        env.delete_object(ROOT, model.CaseTypeSet, "case_type_set99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_case_type_set_member_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_type_set_member(
                    exec_user, "case_type_set1", f"case_type1"
                )

    def test_create_case_type_col_set_member(self, env: Env) -> None:
        env.create_case_type_col_set(
            ROOT,
            "case_type_col_set99",
            set(),
        )
        for i, exec_user in enumerate(APP_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_case_type_col_set_member(
                exec_user, "case_type_col_set99", f"case_type_col1_1_1_{i}"
            )
        env.delete_object(ROOT, model.CaseTypeColSet, "case_type_col_set99")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_case_type_col_set_member_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_type_col_set_member(
                    exec_user, "case_type_col_set1", f"case_type_col1_1_1_1"
                )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_object_invalid_reference(self, env: Env) -> None:
        # User.organization does not exist
        with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
            env.invite_and_register_user(ROOT, "root11_1", set_dummy_organization=True)
        # UserInvitation.token is invalid
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user(ROOT, "root1_11", set_dummy_token=True)
        # Concept.concept_set does not exist
        with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
            env.create_concept(
                ROOT,
                "concept11_1",
                set_dummy_concept_set=True,
            )
        # Region.region_set does not exist
        with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
            env.create_region(
                ROOT,
                "region11_1",
                "region_set11",
                set_dummy_region_set=True,
            )
        # RegionSetShape.region_set does not exist
        with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
            env.create_region_set_shape(
                ROOT,
                "region_set11",
                1,
                set_dummy_region_set=True,
            )
        # Col.concept_set does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                index = [
                    i
                    for i, x in enumerate(enum.DimType, start=1)
                    if x == enum.DimType.TEXT
                ][0]
                env.create_col(
                    ROOT,
                    f"col{index}_99",
                    col_type=enum.ColType.NOMINAL,
                    concept_set="concept_set11_nominal",
                    set_dummy_concept_set=True,
                )
        # Col.region_set does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                index = [
                    i
                    for i, x in enumerate(enum.DimType, start=1)
                    if x == enum.DimType.GEO
                ][0]
                env.create_col(
                    ROOT,
                    f"col{index}_99",
                    col_type=enum.ColType.GEO_REGION,
                    region_set="region_set11",
                    set_dummy_region_set=True,
                )
        # Col.genetic_distance_protocol does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                index = [
                    i
                    for i, x in enumerate(enum.DimType, start=1)
                    if x == enum.DimType.TEXT
                ][0]
                env.create_col(
                    ROOT,
                    f"col{index}_99",
                    col_type=enum.ColType.GENETIC_DISTANCE,
                    genetic_distance_protocol="genetic_distance_protocol11",
                    set_dummy_genetic_distance_protocol=True,
                )
        # Etiology.disease does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                env.create_etiology(
                    ROOT,
                    "disease11",
                    "etiological_agent1",
                    set_dummy_disease=True,
                )
        # Etiology.etiological_agent does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                env.create_etiology(
                    ROOT,
                    "disease1",
                    "etiological_agent11",
                    set_dummy_etiological_agent=True,
                )
        # CaseType.disease does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                env.create_case_type(
                    ROOT, "case_type11", "disease11", None, set_dummy_disease=True
                )
        # CaseType.etiological_agent does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                env.create_case_type(
                    ROOT,
                    "case_type11",
                    None,
                    "etiological_agent11",
                    set_dummy_etiological_agent=True,
                )
        # CaseTypeSet.case_type_set_category does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                env.create_case_type_set(
                    ROOT,
                    "case_type_set11",
                    {"case_type1"},
                    "case_type_set_category11",
                    set_dummy_case_type_set_category=True,
                )
        # CaseTypeSetMember.case_type does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                env.create_case_type_set(
                    ROOT,
                    "case_type_set11",
                    {"case_type11"},
                    "case_type_set_category1",
                    set_dummy_case_types=True,
                )
        # CaseTypeDim.dim does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                env.create_case_type_dim(ROOT, "case_type_dim1_1_1", set_dummy_dim=True)
        # CaseTypeCol.case_type does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(
                (
                    exc.InvalidLinkIdsError,
                    exc.InvalidIdsError,
                    exc.InvalidArgumentsError,
                )
            ):
                env.create_case_type_col(
                    ROOT, "case_type_col1_1_1_1", set_dummy_case_type=True
                )
        # CaseTypeCol.col does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                env.create_case_type_col(
                    ROOT, "case_type_col1_1_1_1", set_dummy_col=True
                )
        # CaseTypeColSetMember.case_type_col does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises((exc.InvalidLinkIdsError, exc.InvalidIdsError)):
                env.create_case_type_col_set(
                    ROOT,
                    "case_type_col_set11",
                    {"case_type_col1_1_1_99"},
                    set_dummy_case_type_cols=True,
                )

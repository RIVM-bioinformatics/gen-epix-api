import test.test_client.util as test_util
from test.casedb.casedb_service_test_client import CasedbServiceTestClient as Env
from test.casedb.integration.build_db.base import (
    BELOW_APP_ADMIN_DATA_USERS,
    BELOW_APP_ADMIN_USERS,
    METADATA_ADMIN_OR_ABOVE_USERS,
    SKIP_CREATE_DATA,
    SKIP_RAISE,
)

import pytest

from gen_epix.casedb.domain import enum, exc, model


class TestCreate:
    # CREATE tests

    def test_create_user_first_root(self, env: Env) -> None:
        # Create a first root user and organization
        user = test_util.create_root_user_from_claims(env.cfg, env.app)
        env._set_obj(user)
        env._set_obj(
            env.read_one_by_property("root1_1", model.Organization, "name", "org1")
        )

    def test_create_user_additional_root(self, env: Env) -> None:
        # Create additional root user, including in a different organization
        env.invite_and_register_user("root1_1", "root1_2")
        env.create_organization("root1_2", "org2")
        env.create_organization("root1_2", "org3")
        env.invite_and_register_user("root1_2", "root2_1")
        env.invite_and_register_user("root1_2", "root2_2")
        env.check_user_has_role("root1_2", enum.Role.ROOT, exclusive=True)
        env.check_user_has_role("root2_1", enum.Role.ROOT, exclusive=True)
        env.check_user_has_role("root2_2", enum.Role.ROOT, exclusive=True)

    def test_create_user_app_admin(self, env: Env) -> None:
        # Create invitations for app_admin as root
        env.invite_and_register_user("root1_1", "app_admin1_1")
        env.invite_and_register_user("root2_1", "app_admin1_2")
        env.invite_and_register_user("root1_2", "app_admin2_1")
        env.invite_and_register_user("root2_2", "app_admin2_2")
        env.invite_and_register_user("root1_2", "app_admin3_1")
        env.invite_and_register_user("root2_2", "app_admin3_2")
        env.check_user_has_role("app_admin1_1", enum.Role.APP_ADMIN, exclusive=True)
        env.check_user_has_role("app_admin1_2", enum.Role.APP_ADMIN, exclusive=True)
        env.check_user_has_role("app_admin2_1", enum.Role.APP_ADMIN, exclusive=True)
        env.check_user_has_role("app_admin2_2", enum.Role.APP_ADMIN, exclusive=True)
        env.check_user_has_role("app_admin3_1", enum.Role.APP_ADMIN, exclusive=True)
        env.check_user_has_role("app_admin3_2", enum.Role.APP_ADMIN, exclusive=True)

    def test_create_user_organization(self, env: Env) -> None:
        # Create organizations as root and app_admin
        env.create_organization("root1_2", "org4")
        env.create_organization("app_admin1_2", "org5")
        env.create_organization("app_admin2_1", "org6")
        if env.verbose:
            env.print_organizations()

    def test_create_user_metadata_admin(self, env: Env) -> None:
        # Create metadata_admin as root and app_admin
        env.invite_and_register_user("root2_1", "metadata_admin1_1")
        env.invite_and_register_user("app_admin2_1", "metadata_admin1_2")
        env.invite_and_register_user("app_admin1_1", "metadata_admin2_1")
        env.invite_and_register_user("app_admin1_2", "metadata_admin2_2")
        env.check_user_has_role(
            "metadata_admin1_1", enum.Role.METADATA_ADMIN, exclusive=True
        )
        env.check_user_has_role(
            "metadata_admin1_2", enum.Role.METADATA_ADMIN, exclusive=True
        )
        env.check_user_has_role(
            "metadata_admin2_1", enum.Role.METADATA_ADMIN, exclusive=True
        )
        env.check_user_has_role(
            "metadata_admin2_2", enum.Role.METADATA_ADMIN, exclusive=True
        )

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
        if not all(
            [
                env.check_user_has_role(
                    "org_admin1_1", enum.Role.ORG_ADMIN, exclusive=True
                ),
                env.check_user_has_role(
                    "org_admin1_2", enum.Role.ORG_ADMIN, exclusive=True
                ),
                env.check_user_has_role(
                    "org_admin2_1", enum.Role.ORG_ADMIN, exclusive=True
                ),
                env.check_user_has_role(
                    "org_admin2_2", enum.Role.ORG_ADMIN, exclusive=True
                ),
                env.check_user_has_role(
                    "org_admin3_1", enum.Role.ORG_ADMIN, exclusive=True
                ),
                env.check_user_has_role(
                    "org_admin3_2", enum.Role.ORG_ADMIN, exclusive=True
                ),
                env.check_user_has_role(
                    "org_admin4_1", enum.Role.ORG_ADMIN, exclusive=True
                ),
                env.check_user_has_role(
                    "org_admin4_2", enum.Role.ORG_ADMIN, exclusive=True
                ),
            ]
        ):
            raise AssertionError("Failed to create org_admin users")

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
            env.invite_and_register_user("org_admin1_1", "app_admin1_1")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("org_admin1_1", "metadata_admin1_1")
        for exec_user in ["org_user1_1", "guest1_1"]:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "root2_1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "app_admin2_1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "metadata_admin2_1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "org_admin2_1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "org_user2_1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "guest2_1")
        # Invite user by org admin
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("org_admin1_1", "app_admin1_1")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_organization_raise(self, env: Env) -> None:
        # Check if non-root, non-app_admin users cannot create an organization
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("org_admin1_1", "org11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("metadata_admin1_1", "org11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("org_user1_1", "org11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("guest1_1", "org11")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_org_admin_policy_raise(self, env: Env) -> None:
        for exec_user in [
            "org_admin1_1",
            "metadata_admin1_1",
            "org_user1_1",
            "guest1_1",
        ]:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "root2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "app_admin2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "metadata_admin2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "org_admin2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "org_user2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "guest2_1", "org1")

    # TODO: test_create_site

    # TODO: test_create_site_raise

    # TODO: test_create_contact

    # TODO: test_create_contact_raise

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_concept(self, env: Env) -> None:
        # Create concept as root, app_admin, metadata_admin
        env.create_concept("root1_1", "category1_1")
        env.create_concept("app_admin1_1", "category1_2")
        env.create_concept("metadata_admin1_1", "level2_1")
        env.create_concept("metadata_admin1_2", "level2_2")
        env.create_concept("metadata_admin2_1", "interval3_1")
        env.create_concept("metadata_admin2_2", "interval3_2")
        env.create_concept("metadata_admin1_1", "category4_1")
        env.create_concept("metadata_admin1_2", "category4_2")
        env.create_concept("metadata_admin1_1", "category5_1")
        env.create_concept("metadata_admin1_2", "category5_2")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_concept_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_concept(exec_user, "category1_1")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_concept_set(self, env: Env) -> None:
        # Create concept_set as root, app_admin, metadata_admin
        env.create_concept_set(
            "root1_1",
            "concept_set1_nominal",
            ["category1_1", "category1_2"],
            enum.ConceptSetType.NOMINAL,
        )
        env.create_concept_set(
            "app_admin1_1",
            "concept_set2_ordinal",
            ["level2_1", "level2_2"],
            enum.ConceptSetType.ORDINAL,
        )
        env.create_concept_set(
            "metadata_admin1_1",
            "concept_set3_interval",
            ["interval3_1", "interval3_2"],
            enum.ConceptSetType.INTERVAL,
        )
        env.create_concept_set(
            "metadata_admin1_2",
            "concept_set4_regex",
            [],
            enum.ConceptSetType.REGULAR_LANGUAGE,
            regex=r"^ST(\d*)$",
        )
        env.create_concept_set(
            "metadata_admin2_1",
            "concept_set5_context_free_grammar_json",
            [],
            enum.ConceptSetType.CONTEXT_FREE_GRAMMAR_JSON,
            schema_definition="{}",
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
                    {"category1_1"},
                    enum.ConceptSetType.NOMINAL,
                )

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_region_set(self, env: Env) -> None:
        # Create region_set as root, app_admin, metadata_admin
        env.create_region_set("root1_1", "region_set1")
        env.create_region_set("app_admin1_1", "region_set2")
        env.create_region_set("metadata_admin1_1", "region_set3")
        env.create_region_set("metadata_admin1_2", "region_set4")
        env.create_region_set("metadata_admin2_1", "region_set5")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_region_set_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_region_set(exec_user, "region_set11")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_region_set_shape(self, env: Env) -> None:
        # Create region_set_shape as root, app_admin, metadata_admin
        env.create_region_set_shape("root1_1", "region_set1", 1)
        env.create_region_set_shape("app_admin1_1", "region_set2", 1)
        env.create_region_set_shape("metadata_admin1_1", "region_set3", 1)
        env.create_region_set_shape("metadata_admin1_2", "region_set4", 1)
        env.create_region_set_shape("metadata_admin2_1", "region_set5", 1)

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_region_set_shape_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_region_set_shape(exec_user, "region_set1", 1)

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_region(self, env: Env) -> None:
        # Create region as root, app_admin, metadata_admin
        env.create_region("root1_1", "region1_1", "region_set1")
        env.create_region("app_admin1_1", "region1_2", "region_set1")
        env.create_region("metadata_admin1_1", "region2_1", "region_set2")
        env.create_region("metadata_admin1_2", "region2_2", "region_set2")
        env.create_region("metadata_admin2_1", "region3_1", "region_set3")
        env.create_region("metadata_admin2_2", "region3_2", "region_set3")
        env.create_region("metadata_admin1_1", "region4_1", "region_set4")
        env.create_region("metadata_admin1_2", "region4_2", "region_set4")
        env.create_region("metadata_admin1_1", "region5_1", "region_set5")
        env.create_region("metadata_admin1_2", "region5_2", "region_set5")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_region_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_region(exec_user, "region11", "region_set1")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_genetic_distance_protocol(self, env: Env) -> None:
        # Create genetic_distance_protocol as root, app_admin, metadata_admin
        env.create_genetic_distance_protocol("root1_1", "genetic_distance_protocol1")
        env.create_genetic_distance_protocol(
            "app_admin1_1", "genetic_distance_protocol2"
        )
        env.create_genetic_distance_protocol(
            "metadata_admin1_1", "genetic_distance_protocol3"
        )
        env.create_genetic_distance_protocol(
            "metadata_admin1_2", "genetic_distance_protocol4"
        )
        env.create_genetic_distance_protocol(
            "metadata_admin2_1", "genetic_distance_protocol5"
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
        # Create dim as root, app_admin, metadata_admin
        for i in range(1, 6):
            env.create_dim("root1_1", f"text{i}", enum.DimType.TIME)
            env.create_dim("app_admin1_1", f"number{i}", enum.DimType.NUMBER)
            env.create_dim("metadata_admin1_1", f"time{i}", enum.DimType.TEXT)
            env.create_dim("metadata_admin1_1", f"geo{i}", enum.DimType.GEO)
            env.create_dim("metadata_admin1_1", f"id{i}", enum.DimType.IDENTIFIER)
            env.create_dim("metadata_admin1_1", f"org{i}", enum.DimType.ORGANIZATION)
            env.create_dim("metadata_admin1_1", f"other{i}", enum.DimType.OTHER)

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_dim_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_dim(exec_user, "time11", enum.DimType.TIME)

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_col(self, env: Env) -> None:
        # Create col as root, app_admin, metadata_admin
        for i in range(1, 6):
            # DimType.TEXT can have any column under it
            dim = f"text{i}"
            for j, col_type in enumerate(
                [
                    enum.ColType.NOMINAL,
                    enum.ColType.ORDINAL,
                    enum.ColType.INTERVAL,
                    enum.ColType.REGEX,
                    enum.ColType.CONTEXT_FREE_GRAMMAR_JSON,
                ]
            ):
                j += 1
                col_type_str = col_type.value.lower()
                env.create_col(
                    "metadata_admin1_1",
                    f"{dim}_{j}_{col_type_str}",
                    col_type,
                    concept_set=f"concept_set{j}_{col_type_str}",
                )
            env.create_col("root1_1", f"{dim}_6_text", enum.ColType.TEXT)
            env.create_col(
                "root1_1", f"{dim}_7_number_decimal_0", enum.ColType.DECIMAL_0
            )
            env.create_col("app_admin1_1", f"{dim}_8_time_year", enum.ColType.TIME_YEAR)
            env.create_col(
                "metadata_admin1_1",
                f"{dim}_9_genetic_distance",
                enum.ColType.GENETIC_SEQUENCE,
            )
            env.create_col(
                "metadata_admin1_1",
                f"{dim}_10_genetic_distance",
                enum.ColType.GENETIC_DISTANCE,
                genetic_distance_protocol=f"genetic_distance_protocol{i}",
                # tree_algorithm_codes=[enum.TreeAlgorithm.NJ, enum.TreeAlgorithm.SLINK],
            )
            # DimType.TIME can have time columns under it
            dim = f"time{i}"
            for j, col_type in enumerate(
                [
                    enum.ColType.TIME_DAY,
                    enum.ColType.TIME_WEEK,
                    enum.ColType.TIME_MONTH,
                    enum.ColType.TIME_QUARTER,
                    enum.ColType.TIME_YEAR,
                    enum.ColType.TIME_MONTH,
                ]
            ):
                j += 1
                col_type_str = col_type.value.lower()
                env.create_col(
                    "metadata_admin1_1", f"{dim}_{j}_{col_type_str}", col_type
                )
            # DimType.NUMBER can have number columns under it
            dim = f"number{i}"
            for j, col_type in enumerate(
                [
                    enum.ColType.DECIMAL_0,
                    enum.ColType.DECIMAL_1,
                    enum.ColType.DECIMAL_2,
                    enum.ColType.DECIMAL_3,
                    enum.ColType.DECIMAL_4,
                    enum.ColType.DECIMAL_5,
                    enum.ColType.DECIMAL_6,
                ]
            ):
                j += 1
                col_type_str = col_type.value.lower()
                env.create_col(
                    "metadata_admin1_1", f"{dim}_{j}_{col_type_str}", col_type
                )
            # DimType.GEO can have geo columns under it
            dim = f"geo{i}"
            for j in range(0, 3):
                j += 1
                region_set = f"region_set{j}"
                env.create_col(
                    "metadata_admin1_1",
                    f"{dim}_{j}_{region_set}",
                    enum.ColType.GEO_REGION,
                    region_set=region_set,
                )
            # DimType.IDENTIFIER can have identifier columns under it
            dim = f"id{i}"
            for j, col_type in enumerate(
                [
                    enum.ColType.ID_DIRECT,
                    enum.ColType.ID_PSEUDONYMISED,
                    enum.ColType.ID_ANONYMISED,
                ]
            ):
                j += 1
                col_type_str = col_type.value.lower()
                env.create_col(
                    "metadata_admin1_1", f"{dim}_{j}_{col_type_str}", col_type
                )
            # DimType.ORGANIZATION can have organization columns under it
            dim = f"org{i}"
            for j in range(0, 3):
                j += 1
                env.create_col(
                    "metadata_admin1_1",
                    f"{dim}_{j}_organization",
                    enum.ColType.ORGANIZATION,
                )

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_col_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_col(
                    exec_user,
                    "text1_1_nominal",
                    enum.ColType.NOMINAL,
                    "concept_set1_nominal",
                )

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_disease(self, env: Env) -> None:
        # Create disease as root, app_admin, metadata_admin
        env.create_disease("root1_1", "disease1")
        env.create_disease("app_admin1_1", "disease2")
        env.create_disease("metadata_admin1_1", "disease3")
        env.create_disease("metadata_admin1_1", "disease4")
        env.create_disease("metadata_admin2_1", "disease5")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_disease_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_disease(exec_user, "disease11")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_etiological_agent(self, env: Env) -> None:
        # Create etiological_agent as root, app_admin, metadata_admin
        env.create_etiological_agent("root1_1", "etiological_agent1")
        env.create_etiological_agent("app_admin1_1", "etiological_agent2")
        env.create_etiological_agent("metadata_admin1_1", "etiological_agent3")
        env.create_etiological_agent("metadata_admin1_2", "etiological_agent4")
        env.create_etiological_agent("metadata_admin2_1", "etiological_agent5")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_etiological_agent_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_etiological_agent(exec_user, "etiological_agent11")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_etiology(self, env: Env) -> None:
        # Create etiology as root, app_admin, metadata_admin
        env.create_etiology("root1_1", "disease1", "etiological_agent1")
        env.create_etiology("app_admin1_1", "disease1", "etiological_agent2")
        env.create_etiology("metadata_admin1_1", "disease2", "etiological_agent3")
        env.create_etiology("metadata_admin1_2", "disease3", "etiological_agent3")
        env.create_etiology("metadata_admin2_1", "disease4", "etiological_agent4")
        env.create_etiology("metadata_admin2_1", "disease5", "etiological_agent5")

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
        # Create case_type as root, app_admin, metadata_admin
        env.create_case_type("root1_1", "case_type1", "disease1", "etiological_agent1")
        env.create_case_type(
            "app_admin1_1", "case_type2", "disease1", "etiological_agent2"
        )
        env.create_case_type(
            "metadata_admin1_1", "case_type3", "disease2", "etiological_agent3"
        )
        env.create_case_type(
            "metadata_admin1_2", "case_type4", "disease3", "etiological_agent3"
        )
        env.create_case_type(
            "metadata_admin2_1", "case_type5", "disease4", "etiological_agent4"
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
        # Create case_type_set_category as root, app_admin, metadata_admin
        env.create_case_type_set_category("root1_1", "case_type_set_category1")
        env.create_case_type_set_category("app_admin1_1", "case_type_set_category2")
        env.create_case_type_set_category(
            "metadata_admin1_1", "case_type_set_category3"
        )
        env.create_case_type_set_category(
            "metadata_admin1_2", "case_type_set_category4"
        )
        env.create_case_type_set_category(
            "metadata_admin2_1", "case_type_set_category5"
        )

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_type_set_category_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_type_set_category(exec_user, "case_type_set_category11")

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_case_type_set(self, env: Env) -> None:
        # Create case_type_set as root, app_admin, metadata_admin
        env.create_case_type_set(
            "root1_1", "case_type_set1", {"case_type1"}, "case_type_set_category1"
        )
        env.create_case_type_set(
            "app_admin1_1", "case_type_set2", {"case_type2"}, "case_type_set_category2"
        )
        env.create_case_type_set(
            "app_admin1_1", "case_type_set3", {"case_type3"}, "case_type_set_category3"
        )
        env.create_case_type_set(
            "metadata_admin1_1",
            "case_type_set4",
            {"case_type1", "case_type2"},
            "case_type_set_category4",
        )
        env.create_case_type_set(
            "metadata_admin1_2",
            "case_type_set5",
            {"case_type2", "case_type3"},
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
    def test_create_case_type_col(self, env: Env) -> None:
        # Create case_type_col as root, app_admin, metadata_admin
        cols = env.read_all("root1_1", model.Col)
        # Series of case types with only text columns
        for i in range(1, 4):
            case_type = f"case_type{i}"
            for j in range(1, 6):
                dim = f"text{j}"
                case_type_col = env.create_case_type_col(
                    "root1_1", f"{case_type}_{dim}_6_text"
                )
        for i in range(4, 6):
            for col in cols:
                kwargs = {}
                if col.col_type == enum.ColType.GENETIC_DISTANCE:
                    kwargs["genetic_sequence_case_type_col_id"] = (
                        genetic_sequence_case_type_col.id
                    )
                    kwargs["tree_algorithm_codes"] = {
                        enum.TreeAlgorithmType.NJ,
                        enum.TreeAlgorithmType.SLINK,
                    }
                case_type_col = env.create_case_type_col(
                    "metadata_admin1_1", f"case_type{i}_{col.code}", **kwargs
                )
                if col.col_type == enum.ColType.GENETIC_SEQUENCE:
                    genetic_sequence_case_type_col = case_type_col
            case_type_col = env.create_case_type_col(
                "root1_1",
                f"case_type{i}_text1_8_time_year_2",
                col="text1_8_time_year",
                occurrence=2,
            )
            case_type_col = env.create_case_type_col(
                "app_admin1_1",
                f"case_type{i}_text1_8_time_year_3",
                col="text1_8_time_year",
                occurrence=3,
            )
        # if env.verbose:
        #     env.print_case_type_cols()

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_type_col_raise(self, env: Env) -> None:
        cols = env.read_all("root1_1", model.Col)
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                for col in cols:
                    kwargs = {}
                    if col.col_type == enum.ColType.GENETIC_DISTANCE:
                        kwargs["genetic_sequence_case_type_col_id"] = (
                            genetic_sequence_case_type_col.id
                        )
                        kwargs["tree_algorithm_codes"] = {
                            enum.TreeAlgorithmType.NJ,
                            enum.TreeAlgorithmType.SLINK,
                        }
                    case_type_col = env.create_case_type_col(
                        exec_user, f"case_type1_{col.code}", **kwargs
                    )
                    if col.col_type == enum.ColType.GENETIC_SEQUENCE:
                        genetic_sequence_case_type_col = case_type_col

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_case_type_col_set(self, env: Env) -> None:
        # Create case_type_col_set as root, app_admin, metadata_admin
        env.create_case_type_col_set(
            "root1_1",
            "case_type_col_set1",
            {f"case_type1_text{i+1}_6_text" for i in range(0, 5)},
        )
        env.create_case_type_col_set(
            "app_admin1_1",
            "case_type_col_set2",
            {f"case_type2_text{i+1}_6_text" for i in range(0, 5)},
        )
        env.create_case_type_col_set(
            "metadata_admin1_1",
            "case_type_col_set3",
            {f"case_type3_text{i+1}_6_text" for i in range(0, 5)},
        )
        env.create_case_type_col_set(
            "metadata_admin1_1",
            "case_type_col_set4",
            {
                "case_type1_text1_6_text",
                "case_type1_text2_6_text",
                "case_type2_text1_6_text",
                "case_type2_text2_6_text",
            },
        )
        env.create_case_type_col_set(
            "metadata_admin1_1",
            "case_type_col_set5",
            {
                "case_type2_text2_6_text",
                "case_type2_text3_6_text",
                "case_type3_text2_6_text",
                "case_type3_text3_6_text",
            },
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
                        "case_type1_text1_6_text",
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

    # TODO: remove when ok. Replaced by case access integration test.
    # @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    # def test_create_case(self, env: Env) -> None:
    #     # Create case as org_user
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             env.create_case(
    #                 f"org_user{i}_1",
    #                 f"case{i}_{j}",
    #                 f"data_collection{i}",
    #                 col_index_pattern=r"text(\d+)_6_text",
    #             )
    #     # Custom cases: (org_user, case, data_collections)
    #     data = [
    #         ("1_2", "1_4", ("1", "4")),
    #         ("2_2", "2_4", ("2", "5")),
    #         ("3_2", "3_4", ("3", "4")),
    #         ("3_2", "3_5", ("3", "5")),
    #     ]
    #     for x in data:
    #         env.create_case(
    #             f"org_user{x[0]}",
    #             f"case{x[1]}",
    #             [f"data_collection{y}" for y in x[2]],
    #             col_index_pattern=r"text(\d+)_6_text",
    #         )
    #     if env.verbose:
    #         env.print_cases()

    @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    def test_create_case_set_category(self, env: Env) -> None:
        # Create case_set_category as root, app_admin
        env.create_case_set_category("root1_1", "case_set_category1")
        env.create_case_set_category("app_admin1_1", "case_set_category2")

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_set_category_raise(self, env: Env) -> None:
        for user in ["metadata_admin1_1"] + BELOW_APP_ADMIN_DATA_USERS:
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
        for user in ["metadata_admin1_1"] + BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_set_status(user, "case_set_status11")

    # TODO: remove when ok. Replaced by case access integration test.
    # @pytest.mark.skipif(SKIP_CREATE_DATA, reason="Skipped to facilitate debugging")
    # def test_create_case_set(self, env: Env) -> None:
    #     # Create case set as org_user
    #     for i in range(1, 4):
    #         for j in range(1, 4):
    #             env.create_case_set(
    #                 f"org_user{i}_3",
    #                 f"case_set{i}_{j}",
    #                 "case_set_category1",
    #                 "case_set_status1",
    #                 f"data_collection{i}",
    #                 cases=[f"case{i}_{j}"],
    #             )
    #     # Custom cases: (org_user, name, cases, data_collections)
    #     data = [
    #         ("1_2", "1_4", ("1_4",), ("1", "4")),
    #         ("2_2", "2_4", ("2_4",), ("2", "5")),
    #         ("3_2", "3_4", ("3_4", "3_5"), ("3", "4", "5")),
    #     ]
    #     for x in data:
    #         env.create_case_set(
    #             f"org_user{x[0]}",
    #             f"case_set{x[1]}",
    #             "case_set_category1",
    #             "case_set_status1",
    #             [f"data_collection{y}" for y in x[3]],
    #             cases=[f"case{y}" for y in x[2]],
    #         )

    @pytest.mark.skipif(
        SKIP_RAISE or SKIP_CREATE_DATA, reason="Skipped to facilitate debugging"
    )
    def test_create_case_set_raise(self, env: Env) -> None:
        # TODO: Create case set as org_user1_1 for cases that they do not have access to
        # TODO: Create case set as org_user1_1 for cases that org_user4_1 has access to
        # TODO: Create case set as org_user1_1 for cases that org_user2_1 does not have access to
        # TODO: Create case set as org_admin1_1, app_admin1_1 and root1_1 for cases that org_user1_1 has access to
        # TODO: Create case set for cases some of which do not exist
        # TODO: Create case set for cases some of which are for a different case type
        # TODO: Create case set for cases some of which are not in the case set's data collections even though the user has access to them

        # Update scenarios
        # TODO: Remove data collection from case set: only if write access to data collection/case type
        # TODO: XXX
        pass

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_object_already_exists(self, env: Env) -> None:
        # Organization already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_organization("root2_2", "org2")
        # User already exists
        with pytest.raises(exc.UserAlreadyExistsAuthError):
            env.invite_and_register_user("root1_2", "root2_1")
        with pytest.raises(exc.UserAlreadyExistsAuthError):
            env.invite_and_register_user("app_admin1_1", "org_admin2_1")
        # Organization admin policy already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_org_admin_policy("app_admin1_1", "org_admin1_1", "org1")
        # Concept already exists
        # TODO: uncomment when concept abbreviation uniqueness is enforced
        # with pytest.raises(exc.UniqueConstraintViolationError):
        #     env.create_concept("root1_1", "category1_1")
        # Concept set already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_concept_set(
                    "root1_1",
                    "concept_set1_nominal",
                    {"category1_1"},
                    enum.ConceptSetType.NOMINAL,
                )
        # RegionSet already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_region_set("root1_1", "region_set1")
        # RegionSetShape already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_region_set_shape("root1_1", "region_set1", 1)
        # Region already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_region("root1_1", "region1_1", "region_set1")
        # GeneticDistanceProtocol already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_genetic_distance_protocol(
                    "root1_1", "genetic_distance_protocol1"
                )
        # Dim already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_dim("root1_1", "time1", enum.DimType.TIME)
        # Col already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_col(
                    "root1_1",
                    "text1_1_nominal",
                    enum.ColType.NOMINAL,
                    concept_set="concept_set1_nominal",
                )
        # Disease already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_disease("root1_1", "disease1")
        # EtiologicalAgent already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_etiological_agent("root1_1", "etiological_agent1")
        # Etiology already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_etiology("root1_1", "disease1", "etiological_agent1")
        # DataCollection already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_data_collection("root1_1", "data_collection1")
        # CaseType already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_case_type(
                    "root1_1", "case_type1", "disease1", "etiological_agent1"
                )
        # CaseTypeSetCategory already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_case_type_set_category("root1_1", "case_type_set_category1")
        # CaseTypeSet already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_case_type_set(
                    "root1_1",
                    "case_type_set1",
                    {"case_type1"},
                    "case_type_set_category1",
                )
        # CaseTypeCol already exists
        if not SKIP_CREATE_DATA and env.repository_type.value.upper() not in {
            "SA_SQLITE"
        }:
            # sqlite does not enforce unique constraints on nullable columns.
            # CaseTypeCol.occurrence, which is part of a unique constraint, is
            # nullable, so this this test will fail for sqlite and should therefore
            # not be executed for this type of repository.
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_case_type_col("root1_1", "case_type1_text1_6_text")
        # CaseTypeColSet already exists
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.UniqueConstraintViolationError):
                env.create_case_type_col_set(
                    "root1_1",
                    "case_type_col_set1",
                    {},
                )
        # TODO: add OrganizationAccessCasePolicy and UserAccessCasePolicy already exist

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_object_invalid_reference(self, env: Env) -> None:
        # User.organization does not exist
        with pytest.raises(exc.InvalidIdsError):
            env.invite_and_register_user(
                "root1_1", "root11_1", set_dummy_organization=True
            )
        # UserInvitation.token is invalid
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("root1_1", "root1_11", set_dummy_token=True)
        # ConceptSetMember.concept do not exist
        with pytest.raises(exc.InvalidLinkIdsError):
            env.create_concept_set(
                "root1_1",
                "concept_set11_nominal",
                {"concept11"},
                enum.ConceptSetType.NOMINAL,
                set_dummy_concepts=True,
            )
        # Region.region_set does not exist
        with pytest.raises(exc.InvalidLinkIdsError):
            env.create_region(
                "root1_1",
                "region11_1",
                "region_set11",
                set_dummy_region_set=True,
            )
        # RegionSetShape.region_set does not exist
        with pytest.raises(exc.InvalidLinkIdsError):
            env.create_region_set_shape(
                "root1_1",
                "region_set11",
                1,
                set_dummy_region_set=True,
            )
        # Col.concept_set does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_col(
                    "root1_1",
                    "text1_1_nominal",
                    enum.ColType.NOMINAL,
                    concept_set="concept_set11_nominal",
                    set_dummy_concept_set=True,
                )
        # Col.region_set does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_col(
                    "root1_1",
                    "geo1_1_region",
                    enum.ColType.GEO_REGION,
                    region_set="region_set11",
                    set_dummy_region_set=True,
                )
        # Col.genetic_distance_protocol does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_col(
                    "root1_1",
                    "text1_1_genetic_distance",
                    enum.ColType.GENETIC_DISTANCE,
                    genetic_distance_protocol="genetic_distance_protocol11",
                    set_dummy_genetic_distance_protocol=True,
                )
        # Etiology.disease does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_etiology(
                    "root1_1",
                    "disease11",
                    "etiological_agent1",
                    set_dummy_disease=True,
                )
        # Etiology.etiological_agent does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_etiology(
                    "root1_1",
                    "disease1",
                    "etiological_agent11",
                    set_dummy_etiological_agent=True,
                )
        # CaseType.disease does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_case_type(
                    "root1_1", "case_type11", "disease11", None, set_dummy_disease=True
                )
        # CaseType.etiological_agent does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_case_type(
                    "root1_1",
                    "case_type11",
                    None,
                    "etiological_agent11",
                    set_dummy_etiological_agent=True,
                )
        # CaseTypeSet.case_type_set_category does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_case_type_set(
                    "root1_1",
                    "case_type_set11",
                    {"case_type1"},
                    "case_type_set_category11",
                    set_dummy_case_type_set_category=True,
                )
        # CaseTypeSetMember.case_type does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_case_type_set(
                    "root1_1",
                    "case_type_set11",
                    {"case_type11"},
                    "case_type_set_category1",
                    set_dummy_case_types=True,
                )
        # CaseTypeCol.case_type does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_case_type_col(
                    "root1_1", "case_type1_text1_6_text", set_dummy_case_type=True
                )
        # CaseTypeCol.col does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_case_type_col(
                    "root1_1", "case_type1_text1_6_text", set_dummy_col=True
                )
        # CaseTypeColSetMember.case_type_col does not exist
        if not SKIP_CREATE_DATA:
            with pytest.raises(exc.InvalidLinkIdsError):
                env.create_case_type_col_set(
                    "root1_1",
                    "case_type_col_set11",
                    {"case_type_col11"},
                    set_dummy_case_type_cols=True,
                )

    def test_create_case_type_set_member(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRU
        - metadata_admin: CRU
        - org_admin: R
        - org_user: R
        - guest: -
        """
        env.create_case_type_set(
            "metadata_admin1_1",
            "case_type_set21",
            set(),
            "case_type_set_category1",
        )
        for i, exec_user in enumerate(METADATA_ADMIN_OR_ABOVE_USERS):
            i += 1
            env.create_case_type_set_member(
                exec_user, "case_type_set21", f"case_type{i}"
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_case_type_set_member_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_type_set_member(
                    exec_user, "case_type_set21", f"case_type1"
                )

    def test_create_case_type_col_set_member(self, env: Env) -> None:
        """
        RBAC permissions:
        - root: CRUD
        - app_admin: CRUD
        - metadata_admin: CRUD
        - org_admin: -
        - org_user: -
        - guest: -
        """
        env.create_case_type_col_set(
            "metadata_admin1_1",
            "case_type_col_set21",
            set(),
        )
        for i, exec_user in enumerate(METADATA_ADMIN_OR_ABOVE_USERS, start=1):
            i += 1
            env.create_case_type_col_set_member(
                exec_user, "case_type_col_set21", f"case_type1_text{i}_6_text"
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_case_type_col_set_member_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case_type_col_set_member(
                    exec_user, "case_type_col_set21", f"case_type1_text1_6_text"
                )

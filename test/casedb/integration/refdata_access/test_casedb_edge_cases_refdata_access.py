import pytest
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.refdata_access.base_empty import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)

import logging
from gen_epix.casedb.domain import enum, model
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.casedb.domain.command import CaseTypeCrudCommand


SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB, seqdb_enum.ServiceType, seqdb_enum.RepositoryType, TEST_TYPE
)
CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    """
    Get a test client for CaseDB integration tests.
    This fixture initializes a test client with the appropriate configuration for CaseDB integration tests.
    It uses the DEV_REPOSITORY_CONFIG specified in the base_empty.py file,
    which is set to use an empty dictionary repository for testing edge cases with no data.
    """
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


@pytest.fixture(scope="module")
def setup_test_users_and_organizations(env: Env) -> None:
    """
    Set up common test data used across all tests.
    Bootstrap root user and org1 into env.db for name-based lookups.
    """
    root_user = env.get_root_user()
    env._set_obj(root_user)

    org1 = env.read_one_by_property(root_user, model.Organization, "name", "org1")
    env._set_obj(org1)

    env.create_organization(root_user, "org2")

    # User with org policy but no user policy (should have access to case types shared with org)
    env.invite_and_register_user(root_user, "org_user1_1")

    # User with both org and user policies (should only have access to org-shared case types)
    env.invite_and_register_user(root_user, "org_user1_2")

    # User with both org and user policies on the same case type set (should have access to org-shared case types)
    env.invite_and_register_user(root_user, "org_user1_3")

    # User with no policies (should have no access to case types)
    env.invite_and_register_user(root_user, "org_user2_1")

    # User with user policy but no org policy (should have no access to case types, since case types are shared at org level)
    env.invite_and_register_user(root_user, "org_user2_2")


# The test_data fixture needs to declare a dependency on base_setup
# to ensure it runs after the user is properly set up.
# => properly setting up the root user and organization before the case test data creation begins.
@pytest.fixture(scope="module")
def setup_case_type_data(env: Env, setup_test_users_and_organizations: None) -> None:
    """
    Create reference data (diseases, etiological agents, case types and share policies) for tests.
    Objects are automatically stored in env.db by create methods.
    """
    root_user = env.get_root_user()

    env.create_disease(root_user, "disease_1")
    env.create_disease(root_user, "disease_2")

    env.create_etiological_agent(root_user, "etiological_agent_1")
    env.create_etiological_agent(root_user, "etiological_agent_2")

    # Create case type using pre-created reference data from env.db
    # This case type should only be accessible to users with proper ABAC policies
    case_type_1 = env.create_case_type(
        root_user, "case_type_1", "disease_1", "etiological_agent_1"
    )
    assert case_type_1 is not None

    # case type 2 is created to test that users with access to case type 1 do not automatically
    # get access to case type 2 (i.e. no over-permissioning)
    # It will also be used for user policy access tests
    # (user policy should be commpletely ignored for reference data access,
    # but we want to verify that in the tests)
    case_type_2 = env.create_case_type(
        root_user, "case_type_2", "disease_1", "etiological_agent_1"
    )

    # Create case type set category
    env.create_case_type_set_category(root_user, "category_1", 0)

    # Create case type sets
    env.create_case_type_set(
        root_user, "case_type_set1", [case_type_1.id], "category_1"
    )
    env.create_case_type_set(
        root_user, "case_type_set2", [case_type_2.id], "category_1"
    )
    # Create data collection
    env.create_data_collection(root_user, "data_collection1")

    # Create organization access policy for the case type 1 through case type set 1 for org1
    # This policy should grant access to org users for the case type
    env.create_organization_access_case_policy(
        root_user, "org_case_policy1_1", "case_type_set1"
    )

    # org2 should not have any org policies to test that users in org2 do not have access to case types since there are no org policies granting access to their org

    # for org_user1_2 we will create both org and user policies to test that user policy does not grant additional access beyond org policy for reference data access
    # there is already an org policy that grants access to case_type_1, so we will create a user policy that grants access to case_type_2
    # and verify that it does not grant access to case_type_2 since case types are shared at org level for reference data access
    env.create_user_access_case_policy(
        root_user, "org_user1_2", "data_collection1", "case_type_set2"
    )

    # for org_user1_3 we will create both org and user policies that grant access to the same case type set
    # to verify that it does not cause any issues and user still has access to the case type via the org policy
    env.create_user_access_case_policy(
        root_user, "org_user1_3", "data_collection1", "case_type_set1"
    )

    # for org_user2_2 we will create a user policy that grants access to case_type_1 but no org policy to verify that user policies do not grant access to case types for reference data access since case types are shared at org level
    env.create_user_access_case_policy(
        root_user, "org_user2_2", "data_collection1", "case_type_set1"
    )


@pytest.mark.integration
class TestCaseDBEdgeCasesRefDataAccess:
    """Test edge cases for ABAC filtering on reference data access.

    This test class is designed to test various ABAC policy scenarios:
    - User with no policies (should have no access)
    - User with only org policies (should have access to case types shared with org)
    - User with only user policies (should have no access to case types shared with user)
    - User with both org and user policies (should have access to only case types shared with org, since case types are shared at org level)
    - User with policies that do not match any case types (should have no access)
    """

    @pytest.fixture(autouse=True)
    def setup(self, env: Env) -> None:
        """Auto-inject the env fixture into the class."""
        self.env = env

    def _get_user(self, user_name: str) -> model.User:
        """
        helper method to retrieve a user by name.
        This is necessary because the env fixture and its helper methods are designed to retrieve objects by ID,
        but for these tests we need to retrieve users by their name property.
        This method uses the root user to perform a lookup in the database for a user with the specified name
        and returns the user object if found.
        """
        root_user = self.env.get_root_user()

        retrieved_user = self.env.read_one_by_property(
            root_user, model.User, "name", user_name
        )
        assert isinstance(retrieved_user, model.User)
        assert retrieved_user is not None
        assert retrieved_user.name == user_name

        return retrieved_user

    def test_org_user_1_exists(self, setup_test_users_and_organizations: None) -> None:
        """Test to verify org user 1 exists and can be retrieved."""
        # This test is just to verify that the org user created in the setup can be retrieved successfully.
        # It's a sanity check to ensure that the user setup is correct before we run access tests.
        org_user = self._get_user("org_user1_1")
        assert org_user is not None
        assert org_user.name == "org_user1_1"
        print(f"Retrieved user: {org_user.id} with name: {org_user.name}")

    def test_root_user_has_access_to_all_case_types(
        self, setup_case_type_data: None
    ) -> None:
        """
        Root user should have access to all case types regardless of policies, since they are the superuser.
        (Also basic test to verify case type access works.)
        """
        root_user = self.env.get_root_user()

        # Try to get case types as root user (should have access)
        get_cmd = CaseTypeCrudCommand(user=root_user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd)

        # Root user should have access to case types
        assert isinstance(result, list)
        assert len(result) >= 2, "Root user should have access to all case types"

    def test_organization_user_with_no_policies_has_no_access(
        self, setup_case_type_data: None
    ) -> None:
        """Organization user with no policies should have no access to any case types."""
        # SETUP
        # Create org user with no ABAC policies
        # Note: ORG_USER has RBAC permission to read case types,
        # but needs ABAC policies for actual access to specific case types

        org_user = self._get_user("org_user2_1")

        # TEST
        # Try to get case types as org user with no ABAC policies
        get_cmd = CaseTypeCrudCommand(user=org_user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd)

        # ASSERT
        # User with no ABAC policies should have no access to case types
        assert isinstance(result, list)
        assert (
            len(result) == 0
        ), "User with no policies should not have access to any case types"

    def test_user_with_only_org_policies_has_org_access(
        self, setup_case_type_data: None
    ) -> None:
        """User with only org policies should access org-shared case types."""
        # TODO: Implement test with proper ABAC policy setup

        # SETUP
        # Create org user with no ABAC policies
        # Note: ORG_USER has RBAC permission to read case types,
        # but needs ABAC policies for actual access to specific case types

        # I want to retrieve user by name not by key
        # Verify user was created and can be retrieved by name
        org_user = self._get_user("org_user1_1")
        # TEST
        # Try to get case types as org user with no ABAC policies
        get_cmd = CaseTypeCrudCommand(user=org_user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd)

        # ASSERT
        # assert that the first case type in result has the expected name (the one we created in the test data setup)

        case_type_names = [ct.name for ct in result]

        # assert that the user has access to the first case type which is shared with the org via the org policy
        assert (
            "case_type_1" in case_type_names
        ), "User with org policy should have access to org-shared case type"

        # Also assert that the user does not have access to the second case type which is not shared with the org
        assert (
            "case_type_2" not in case_type_names
        ), "User with org policy should not have access to case types not shared with org"

    def test_user_with_both_org_and_user_policies_has_only_org_access(
        self, setup_case_type_data: None
    ) -> None:
        """User with both org and user policies should only access types shared with the org."""
        # TODO: Implement test with proper ABAC policy setup
        org_user_plus_user_policy = self._get_user("org_user1_2")

        get_cmd = CaseTypeCrudCommand(
            user=org_user_plus_user_policy, operation=CrudOperation.READ_ALL
        )
        result = self.env.app.handle(get_cmd)

        case_type_names = [ct.name for ct in result]
        # assert that the user has access to the first case type which is shared with the org via the org policy
        assert (
            "case_type_1" in case_type_names
        ), "User with org policy should have access to org-shared case type"

        # assert that the user does not have access to the second case type which is not shared with the org and only shared with the user via user policy
        assert (
            "case_type_2" not in case_type_names
        ), "User with org and user policy should not have access to case types not shared with org"

    # Add a test for user org_user1_3 who has both org and user policies on the same case type set to verify that it does not cause any issues and user still has access to the case type via the org policy
    def test_user_with_org_and_user_policies_on_same_case_type_set_has_org_access(
        self, setup_case_type_data: None
    ) -> None:
        """
        User with both org and user policies on the same case type set should have access to org-shared case types.
        """
        org_user_plus_user_policy_same_set = self._get_user("org_user1_3")

        get_cmd = CaseTypeCrudCommand(
            user=org_user_plus_user_policy_same_set, operation=CrudOperation.READ_ALL
        )
        result = self.env.app.handle(get_cmd)

        case_type_names = [ct.name for ct in result]
        # assert that the user has access to the first case type which is shared with the org via the org policy
        assert (
            "case_type_1" in case_type_names
        ), "User with org policy should have access to org-shared case type"

    def test_user_with_only_user_policies_has_no_access(
        self, setup_case_type_data: None
    ) -> None:
        """User with only user policies should have no access to case types, since case types are shared at org level."""
        user_with_only_user_policy = self._get_user("org_user2_2")

        get_cmd = CaseTypeCrudCommand(
            user=user_with_only_user_policy, operation=CrudOperation.READ_ALL
        )
        result = self.env.app.handle(get_cmd)

        case_type_names = [ct.name for ct in result]
        # assert that the user has no access to any case types
        assert (
            not case_type_names
        ), "User with only user policies should have no access to case types"

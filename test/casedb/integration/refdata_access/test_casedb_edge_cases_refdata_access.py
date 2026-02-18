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
def base_setup(env: Env) -> None:
    """
    Set up common test data used across all tests.
    Bootstrap root user and org1 into env.db for name-based lookups.
    """
    root_user = env.get_root_user()
    env._set_obj(root_user)

    org1 = env.read_one_by_property(root_user, model.Organization, "name", "org1")
    env._set_obj(org1)

    env.create_organization(root_user, "org2")

    # User with org policy (should have access to case types shared with org)
    env.invite_and_register_user(root_user, "org_user1_1")
    env.invite_and_register_user(root_user, "org_user1_2")

    # User with no policies (should have no access to case types)
    env.invite_and_register_user(root_user, "org_user2_1")


# The test_data fixture needs to declare a dependency on base_setup
# to ensure it runs after the user is properly set up
# => properly setting up the root user and organization before the test data creation begins.
@pytest.fixture(scope="module")
def case_test_data(env: Env, base_setup: None) -> None:
    """
    Create reference data (diseases, etiological agents) for tests.
    Objects are automatically stored in env.db by create methods.
    """
    root_user = env.get_root_user()

    env.create_disease(root_user, "disease_1")
    env.create_disease(root_user, "disease_2")

    env.create_etiological_agent(root_user, "etiological_agent_1")
    env.create_etiological_agent(root_user, "etiological_agent_2")

    # Create case type using pre-created reference data from env.db
    # This case type should only be accessible to users with proper ABAC policies
    created_case_type = env.create_case_type(
        root_user, "case_type_1", "disease_1", "etiological_agent_1"
    )
    assert created_case_type is not None

    # Create case type set category
    env.create_case_type_set_category(root_user, "category_1", 0)

    # Create case type set
    env.create_case_type_set(
        root_user, "case_type_set1", [created_case_type.id], "category_1"
    )
    # Create data collection
    env.create_data_collection(root_user, "data_collection1")

    # Create organization access policy for the case type
    # This policy should grant access to org users for the case type
    env.create_organization_access_case_policy(
        root_user, "org_case_policy1_1", "case_type_set1"
    )


@pytest.mark.integration
class TestCaseDBEdgeCasesRefDataAccess:
    """Test edge cases for ABAC filtering on reference data access.

    This test class is designed to test various ABAC policy scenarios:
    - User with no policies (should have no access)
    - User with only org policies (should have access to case types shared with org)
    - User with only user policies (should have access to case types shared with user)
    - User with both org and user policies (should have access to both types)
    - User with policies that do not match any case types (should have no access)
    """

    @pytest.fixture(autouse=True)
    def setup(self, env: Env) -> None:
        """Auto-inject the env fixture into the class."""
        self.env = env

    # created this because env (and its helper methods) only supports retrieving objects by ID, but we need to retrieve users by name for these tests
    # It could have gone in the
    def _get_user(self, user_name: str) -> model.User:
        """Helper method to retrieve a user by name."""
        root_user = self.env.get_root_user()

        retrieved_user = self.env.read_one_by_property(
            root_user, model.User, "name", user_name
        )
        assert isinstance(retrieved_user, model.User)
        assert retrieved_user is not None
        assert retrieved_user.name == user_name

        return retrieved_user

    def test_basic_case_type_access(self) -> None:
        """Basic test to verify case type access works."""
        root_user = self.env.get_root_user()

        # Try to get case types as root user (should have access)
        get_cmd = CaseTypeCrudCommand(user=root_user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd)

        # Root user should have access to case types
        assert isinstance(result, list)

    def test_org_user_1_exists(self, base_setup: None) -> None:
        """Test to verify org user 1 exists and can be retrieved."""
        # This test is just to verify that the org user created in the setup can be retrieved successfully.
        # It's a sanity check to ensure that the user setup is correct before we run access tests.
        org_user = self._get_user("org_user1_1")
        assert org_user is not None
        assert org_user.name == "org_user1_1"
        print(f"Retrieved user: {org_user.id} with name: {org_user.name}")

    def test_organization_user_with_no_policies_has_no_access(
        self, case_test_data: None
    ) -> None:
        """Organization user with no policies should have no access to any case types."""
        # SETUP
        # Create org user with no ABAC policies
        # Note: ORG_USER has RBAC permission to read case types,
        # but needs ABAC policies for actual access to specific case types

        # I want to retrieve user by name not by key
        # Verify user was created and can be retrieved by name
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

    def test_user_with_only_org_policies_has_org_access(self, base_setup: None) -> None:
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
        first_case_type = result[0] if len(result) > 0 else None
        assert first_case_type is not None, "Expected at least one case type in result"
        assert (
            first_case_type.name == "case_type_1"
        ), "User with org policy should have access to org-shared case type"

    @pytest.mark.skip(reason="Not implemented yet - needs proper ABAC policy setup")
    def test_user_with_only_user_policies_has_user_access(
        self, base_setup: None
    ) -> None:
        """User with only user policies should access user-shared case types."""
        # TODO: Implement test with proper ABAC policy setup
        pass

    @pytest.mark.skip(reason="Not implemented yet - needs proper ABAC policy setup")
    def test_user_with_both_org_and_user_policies_has_combined_access(
        self, base_setup: None
    ) -> None:
        """User with both org and user policies should access both types."""
        # TODO: Implement test with proper ABAC policy setup
        pass

    @pytest.mark.skip(reason="Not implemented yet - needs proper ABAC policy setup")
    def test_user_with_non_matching_policies_has_no_access(self) -> None:
        """User with policies that don't match any case types has no access."""
        # TODO: Implement test with proper ABAC policy setup
        pass

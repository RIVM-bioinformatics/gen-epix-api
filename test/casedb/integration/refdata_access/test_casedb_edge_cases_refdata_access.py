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


# The test_data fixture needs to declare a dependency on base_setup
# to ensure it runs after the user is properly set up
# => properly setting up the root user and organization before the test data creation begins.
@pytest.fixture(scope="module")
def test_data(env: Env, base_setup: None) -> None:
    """
    Create reference data (diseases, etiological agents) for tests.
    Objects are automatically stored in env.db by create methods.
    """
    root_user = env.get_root_user()

    env.create_disease(root_user, "disease_1")
    env.create_disease(root_user, "disease_2")

    env.create_etiological_agent(root_user, "etiological_agent_1")
    env.create_etiological_agent(root_user, "etiological_agent_2")


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

    def test_basic_case_type_access(self, env: Env) -> None:
        """Basic test to verify case type access works."""
        root_user = env.get_root_user()

        # Try to get case types as root user (should have access)
        get_cmd = CaseTypeCrudCommand(user=root_user, operation=CrudOperation.READ_ALL)
        result = env.app.handle(get_cmd)

        # Root user should have access to case types
        assert isinstance(result, list)

    def test_organization_user_with_no_policies_has_no_access(
        self, env: Env, test_data: None
    ) -> None:
        """Organization user with no policies should have no access to any case types."""
        root_user = env.get_root_user()

        # Create org user with no ABAC policies
        # Note: ORG_USER has RBAC permission to read case types,
        # but needs ABAC policies for actual access to specific case types
        org_user = env.invite_and_register_user(root_user, "org_user1_1")

        # Create case type using pre-created reference data from env.db
        # This case type should only be accessible to users with proper ABAC policies
        created_case_type = env.create_case_type(
            root_user, "case_type_1", "disease_1", "etiological_agent_1"
        )
        assert created_case_type is not None

        # Try to get case types as org user with no ABAC policies
        get_cmd = CaseTypeCrudCommand(user=org_user, operation=CrudOperation.READ_ALL)
        result = env.app.handle(get_cmd)

        # User with no ABAC policies should have no access to case types
        assert isinstance(result, list)
        assert (
            len(result) == 0
        ), "User with no policies should not have access to any case types"

    @pytest.mark.skip(reason="Not implemented yet - needs proper ABAC policy setup")
    def test_user_with_only_org_policies_has_org_access(self, env: Env) -> None:
        """User with only org policies should access org-shared case types."""
        # TODO: Implement test with proper ABAC policy setup
        pass

    @pytest.mark.skip(reason="Not implemented yet - needs proper ABAC policy setup")
    def test_user_with_only_user_policies_has_user_access(self, env: Env) -> None:
        """User with only user policies should access user-shared case types."""
        # TODO: Implement test with proper ABAC policy setup
        pass

    @pytest.mark.skip(reason="Not implemented yet - needs proper ABAC policy setup")
    def test_user_with_both_org_and_user_policies_has_combined_access(
        self, env: Env
    ) -> None:
        """User with both org and user policies should access both types."""
        # TODO: Implement test with proper ABAC policy setup
        pass

    @pytest.mark.skip(reason="Not implemented yet - needs proper ABAC policy setup")
    def test_user_with_non_matching_policies_has_no_access(self, env: Env) -> None:
        """User with policies that don't match any case types has no access."""
        # TODO: Implement test with proper ABAC policy setup
        pass

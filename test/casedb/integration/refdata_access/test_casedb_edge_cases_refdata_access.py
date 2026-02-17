import pytest
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.refdata_access.base_empty import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)

from gen_epix.commondb.domain import enum, model
from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.command import CaseTypeCrudCommand
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum

import logging


SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
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

    def test_user_with_no_policies_has_no_access(self, env: Env) -> None:
        """User with no policies should have no access to any case types."""

        root_user = env.get_root_user()
        env._set_obj(root_user)  # Bootstrap root user into tracking db

        # Bootstrap org1 into tracking db (it exists in the actual database)

        org1 = env.read_one_by_property(root_user, model.Organization, "name", "org1")
        env._set_obj(org1)

        # Create a guest user with no ABAC policies
        org_user = env.invite_and_register_user(root_user, "org_user1_1")

        # Note: Create case types with different sharing levels and verify that the user with no policies does not have access to any of them,
        # while users with org/user policies have access to the appropriate ones.
        # This will require setting up proper ABAC policies for the test users and
        # creating case types with different sharing levels (org-shared, user-shared, etc.)

        # create disease1
        assert env.create_disease(root_user, "disease1") is not None
        # create etiological_agent1
        assert env.create_etiological_agent(root_user, "etiological_agent1") is not None

        # Create case type
        # Create a case type that should be accessible to users with proper policies
        created_case_type = env.create_case_type(
            root_user, "case_type1", "disease1", "etiological_agent1"
        )
        # Verify case type was created
        assert created_case_type is not None

        # Try to get case types as organisation user with no ABAC policies
        get_cmd = CaseTypeCrudCommand(user=org_user, operation=CrudOperation.READ_ALL)
        result = env.app.handle(get_cmd)

        # User with no policies should have no access to case types
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

import pytest

from test.casedb.casedb_test_client import CasedbTestClient as Env

from test.casedb.integration.case_access.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)

import logging
from gen_epix.casedb.domain import enum, model
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.seqdb.domain import enum as seqdb_enum


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


@pytest.fixture(scope="module")

# Note: There is code duplicatio between this file and test_casedb/integration/refdata_access/test_casedb_edge_cases_refdata_access.py.
# This will be resolved with a test builder pattern in a future refactor, but for now we can allow some duplication for clarity and to avoid over-engineering the test setup at this stage.
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
class TestCasedbEdgeCasesAccess:
    """
    Integration tests for edge cases in case access control within the CASEDB service.
    Covers ABAC/RBAC boundary conditions, cross-organization access, and permission escalation attempts.
    """

    @pytest.fixture(autouse=True)
    def setup(self, env: Env) -> None:
        """Auto-inject the env fixture into the class."""
        self.env = env

    # -------------------------------------------------------------------------
    # Read access edge cases
    # -------------------------------------------------------------------------
    def test_org_user_1_exists(self, setup_test_users_and_organizations: None) -> None:
        """
        Test to verify org user 1 exists and can be retrieved.
        """

        # This test is just to verify that the org user created in the setup can be retrieved successfully.
        # It's a sanity check to ensure that the user setup is correct before we run access tests.
        org_user = self.env.get_user("org_user1_1")

        assert org_user is not None
        assert org_user.name == "org_user1_1"
        print(f"Retrieved user: {org_user.id} with name: {org_user.name}")

import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.case_access.base_edge_cases import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)

import pytest

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

    def get_user(self, user_name: str) -> model.User:
        """Helper method to retrieve a user by name from the test client environment."""
        return self.env._get_obj(model.User, user_name)  # type: ignore[return-value]

    # -------------------------------------------------------------------------
    # Read access edge cases
    # -------------------------------------------------------------------------
    def test_org_user_1_exists(self, setup_test_users_and_organizations: None) -> None:
        """
        Test to verify org user 1 exists and can be retrieved.
        """

        # This test is just to verify that the org user created in the setup can be retrieved successfully.
        # It's a sanity check to ensure that the user setup is correct before we run access tests.
        org_user = self.get_user("org_user1_1")

        assert org_user is not None
        assert org_user.name == "org_user1_1"
        print(f"Retrieved user: {org_user.id} with name: {org_user.name}")

    def test_root_user_can_create_case(self, setup_case_type_data: None) -> None:
        """
        Test that a root user can create a case and that the created case is retrievable.
        This verifies that root users have the necessary permissions to create and access cases.
        """
        root_user = self.env.get_root_user()

        # case_type1 and data_collection1 are created in the setup_case_type_data fixture

        # created_at = datetime(2025, 1, 1, tzinfo=UTC)
        # modified_at = datetime(2025, 6, 1, tzinfo=UTC)

        # Override modified_by to be a different user to verify that the value set by the test client
        # is not being overridden by the policy,
        # since root user should bypass the policy and keep the values provided in the command.
        modified_by = self.get_user("org_user1_1").id

        case_result = self.env.create_case(
            root_user,
            code="case_1_1",
            data_collections="data_collection1",
            # created_at=created_at,
            # modified_at=modified_at,
            # modified_by=modified_by,
        )

        assert isinstance(case_result, model.Case)

        print(f"Created case with id: {case_result.id}")

        # Now verift that the created case has created_at, modified_at, and modified_by fields set by the SetModelProcessMetadataPolicy,
        # which should be the case since root user should bypass the policy and keep the values provided in the command,
        # which are set to fixed values in the test client for testing purposes.
        # assert (
        #     case_result.created_at == created_at
        # ), "created_at should be set to the fixed value provided in the command for root user"
        # assert (
        #     case_result.modified_at == modified_at
        # ), "modified_at should be set to the fixed value provided in the command for root user"
        # assert (
        #     case_result.modified_by == modified_by
        # ), "modified_by should be set to the user specified in the command for root user"

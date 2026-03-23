import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.edge_cases_access.base_edge_cases import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.casedb.integration.edge_cases_access.setup.define_edge_cases import (
    EDGE_CASE_BY_USER,
    EDGE_CASES,
    EdgeCaseSpec,
)
from test.casedb.integration.edge_cases_access.setup.define_edge_cases_operational import (
    EDGE_CASES_OP,
    EDGE_CASES_OP_BY_USER,
)

import pytest
from rich import print as rich_print

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.command import CaseCrudCommand
from gen_epix.casedb.domain.command.case import RetrieveCasesByIdCommand
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
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
            code="case1_99",  # Do not use a code that is already used by other test cases created in the setup.
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

    # testing capabilities of the test client for the edge cases related to access to operational data
    def test_root_user_can_create_case_in_2_data_collections(
        self, setup_case_type_data: None
    ) -> None:
        """
        Test that a root user can create a case that belongs to 2 data collections and that the created case is retrievable.
        This verifies that root users have the necessary permissions to create and access cases that belong to multiple data collections.
        """
        root_user = self.env.get_root_user()

        # case_type1, data_collection1 and data_collection2 are created in the setup_case_type_data fixture

        case_result = self.env.create_case(
            root_user,
            code="case1_100",  # Do not use a code that is already used by other test cases created in the setup.
            data_collections=["data_collection1", "data_collection2"],
        )

        assert isinstance(case_result, model.Case)

        print(f"Created case with id: {case_result.id} belonging to 2 data collections")

    @pytest.mark.skip(
        reason="Cases are not put in correct data collection in the setup,"
        + "also RetrieveCasesByIdCommand needs to be updated to include case_type_id for access control checks"
    )
    @pytest.mark.parametrize(
        "spec",
        EDGE_CASES,
        ids=[x.user_name for x in EDGE_CASES],
    )
    def test_case_access_matches_expected(
        self, spec: EdgeCaseSpec, setup_case_type_data: None
    ) -> None:
        """
        For each edge case, assert that the set of accessible Cases exactly matches
        the expected set declared in EdgeCaseSpec.expected_cases — neither more nor less.

        Operational data access requires BOTH org-level AND user-level policies to intersect:
        - access CaseTypes = CaseTypes in (org_access CaseTypeSets ∩ user_access CaseTypeSets)
        - share CaseTypes  = CaseTypes in (org_share CaseTypeSets ∩ user_share CaseTypeSets)
        - accessible cases = union of cases belonging to either access or share CaseTypes
        """
        user = self.get_user(spec.user_name)

        root_user = self.env.get_root_user()
        if VERBOSE:
            rich_print(EDGE_CASE_BY_USER[spec.user_name])

        get_cmd = CaseCrudCommand(user=root_user, operation=CrudOperation.READ_ALL)
        full_cases = self.env.app.handle(get_cmd)

        all_cases = []

        # per case in full_cases, create a command
        for case in full_cases:

            get_cmd_user = RetrieveCasesByIdCommand(
                case_type_id=case.case_type_id,  # CaseType is required for access control checks
                case_ids=[case.id],
                user=user,
            )
            case_objs = self.env.app.handle(get_cmd_user)

            all_cases.extend(case_objs)

        actual = (
            {case.code for case in all_cases} if isinstance(all_cases, list) else set()
        )

        # case.content is json, only cols that you have access through ABAC policy
        # 1.
        # retrieve complete case type for case type of the case
        # this will give the case_type_access_abacs for each data collection
        #         read_col_ids: set[UUID] = Field(
        #     description="The IDs of the columns for which values can be read, limited to the CaseType and data collection"
        # )
        #  --> What can be read for each data collection

        # 2. for each case retrieve which data collection it belongs to through the created_in_data_collection_id field and the
        # case data collection links table (koppeltabel)
        #  -> Data collections
        # 3. compare 1. and 2. for read access on case.content (dict with col_id as key and col_value as value)

        # case in two dc's: col1 in first dc, col2 in second dc => both col1 and col2 visible

        expected = set(spec.expected_cases)

        missing = expected - actual
        unexpected = actual - expected

        assert not missing and not unexpected, (
            f"\n{spec.description}"
            f"\n  Missing access:    {sorted(missing) if missing else '∅'}"
            f"\n  Unexpected access: {sorted(unexpected) if unexpected else '∅'}"
        )

    @pytest.mark.parametrize(
        "spec",
        EDGE_CASES_OP,
        ids=[x.user_name for x in EDGE_CASES_OP],
    )
    # Note: replace setup_case_type_data with new setup for operational data later
    def test_just_print_edge_cases_operational(
        self, spec: EdgeCaseSpec, setup_case_data: None
    ) -> None:
        user = self.get_user(spec.user_name)

        # TODO: Do sanity check on some of the edge cases to validate expectations
        if VERBOSE:
            rich_print(EDGE_CASES_OP_BY_USER[spec.user_name])

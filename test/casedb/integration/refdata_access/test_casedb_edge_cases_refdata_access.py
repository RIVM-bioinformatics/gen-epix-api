import logging

import pytest

from rich import print as rich_print
from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.command import CaseTypeCrudCommand
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum
from test.casedb.casedb_test_client import CasedbTestClient as Env

from test.casedb.integration.conftest import (
    EDGE_CASES,
    EdgeCaseSpec,
)
from test.casedb.integration.refdata_access.base_empty import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)


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
class TestCaseDBEdgeCasesRefDataAccess:
    """Test ABAC filtering on reference data (case type) access across all edge cases.

    Each user in EDGE_CASES represents one combination of org membership, org-level policies,
    and user-level policies. A single parametrized test iterates all specs and asserts that
    the accessible case types exactly match the expected set declared in EdgeCaseSpec.

    The root user is tested separately as a superuser baseline (not an ABAC edge case).
    """

    @pytest.fixture(autouse=True)
    def setup(self, env: Env) -> None:
        """Auto-inject the env fixture into the class."""
        self.env = env

    def get_user(self, user_name: str) -> model.User:
        """Helper method to retrieve a user by name from the test client environment."""
        return self.env._get_obj(model.User, user_name)  # type: ignore[return-value]

    def test_root_user_has_access_to_all_case_types(
        self, setup_case_type_data: None
    ) -> None:
        """Root user should have access to all case types regardless of policies (superuser baseline)."""
        root_user = self.env.get_root_user()

        get_cmd = CaseTypeCrudCommand(user=root_user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd)

        assert isinstance(result, list)
        assert len(result) >= 2, "Root user should have access to all case types"

    @pytest.mark.parametrize(
        "spec",
        EDGE_CASES,
        ids=[s.user_name for s in EDGE_CASES],
    )
    def test_case_type_access_matches_expected(
        self, spec: EdgeCaseSpec, setup_case_type_data: None
    ) -> None:
        """
        For each edge case, assert that the set of accessible case types exactly matches
        the expected set declared in EdgeCaseSpec — neither more nor less.

        Failure output includes the full edge case description so the cause is immediately clear:
          [org_user1_2@org1] org_policies=[case_type_set1], user_policies=[case_type_set2] → expected=[case_type_1]
          Missing access:    ∅
          Unexpected access: ['case_type_2']
        """

        rich_print(EDGE_CASES)  # Debug print to verify the test cases being run

        user = self.get_user(spec.user_name)

        get_cmd = CaseTypeCrudCommand(user=user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd)

        actual = {ct.name for ct in result}
        expected = set(spec.expected_case_types)

        missing = expected - actual
        unexpected = actual - expected

        assert not missing and not unexpected, (
            f"\n{spec.description}"
            f"\n  Missing access:    {sorted(missing) if missing else '∅'}"
            f"\n  Unexpected access: {sorted(unexpected) if unexpected else '∅'}"
        )

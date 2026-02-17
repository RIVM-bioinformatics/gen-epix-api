import pytest
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.refdata_access.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.command import (
    CaseTypeCrudCommand,
)
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
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


@pytest.mark.integration
class TestCaseDBRefDataAccessEdgeCases:
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

    @pytest.mark.skip(reason="Not implemented yet - needs proper ABAC policy setup")
    def test_user_with_no_policies_has_no_access(self, env: Env) -> None:
        """User with no policies should have no access to any case types."""
        # TODO: Implement test with proper user creation and ABAC policy setup
        pass

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

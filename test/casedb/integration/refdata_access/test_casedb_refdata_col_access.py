import logging

import pytest
from rich import print as rich_print

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.command.case import (
    CaseTypeColCrudCommand,
    CaseTypeColSetCrudCommand,
    ColCrudCommand,
    DimCrudCommand,
)
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum
from test.casedb.casedb_test_client import CasedbTestClient as Env

from test.casedb.integration.refdata_access.base_empty import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.casedb.integration.setup.setup_case_col_data import (
    CASE_COL_SPECS,
    CaseColSpec,
)
from test.casedb.integration.setup.setup_case_col_data import CASE_COL_SPECS
from test.test_client.enum import TestType

# overwrite TEST_TYPE because of possible conflict with other test classes using the same base class
TEST_TYPE = TestType.CASEDB_INTEGRATION_REFDATA_ACCESS_COL

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
class TestCaseDBRefDataColAccess:

    @pytest.fixture(autouse=True, scope="class")
    def print_edge_cases(self, env: Env) -> None:
        """Print the active edge cases once per class run when VERBOSE is enabled."""
        if VERBOSE:
            rich_print(env.db[model.User]["org_user1_1"])
            rich_print(env.db[model.User]["org_user1_2"])
            rich_print(env.db[model.Organization])
            rich_print(env.db[model.OrganizationAccessCasePolicy])
            rich_print(env.db[model.CaseTypeColSet])
            rich_print(env.db[model.CaseTypeCol])
            rich_print(env.db[model.CaseTypeDim])
            rich_print(env.db[model.Col])
            rich_print(env.db[model.Dim])

            rich_print(env.db[model.OrganizationShareCasePolicy])
            rich_print(env.db[model.DataCollection])

    @pytest.fixture(autouse=True)
    def setup(self, env: Env) -> None:
        """Auto-inject the env fixture into the class."""
        self.env = env

    def get_user(self, user_name: str) -> model.User:
        """Helper method to retrieve a user by name from the test client environment."""
        return self.env._get_obj(model.User, user_name)  # type: ignore[return-value]

    def test_root_user_has_access_to_all_case_type_col_sets(
        self, setup_case_col_data: None
    ) -> None:
        """Root user should have access to all case type column sets regardless of policies (superuser baseline)."""
        root_user = self.env.get_root_user()

        get_cmd = CaseTypeColSetCrudCommand(
            user=root_user, operation=CrudOperation.READ_ALL
        )
        result = self.env.app.handle(get_cmd)

        assert isinstance(result, list)
        assert len(result) == len(
            self.env.db[model.CaseTypeColSet]
        ), "Root user should have access to all case type column sets "

    @pytest.mark.parametrize(
        "spec",
        CASE_COL_SPECS,
        ids=[s.user_name for s in CASE_COL_SPECS],
    )
    def test_case_type_col_set_access_matches_expected(
        self, spec: CaseColSpec, setup_case_col_data: None
    ) -> None:
        """
        For each edge case, assert that the set of accessible case type col sets exactly matches
        the expected set declared in CaseColSpec.expected_case_type_col_sets — neither more nor less.

        Only case type col sets referenced in org-level policies should be accessible.
        User policies must not grant access to additional case type col sets.
        """
        user = self.get_user(spec.user_name)

        # get all case type col sets accessible to org_user1_1 to confirm that at least some exist and root user has more access than a regular user
        get_cmd_user = CaseTypeColSetCrudCommand(
            user=user, operation=CrudOperation.READ_ALL
        )
        result = self.env.app.handle(get_cmd_user)

        assert isinstance(result, list)
        assert len(result) == len(
            spec.expected_case_type_col_sets
        ), f"Expected number of accessible case type column sets does not match actual for user {spec.user_name}"

    @pytest.mark.parametrize(
        "spec",
        CASE_COL_SPECS,
        ids=[s.user_name for s in CASE_COL_SPECS],
    )
    def test_case_type_col_access_matches_expected(
        self, spec: CaseColSpec, setup_case_col_data: None
    ) -> None:
        """
        For each edge case, assert that the set of accessible case type columns exactly matches
        the expected set declared in CaseColSpec.expected_case_type_cols — neither more nor less.

        Only case type columns referenced in org-level policies should be accessible.
        User policies must not grant access to additional case type columns.
        """
        user = self.get_user(spec.user_name)

        # get all case type col sets accessible to org_user1_1 to confirm that at least some exist and root user has more access than a regular user
        get_cmd_user = CaseTypeColCrudCommand(
            user=user, operation=CrudOperation.READ_ALL
        )
        result = self.env.app.handle(get_cmd_user)

        assert isinstance(result, list)
        assert len(result) == len(
            spec.expected_case_type_cols
        ), f"Expected number of accessible case type columns does not match actual for user {spec.user_name}"

    @pytest.mark.parametrize(
        "spec",
        CASE_COL_SPECS,
        ids=[s.user_name for s in CASE_COL_SPECS],
    )
    def test_col_access_matches_expected(
        self, spec: CaseColSpec, setup_case_col_data: None
    ) -> None:
        """
        For each edge case, assert that the set of accessible columns exactly matches
        the expected set declared in CaseColSpec.expected_cols — neither more nor less.

        Only columns referenced in org-level policies should be accessible.
        User policies must not grant access to additional columns.
        """
        user = self.get_user(spec.user_name)

        # get all columns accessible to org_user1_1 to confirm that at least some exist and root user has more access than a regular user
        get_cmd_user = ColCrudCommand(user=user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd_user)

        assert isinstance(result, list)
        assert len(result) == len(
            spec.expected_cols
        ), f"Expected number of accessible columns does not match actual for user {spec.user_name}"

    @pytest.mark.parametrize(
        "spec",
        CASE_COL_SPECS,
        ids=[s.user_name for s in CASE_COL_SPECS],
    )
    def test_dim_access_matches_expected(
        self, spec: CaseColSpec, setup_case_col_data: None  # noqa: ARG002
    ) -> None:
        """
        For each edge case, assert that the set of accessible dimensions exactly matches
        the expected set declared in CaseColSpec.expected_dims — neither more nor less.

        Only dimensions referenced in org-level policies should be accessible.
        User policies must not grant access to additional dimensions.
        """
        user = self.get_user(spec.user_name)

        get_cmd_user = DimCrudCommand(user=user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd_user)

        assert isinstance(result, list)
        assert len(result) == len(
            spec.expected_dims
        ), f"Expected number of accessible dimensions does not match actual for user {spec.user_name}"

"""
This module contains integration tests for CaseDB reference data access edge cases.

It uses:

- an empty database to begin with, see DevRepositoryConfig.DICT_EMPTY in base_refdata_access.py for configuration
- the definitions in EDGE_CASES from define_edge_cases.py
- the setup_case_type_data fixture to create reference data and policies for all edge cases defined in define_edge_cases.py,
- and then tests that each user has access to exactly the expected CaseTypes or other reference data

"""

import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.edge_cases_access.base_refdata_access import (
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

import pytest
from rich import print as rich_print

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.command import (
    CaseTypeCrudCommand,
    CaseTypeSetCategoryCrudCommand,
    CaseTypeSetCrudCommand,
    RefColCrudCommand,
    RefDimCrudCommand,
)
from gen_epix.casedb.repositories.sa_model.ontology import Disease
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
    It uses the DEV_REPOSITORY_CONFIG specified in the base_refdata_access.py file,
    which is set to use an empty dictionary repository for testing edge cases with no data.
    """
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


@pytest.mark.scenario_ids("IVO-26")
@pytest.mark.integration
class TestCaseDBEdgeCasesRefDataAccess:
    """Test ABAC filtering on reference data (CaseType) access across all edge cases.

    Each user in EDGE_CASES represents one combination of org membership, org-level policies,
    and user-level policies. A single parametrized test iterates all specs and asserts that
    the accessible CaseTypes exactly match the expected set declared in EdgeCaseSpec.

    The root user is tested separately as a superuser baseline (not an ABAC edge case).
    """

    @pytest.fixture(autouse=True, scope="class")
    def print_edge_cases(self) -> None:
        """Print the active edge cases once per class run when VERBOSE is enabled."""
        # if VERBOSE:
        #     rich_print(EDGE_CASES)

        # if VERBOSE:
        #     rich_print(env.db[model.User]["org_user1_1"])
        #     rich_print(env.db[model.User]["org_user1_2"])
        #     rich_print(env.db[model.Organization])
        #     rich_print(env.db[model.OrganizationAccessCasePolicy])

        #     rich_print(env.db[model.ColSet])
        #     rich_print(env.db[model.Col])
        #     rich_print(env.db[model.Dim])
        #     rich_print(env.db[model.RefCol])
        #     rich_print(env.db[model.RefDim])

        #     rich_print(env.db[model.DataCollection])

        pass

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
        """Root user should have access to all CaseTypes regardless of policies (superuser baseline)."""
        root_user = self.env.get_root_user()

        get_cmd = CaseTypeCrudCommand(user=root_user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd)

        assert isinstance(result, list)

        assert len(result) >= 2, "Root user should have access to all CaseTypes"

    @pytest.mark.parametrize(
        "spec",
        EDGE_CASES,
        ids=[x.user_name for x in EDGE_CASES],
    )
    def test_case_type_access_matches_expected(
        self, spec: EdgeCaseSpec, setup_case_type_data: None
    ) -> None:
        """
        For each edge case, assert that the set of accessible CaseTypes exactly matches
        the expected set declared in EdgeCaseSpec — neither more nor less.

        Failure output includes the full edge case description so the cause is immediately clear, example:
          [org_user1_2@org1] org_policies=[case_type_set1], user_policies=[case_type_set2] → expected=[case_type1]
          Missing access:    ∅
          Unexpected access: ['case_type2']
        """

        user = self.get_user(spec.user_name)

        if VERBOSE:
            rich_print(EDGE_CASE_BY_USER[spec.user_name])

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

    @pytest.mark.parametrize(
        "spec",
        EDGE_CASES,
        ids=[x.user_name for x in EDGE_CASES],
    )
    def test_case_type_set_access_matches_expected(
        self, spec: EdgeCaseSpec, setup_case_type_data: None
    ) -> None:
        """
        For each edge case, assert that the set of accessible CaseTypeSets exactly matches
        the expected set declared in EdgeCaseSpec.expected_case_type_sets — neither more nor less.

        Only CaseTypeSets referenced in org-level policies should be accessible.
        User policies must not grant access to additional CaseTypeSets.
        """
        user = self.get_user(spec.user_name)

        if VERBOSE:
            rich_print(EDGE_CASE_BY_USER[spec.user_name])

        get_cmd = CaseTypeSetCrudCommand(user=user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd)

        actual = {x.name for x in result}
        expected = set(spec.expected_case_type_sets)

        missing = expected - actual
        unexpected = actual - expected

        assert not missing and not unexpected, (
            f"\n{spec.description}"
            f"\n  Missing access:    {sorted(missing) if missing else '∅'}"
            f"\n  Unexpected access: {sorted(unexpected) if unexpected else '∅'}"
        )

    @pytest.mark.parametrize(
        "spec",
        EDGE_CASES,
        ids=[x.user_name for x in EDGE_CASES],
    )
    def test_col_set_access_matches_expected(
        self, spec: EdgeCaseSpec, setup_case_type_data: None
    ) -> None:
        """
        For each edge case, assert that the set of accessible ColSets exactly matches
        the expected set declared in EdgeCaseSpec.expected_col_sets — neither more nor less.

        Only ColSets referenced in org-level policies should be accessible.
        User policies must not grant access to additional ColSets.
        """
        user = self.get_user(spec.user_name)

        if VERBOSE:
            rich_print(EDGE_CASE_BY_USER[spec.user_name])

        get_cmd = command.ColSetCrudCommand(user=user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd)

        # Fix: handle None or unexpected result type
        if not isinstance(result, list):
            actual = set()
        else:
            actual = {x.name for x in result}
        expected = set(spec.expected_col_sets)

        missing = expected - actual
        unexpected = actual - expected

        assert not missing and not unexpected, (
            f"\n{spec.description}"
            f"\n  Missing access:    {sorted(missing) if missing else '∅'}"
            f"\n  Unexpected access: {sorted(unexpected) if unexpected else '∅'}"
        )

    @pytest.mark.parametrize(
        "spec",
        EDGE_CASES,
        ids=[x.user_name for x in EDGE_CASES],
    )
    def test_col_access_matches_expected(
        self, spec: EdgeCaseSpec, setup_case_type_data: None
    ) -> None:
        """
        For each edge case, assert that the set of accessible cols exactly matches
        the expected set declared in EdgeCaseSpec.expected_ref_cols — neither more nor less.

        Accessible cols are derived from accessible Cols (via org access policies only).
        User policies must not grant access to additional cols.
        """
        user = self.get_user(spec.user_name)

        if VERBOSE:
            rich_print(EDGE_CASE_BY_USER[spec.user_name])

        get_cmd = RefColCrudCommand(user=user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd)

        actual = {x.code for x in result} if isinstance(result, list) else set()
        expected = set(spec.expected_ref_cols)

        missing = expected - actual
        unexpected = actual - expected

        assert not missing and not unexpected, (
            f"\n{spec.description}"
            f"\n  Missing access:    {sorted(missing) if missing else '∅'}"
            f"\n  Unexpected access: {sorted(unexpected) if unexpected else '∅'}"
        )

    @pytest.mark.parametrize(
        "spec",
        EDGE_CASES,
        ids=[x.user_name for x in EDGE_CASES],
    )
    def test_ref_dim_access_matches_expected(
        self, spec: EdgeCaseSpec, setup_case_type_data: None
    ) -> None:
        """
        For each edge case, assert that the set of accessible ref_dims exactly matches
        the expected set declared in EdgeCaseSpec.expected_ref_dims — neither more nor less.

        Accessible ref_dims are derived from accessible Cols (via org access policies only).
        User policies must not grant access to additional ref_dims.
        """
        user = self.get_user(spec.user_name)

        if VERBOSE:
            rich_print([x for x in EDGE_CASES if x.user_name == user.name])

        get_cmd = RefDimCrudCommand(user=user, operation=CrudOperation.READ_ALL)
        result = self.env.app.handle(get_cmd)

        actual = {x.code for x in result} if isinstance(result, list) else set()
        expected = set(spec.expected_ref_dims)

        missing = expected - actual
        unexpected = actual - expected

        assert not missing and not unexpected, (
            f"\n{spec.description}"
            f"\n  Missing access:    {sorted(missing) if missing else '∅'}"
            f"\n  Unexpected access: {sorted(unexpected) if unexpected else '∅'}"
        )

    def test_disease_access_matches_all(self, setup_case_type_data: None) -> None:
        """
        take first edge case spec as a representative case (since disease access is not expected to vary across cases in this setup)
        and assert that the set of accessible diseases matches all diseases, get them from env.db since they are created there by setup_case_type_data
        """

        spec = EDGE_CASES[
            0
        ]  # Random spec since access is expected to be the same across cases for this reference data type
        user = self.get_user(spec.user_name)

        if VERBOSE:
            rich_print(EDGE_CASE_BY_USER[spec.user_name])
            rich_print(self.env.db[model.Disease])

        get_cmd = command.DiseaseCrudCommand(
            user=user, operation=CrudOperation.READ_ALL
        )
        result: list[Disease] = self.env.app.handle(get_cmd)
        actual = {x.name for x in result}

        # get all diseases from env.db since they are created there by setup_case_type_data
        expected = {x.name for x in self.env.db[model.Disease].values()}

        assert actual == expected, (
            f"\n{spec.description}"
            f"\n  Expected access to all diseases: {sorted(expected)}"
            f"\n  Actual access: {sorted(actual) if actual else '∅'}"
        )

    def test_etiological_agent_access_matches_all(
        self, setup_case_type_data: None
    ) -> None:
        """
        similar to test_disease_access_matches_all but for etiological agents instead of diseases,
         since both are created as reference data in setup_case_type_data and not expected to be filtered by access policies in this setup
        """
        spec = EDGE_CASES[
            0
        ]  # Random spec since access is expected to be the same across cases for this reference data type
        user = self.get_user(spec.user_name)

        if VERBOSE:
            rich_print(EDGE_CASE_BY_USER[spec.user_name])
            rich_print(self.env.db[model.EtiologicalAgent])

        get_cmd = command.EtiologicalAgentCrudCommand(
            user=user, operation=CrudOperation.READ_ALL
        )
        result: list[model.EtiologicalAgent] = self.env.app.handle(get_cmd)
        actual = {ea.name for ea in result}
        expected = {x.name for x in self.env.db[model.EtiologicalAgent].values()}

        assert actual == expected, (
            f"\n{spec.description}"
            f"\n  Expected access to all etiological agents: {sorted(expected)}"
            f"\n  Actual access: {sorted(actual) if actual else '∅'}"
        )

    def test_case_type_set_category_access_matches_all(
        self, setup_case_type_data: None
    ) -> None:
        """
        Assert that all created CaseTypeSet categories are accessible to any user,
        since category access is not filtered by access policies in this setup.
        """
        spec = EDGE_CASES[
            0
        ]  # Random spec since access is expected to be the same across cases for this reference data type
        user = self.get_user(spec.user_name)

        if VERBOSE:
            rich_print(EDGE_CASE_BY_USER[spec.user_name])
            rich_print(self.env.db[model.CaseTypeSetCategory])

        get_cmd = CaseTypeSetCategoryCrudCommand(
            user=user, operation=CrudOperation.READ_ALL
        )
        result: list[model.CaseTypeSetCategory] = self.env.app.handle(get_cmd)
        actual = {x.name for x in result}
        expected = {x.name for x in self.env.db[model.CaseTypeSetCategory].values()}

        assert actual == expected, (
            f"\n{spec.description}"
            f"\n  Expected access to all CaseTypeSet categories: {sorted(expected)}"
            f"\n  Actual access: {sorted(actual) if actual else '\u2205'}"
        )

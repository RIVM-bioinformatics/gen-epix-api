"""
Integration tests for model process metadata field behaviour in CaseDB.

Verifies that:
- Superusers (ROOT) receive metadata fields (created_at, modified_at, modified_by) populated.
- Regular org users have those fields masked to None by MaskModelProcessMetadataPolicy.

Uses an empty dictionary repository and the same edge-case data setup as the other
refdata access tests in this folder.


We will test on case types since they are a commonly accessed reference data type
that all users have access to, and thus a good way to verify the masking behaviour in a realistic scenario.
The test reads case types through the app layer (not directly from the db) to ensure that policies are applied.

"""

import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.refdata_access.base_empty import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.casedb.integration.setup.define_edge_cases import (
    EDGE_CASE_BY_USER,
    EDGE_CASES,
)

import pytest
from rich import print as rich_print

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.command import CaseTypeCrudCommand
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
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


@pytest.mark.integration
class TestCaseDBModelProcessMetadata:
    """
    Tests that MaskModelProcessMetadataPolicy and SetModelProcessMetadataPolicy
    are wired correctly in the CaseDB integration environment.

    Superusers bypass masking — their reads return populated metadata.
    Org users are subject to masking — their reads return None for all three fields.
    """

    @pytest.fixture(autouse=True)
    def setup(self, env: Env) -> None:
        self.env = env

    def get_user(self, user_name: str) -> model.User:
        return self.env._get_obj(model.User, user_name)  # type: ignore[return-value]

    def test_case_type_contains_metadata_for_super_users(
        self, setup_case_type_data: None
    ) -> None:
        """
        Assert that case types returned to the root user contain metadata fields
        (created_at, modified_at, modified_by), since superusers bypass masking.
        """
        root_user = self.env.get_root_user()

        result = self.env.app.handle(
            CaseTypeCrudCommand(user=root_user, operation=CrudOperation.READ_ALL)
        )

        assert isinstance(result, list)
        assert len(result) > 0, "Expected at least one case type"

        for ct in result:
            assert (
                ct.created_at is not None
            ), f"{ct.name}: created_at should not be None for root user"
            assert (
                ct.modified_at is not None
            ), f"{ct.name}: modified_at should not be None for root user"
            assert (
                ct.modified_by is not None
            ), f"{ct.name}: modified_by should not be None for root user"

    # Note: This should be different for other domains like seqdb and omopdb
    # where everybody can see the process metadata
    def test_case_type_should_not_contain_metadata_for_org_users(
        self, setup_case_type_data: None
    ) -> None:
        """
        Assert that case types returned to org users have metadata fields
        (created_at, modified_at, modified_by) nulled out by MaskModelProcessMetadataPolicy.
        """
        spec = EDGE_CASES[
            10
        ]  # An org user having access to case types through org share policy, which is a common way org users access case types. Tests the masking in a realistic scenario.

        if VERBOSE:
            rich_print(EDGE_CASE_BY_USER[spec.user_name])

        user = self.get_user(spec.user_name)

        result = self.env.app.handle(
            CaseTypeCrudCommand(user=user, operation=CrudOperation.READ_ALL)
        )

        assert isinstance(result, list)
        assert (
            len(result) > 0
        ), "Expected at least one case type accessible to this user"

        for ct in result:
            assert (
                ct.created_at is None
            ), f"{ct.name}: created_at should be masked for org user"
            assert (
                ct.modified_at is None
            ), f"{ct.name}: modified_at should be masked for org user"
            assert (
                ct.modified_by is None
            ), f"{ct.name}: modified_by should be masked for org user"
            assert (
                ct.modified_by is None
            ), f"{ct.name}: modified_by should be masked for org user"

    # Additional tests could include write tests to verify that SetModelProcessMetadataPolicy is setting the fields correctly 
    # on create/update operations, but this would require more setup to create objects and check their metadata after creation/modification. 
    # The current tests focus on the masking behaviour for reads, which is the main purpose of MaskModelProcessMetadataPolicy.

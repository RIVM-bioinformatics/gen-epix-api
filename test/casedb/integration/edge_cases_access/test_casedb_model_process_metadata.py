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
from datetime import UTC, datetime
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.edge_cases_access.setup.define_edge_cases import (
    EDGE_CASE_BY_USER,
    EDGE_CASES,
)
from test.casedb.integration.refdata_access.base_metadata import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)

import pytest
from rich import print as rich_print

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.command.case import CaseTypeCrudCommand
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp.enum import CrudOperation
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

    def test_create_case_type_without_setting_metadata_fields_should_set_metadata_fields(
        self, setup_case_type_data: None
    ) -> None:
        """
        Assert that when a case type is created without explicitly setting metadata fields,
        the SetModelProcessMetadataPolicy populates the created_at, modified_at, and modified_by fields.
        This test verifies that the policy is correctly setting these fields on creation even when they are not provided in the command.
        """
        root_user = self.env.get_root_user()

        result = self.env.create_case_type(
            root_user,
            "test casetype for metadata creation",
            "disease_1",
            "etiological_agent_1",
        )

        assert isinstance(result, model.CaseType)
        assert (
            result.created_at is not None
        ), "created_at should be set by policy on creation"
        assert (
            result.modified_at is not None
        ), "modified_at should be set by policy on creation"
        assert (
            result.modified_by == root_user.id
        ), "modified_by should be set to creating user by policy on creation"

    def test_update_case_type_should_not_override_metadata(
        self, setup_case_type_data: None
    ) -> None:
        """
        test that verifies that when a case type is updated,
        the created_at, modified_at, and modified_by fields are not updated by the mapper.
        This is to verify that the CommondbSAMapper is not allowing updates to
        these fields and that they remain unchanged after an update operation,
        which is the expected behavior since these fields should only be set
        on creation and not modified afterwards.
        Note: this test assumes that the update command is providing new values for these fields,
        but the mapper should ignore them and keep the original values in the database unchanged.
        """
        root_user = self.env.get_root_user()

        case_type = self.env.create_case_type(
            root_user, "case_type99", "disease_1", "etiological_agent_1"
        )

        old_created_at = case_type.created_at

        new_created_at = datetime(2025, 1, 1, tzinfo=UTC)
        new_modified_at = datetime(2025, 6, 1, tzinfo=UTC)

        new_modified_by = self.get_user("org_user1_1").id

        self.env.update_object(
            root_user,
            model.CaseType,
            "case_type99",
            props={
                "description": "test update",
                "created_at": new_created_at,
                "modified_at": new_modified_at,
                "modified_by": new_modified_by,
                # "created_at": None,
            },  # should be overridden by policy},
        )
        # And now retrieve the case type to check the metadata fields

        result = self.env.app.handle(
            CaseTypeCrudCommand(
                user=root_user, operation=CrudOperation.READ_ONE, obj_ids=case_type.id
            )
        )
        assert isinstance(result, model.CaseType)

        if VERBOSE:
            print("old_created_at:", old_created_at)
            print("old_modified_at:", case_type.modified_at)
            print("old_modified_by:", case_type.modified_by)
            print("new_created_at provided in update command:", new_created_at)
            print("new_modified_at provided in update command:", new_modified_at)
            print("new_modified_by provided in update command:", new_modified_by)
            print(f"result.created_at: {result.created_at}")
            print(f"result.modified_at: {result.modified_at}")
            print(f"result.modified_by: {result.modified_by}")

        assert (
            result.created_at == old_created_at
        ), "created_at should not be changed on update"
        assert (
            result.modified_at != new_modified_at
        ), "modified_at should not be updated to the new value provided in the update command"
        assert (
            result.modified_by == root_user.id
        ), "modified_by should be updated to the root user since they are performing the update"

    def test_read_all_case_type_contains_metadata_for_super_users(
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
    def test_read_all_case_type_should_not_contain_metadata_for_org_users(
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

"""Integration test for the delete-all-except-users-and-organizations command."""

import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.test_client.enum import (
    EnumTestType as EnumTestType,  # to avoid PyTest warning
)

import pytest

from gen_epix.casedb.domain import command, enum
from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.commondb.test.util import set_log_level
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum

TEST_TYPE = EnumTestType.CASEDB_INTEGRATION_CONTENT

SKIP_ENDPOINTS = True
VERBOSE = False
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.DICT_DEMO

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
    log_any=VERBOSE,
)
CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
    log_any=VERBOSE,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    """Create a casedb client backed by the demo dictionary repository."""
    set_log_level("seqdb", logging.ERROR)
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


class TestDeleteRefData:
    """Exercise DeleteAllRefDataCommand against seeded demo content."""

    def _read_all(self, env: Env, crud_command_class: type, user: object) -> list:
        return env.handle(
            crud_command_class(user=user, operation=CrudOperation.READ_ALL)
        )

    def test_delete_all_ref_data_preserves_users_and_organizations(
        self, env: Env
    ) -> None:
        """Deletes all domain data while preserving users and organizations."""
        root_user = env.get_root_user()

        # Demo repository is expected to contain domain data and backbone data.
        users_before = self._read_all(env, command.UserCrudCommand, root_user)
        orgs_before = self._read_all(env, command.OrganizationCrudCommand, root_user)
        assert users_before, "expected demo users to exist before deletion"
        assert orgs_before, "expected demo organizations to exist before deletion"
        assert self._read_all(
            env, command.CaseTypeCrudCommand, root_user
        ), "expected demo case types (reference data) to exist before deletion"

        ops_result = env.handle(command.DeleteAllOperationalDataCommand(user=root_user))
        assert ops_result.success, ops_result.details

        result = env.handle(command.DeleteAllRefDataCommand(user=root_user))

        assert result.success, {
            key: value[:300]
            for key, value in result.details.items()
            if isinstance(value, str)
        }

        # Backbone data preserved.
        users_after = self._read_all(env, command.UserCrudCommand, root_user)
        orgs_after = self._read_all(env, command.OrganizationCrudCommand, root_user)
        assert {u.id for u in users_after} == {u.id for u in users_before}
        assert {o.id for o in orgs_after} == {o.id for o in orgs_before}

        # Domain and reference data deleted.
        assert self._read_all(env, command.CaseCrudCommand, root_user) == []
        assert self._read_all(env, command.CaseSetCrudCommand, root_user) == []
        assert self._read_all(env, command.CaseTypeCrudCommand, root_user) == []
        assert self._read_all(env, command.DiseaseCrudCommand, root_user) == []
        assert self._read_all(env, command.RegionCrudCommand, root_user) == []

        # Users and organizations were never reported in the deletion details.
        assert "user" not in result.details
        assert "organization" not in result.details

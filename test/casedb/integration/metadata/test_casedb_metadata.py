"""
Integration tests for metadata field stamping (created_at, modified_at, modified_by)
in CaseDB on create and update operations.

Parametrized for both the SQLite and dictionary backends.
Uses CaseType as the test model (requires Disease + EtiologicalAgent dependencies,
but no user policies — root can create freely).
"""

import copy
import datetime
import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.test_client.enum import TestType
from test.test_client.pytest_params import BuildDbParams

import pytest

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.command.case import CaseTypeCrudCommand
from gen_epix.commondb.domain import enum as commondb_enum
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum

TEST_TYPE = TestType.CASEDB_INTEGRATION_METADATA

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

_PARAMS = [
    BuildDbParams(
        skip_endpoints=True,
        dev_repository_config=commondb_enum.DevRepositoryConfig.SA_SQLITE_EMPTY,
    ),
    BuildDbParams(
        skip_endpoints=True,
        dev_repository_config=commondb_enum.DevRepositoryConfig.DICT_EMPTY,
    ),
]


@pytest.fixture(
    scope="module",
    name="env",
    params=_PARAMS,
    ids=[p.id for p in _PARAMS],
)
def get_test_client(request) -> Env:
    params: BuildDbParams = request.param
    cfg_key = f"{TEST_TYPE.value}__{params.dev_repository_config.value}"
    app_cfg = copy.copy(CASEDB_APP_CFGS[cfg_key])
    app_cfg._name = f"{TEST_TYPE.value}__{params.id}"
    app_cfg.cfg["service"]["seqdb"]["props"]["seqdb_local_app"]["app_cfg"] = (
        SEQDB_APP_CFGS[cfg_key]
    )
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=app_cfg,
        verbose=False,
        log_level=logging.ERROR,
        use_endpoints=not params.skip_endpoints,
    )


@pytest.fixture(scope="module", autouse=True)
def setup_reference_data(env: Env) -> None:
    """Register root1_1 + org1, invite root1_2, and create minimum CaseType dependencies."""
    root_user = env.get_root_user()
    root_user.name = "root1_1"
    env._set_obj(root_user)  # noqa: SLF001

    org1 = env.read_one_by_property(root_user, model.Organization, "name", "org1")
    env._set_obj(org1)  # noqa: SLF001

    env.invite_and_register_user("root1_1", "root1_2")

    env.create_disease(root_user, "disease_1")
    env.create_etiological_agent(root_user, "etiological_agent_1")


@pytest.mark.integration
class TestCasedbModelProcessMetadata:
    """
    Verifies that the CommondbSAMapper (SA backend) and CommondbDictModelModifier
    (dict backend) correctly stamp metadata fields on CaseType create and update.
    """

    @pytest.fixture(autouse=True)
    def setup(self, env: Env) -> None:
        self.env = env

    # ------------------------------------------------------------------ create

    def test_create_case_type_stamps_all_metadata(self) -> None:
        """created_at, modified_at, and modified_by must all be set by the backend on creation."""
        root_user = self.env.get_root_user()

        result = self.env.create_case_type(
            root_user, "ct_meta_create_1", "disease_1", "etiological_agent_1"
        )

        assert isinstance(result, model.CaseType)
        assert result.created_at is not None, "created_at should be set on creation"
        assert result.modified_at is not None, "modified_at should be set on creation"
        assert (
            result.modified_by == root_user.id
        ), "modified_by should be set to the creating user"

    # ------------------------------------------------------------------ update

    def test_update_case_type_preserves_created_at(self) -> None:
        """created_at must not change when a record is updated."""
        root_user = self.env.get_root_user()

        created = self.env.create_case_type(
            root_user, "ct_meta_update_1", "disease_1", "etiological_agent_1"
        )
        original_created_at = created.created_at

        self.env.update_object(
            root_user,
            model.CaseType,
            "ct_meta_update_1",
            {
                "description": "updated",
                "created_at": datetime.datetime(
                    2000, 1, 1, tzinfo=datetime.timezone.utc
                ),
            },
        )

        result = self.env.app.handle(
            CaseTypeCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ONE,
                obj_ids=created.id,
            )
        )

        assert isinstance(result, model.CaseType)
        assert (
            result.created_at == original_created_at
        ), "created_at must not be overwritten on update"

    def test_update_case_type_does_not_accept_arbitrary_modified_at(self) -> None:
        """modified_at supplied in the update payload must be ignored by the backend."""
        root_user = self.env.get_root_user()

        created = self.env.create_case_type(
            root_user, "ct_meta_update_2", "disease_1", "etiological_agent_1"
        )
        arbitrary_modified_at = datetime.datetime(
            2000, 6, 1, tzinfo=datetime.timezone.utc
        )

        self.env.update_object(
            root_user,
            model.CaseType,
            "ct_meta_update_2",
            {
                "description": "updated",
                "modified_at": arbitrary_modified_at,
            },
        )

        result = self.env.app.handle(
            CaseTypeCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ONE,
                obj_ids=created.id,
            )
        )

        assert isinstance(result, model.CaseType)
        assert (
            result.modified_at != arbitrary_modified_at
        ), "modified_at should not be set to the arbitrary value supplied in the update"

    def test_update_case_type_updates_modified_by(self) -> None:
        """modified_by must be stamped with the updating user, not the creating user."""
        root_user = self.env.get_root_user()
        root2: model.User = self.env._get_obj(model.User, "root1_2")  # type: ignore[assignment]
        assert root_user.id != root2.id, "test requires two distinct users"

        self.env.create_case_type(
            root_user, "ct_meta_update_3", "disease_1", "etiological_agent_1"
        )

        self.env.update_object(
            root2,
            model.CaseType,
            "ct_meta_update_3",
            {"description": "changed by root2"},
        )

        result = self.env.app.handle(
            CaseTypeCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ONE,
                obj_ids=self.env._get_obj(model.CaseType, "ct_meta_update_3").id,
            )
        )

        assert isinstance(result, model.CaseType)
        assert (
            result.modified_by == root2.id
        ), "modified_by should be set to the user who performed the update, not the creator"

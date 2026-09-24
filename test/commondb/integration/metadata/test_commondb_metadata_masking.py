"""
Integration tests for metadata field visibility in commondb.

Verifies that created_at, modified_at, and modified_by are visible to ALL users
(root and org users alike) when reading DataCollections, because commondb does
not register MaskModelProcessMetadataPolicy — unlike casedb.

Parametrized for both the SQLite and dictionary backends.
"""

import copy
import logging
from test.commondb.test_client.util import get_test_client as commondb_get_test_client
from test.test_client.enum import EnumTestType
from test.test_client.pytest_params import BuildDbParams

import pytest

from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.commondb.test.test_client import TestClient as Env
from gen_epix.fastapp.enum import CrudOperation

COMMONDB_TEST_TYPE = EnumTestType.COMMONDB_INTEGRATION_METADATA_MASKING

APP_CFGS = get_app_cfgs(
    AppType.COMMONDB,
    enum.ServiceType,
    enum.RepositoryType,
    COMMONDB_TEST_TYPE,
    log_any=False,
)

_PARAMS = [
    BuildDbParams(
        skip_endpoints=True,
        dev_repository_config=enum.DevRepositoryConfig.SA_SQLITE_EMPTY,
    ),
    BuildDbParams(
        skip_endpoints=True,
        dev_repository_config=enum.DevRepositoryConfig.DICT_EMPTY,
    ),
]

ALL_USERS_NO_GUEST = [
    "root1_1",
    "app_admin1_1",
    "refdata_admin1_1",
    "org_admin1_1",
    "org_user1_1",
]

APP_ADMIN_OR_ABOVE_USERS = [
    "root1_1",
    "app_admin1_1",
]


@pytest.fixture(
    scope="module",
    name="env",
    params=_PARAMS,
    ids=[p.id for p in _PARAMS],
)
def get_test_client(request: pytest.FixtureRequest) -> Env:
    params: BuildDbParams = request.param
    app_cfg = copy.copy(
        APP_CFGS[f"{COMMONDB_TEST_TYPE.value}__{params.dev_repository_config.value}"]
    )
    app_cfg._name = f"{COMMONDB_TEST_TYPE.value}__{params.id}"
    return commondb_get_test_client(
        test_type=COMMONDB_TEST_TYPE.value,
        app_cfg=app_cfg,
        verbose=False,
        log_level=logging.ERROR,
        use_endpoints=not params.skip_endpoints,
    )


@pytest.fixture(scope="module", autouse=True)
def setup_users(env: Env) -> None:
    """Register root1_1 + org1, then invite an org_user and an org_admin."""
    user: model.User = env.retrieve_user_by_key("root1_1@org1.org")  # type: ignore[assignment]
    user.name = "root1_1"
    env.set_obj(user)
    env.set_obj(env.read_one_by_property("root1_1", model.Organization, "name", "org1"))
    env.invite_and_register_user("root1_1", "app_admin1_1")
    env.invite_and_register_user("root1_1", "refdata_admin1_1")
    env.invite_and_register_user("root1_1", "org_user1_1")
    env.invite_and_register_user("root1_1", "org_admin1_1")


@pytest.mark.integration
@pytest.mark.scenario_ids("TC-MET-01-01")
class TestCommondbMetadataMasking:
    """
    Verifies that commondb does NOT mask metadata fields for any user role.

    In casedb, MaskModelProcessMetadataPolicy hides created_at / modified_at /
    modified_by from org users.  commondb never registers that policy, so root
    users, org admins, and org users should all see populated metadata values.
    """

    @pytest.fixture(autouse=True)
    def setup(self, env: Env) -> None:
        self.env = env

    def _read_all_data_collections(
        self, user: model.User
    ) -> list[model.DataCollection]:
        result = self.env.app.handle(
            command.DataCollectionCrudCommand(
                user=user,
                operation=CrudOperation.READ_ALL,
            )
        )
        assert isinstance(result, list)
        return result  # type: ignore[return-value]

    # ------------------------------------------------------------------ root user

    def test_read_all_data_collections(self) -> None:
        """Only APP_ADMIN or ROOT users can see created_at, modified_at, and modified_by, otherwise they are masked as None"""
        self.env.create_data_collection("root1_1", f"data_collection1")
        for user_str in ALL_USERS_NO_GUEST:
            user: model.User = self.env.get_obj(model.User, user_str)  # type: ignore[assignment]
            read_data_collections = self._read_all_data_collections(user)
            is_masked = user_str not in APP_ADMIN_OR_ABOVE_USERS
            assert (
                len(read_data_collections) > 0
            ), "Expected at least one DataCollection"
            for data_collection in read_data_collections:
                assert (
                    data_collection.created_at is None
                ) == is_masked, f"{data_collection.name}: created_at should {'be None' if is_masked else 'not be None'} for {user_str}"
                assert (
                    data_collection.modified_at is None
                ) == is_masked, f"{data_collection.name}: modified_at should {'be None' if is_masked else 'not be None'} for {user_str}"
                assert (
                    data_collection.modified_by is None
                ) == is_masked, f"{data_collection.name}: modified_by should {'be None' if is_masked else 'not be None'} for {user_str}"

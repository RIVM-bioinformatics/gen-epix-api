"""
Integration tests for metadata field visibility in CommonDB.

Verifies that created_at, modified_at, and modified_by are visible to ALL users
(root and org users alike) when reading DataCollections, because CommonDB does
not register MaskModelProcessMetadataPolicy — unlike CaseDB.

Parametrized for both the SQLite and dictionary backends.
"""

import copy
import logging
from test.commondb.test_client.util import get_test_client as commondb_get_test_client
from test.test_client.enum import TestType
from test.test_client.pytest_params import BuildDbParams

import pytest

from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.commondb.test.test_client import TestClient as Env
from gen_epix.fastapp.enum import CrudOperation

TEST_TYPE = TestType.COMMONDB_INTEGRATION_METADATA_MASKING

APP_CFGS = get_app_cfgs(
    AppType.COMMONDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
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


@pytest.fixture(
    scope="module",
    name="env",
    params=_PARAMS,
    ids=[p.id for p in _PARAMS],
)
def get_test_client(request) -> Env:
    params: BuildDbParams = request.param
    app_cfg = copy.copy(
        APP_CFGS[f"{TEST_TYPE.value}__{params.dev_repository_config.value}"]
    )
    app_cfg._name = f"{TEST_TYPE.value}__{params.id}"
    return commondb_get_test_client(
        test_type=TEST_TYPE.value,
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
    env._set_obj(user)
    env._set_obj(
        env.read_one_by_property("root1_1", model.Organization, "name", "org1")
    )
    env.invite_and_register_user("root1_1", "org_user1_1")
    env.invite_and_register_user("root1_1", "org_admin1_1")


@pytest.mark.integration
class TestCommondbMetadataMasking:
    """
    Verifies that CommonDB does NOT mask metadata fields for any user role.

    In CaseDB, MaskModelProcessMetadataPolicy hides created_at / modified_at /
    modified_by from org users.  CommonDB never registers that policy, so root
    users, org admins, and org users should all see populated metadata values.
    """

    @pytest.fixture(autouse=True)
    def setup(self, env: Env) -> None:
        self.env = env

    def _read_all_data_collections(self, user: model.User) -> list[model.DataCollection]:
        result = self.env.app.handle(
            command.DataCollectionCrudCommand(
                user=user,
                operation=CrudOperation.READ_ALL,
            )
        )
        assert isinstance(result, list)
        return result  # type: ignore[return-value]

    # ------------------------------------------------------------------ root user

    def test_read_all_data_collections_root_user_sees_all_metadata(self) -> None:
        """Root user must see all three metadata fields populated on every DataCollection."""
        root_user = self.env.get_root_user()
        self.env.create_data_collection(root_user, "dc_mask_root_1")

        result = self._read_all_data_collections(root_user)

        assert len(result) > 0, "Expected at least one DataCollection"
        for dc in result:
            assert dc.created_at is not None, f"{dc.name}: created_at should not be None for root user"
            assert dc.modified_at is not None, f"{dc.name}: modified_at should not be None for root user"
            assert dc.modified_by is not None, f"{dc.name}: modified_by should not be None for root user"

    # ------------------------------------------------------------------ org user

    def test_read_all_data_collections_org_user_sees_all_metadata(self) -> None:
        """Org user must see all three metadata fields populated — CommonDB applies no masking policy."""
        root_user = self.env.get_root_user()
        org_user: model.User = self.env._get_obj(model.User, "org_user1_1")  # type: ignore[assignment]
        self.env.create_data_collection(root_user, "dc_mask_org_user_1")

        result = self._read_all_data_collections(org_user)

        assert len(result) > 0, "Expected at least one DataCollection visible to org_user1_1"
        for dc in result:
            assert dc.created_at is not None, f"{dc.name}: created_at should not be masked for org user in commondb"
            assert dc.modified_at is not None, f"{dc.name}: modified_at should not be masked for org user in commondb"
            assert dc.modified_by is not None, f"{dc.name}: modified_by should not be masked for org user in commondb"

    # ------------------------------------------------------------------ org admin

    def test_read_all_data_collections_org_admin_sees_all_metadata(self) -> None:
        """Org admin must see all three metadata fields populated — CommonDB applies no masking policy."""
        root_user = self.env.get_root_user()
        org_admin: model.User = self.env._get_obj(model.User, "org_admin1_1")  # type: ignore[assignment]
        self.env.create_data_collection(root_user, "dc_mask_org_admin_1")

        result = self._read_all_data_collections(org_admin)

        assert len(result) > 0, "Expected at least one DataCollection visible to org_admin1_1"
        for dc in result:
            assert dc.created_at is not None, f"{dc.name}: created_at should not be masked for org admin in commondb"
            assert dc.modified_at is not None, f"{dc.name}: modified_at should not be masked for org admin in commondb"
            assert dc.modified_by is not None, f"{dc.name}: modified_by should not be masked for org admin in commondb"

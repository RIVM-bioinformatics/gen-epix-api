"""
Integration tests for model process metadata field behaviour in commondb.

Verifies that created_at, modified_at, and modified_by are correctly stamped
on creation and correctly preserved / updated on update, for both the
dictionary backend and the SQLite backend.

Uses DataCollection as a test model because it has no foreign-key dependencies
and can therefore be created with only a root user present.
"""

import copy
import datetime
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

TEST_TYPE = EnumTestType.COMMONDB_INTEGRATION_METADATA

APP_CFGS = get_app_cfgs(
    AppType.COMMONDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
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
    """Register root1_1 + org1, then invite root1_2 so tests have two distinct users."""
    user: model.User = env.retrieve_user_by_key("root1_1@org1.org")  # type: ignore[assignment]
    user.name = "root1_1"
    env.set_obj(user)
    env.set_obj(env.read_one_by_property("root1_1", model.Organization, "name", "org1"))
    env.invite_and_register_user("root1_1", "root1_2")


@pytest.mark.integration
@pytest.mark.scenario_ids("TC-MET-01-01")
class TestCommondbModelProcessMetadata:
    """
    Verifies that the CommondbSAMapper (SA backend) and CommondbDictModelModifier
    (dict backend) correctly stamp metadata fields on create and update.

    No masking policy is registered for commondb, so root always sees the raw values.
    """

    @pytest.fixture(autouse=True)
    def setup(self, env: Env) -> None:
        self.env = env

    # ------------------------------------------------------------------ create

    def test_create_data_collection_stamps_created_at(self) -> None:
        """created_at must be set by the backend on creation."""
        root_user = self.env.get_root_user()

        result = self.env.create_data_collection(root_user, "dc_meta_create_1")

        assert isinstance(result, model.DataCollection)
        assert result.created_at is not None, "created_at should be set on creation"

    def test_create_data_collection_stamps_modified_at(self) -> None:
        """modified_at must be set by the backend on creation."""
        root_user = self.env.get_root_user()

        result = self.env.create_data_collection(root_user, "dc_meta_create_2")

        assert isinstance(result, model.DataCollection)
        assert result.modified_at is not None, "modified_at should be set on creation"

    def test_create_data_collection_stamps_modified_by(self) -> None:
        """modified_by must be set to the creating user's id."""
        root_user = self.env.get_root_user()

        result = self.env.create_data_collection(root_user, "dc_meta_create_3")

        assert isinstance(result, model.DataCollection)
        assert (
            result.modified_by == root_user.id
        ), "modified_by should be set to the creating user"

    # ------------------------------------------------------------------ update

    def test_update_data_collection_preserves_created_at(self) -> None:
        """created_at must not change when a record is updated."""
        root_user = self.env.get_root_user()

        created = self.env.create_data_collection(root_user, "dc_meta_update_1")
        original_created_at = created.created_at

        # Attempt to overwrite created_at with an arbitrary past date
        self.env.update_object(
            root_user,
            model.DataCollection,
            "dc_meta_update_1",
            {
                "description": "updated",
                "created_at": datetime.datetime(
                    2000, 1, 1, tzinfo=datetime.timezone.utc
                ),
            },
        )

        result = self.env.app.handle(
            command.DataCollectionCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ONE,
                obj_ids=created.id,
            )
        )

        assert isinstance(result, model.DataCollection)
        assert (
            result.created_at == original_created_at
        ), "created_at must not be overwritten on update"

    def test_update_data_collection_updates_modified_by(self) -> None:
        """modified_by must be stamped with the updating user, not the creating user."""
        root1 = self.env.get_root_user()
        root2: model.User = self.env.get_obj(model.User, "root1_2")  # type: ignore[assignment]
        assert root1.id != root2.id, "test requires two distinct users"

        self.env.create_data_collection(root1, "dc_meta_update_2")

        self.env.update_object(
            root2,
            model.DataCollection,
            "dc_meta_update_2",
            {"description": "changed"},
        )

        result = self.env.app.handle(
            command.DataCollectionCrudCommand(
                user=root1,
                operation=CrudOperation.READ_ONE,
                obj_ids=self.env.get_obj(model.DataCollection, "dc_meta_update_2").id,
            )
        )

        assert isinstance(result, model.DataCollection)
        assert (
            result.modified_by == root2.id
        ), "modified_by should be set to the user who performed the update, not the creator"

    def test_update_data_collection_does_not_accept_arbitrary_modified_at(
        self,
    ) -> None:
        """modified_at supplied in the update payload must be ignored by the backend."""
        root_user = self.env.get_root_user()

        self.env.create_data_collection(root_user, "dc_meta_update_3")

        arbitrary_modified_at = datetime.datetime(
            2000, 6, 1, tzinfo=datetime.timezone.utc
        )

        self.env.update_object(
            root_user,
            model.DataCollection,
            "dc_meta_update_3",
            {
                "description": "changed",
                "modified_at": arbitrary_modified_at,
            },
        )

        result = self.env.app.handle(
            command.DataCollectionCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ONE,
                obj_ids=self.env.get_obj(model.DataCollection, "dc_meta_update_3").id,
            )
        )

        assert isinstance(result, model.DataCollection)
        assert (
            result.modified_at != arbitrary_modified_at
        ), "modified_at should not be set to the arbitrary value supplied in the update"

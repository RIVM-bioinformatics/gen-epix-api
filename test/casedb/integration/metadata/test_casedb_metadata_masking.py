"""
Integration tests for metadata field masking in casedb.

Verifies that created_at, modified_at, and modified_by are:
- visible to root users (superusers bypass MaskModelProcessMetadataPolicy)
- masked to None for org admins and org users (MaskModelProcessMetadataPolicy applies)

Uses CaseType as the test model. A minimal org access policy is created so that
org_admin1_1 and org_user1_1 can read case types (required to have results to assert on).

Parametrized for both the SQLite and dictionary backends.
"""

import copy
import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.test_client.enum import EnumTestType
from test.test_client.pytest_params import BuildDbParams

import pytest

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.domain.command.case import CaseTypeCrudCommand
from gen_epix.commondb.domain import enum as commondb_enum
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum

TEST_TYPE = EnumTestType.CASEDB_INTEGRATION_METADATA_MASKING

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
def setup_users_and_data(env: Env) -> None:
    """
    Minimal setup: root + org1 (from bootstrap), invite org_admin and org_user,
    create one CaseType with an org access policy so non-root users can read it.
    """
    root_user = env.get_root_user()
    root_user.name = "root1_1"
    env.set_obj(root_user)  # noqa: SLF001

    org1 = env.read_one_by_property(root_user, model.Organization, "name", "org1")
    env.set_obj(org1)  # noqa: SLF001

    env.invite_and_register_user("root1_1", "org_admin1_1")
    env.invite_and_register_user("root1_1", "org_user1_1")

    env.create_disease(root_user, "disease_1")
    env.create_etiological_agent(root_user, "etiological_agent_1")
    env.create_case_type_set_category(root_user, "category_1", 0)
    env.create_case_type(
        root_user, "case_type_mask_1", "disease_1", "etiological_agent_1"
    )
    env.create_case_type_set(
        root_user, "case_type_set_1", {"case_type_mask_1"}, "category_1"
    )
    env.create_data_collection(root_user, "data_collection1")
    # org_access_policy1_1: org1 gets access to case_type_set_1 in data_collection1
    env.create_organization_access_case_policy(
        root_user, "org_access_policy1_1", "case_type_set_1"
    )


@pytest.mark.integration
class TestCasedbMetadataMasking:
    """
    Verifies that MaskModelProcessMetadataPolicy is correctly wired in casedb.

    Root users bypass masking and see populated metadata.
    Org admins and org users are subject to masking and see None for all three fields.
    """

    @pytest.fixture(autouse=True)
    def setup(self, env: Env) -> None:
        self.env = env

    def _read_all_case_types(self, user: model.User) -> list[model.CaseType]:
        result = self.env.app.handle(
            CaseTypeCrudCommand(user=user, operation=CrudOperation.READ_ALL)
        )
        assert isinstance(result, list)
        return result  # type: ignore[return-value]

    # ------------------------------------------------------------------ root user

    def test_read_all_case_types_root_user_sees_all_metadata(self) -> None:
        """Root user must see all three metadata fields populated — superusers bypass masking."""
        root_user = self.env.get_root_user()

        result = self._read_all_case_types(root_user)

        assert len(result) > 0, "Expected at least one CaseType"
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

    # ------------------------------------------------------------------ org admin

    def test_read_all_case_types_org_admin_does_not_see_masked_metadata(self) -> None:
        """Org admin must see all three metadata fields masked to None by MaskModelProcessMetadataPolicy."""
        org_admin: model.User = self.env.get_obj(model.User, "org_admin1_1")  # type: ignore[assignment]

        result = self._read_all_case_types(org_admin)

        assert (
            len(result) > 0
        ), "Expected at least one CaseType accessible to org_admin1_1"
        for ct in result:
            assert (
                ct.created_at is None
            ), f"{ct.name}: created_at should be masked for org admin"
            assert (
                ct.modified_at is None
            ), f"{ct.name}: modified_at should be masked for org admin"
            assert (
                ct.modified_by is None
            ), f"{ct.name}: modified_by should be masked for org admin"

    # ------------------------------------------------------------------ org user

    def test_read_all_case_types_org_user_does_not_see_masked_metadata(self) -> None:
        """Org user must see all three metadata fields masked to None by MaskModelProcessMetadataPolicy."""
        org_user: model.User = self.env.get_obj(model.User, "org_user1_1")  # type: ignore[assignment]

        result = self._read_all_case_types(org_user)

        assert (
            len(result) > 0
        ), "Expected at least one CaseType accessible to org_user1_1"
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

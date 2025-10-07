import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.build_db.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    VERBOSE,
)

# Import test classes in order of dependency of execution
from test.casedb.integration.build_db.create import TestCreate as ModuleTestCreate
from test.casedb.integration.build_db.delete import TestDelete as ModuleTestDelete
from test.casedb.integration.build_db.read import TestRead as ModuleTestRead
from test.casedb.integration.build_db.update import TestUpdate as ModuleTestUpdate
from test.test_client.enum import TestType as EnumTestType

import pytest

from gen_epix.casedb.domain import enum
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
from gen_epix.commondb.util import set_env_variables
from gen_epix.seqdb.domain import enum as seqdb_enum

APP_CFGS: dict[str, AppCfg] = {}
SEQDB_APP_CFGS: dict[str, AppCfg] = {}
for dev_repository_config in DevRepositoryConfig:
    name = f"{EnumTestType.CASEDB_INTEGRATION_BUILD_DB}_{dev_repository_config.value}"
    set_env_variables(AppType.CASEDB, DevIdpConfig.NONE, dev_repository_config)
    APP_CFGS[name] = AppCfg(
        AppType.CASEDB,
        enum.ServiceType,
        enum.RepositoryType,
        name=name,
        log_setup=False,
    )
    SEQDB_APP_CFGS[name] = AppCfg(
        AppType.SEQDB,
        seqdb_enum.ServiceType,
        seqdb_enum.RepositoryType,
        name=name,
        log_setup=False,
    )
    # Add seqdb app_cfg to casedb app_cfg for seqdb service local app so that when the latter is instantiated, it can directly use this app_cfg without risk of having seqdb env variables being altered in the meantime
    APP_CFGS[name].cfg["service"]["seqdb"]["props"]["seqdb_local_app"]["app_cfg"] = (
        SEQDB_APP_CFGS[name]
    )


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=EnumTestType.CASEDB_INTEGRATION_BUILD_DB.value,
        app_cfg=APP_CFGS[
            f"{EnumTestType.CASEDB_INTEGRATION_BUILD_DB}_{DEV_REPOSITORY_CONFIG.value}"
        ],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


@pytest.mark.dependency()
class TestCreate(ModuleTestCreate):
    pass


@pytest.mark.dependency(depends=["TestCreate::test_create_user_first_root"])
class TestRead(ModuleTestRead):
    pass


@pytest.mark.dependency(depends=["TestRead::test_read_user"])
class TestUpdate(ModuleTestUpdate):
    pass


@pytest.mark.dependency(depends=["TestUpdate::test_update_user"])
class TestDelete(ModuleTestDelete):
    pass

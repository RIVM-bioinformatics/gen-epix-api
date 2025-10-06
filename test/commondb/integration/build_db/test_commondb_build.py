import logging
from test.commondb.integration.build_db.base import (  # REPOSITORY_TYPE,
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    VERBOSE,
)

# Import test classes in order of dependency of execution
from test.commondb.integration.build_db.create import TestCreate as ModuleTestCreate
from test.commondb.integration.build_db.delete import TestDelete as ModuleTestDelete
from test.commondb.integration.build_db.read import TestRead as ModuleTestRead
from test.commondb.integration.build_db.update import TestUpdate as ModuleTestUpdate
from test.commondb.test_client.util import get_test_client as commondb_get_test_client
from test.test_client.enum import TestType as EnumTestType

import pytest

from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain import enum
from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
from gen_epix.commondb.test.test_client import TestClient as Env
from gen_epix.commondb.util import set_env_variables

APP_CFGS: dict[str, AppCfg] = {}
for dev_repository_config in DevRepositoryConfig:
    name = f"{EnumTestType.COMMONDB_INTEGRATION_BUILD_DB}_{dev_repository_config}"
    set_env_variables(AppType.COMMONDB, DevIdpConfig.MOCK, dev_repository_config)
    APP_CFGS[name] = AppCfg(
        AppType.COMMONDB,
        enum.ServiceType,
        enum.RepositoryType,
        name=name,
        setup_logger_level=logging.WARNING,
    )


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return commondb_get_test_client(
        test_type=EnumTestType.COMMONDB_INTEGRATION_BUILD_DB.value,
        app_cfg=APP_CFGS[
            f"{EnumTestType.COMMONDB_INTEGRATION_BUILD_DB}_{DEV_REPOSITORY_CONFIG}"
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

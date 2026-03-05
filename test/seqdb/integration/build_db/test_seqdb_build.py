import logging
from test.seqdb.integration.build_db.base import (  # REPOSITORY_TYPE,
    DEV_REPOSITORY_CONFIG, SKIP_ENDPOINTS, TEST_TYPE, VERBOSE)
# Import test classes in order of dependency of execution
from test.seqdb.integration.build_db.create import \
    TestCreate as ModuleTestCreate
from test.seqdb.integration.build_db.delete import \
    TestDelete as ModuleTestDelete
from test.seqdb.integration.build_db.read import TestRead as ModuleTestRead
from test.seqdb.integration.build_db.update import \
    TestUpdate as ModuleTestUpdate
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env

import pytest

from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.seqdb.domain import enum

APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
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

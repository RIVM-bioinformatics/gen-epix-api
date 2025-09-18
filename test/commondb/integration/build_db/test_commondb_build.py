import logging
from test.commondb.integration.build_db.base import (
    REPOSITORY_TYPE,
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

from gen_epix.commondb.test.test_client import TestClient as Env


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return commondb_get_test_client(
        test_name=EnumTestType.COMMONDB_INTEGRATION_BUILD_DB.value,
        repository_type=REPOSITORY_TYPE,
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
        data_fixture_name="EMPTY",
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

import logging
from test.common.integration.build_db.base import (
    REPOSITORY_TYPE,
    SKIP_ENDPOINTS,
    VERBOSE,
)
from test.common.integration.build_db.create import TestCreate as ModuleTestCreate
from test.test_client.enum import TestType as EnumTestType

import pytest

from gen_epix.common.test.test_client_old import CommonServiceTestClient as Env

# Very basic first setup of the common build_db tests
# get_test_client() changed in the meantime, so probably rewrite needed


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(
        test_type=EnumTestType.CASEDB_INTEGRATION_BUILD_DB,
        repository_type=REPOSITORY_TYPE,
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
        load_target="EMPTY",
    )


@pytest.mark.dependency()
class TestCreate(ModuleTestCreate):
    pass

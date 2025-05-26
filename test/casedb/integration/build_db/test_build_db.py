import logging
from test.casedb.casedb_service_test_client import CasedbServiceTestClient as Env
from test.casedb.integration.build_db.base import (
    REPOSITORY_TYPE,
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


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(
        test_type=EnumTestType.CASEDB_INTEGRATION_BUILD_DB,
        repository_type=REPOSITORY_TYPE,
        # repository_type=enum.RepositoryType.SA_SQLITE,
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
        load_target="EMPTY",
    )
    # return Env.get_env(test_type=EnumTestType.INTEGRATION_BUILD_DB, repository_type=enum.RepositoryType.SA_SQLITE, verbose=False, log_level=logging.ERROR)


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

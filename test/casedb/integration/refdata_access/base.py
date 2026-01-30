from test.test_client.enum import TestType

# Variables for debugging purposes
from gen_epix.commondb.domain.enum import DevRepositoryConfig

TEST_TYPE = TestType.CASEDB_INTEGRATION_REFDATA_ACCESS

SKIP_ENDPOINTS = False  # False (i.e. using endpoints) does not work with SA_SQLITE due to multi-threading issue
SKIP_RAISE = False
SKIP_CREATE_DATA = False
VERBOSE = False
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.DICT_DEMO
# DEV_REPOSITORY_CONFIG = DevRepositoryConfig.SA_SQLITE_DEMO

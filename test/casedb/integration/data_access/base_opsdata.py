from test.test_client.enum import TestType

# Variables for debugging purposes
from gen_epix.commondb.domain.enum import DevRepositoryConfig

TEST_TYPE = TestType.CASEDB_INTEGRATION_CASE_ACCESS_EDGE_CASES

SKIP_ENDPOINTS = True
SKIP_RAISE = False
SKIP_CREATE_DATA = False
VERBOSE = False
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.DICT_EMPTY
# DEV_REPOSITORY_CONFIG = DevRepositoryConfig.SA_SQLITE_EMPTY

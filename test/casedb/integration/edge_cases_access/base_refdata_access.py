from test.test_client.enum import TestType

# Variables for debugging purposes
from gen_epix.commondb.domain.enum import DevRepositoryConfig

TEST_TYPE = TestType.CASEDB_INTEGRATION_REFDATA_ACCESS

SKIP_ENDPOINTS = True  # False (i.e. using endpoints) does not work with SA_SQLITE due to multi-threading issue
SKIP_RAISE = False
SKIP_CREATE_DATA = False
VERBOSE = False
# Note: switch here
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.DICT_EMPTY
# DEV_REPOSITORY_CONFIG = DevRepositoryConfig.SA_SQLITE_EMPTY

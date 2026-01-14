from test.test_client.enum import TestType

# Variables for debugging purposes
from gen_epix.commondb.domain.enum import DevRepositoryConfig

TEST_TYPE = TestType.CASEDB_INTEGRATION_CASE_VALIDATION

SKIP_ENDPOINTS = False
SKIP_RAISE = False
SKIP_CREATE_DATA = False
VERBOSE = False
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.DICT_EMPTY
# DEV_REPOSITORY_CONFIG = DevRepositoryConfig.SA_SQLITE_EMPTY

# Variables used in tests
REFDATA_ADMIN_OR_ABOVE_USERS = [
    "root1_1",
    "app_admin1_1",
    "refdata_admin1_1",
]

BELOW_APP_ADMIN_DATA_USERS = [
    "org_admin1_1",
    "org_user1_1",
    "guest1_1",
]

BELOW_USER_ADMIN_USERS = [
    "refdata_admin1_1",
    "org_user1_1",
    "guest1_1",
]

NO_DATA_USERS = [
    "refdata_admin1_1",
    "guest1_1",
]

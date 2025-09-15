# Variables for debugging purposes
from gen_epix.casedb.domain import enum

SKIP_ENDPOINTS = False
SKIP_RAISE = False
SKIP_CREATE_DATA = False
VERBOSE = False
REPOSITORY_TYPE = enum.RepositoryType.DICT
# REPOSITORY_TYPE = enum.RepositoryType.SA_SQLITE

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

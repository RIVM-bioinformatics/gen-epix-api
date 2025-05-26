# Variables for debugging purposes
from gen_epix.casedb.domain import enum

SKIP_ENDPOINTS = False
SKIP_RAISE = False
SKIP_CREATE_DATA = False
VERBOSE = False
REPOSITORY_TYPE = enum.RepositoryType.DICT
# REPOSITORY_TYPE = enum.RepositoryType.SA_SQLITE

ALL_USERS = [
    "root1_1",
    "app_admin1_1",
    "metadata_admin1_1",
    "org_admin1_1",
    "org_user1_1",
    "guest1_1",
]

# Variables used in tests
BELOW_ROOT_USERS = [
    "app_admin1_1",
    "metadata_admin1_1",
    "org_admin1_1",
    "org_user1_1",
    "guest1_1",
]

APP_ADMIN_OR_ABOVE_USERS = [
    "root1_1",
    "app_admin1_1",
]

METADATA_ADMIN_OR_ABOVE_USERS = [
    "root1_1",
    "app_admin1_1",
    "metadata_admin1_1",
]

BELOW_APP_ADMIN_USERS = [
    "metadata_admin1_1",
    "org_admin1_1",
    "org_user1_1",
    "guest1_1",
]

BELOW_APP_ADMIN_METADATA_USERS = [
    "metadata_admin1_1",
]

BELOW_APP_ADMIN_DATA_USERS = [
    "org_admin1_1",
    "org_user1_1",
    "guest1_1",
]

BELOW_USER_ADMIN_USERS = [
    "metadata_admin1_1",
    "org_user1_1",
    "guest1_1",
]

NO_DATA_USERS = [
    "metadata_admin1_1",
    "guest1_1",
]

GUEST_USERS = [
    "guest1_1",
]

DATA_USERS = [
    "root1_1",
    "app_admin1_1",
    "org_admin1_1",
    "org_user1_1",
]

NON_GUEST_USERS = [
    "root1_1",
    "app_admin1_1",
    "metadata_admin1_1",
    "org_admin1_1",
    "org_user1_1",
]

ROOT = "root1_1"
APP_ADMIN = "app_admin1_1"
METADATA_ADMIN = "metadata_admin1_1"
ORG_ADMIN = "org_admin1_1"
ORG_USER = "org_user1_1"
GUEST = "guest1_1"

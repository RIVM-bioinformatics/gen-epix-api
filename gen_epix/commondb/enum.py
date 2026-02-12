from enum import Enum, IntEnum


class Role(Enum):
    ROOT = "COMMONDB_ROOT"
    APP_ADMIN = "COMMONDB_APP_ADMIN"
    ORG_ADMIN = "COMMONDB_ORG_ADMIN"
    REFDATA_ADMIN = "COMMONDB_REFDATA_ADMIN"
    ORG_USER = "COMMONDB_ORG_USER"
    GUEST = "COMMONDB_GUEST"
    ROLE1 = "COMMONDB_ROLE1"


class RoleSet(Enum):
    ALL = frozenset(
        {
            Role.ROOT,
            Role.APP_ADMIN,
            Role.ORG_ADMIN,
            Role.REFDATA_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        }
    )
    GE_APP_ADMIN = frozenset({Role.ROOT, Role.APP_ADMIN})
    GE_ORG_ADMIN = frozenset({Role.ROOT, Role.APP_ADMIN, Role.ORG_ADMIN})
    GE_REFDATA_ADMIN = frozenset({Role.ROOT, Role.APP_ADMIN, Role.REFDATA_ADMIN})
    GE_ORG_USER = frozenset(
        {
            Role.ROOT,
            Role.APP_ADMIN,
            Role.ORG_ADMIN,
            Role.ORG_USER,
        }
    )
    GE_GUEST = frozenset(
        {
            Role.ROOT,
            Role.APP_ADMIN,
            Role.ORG_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        }
    )
    LT_ORG_ADMIN = frozenset({Role.ORG_USER, Role.GUEST})
    ROOT = frozenset({Role.ROOT})
    APPLICATION = frozenset({Role.APP_ADMIN})
    ORGANIZATION = frozenset({Role.APP_ADMIN, Role.ORG_ADMIN})
    METADATA = frozenset({Role.REFDATA_ADMIN})
    OPERATIONAL = frozenset({Role.ORG_USER, Role.GUEST})


class ServiceType(Enum):
    AUTH = "AUTH"
    ORGANIZATION = "ORGANIZATION"
    SYSTEM = "SYSTEM"
    RBAC = "RBAC"
    ABAC = "ABAC"


class IdentifierType(IntEnum):
    PERSON = 1
    ORGANIZATION = 2
    CASE = 3
    SAMPLE = 4
    CASE_SET = 5
    GENETIC_SEQUENCE = 6


class OnExistsUploadAction(Enum):
    ERROR = "ERROR"
    UPDATE = "UPDATE"
    SKIP = "SKIP"


class RepositoryType(Enum):
    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"


class AppType(Enum):
    COMMONDB = "COMMONDB"
    CASEDB = "CASEDB"
    SEQDB = "SEQDB"
    OMOPDB = "OMOPDB"
    ALL = "ALL"


class AppTypeSet(Enum):
    ALL = frozenset({AppType.COMMONDB, AppType.CASEDB, AppType.SEQDB, AppType.OMOPDB})


class AppConfigType(Enum):
    IDPS = "idps"
    MOCK_IDPS = "mock_idps"
    NO_AUTH = "no_auth"
    DEBUG = "debug"


class DevIdpConfig(Enum):
    IDPS = "IDPS"
    MOCK = "MOCK"
    NONE = "NONE"


class DevRepositoryConfig(Enum):
    DICT_DEMO = "DICT_DEMO"
    DICT_EMPTY = "DICT_EMPTY"
    SA_SQLITE_DEMO = "SA_SQLITE_DEMO"
    SA_SQLITE_EMPTY = "SA_SQLITE_EMPTY"
    SA_SQL = "SA_SQL"


class DevRepositoryConfigSet(Enum):
    DICT = frozenset({DevRepositoryConfig.DICT_DEMO, DevRepositoryConfig.DICT_EMPTY})
    SA = frozenset(
        {
            DevRepositoryConfig.SA_SQLITE_DEMO,
            DevRepositoryConfig.SA_SQLITE_EMPTY,
            DevRepositoryConfig.SA_SQL,
        }
    )
    SA_SQLITE = frozenset(
        {DevRepositoryConfig.SA_SQLITE_DEMO, DevRepositoryConfig.SA_SQLITE_EMPTY}
    )
    SA_SQL = frozenset({DevRepositoryConfig.SA_SQL})
    DEMO = frozenset(
        {DevRepositoryConfig.DICT_DEMO, DevRepositoryConfig.SA_SQLITE_DEMO}
    )
    EMPTY = frozenset(
        {DevRepositoryConfig.DICT_EMPTY, DevRepositoryConfig.SA_SQLITE_EMPTY}
    )


class UploadStatus(Enum):
    PENDING = "PENDING"  # Yet to be processed
    SKIPPED = "SKIPPED"  # No changes stored
    FAILED = "FAILED"
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    PROCESSED = "PROCESSED"  # Skipped, created or updated (not failed)


class UploadStatusSet(Enum):
    NOT_FAILED = frozenset(
        {
            UploadStatus.PENDING,
            UploadStatus.SKIPPED,
            UploadStatus.CREATED,
            UploadStatus.UPDATED,
            UploadStatus.PROCESSED,
        }
    )
    FAILED = frozenset({UploadStatus.FAILED})
    PROCESSED = frozenset(
        {
            UploadStatus.SKIPPED,
            UploadStatus.CREATED,
            UploadStatus.UPDATED,
            UploadStatus.PROCESSED,
        }
    )
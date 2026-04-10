import datetime
import uuid
from enum import Enum

import ulid


class LogLevel(Enum):
    INFO = "INFO"
    DEBUG = "DEBUG"


class TimestampFactory(Enum):
    DATETIME_NOW = lambda: datetime.datetime.now(datetime.timezone.utc)


class IdFactory(Enum):
    UUID4 = uuid.uuid4
    ULID = lambda: ulid.api.new().uuid


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
    REFDATA = frozenset({Role.REFDATA_ADMIN})
    OPERATIONAL = frozenset({Role.ORG_USER, Role.GUEST})


class ServiceType(Enum):
    AUTH = "AUTH"
    ORGANIZATION = "ORGANIZATION"
    SYSTEM = "SYSTEM"
    RBAC = "RBAC"
    ABAC = "ABAC"


class UploadAction(Enum):
    ERROR = "ERROR"
    UPDATE = "UPDATE"
    CREATE = "CREATE"
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


class EtlStatus(Enum):
    INITIALIZED = "INITIALIZED"
    PENDING = "PENDING"  # Yet to be processed
    SKIPPED = "SKIPPED"  # No changes stored
    FAILED = "FAILED"
    ERROR = "ERROR"  # TODO: should likely be merged with FAILED, or at least clarify the distinction
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    MIXED = "MIXED"  # TODO: should likely be merged with PROCESSED, or at least clarify the distinction
    PROCESSED = "PROCESSED"  # Skipped, created or updated (not failed)
    SUCCESS = "SUCCESS"


class UploadStatusSet(Enum):
    NOT_FAILED = frozenset(
        {
            EtlStatus.PENDING,
            EtlStatus.SKIPPED,
            EtlStatus.CREATED,
            EtlStatus.UPDATED,
            EtlStatus.PROCESSED,
        }
    )
    FAILED = frozenset({EtlStatus.FAILED})
    PROCESSED = frozenset(
        {
            EtlStatus.SKIPPED,
            EtlStatus.CREATED,
            EtlStatus.UPDATED,
            EtlStatus.PROCESSED,
        }
    )


class DataIssueType(Enum):
    MISSING = "MISSING"
    INVALID = "INVALID"
    UNAUTHORIZED = "UNAUTHORIZED"
    CONFLICT = "CONFLICT"
    DERIVED = "DERIVED"
    TRANSFORMED = "TRANSFORMED"


class DataIssueTypeSet(Enum):
    ERROR = frozenset(
        {
            DataIssueType.INVALID,
            DataIssueType.UNAUTHORIZED,
            DataIssueType.CONFLICT,
        }
    )
    WARNING = frozenset(
        {
            DataIssueType.MISSING,
        }
    )
    INFO = frozenset(
        {
            DataIssueType.DERIVED,
            DataIssueType.TRANSFORMED,
        }
    )

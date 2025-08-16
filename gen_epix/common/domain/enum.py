from enum import Enum


class ServiceType(Enum):
    AUTH = "AUTH"
    ORGANIZATION = "ORGANIZATION"
    SYSTEM = "SYSTEM"
    RBAC = "RBAC"


class AppType(Enum):
    CASEDB = "casedb"
    SEQDB = "seqdb"
    OMOPDB = "omopdb"
    ALL = "all"


class AppTypeSet(Enum):
    ALL = frozenset({AppType.CASEDB, AppType.SEQDB, AppType.OMOPDB})


class AppConfigType(Enum):
    IDPS = "idps"
    MOCK_IDPS = "mock_idps"
    NO_AUTH = "no_auth"
    DEBUG = "debug"
    NO_SSL = "no_ssl"

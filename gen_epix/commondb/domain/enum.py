from enum import Enum


class Role(Enum):
    ROOT = "ROOT"
    APP_ADMIN = "APP_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    REFDATA_ADMIN = "REFDATA_ADMIN"
    ORG_USER = "ORG_USER"
    GUEST = "GUEST"
    ROLE1 = "ROLE1"


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
    GE_ORG_USER = frozenset({Role.ROOT, Role.APP_ADMIN, Role.ORG_ADMIN, Role.ORG_USER})
    GE_GUEST = frozenset(
        {
            Role.ROOT,
            Role.APP_ADMIN,
            Role.ORG_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        }
    )
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

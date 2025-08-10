# pylint: disable=wildcard-import, unused-import
# because this is a package, and imported as such in other modules
from __future__ import annotations

import datetime
import uuid
from enum import Enum

import ulid


class TimestampFactory(Enum):
    DATETIME_NOW = lambda: datetime.datetime.now()


class IdFactory(Enum):
    UUID4 = uuid.uuid4
    ULID = lambda: ulid.api.new().uuid


class ServiceType(Enum):
    ORGANIZATION = "ORGANIZATION"
    AUTH = "AUTH"
    RBAC = "RBAC"
    OMOP = "OMOP"
    SYSTEM = "SYSTEM"


class RepositoryType(Enum):
    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"


class Role(Enum):
    ROOT = "ROOT"
    APP_ADMIN = "APP_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    METADATA_ADMIN = "METADATA_ADMIN"
    ORG_USER = "ORG_USER"
    GUEST = "GUEST"
    ROLE1 = "ROLE1"


class RoleSet(Enum):
    ALL = frozenset(
        {
            Role.ROOT,
            Role.APP_ADMIN,
            Role.ORG_ADMIN,
            Role.METADATA_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        }
    )
    GE_APP_ADMIN = frozenset({Role.ROOT, Role.APP_ADMIN})
    GE_ORG_ADMIN = frozenset({Role.ROOT, Role.APP_ADMIN, Role.ORG_ADMIN})
    GE_METADATA_ADMIN = frozenset({Role.ROOT, Role.APP_ADMIN, Role.METADATA_ADMIN})
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
    APPLICATION = frozenset({Role.APP_ADMIN})
    ORGANIZATION = frozenset({Role.APP_ADMIN, Role.ORG_ADMIN})
    METADATA = frozenset({Role.METADATA_ADMIN})
    OPERATIONAL = frozenset({Role.ORG_USER, Role.GUEST})


class ConceptSetType(Enum):
    CONTEXT_FREE_GRAMMAR_JSON = "CONTEXT_FREE_GRAMMAR_JSON"
    CONTEXT_FREE_GRAMMAR_XML = "CONTEXT_FREE_GRAMMAR_XML"
    REGULAR_LANGUAGE = "REGULAR_LANGUAGE"
    NOMINAL = "NOMINAL"
    ORDINAL = "ORDINAL"
    INTERVAL = "INTERVAL"


class AnonStrictness(Enum):
    IGNORE = "ignore"
    WARN = "warn"
    STRICT = "strict"


class AnonMethod(Enum):
    MAKE_NULL = "make_null"
    SHIFT = "shift"
    RANDOM = "random"
    CATEGORICAL = "categorical"
    MODEL_ANONYIMIZATION = "model_anonymization"  # for future use

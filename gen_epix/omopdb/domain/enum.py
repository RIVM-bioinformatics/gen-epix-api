# pylint: disable=wildcard-import, unused-import
# because this is a package, and imported as such in other modules
from __future__ import annotations

import datetime
import uuid
from enum import Enum

import ulid

from gen_epix.commondb.enum import RoleSet as RoleSet


class TimestampFactory(Enum):
    DATETIME_NOW = lambda: datetime.datetime.now(datetime.timezone.utc)


class IdFactory(Enum):
    UUID4 = uuid.uuid4
    ULID = lambda: ulid.api.new().uuid


class ServiceType(Enum):
    AUTH = "AUTH"
    ORGANIZATION = "ORGANIZATION"
    SYSTEM = "SYSTEM"
    RBAC = "RBAC"
    ABAC = "ABAC"
    OMOP = "OMOP"


class RepositoryType(Enum):
    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"


class Role(Enum):
    ROOT = "OMOPDB_ROOT"
    APP_ADMIN = "OMOPDB_APP_ADMIN"
    ORG_ADMIN = "OMOPDB_ORG_ADMIN"
    REFDATA_ADMIN = "OMOPDB_REFDATA_ADMIN"
    ORG_USER = "OMOPDB_ORG_USER"
    GUEST = "OMOPDB_GUEST"
    ROLE1 = "OMOPDB_ROLE1"


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

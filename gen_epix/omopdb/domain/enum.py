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
    ADMIN = "ADMIN"
    REFDATA_ADMIN = "REFDATA_ADMIN"
    DATA_READER = "DATA_READER"
    DATA_WRITER = "DATA_WRITER"
    GUEST = "GUEST"


class RoleSet(Enum):
    ALL = frozenset(
        {
            Role.ROOT,
            Role.ADMIN,
            Role.REFDATA_ADMIN,
            Role.DATA_READER,
            Role.DATA_WRITER,
            Role.GUEST,
        }
    )
    APPLICATION = frozenset({Role.ADMIN})
    REFDATA = frozenset({Role.REFDATA_ADMIN})
    OPERATIONAL = frozenset({Role.DATA_READER, Role.DATA_WRITER, Role.GUEST})


class ConceptSetType(Enum):
    CONTEXT_FREE_GRAMMAR_JSON = "CONTEXT_FREE_GRAMMAR_JSON"
    CONTEXT_FREE_GRAMMAR_XML = "CONTEXT_FREE_GRAMMAR_XML"
    REGULAR_LANGUAGE = "REGULAR_LANGUAGE"
    NOMINAL = "NOMINAL"
    ORDINAL = "ORDINAL"
    INTERVAL = "INTERVAL"

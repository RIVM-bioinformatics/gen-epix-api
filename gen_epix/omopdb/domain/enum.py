"""Enumerations configuring OmopDB services, persistence, roles, and anonymization."""

# pylint: disable=wildcard-import, unused-import
# because this is a package, and imported as such in other modules
from __future__ import annotations

from enum import Enum

from gen_epix.commondb.domain.enum import IdFactory as IdFactory
from gen_epix.commondb.domain.enum import RoleSet as RoleSet
from gen_epix.commondb.domain.enum import TimestampFactory as TimestampFactory


class ServiceType(Enum):
    """Encapsulates OmopDB and shared service domains."""

    AUTH = "AUTH"
    ORGANIZATION = "ORGANIZATION"
    SYSTEM = "SYSTEM"
    RBAC = "RBAC"
    ABAC = "ABAC"
    OMOP = "OMOP"


class RepositoryType(Enum):
    """Encapsulates supported OmopDB repository implementations."""

    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"


class Role(Enum):
    """Encapsulates roles recognized by OmopDB authorization policies."""

    ROOT = "OMOPDB_ROOT"
    APP_ADMIN = "OMOPDB_APP_ADMIN"
    ORG_ADMIN = "OMOPDB_ORG_ADMIN"
    REFDATA_ADMIN = "OMOPDB_REFDATA_ADMIN"
    ORG_USER = "OMOPDB_ORG_USER"
    GUEST = "OMOPDB_GUEST"
    ROLE1 = "OMOPDB_ROLE1"


class AnonStrictness(Enum):
    """Encapsulates the enforcement level for anonymization requirements."""

    IGNORE = "ignore"
    WARN = "warn"
    STRICT = "strict"


class AnonMethod(Enum):
    """Encapsulates available anonymization transformations."""

    MAKE_NULL = "make_null"
    SHIFT = "shift"
    RANDOM = "random"
    CATEGORICAL = "categorical"
    MODEL_ANONYIMIZATION = "model_anonymization"  # for future use

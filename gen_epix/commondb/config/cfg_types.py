"""Static typing overlay for the AppCfg configuration spine.

These TypedDicts describe the shape of the Dynaconf-backed settings object
exposed by AppCfg.cfg. Dynaconf's live Box object remains the actual runtime
value; a cast() at each cfg/resolved_cfg property is the only place these
types touch the runtime object.

Enum-derived fields (TimestampFactory, IdFactory) are imported only under
TYPE_CHECKING: gen_epix.commondb.domain imports this configuration package
back (through domain.util's own import of AppCfg), so importing them for
real at module load time here would deadlock the import graph. A
TYPE_CHECKING-guarded import never executes at runtime, so it does not.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict

from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.service import BaseService

if TYPE_CHECKING:
    from gen_epix.commondb.domain.enum import IdFactory, TimestampFactory


class AppSectionDict(TypedDict):
    host: str
    debug: bool
    port: int


# Functional syntax is required here: header names such as
# "Content-Security-Policy" and "X-Frame-Options" contain hyphens, which are
# not valid Python identifiers, so class syntax is a SyntaxError for these.
#
# The three header blocks are modeled as three separate, fully-required
# TypedDicts rather than one shared, partially-optional dict, since each
# block always carries its own fixed set of keys, and the three sets differ
# (auth lacks Content-Security-Policy*/Cross-Origin-Opener-Policy).
GeneralHttpHeaderDict = TypedDict(
    "GeneralHttpHeaderDict",
    {
        "CacheControl": str,
        "Content-Security-Policy": str,
        "Content-Security-Policy-Report-Only": str,
        "Cross-Origin-Opener-Policy": str,
        "Expires": str,
        "Pragma": str,
        "Referrer-Policy": str,
        "Strict-Transport-Security": str,
        "X-Content-Type-Options": str,
        "X-Frame-Options": str,
        "X-XSS-Protection": str,
    },
)

OpenapiHttpHeaderDict = TypedDict(
    "OpenapiHttpHeaderDict",
    {
        "CacheControl": str,
        "Expires": str,
        "Pragma": str,
        "Referrer-Policy": str,
        "Strict-Transport-Security": str,
        "X-Content-Type-Options": str,
        "X-Frame-Options": str,
        "X-XSS-Protection": str,
    },
)

AuthHttpHeaderDict = TypedDict(
    "AuthHttpHeaderDict",
    {
        "CacheControl": str,
        "Expires": str,
        "Pragma": str,
        "Strict-Transport-Security": str,
        "X-Content-Type-Options": str,
        "X-Frame-Options": str,
        "X-XSS-Protection": str,
    },
)


class HttpHeaderSectionDict(TypedDict):
    general: GeneralHttpHeaderDict
    openapi: OpenapiHttpHeaderDict
    auth: AuthHttpHeaderDict


class ApiRouteDict(TypedDict):
    v1: str


class ApiSectionDict(TypedDict):
    default_route: str
    gzip_response_minimum_size: int
    http_header: HttpHeaderSectionDict
    route: ApiRouteDict


class CommandObjectSummarizationDict(TypedDict):
    enabled: bool
    max_list_items: int
    max_string_length: int
    max_exception_message_length: int


class LogSectionDict(TypedDict):
    level: str
    command_object_summarization: CommandObjectSummarizationDict


# Keys are FeatureFlag/CasedbFeatureFlag (etc.) .value strings. There is no
# single fixed key set once a per-app flag enum is merged in, so this stays a
# plain string-keyed mapping rather than a closed TypedDict.
type FeatureFlagsDict = dict[str, bool]

# An open bag of constructor keyword arguments for whatever class
# module/class_name names; its shape is defined by that class's __init__,
# not by the config spine itself.
type ServicePropsDict = dict[str, Any]


class ServiceEntryDict(TypedDict):
    """Shape of one `service.<x>` / `repository.<x>` entry before validation."""

    module: str
    class_name: str
    props: NotRequired[ServicePropsDict]


# "class" is a Python keyword and cannot appear as a class-body field name,
# so functional syntax is required for the resolved variant.
ResolvedServiceEntryDict = TypedDict(
    "ResolvedServiceEntryDict",
    {
        "module": str,
        "class_name": str,
        "class": type[BaseService],
        "props": NotRequired[ServicePropsDict],
    },
)

RepositoryEntryDict = ServiceEntryDict  # identical raw shape

ResolvedRepositoryEntryDict = TypedDict(
    "ResolvedRepositoryEntryDict",
    {
        "module": str,
        "class_name": str,
        "class": type[BaseRepository],
        "props": NotRequired[ServicePropsDict],
    },
)


class ServiceDefaultsPropsDict(TypedDict):
    timestamp_factory: str
    id_factory: str


class ResolvedServiceDefaultsPropsDict(TypedDict):
    timestamp_factory: TimestampFactory
    id_factory: IdFactory


class ServiceDefaultsDict(TypedDict):
    props: ServiceDefaultsPropsDict


class ResolvedServiceDefaultsDict(TypedDict):
    props: ResolvedServiceDefaultsPropsDict


class ServiceSectionDict(TypedDict):
    defaults: ServiceDefaultsDict
    abac: ServiceEntryDict
    auth: ServiceEntryDict
    organization: ServiceEntryDict
    rbac: ServiceEntryDict
    system: ServiceEntryDict


class ResolvedServiceSectionDict(TypedDict):
    defaults: ResolvedServiceDefaultsDict
    abac: ResolvedServiceEntryDict
    auth: ResolvedServiceEntryDict
    organization: ResolvedServiceEntryDict
    rbac: ResolvedServiceEntryDict
    system: ResolvedServiceEntryDict


class RepositoryDefaultsDict(TypedDict):
    type: str


class ResolvedRepositoryDefaultsDict(TypedDict):
    # The concrete member type is whichever repository_type_enum was passed
    # to AppCfg.__init__ for this instance — an app-specific choice a
    # structural TypedDict cannot parametrize. Enum is the common type;
    # a specific app's RepositoryType is recovered by a local cast() at the
    # point of use.
    type: Enum


class RepositorySectionDict(TypedDict):
    defaults: RepositoryDefaultsDict
    # Per-service-type entries are looked up dynamically by
    # service_type.value.lower() and only exist for service types that
    # declare a repository, so they are not modeled as fixed fields here.
    # Cast at the point of use, e.g.:
    #   cast(ResolvedRepositoryEntryDict, app_cfg.cfg["repository"][service_type_str])


class ResolvedRepositorySectionDict(TypedDict):
    defaults: ResolvedRepositoryDefaultsDict


class AppCfgSettingsDict(TypedDict):
    """Shape of AppCfg.cfg before AppCfg._init_validate_settings runs."""

    app: AppSectionDict
    api: ApiSectionDict
    log: LogSectionDict
    feature_flags: FeatureFlagsDict
    service: ServiceSectionDict
    repository: NotRequired[RepositorySectionDict]


class ResolvedAppCfgSettingsDict(TypedDict):
    """Shape of AppCfg.cfg once AppCfg._init_validate_settings has run."""

    app: AppSectionDict
    api: ApiSectionDict
    log: LogSectionDict
    feature_flags: FeatureFlagsDict
    service: ResolvedServiceSectionDict
    repository: NotRequired[ResolvedRepositorySectionDict]

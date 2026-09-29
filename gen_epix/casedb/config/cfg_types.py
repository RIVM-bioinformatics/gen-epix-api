"""Static typing overlay for CasedbAppCfg's extra configuration keys."""

from __future__ import annotations

from typing import NotRequired, TypedDict

from gen_epix.commondb.config.cfg_types import (
    ApiSectionDict,
    AppSectionDict,
    FeatureFlagsDict,
    LogSectionDict,
    RepositorySectionDict,
    ResolvedRepositorySectionDict,
    ResolvedServiceEntryDict,
    ResolvedServiceSectionDict,
    ServiceEntryDict,
    ServiceSectionDict,
)


class SeqdbClientLocalUserDict(TypedDict):
    id: str
    key: str
    organization_id: str
    roles: list[str]


class SeqdbClientLocalDict(TypedDict):
    user: SeqdbClientLocalUserDict


class SeqdbClientRemoteDict(TypedDict):
    module: str
    class_name: str
    protocol: str
    host: str
    port: str
    auth_protocol: str
    oauth_flow: str
    oauth_client_id: str
    oauth_client_secret: str
    oauth_scope: str
    oauth_discovery_url: str


class SeqdbClientPropsDict(TypedDict):
    seqdb_client_type: str
    local_client: SeqdbClientLocalDict
    remote_client: SeqdbClientRemoteDict


# Does not inherit ServiceEntryDict: TypedDict fields are invariant, so a
# subclass cannot narrow the inherited `props` field from the open
# ServicePropsDict bag to the specific SeqdbClientPropsDict shape. This is a
# standalone TypedDict with the same module/class_name fields, repeated
# rather than inherited, plus the narrowed props type.
class SeqdbClientEntryDict(TypedDict):
    module: str
    class_name: str
    props: SeqdbClientPropsDict


class CasedbServiceSectionDict(ServiceSectionDict):
    """Adds casedb's own service entries to the base service section.

    TypedDict inheritance adds fields the same way ordinary class
    inheritance does; unlike Enum, TypedDict has no restriction against
    extending a type that already declares fields — only *overriding* an
    inherited field's type is disallowed, which is why this subclass only
    adds new keys rather than narrowing an existing one.
    """

    case: ServiceEntryDict
    geo: ServiceEntryDict
    ontology: ServiceEntryDict
    seqdb: SeqdbClientEntryDict


class ResolvedCasedbServiceSectionDict(ResolvedServiceSectionDict):
    case: ResolvedServiceEntryDict
    geo: ResolvedServiceEntryDict
    ontology: ResolvedServiceEntryDict
    seqdb: ResolvedServiceEntryDict


# Does not inherit AppCfgSettingsDict: TypedDict fields are invariant, so a
# subclass cannot override the inherited `service` field with the wider
# CasedbServiceSectionDict. This is instead a standalone TypedDict that
# reuses every other unchanged nested type by reference and only widens
# `service`.
class CasedbAppCfgSettingsDict(TypedDict):
    app: AppSectionDict
    api: ApiSectionDict
    log: LogSectionDict
    feature_flags: FeatureFlagsDict
    service: CasedbServiceSectionDict
    repository: NotRequired[RepositorySectionDict]


class ResolvedCasedbAppCfgSettingsDict(TypedDict):
    app: AppSectionDict
    api: ApiSectionDict
    log: LogSectionDict
    feature_flags: FeatureFlagsDict
    service: ResolvedCasedbServiceSectionDict
    repository: NotRequired[ResolvedRepositorySectionDict]

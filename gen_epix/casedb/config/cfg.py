"""Casedb-specific configuration, layered on top of the shared AppCfg spine."""

from typing import Any, cast

from dynaconf import Validator

from gen_epix.casedb.config import cfg_types as casedb_cfg_types
from gen_epix.casedb.domain import enum as casedb_enum
from gen_epix.commondb.config.cfg import AppCfg

_MODULE = "gen_epix.casedb.services"


class CasedbAppCfg(AppCfg):
    """AppCfg specialized for the casedb app.

    Supplies casedb's app name and enums as constructor defaults, so
    `CasedbAppCfg()` alone loads casedb's configuration; any AppCfg
    constructor keyword argument (including `settings_files=[...]` for
    tests that need full isolation) still works as an override.
    `_DEFAULT_SETTINGS` layers casedb's own port, its ULID id_factory
    (every other app in this repository uses UUID4), its service module
    paths and organization-user role, its three additional domain services
    (case, geo, ontology), and its client configuration for calling the
    seqdb app's API, on top of AppCfg's own defaults.
    """

    _DEFAULT_SETTINGS: dict[str, Any] = AppCfg._deep_merge(
        AppCfg._DEFAULT_SETTINGS,
        {
            "app": {"port": 8000},
            "service": {
                "defaults": {"props": {"id_factory": "ULID"}},
                "abac": {"module": _MODULE},
                "auth": {
                    "module": _MODULE,
                    "props": {"auto_created_user": {"roles": ["CASEDB_ORG_USER"]}},
                },
                "organization": {"module": _MODULE},
                "rbac": {"module": _MODULE},
                "system": {"module": _MODULE},
                "case": {"module": _MODULE, "class_name": "CaseService"},
                "geo": {"module": _MODULE, "class_name": "GeoService"},
                "ontology": {"module": _MODULE, "class_name": "OntologyService"},
                "seqdb": {
                    "module": _MODULE,
                    "class_name": "SeqdbService",
                    "props": {
                        "seqdb_client_type": "LOCAL",
                        "local_client": {
                            "user": {
                                "id": "018bcd02-eb19-fb14-c520-64cbb78d9135",
                                "key": "root@dummy.org",
                                "organization_id": "018d074d-ea0c-e942-07db-a3cc0ba1d653",
                                "roles": ["SEQDB_APP_ADMIN"],
                            },
                        },
                        "remote_client": {
                            "module": _MODULE,
                            "class_name": "SeqdbClient",
                            "protocol": "HTTPS",
                            "host": "localhost",
                            "port": "8001",
                            "auth_protocol": "OAUTH2",
                            "oauth_flow": "CLIENT_CREDENTIALS",
                            "oauth_client_id": "CASEDB_FOR_SEQDB_DUMMY_CLIENT_ID",
                            "oauth_client_secret": "CASEDB_FOR_SEQDB_DUMMY_CLIENT_SECRET",
                            "oauth_scope": "DUMMY_SCOPE",
                            "oauth_discovery_url": "https://your-idp.com/.well-known/openid-configuration",
                        },
                    },
                },
            },
            "repository": {
                "defaults": {"props": {"database": "casedb"}},
                "abac": {
                    "module": "gen_epix.casedb.repositories",
                    "class_name": "AbacSARepository",
                },
                "organization": {
                    "module": "gen_epix.casedb.repositories",
                    "class_name": "OrganizationSARepository",
                },
                "system": {
                    "module": "gen_epix.casedb.repositories",
                    "class_name": "SystemSARepository",
                },
                "case": {
                    "module": "gen_epix.casedb.repositories",
                    "class_name": "CaseSARepository",
                },
                "geo": {
                    "module": "gen_epix.casedb.repositories",
                    "class_name": "GeoSARepository",
                },
                "ontology": {
                    "module": "gen_epix.casedb.repositories",
                    "class_name": "OntologySARepository",
                },
            },
        },
    )

    def __init__(
        self,
        app_name_or_enum: str = "CASEDB",
        service_type_enum: type = casedb_enum.ServiceType,
        repository_type_enum: type = casedb_enum.RepositoryType,
        **kwargs: Any,
    ) -> None:
        """Initialize casedb configuration; see AppCfg.__init__ for all kwargs."""
        super().__init__(
            app_name_or_enum, service_type_enum, repository_type_enum, **kwargs
        )

    def _get_default_settings(self) -> dict[str, Any]:
        """Return a fresh, mutation-safe copy of casedb's business defaults."""
        settings = super()._get_default_settings()
        settings["feature_flags"].update(
            {flag.value: False for flag in casedb_enum.CasedbFeatureFlag}
        )
        return settings

    def _get_feature_flag_validators(self) -> list[Validator]:
        """Build validators for casedb's own `[feature_flags]` table entries, in addition to the shared ones."""
        return [
            *super()._get_feature_flag_validators(),
            *(
                Validator(f"feature_flags.{flag.value}", is_type_of=bool)
                for flag in casedb_enum.CasedbFeatureFlag
            ),
        ]

    @property
    def resolved_cfg(self) -> casedb_cfg_types.ResolvedCasedbAppCfgSettingsDict:
        """Casedb-widened view of `cfg`, exposing service.case/geo/ontology/seqdb.

        A separate property rather than an override of `cfg`: TypedDict
        field invariance means `ResolvedCasedbAppCfgSettingsDict` is not a
        type-checker subtype of `ResolvedAppCfgSettingsDict`, so overriding
        `cfg` here would fail its override-compatibility check even though
        every concrete value is compatible at runtime. `cfg` (inherited)
        still returns the correctly-typed base shape for callers that only
        need it.
        """
        return cast(casedb_cfg_types.ResolvedCasedbAppCfgSettingsDict, self._cfg)

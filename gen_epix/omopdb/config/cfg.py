"""Omopdb-specific configuration, layered on top of the shared AppCfg spine."""

from typing import Any

from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.omopdb.domain import enum as omopdb_enum

_MODULE = "gen_epix.omopdb.services"


class OmopdbAppCfg(AppCfg):
    """AppCfg specialized for the omopdb app.

    Supplies omopdb's app name and enums as constructor defaults, so
    `OmopdbAppCfg()` alone loads omopdb's configuration. `_DEFAULT_SETTINGS`
    layers omopdb's own port, service module paths and organization-user
    role, and its one additional domain service (omop), on top of AppCfg's
    own defaults.
    """

    _DEFAULT_SETTINGS: dict[str, Any] = AppCfg._deep_merge(
        AppCfg._DEFAULT_SETTINGS,
        {
            "app": {"port": 8002},
            "service": {
                "abac": {"module": _MODULE},
                "auth": {
                    "module": _MODULE,
                    "props": {"auto_created_user": {"roles": ["OMOPDB_ORG_USER"]}},
                },
                "organization": {"module": _MODULE},
                "rbac": {"module": _MODULE},
                "system": {"module": _MODULE},
                "omop": {"module": _MODULE, "class_name": "OmopService"},
            },
            "repository": {
                "defaults": {"props": {"database": "omopdb"}},
                "abac": {
                    "module": "gen_epix.omopdb.repositories",
                    "class_name": "AbacSARepository",
                },
                "organization": {
                    "module": "gen_epix.omopdb.repositories",
                    "class_name": "OrganizationSARepository",
                },
                "system": {
                    "module": "gen_epix.omopdb.repositories",
                    "class_name": "SystemSARepository",
                },
                "omop": {
                    "module": "gen_epix.omopdb.repositories",
                    "class_name": "OmopSARepository",
                },
            },
        },
    )

    def __init__(
        self,
        app_name_or_enum: str = "OMOPDB",
        service_type_enum: type = omopdb_enum.ServiceType,
        repository_type_enum: type = omopdb_enum.RepositoryType,
        **kwargs: Any,
    ) -> None:
        """Initialize omopdb configuration; see AppCfg.__init__ for all kwargs."""
        super().__init__(
            app_name_or_enum, service_type_enum, repository_type_enum, **kwargs
        )

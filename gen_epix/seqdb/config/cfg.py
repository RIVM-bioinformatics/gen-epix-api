"""Seqdb-specific configuration, layered on top of the shared AppCfg spine."""

from typing import Any

from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.seqdb.domain import enum as seqdb_enum

_MODULE = "gen_epix.seqdb.services"


class SeqdbAppCfg(AppCfg):
    """AppCfg specialized for the seqdb app.

    Supplies seqdb's app name and enums as constructor defaults, so
    `SeqdbAppCfg()` alone loads seqdb's configuration. `_DEFAULT_SETTINGS`
    layers seqdb's own port, service module paths and organization-user
    role, and its two additional domain services (seq, file), on top of
    AppCfg's own defaults.
    """

    _DEFAULT_SETTINGS: dict[str, Any] = AppCfg._deep_merge(
        AppCfg._DEFAULT_SETTINGS,
        {
            "app": {"port": 8001},
            "service": {
                "abac": {"module": _MODULE},
                "auth": {
                    "module": _MODULE,
                    "props": {"auto_created_user": {"roles": ["SEQDB_ORG_USER"]}},
                },
                "organization": {"module": _MODULE},
                "rbac": {"module": _MODULE},
                "system": {"module": _MODULE},
                "seq": {"module": _MODULE, "class_name": "SeqService"},
                "file": {"module": _MODULE, "class_name": "FileService"},
            },
            "repository": {
                "defaults": {"props": {"database": "seqdb"}},
                "abac": {
                    "module": "gen_epix.seqdb.repositories",
                    "class_name": "AbacSARepository",
                },
                "organization": {
                    "module": "gen_epix.seqdb.repositories",
                    "class_name": "OrganizationSARepository",
                },
                "system": {
                    "module": "gen_epix.seqdb.repositories",
                    "class_name": "SystemSARepository",
                },
                "seq": {
                    "module": "gen_epix.seqdb.repositories",
                    "class_name": "SeqSARepository",
                },
                "file": {
                    "module": "gen_epix.seqdb.repositories",
                    "class_name": "FileSARepository",
                },
            },
        },
    )

    def __init__(
        self,
        app_name_or_enum: str = "SEQDB",
        service_type_enum: type = seqdb_enum.ServiceType,
        repository_type_enum: type = seqdb_enum.RepositoryType,
        **kwargs: Any,
    ) -> None:
        """Initialize seqdb configuration; see AppCfg.__init__ for all kwargs."""
        super().__init__(
            app_name_or_enum, service_type_enum, repository_type_enum, **kwargs
        )

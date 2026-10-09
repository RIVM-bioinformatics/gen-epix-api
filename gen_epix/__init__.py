"""Expose shared APIs and the Gen-EpiX domain applications.

Shared exports include FastApp, filtering, utility, ETL, configuration,
exception, literal, and common-domain APIs: ``etl``, ``etl_model``, ``fastapp``,
``filter``, ``util``, ``AppCfg``, ``AppComposer``, ``COMMONDB_DOMAIN``,
``CommondbClient``, ``commondb_command``, ``commondb_enum``, ``commondb_model``,
``exc``, ``literal``, ``NULL_ID``, ``AppType``, and ``create_client``.

CASEDB exports include ``CASEDB_DOMAIN``, ``CasedbAppComposer``, ``CasedbClient``,
``casedb_command``, ``casedb_enum``, ``casedb_model``, ``casedb_policy``,
``casedb_service``, and ``casedb_services``. OMOPDB exports include
``OMOPDB_DOMAIN``, ``OmopdbAppComposer``, ``OmopdbClient``, ``omopdb_command``,
``omopdb_enum``, ``omopdb_model``, ``omopdb_policy``, and ``omopdb_service``.
SEQDB exports include ``SEQDB_DOMAIN``, ``SeqdbAppComposer``, ``SeqdbClient``,
``seqdb_command``, ``seqdb_enum``, ``seqdb_model``, ``seqdb_policy``, and
``seqdb_service``.
"""

from typing import TYPE_CHECKING

from gen_epix._lazy import LazyExport, exports_from, lazy_exports

if TYPE_CHECKING:
    # pylint: disable=useless-import-alias
    from gen_epix import etl as etl
    from gen_epix import fastapp as fastapp
    from gen_epix import filter as filter
    from gen_epix import util as util
    from gen_epix.casedb import services as casedb_services
    from gen_epix.casedb.config import CasedbAppCfg as CasedbAppCfg
    from gen_epix.casedb.domain import DOMAIN as CASEDB_DOMAIN
    from gen_epix.casedb.domain import command as casedb_command
    from gen_epix.casedb.domain import enum as casedb_enum
    from gen_epix.casedb.domain import model as casedb_model
    from gen_epix.casedb.domain import policy as casedb_policy
    from gen_epix.casedb.domain import service as casedb_service
    from gen_epix.casedb.env import AppComposer as CasedbAppComposer
    from gen_epix.casedb.services.client import CasedbClient as CasedbClient
    from gen_epix.commondb.client_factory import create_client as create_client
    from gen_epix.commondb.config import AppCfg
    from gen_epix.commondb.domain import DOMAIN as COMMONDB_DOMAIN
    from gen_epix.commondb.domain import command as commondb_command
    from gen_epix.commondb.domain import enum as commondb_enum
    from gen_epix.commondb.domain import exc as exc
    from gen_epix.commondb.domain import literal as literal
    from gen_epix.commondb.domain import model as commondb_model
    from gen_epix.commondb.domain.enum import AppType as AppType
    from gen_epix.commondb.domain.enum import DevIdpConfig as DevIdpConfig
    from gen_epix.commondb.domain.enum import DevRepositoryConfig as DevRepositoryConfig
    from gen_epix.commondb.domain.literal import NULL_ID as NULL_ID
    from gen_epix.commondb.domain.util import get_app_cfg_class as get_app_cfg_class
    from gen_epix.commondb.domain.util import set_env_variables as set_env_variables
    from gen_epix.commondb.env import AppComposer as AppComposer
    from gen_epix.commondb.services.client import CommondbClient as CommondbClient
    from gen_epix.etl import model as etl_model
    from gen_epix.omopdb.config import OmopdbAppCfg as OmopdbAppCfg
    from gen_epix.omopdb.domain import DOMAIN as OMOPDB_DOMAIN
    from gen_epix.omopdb.domain import command as omopdb_command
    from gen_epix.omopdb.domain import enum as omopdb_enum
    from gen_epix.omopdb.domain import model as omopdb_model
    from gen_epix.omopdb.domain import policy as omopdb_policy
    from gen_epix.omopdb.domain import service as omopdb_service
    from gen_epix.omopdb.env import AppComposer as OmopdbAppComposer
    from gen_epix.omopdb.services.client import OmopdbClient as OmopdbClient
    from gen_epix.seqdb.config import SeqdbAppCfg as SeqdbAppCfg
    from gen_epix.seqdb.domain import DOMAIN as SEQDB_DOMAIN
    from gen_epix.seqdb.domain import command as seqdb_command
    from gen_epix.seqdb.domain import enum as seqdb_enum
    from gen_epix.seqdb.domain import model as seqdb_model
    from gen_epix.seqdb.domain import policy as seqdb_policy
    from gen_epix.seqdb.domain import service as seqdb_service
    from gen_epix.seqdb.env import AppComposer as SeqdbAppComposer
    from gen_epix.seqdb.services.client import SeqdbClient as SeqdbClient

# Runtime counterpart of the imports above: nothing is imported until accessed
_EXPORTS: dict[str, LazyExport] = {
    "etl": "gen_epix.etl",
    "fastapp": "gen_epix.fastapp",
    "filter": "gen_epix.filter",
    "util": "gen_epix.util",
    "casedb_services": "gen_epix.casedb.services",
    "CasedbAppCfg": ("gen_epix.casedb.config", "CasedbAppCfg"),
    "CASEDB_DOMAIN": ("gen_epix.casedb.domain", "DOMAIN"),
    "casedb_command": "gen_epix.casedb.domain.command",
    "casedb_enum": "gen_epix.casedb.domain.enum",
    "casedb_model": "gen_epix.casedb.domain.model",
    "casedb_policy": "gen_epix.casedb.domain.policy",
    "casedb_service": "gen_epix.casedb.domain.service",
    "CasedbAppComposer": ("gen_epix.casedb.env", "AppComposer"),
    "CasedbClient": ("gen_epix.casedb.services.client", "CasedbClient"),
    "AppCfg": ("gen_epix.commondb.config", "AppCfg"),
    "create_client": ("gen_epix.commondb.client_factory", "create_client"),
    "COMMONDB_DOMAIN": ("gen_epix.commondb.domain", "DOMAIN"),
    "commondb_command": "gen_epix.commondb.domain.command",
    "commondb_enum": "gen_epix.commondb.domain.enum",
    "exc": "gen_epix.commondb.domain.exc",
    "literal": "gen_epix.commondb.domain.literal",
    "commondb_model": "gen_epix.commondb.domain.model",
    **exports_from(
        "gen_epix.commondb.domain.enum",
        "AppType",
        "DevIdpConfig",
        "DevRepositoryConfig",
    ),
    "NULL_ID": ("gen_epix.commondb.domain.literal", "NULL_ID"),
    **exports_from(
        "gen_epix.commondb.domain.util", "get_app_cfg_class", "set_env_variables"
    ),
    "AppComposer": ("gen_epix.commondb.env", "AppComposer"),
    "CommondbClient": ("gen_epix.commondb.services.client", "CommondbClient"),
    "etl_model": "gen_epix.etl.model",
    "OmopdbAppCfg": ("gen_epix.omopdb.config", "OmopdbAppCfg"),
    "OMOPDB_DOMAIN": ("gen_epix.omopdb.domain", "DOMAIN"),
    "omopdb_command": "gen_epix.omopdb.domain.command",
    "omopdb_enum": "gen_epix.omopdb.domain.enum",
    "omopdb_model": "gen_epix.omopdb.domain.model",
    "omopdb_policy": "gen_epix.omopdb.domain.policy",
    "omopdb_service": "gen_epix.omopdb.domain.service",
    "OmopdbAppComposer": ("gen_epix.omopdb.env", "AppComposer"),
    "OmopdbClient": ("gen_epix.omopdb.services.client", "OmopdbClient"),
    "SeqdbAppCfg": ("gen_epix.seqdb.config", "SeqdbAppCfg"),
    "SEQDB_DOMAIN": ("gen_epix.seqdb.domain", "DOMAIN"),
    "seqdb_command": "gen_epix.seqdb.domain.command",
    "seqdb_enum": "gen_epix.seqdb.domain.enum",
    "seqdb_model": "gen_epix.seqdb.domain.model",
    "seqdb_policy": "gen_epix.seqdb.domain.policy",
    "seqdb_service": "gen_epix.seqdb.domain.service",
    "SeqdbAppComposer": ("gen_epix.seqdb.env", "AppComposer"),
    "SeqdbClient": ("gen_epix.seqdb.services.client", "SeqdbClient"),
}

if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_exports(__name__, _EXPORTS)

# TODO: consider removing _policy since they need not necessarily be part of the public API
__all__ = [
    "etl",
    "exc",
    "fastapp",
    "filter",
    "literal",
    "NULL_ID",
    "AppCfg",
    "AppType",
    "create_client",
    "AppComposer",
    "COMMONDB_DOMAIN",
    "CommondbClient",
    "commondb_command",
    "commondb_enum",
    "commondb_model",
    "DevIdpConfig",
    "DevRepositoryConfig",
    "etl_model",
    "get_app_cfg_class",
    "set_env_variables",
    "CASEDB_DOMAIN",
    "CasedbAppCfg",
    "CasedbAppComposer",
    "CasedbClient",
    "casedb_command",
    "casedb_enum",
    "casedb_model",
    "casedb_policy",
    "casedb_service",
    "casedb_services",
    "OMOPDB_DOMAIN",
    "OmopdbAppCfg",
    "OmopdbAppComposer",
    "OmopdbClient",
    "omopdb_command",
    "omopdb_enum",
    "omopdb_model",
    "omopdb_policy",
    "omopdb_service",
    "SEQDB_DOMAIN",
    "SeqdbAppCfg",
    "SeqdbAppComposer",
    "SeqdbClient",
    "seqdb_command",
    "seqdb_enum",
    "seqdb_model",
    "seqdb_policy",
    "seqdb_service",
    "util",
]

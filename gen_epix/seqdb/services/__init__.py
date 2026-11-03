"""Expose seqdb service implementations for application composition."""

# pylint: disable=useless-import-alias
from typing import TYPE_CHECKING

from gen_epix._lazy import LazyExport, exports_from, lazy_exports

if TYPE_CHECKING:
    from gen_epix.commondb.services import AuthService as AuthService
    from gen_epix.commondb.services import OrganizationService as OrganizationService
    from gen_epix.commondb.services import RbacService as RbacService
    from gen_epix.commondb.services import SystemService as SystemService
    from gen_epix.commondb.services import UserManager as UserManager
    from gen_epix.seqdb.services.abac import AbacService as AbacService
    from gen_epix.seqdb.services.client import SeqdbClient as SeqdbClient
    from gen_epix.seqdb.services.file import FileService as FileService
    from gen_epix.seqdb.services.seq import SeqService as SeqService

# Services are resolved on first access, so that importing one of them, such
# as the remote client, does not load all the others and their dependencies
_LAZY_EXPORTS: dict[str, LazyExport] = {
    **exports_from(
        "gen_epix.commondb.services",
        "AuthService",
        "OrganizationService",
        "RbacService",
        "SystemService",
        "UserManager",
    ),
    **exports_from("gen_epix.seqdb.services.abac", "AbacService"),
    **exports_from("gen_epix.seqdb.services.client", "SeqdbClient"),
    **exports_from("gen_epix.seqdb.services.file", "FileService"),
    **exports_from("gen_epix.seqdb.services.seq", "SeqService"),
}

if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_exports(__name__, _LAZY_EXPORTS)

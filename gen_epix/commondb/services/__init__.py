"""Re-export concrete commondb services and the remote commondb HTTP client.

The package provides ABAC, organization, RBAC, system, upload, and user-manager
implementations alongside FastApp's authentication service.
"""

# pylint: disable=useless-import-alias
from typing import TYPE_CHECKING

from gen_epix._lazy import LazyExport, lazy_exports

if TYPE_CHECKING:
    from gen_epix.commondb.services.abac import AbacService as AbacService
    from gen_epix.commondb.services.client import CommondbClient as CommondbClient
    from gen_epix.commondb.services.organization import (
        OrganizationService as OrganizationService,
    )
    from gen_epix.commondb.services.rbac import RbacService as RbacService
    from gen_epix.commondb.services.system import SystemService as SystemService
    from gen_epix.commondb.services.upload import BatchUploader as BatchUploader
    from gen_epix.commondb.services.user_manager import UserManager as UserManager
    from gen_epix.fastapp.services.auth import AuthService as AuthService

# Services are resolved on first access, so that importing one of them, such
# as the remote client, does not load all the others and their dependencies
_LAZY_EXPORTS: dict[str, LazyExport] = {
    "AbacService": ("gen_epix.commondb.services.abac", "AbacService"),
    "CommondbClient": ("gen_epix.commondb.services.client", "CommondbClient"),
    "OrganizationService": (
        "gen_epix.commondb.services.organization",
        "OrganizationService",
    ),
    "RbacService": ("gen_epix.commondb.services.rbac", "RbacService"),
    "SystemService": ("gen_epix.commondb.services.system", "SystemService"),
    "BatchUploader": ("gen_epix.commondb.services.upload", "BatchUploader"),
    "UserManager": ("gen_epix.commondb.services.user_manager", "UserManager"),
    "AuthService": ("gen_epix.fastapp.services.auth", "AuthService"),
}

if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_exports(__name__, _LAZY_EXPORTS)

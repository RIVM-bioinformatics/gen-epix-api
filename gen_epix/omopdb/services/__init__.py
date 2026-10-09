"""Expose shared and OmopDB service implementations for application composition.

Shared auth, system, organization, RBAC, and user services are re-exported;
OmopDB adds ABAC, OMOP command handling, and specialized organization and RBAC
implementations.
"""

# pylint: disable=useless-import-alias
from typing import TYPE_CHECKING

from gen_epix._lazy import LazyExport, exports_from, lazy_exports

if TYPE_CHECKING:
    from gen_epix.commondb.services import AuthService as AuthService
    from gen_epix.commondb.services import SystemService as SystemService
    from gen_epix.commondb.services import UserManager as UserManager
    from gen_epix.omopdb.services.abac import AbacService as AbacService
    from gen_epix.omopdb.services.omop import OmopService as OmopService
    from gen_epix.omopdb.services.organization import (
        OrganizationService as OrganizationService,
    )
    from gen_epix.omopdb.services.rbac import RbacService as RbacService

# Services are resolved on first access, so that importing one of them, such
# as the remote client, does not load all the others and their dependencies
_LAZY_EXPORTS: dict[str, LazyExport] = {
    **exports_from(
        "gen_epix.commondb.services", "AuthService", "SystemService", "UserManager"
    ),
    **exports_from("gen_epix.omopdb.services.organization", "OrganizationService"),
    **exports_from("gen_epix.omopdb.services.rbac", "RbacService"),
    **exports_from("gen_epix.omopdb.services.abac", "AbacService"),
    **exports_from("gen_epix.omopdb.services.omop", "OmopService"),
}

if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_exports(__name__, _LAZY_EXPORTS)

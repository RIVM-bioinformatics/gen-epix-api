"""Expose concrete casedb and shared services for application composition.

Casedb exports implement ABAC, case, geography, ontology, and local or remote
seqdb collaboration. Shared commondb exports provide authentication, organization,
RBAC, system, and user-management services required by the composed application.
"""

# pylint: disable=useless-import-alias
from typing import TYPE_CHECKING

from gen_epix._lazy import LazyExport, exports_from, lazy_exports

if TYPE_CHECKING:
    from gen_epix.casedb.services.abac import AbacService as AbacService
    from gen_epix.casedb.services.case import CaseService as CaseService
    from gen_epix.casedb.services.geo import GeoService as GeoService
    from gen_epix.casedb.services.ontology import OntologyService as OntologyService
    from gen_epix.casedb.services.seqdb import SeqdbClient as SeqdbClient
    from gen_epix.casedb.services.seqdb import SeqdbService as SeqdbService
    from gen_epix.commondb.services import AuthService as AuthService
    from gen_epix.commondb.services import OrganizationService as OrganizationService
    from gen_epix.commondb.services import SystemService as SystemService
    from gen_epix.commondb.services import UserManager as UserManager
    from gen_epix.commondb.services.rbac import RbacService as RbacService

# Services are resolved on first access, so that importing one of them, such
# as the remote client, does not load all the others and their dependencies
_LAZY_EXPORTS: dict[str, LazyExport] = {
    **exports_from("gen_epix.casedb.services.abac", "AbacService"),
    **exports_from("gen_epix.casedb.services.case", "CaseService"),
    **exports_from("gen_epix.casedb.services.geo", "GeoService"),
    **exports_from("gen_epix.casedb.services.ontology", "OntologyService"),
    **exports_from("gen_epix.casedb.services.seqdb", "SeqdbClient", "SeqdbService"),
    **exports_from(
        "gen_epix.commondb.services",
        "AuthService",
        "OrganizationService",
        "SystemService",
        "UserManager",
    ),
    **exports_from("gen_epix.commondb.services.rbac", "RbacService"),
}

if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_exports(__name__, _LAZY_EXPORTS)

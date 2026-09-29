"""Expose backend-independent repository contracts used by casedb services.

Casedb exports define case, geographic, and ontology persistence operations.
Shared exports provide ABAC, organization, and system repository contracts so
dictionary and SQLAlchemy implementations present the same service boundary.
"""

# pylint: disable=useless-import-alias
from gen_epix.casedb.domain.repository.case import (
    BaseCaseRepository as BaseCaseRepository,
)
from gen_epix.casedb.domain.repository.geo import BaseGeoRepository as BaseGeoRepository
from gen_epix.casedb.domain.repository.ontology import (
    BaseOntologyRepository as BaseOntologyRepository,
)
from gen_epix.commondb.domain.repository import BaseAbacRepository as BaseAbacRepository
from gen_epix.commondb.domain.repository import (
    BaseOrganizationRepository as BaseOrganizationRepository,
)
from gen_epix.commondb.domain.repository import (
    BaseSystemRepository as BaseSystemRepository,
)

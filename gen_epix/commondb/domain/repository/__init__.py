"""Re-export commondb repository interfaces.

ABAC, organization, and system repository interfaces separate service behavior
from persistence implementations and preserve behavior across storage engines.
"""

# pylint: disable=useless-import-alias
from gen_epix.commondb.domain.repository.abac import (
    BaseAbacRepository as BaseAbacRepository,
)
from gen_epix.commondb.domain.repository.organization import (
    BaseOrganizationRepository as BaseOrganizationRepository,
)
from gen_epix.commondb.domain.repository.system import (
    BaseSystemRepository as BaseSystemRepository,
)

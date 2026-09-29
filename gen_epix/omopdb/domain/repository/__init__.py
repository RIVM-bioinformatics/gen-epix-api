"""Expose OmopDB repository contracts for shared and OMOP persistence.

`BaseAbacRepository` governs attribute-based access data, while
`BaseOmopRepository` provides person and cohort-specimen queries. Shared
organization and system repository contracts are re-exported for composition.
"""

# pylint: disable=useless-import-alias
from gen_epix.commondb.domain.repository import (
    BaseOrganizationRepository as BaseOrganizationRepository,
)
from gen_epix.commondb.domain.repository import (
    BaseSystemRepository as BaseSystemRepository,
)
from gen_epix.omopdb.domain.repository.abac import (
    BaseAbacRepository as BaseAbacRepository,
)
from gen_epix.omopdb.domain.repository.omop import (
    BaseOmopRepository as BaseOmopRepository,
)

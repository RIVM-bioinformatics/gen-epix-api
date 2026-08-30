"""Expose OmopDB dictionary and SQLAlchemy repository implementations.

The facade imports SQLAlchemy models for registration and exports shared system
and organization repositories together with OmopDB ABAC and OMOP repositories.
"""

# pylint: disable=useless-import-alias
from gen_epix.commondb.repositories import (
    OrganizationDictRepository as OrganizationDictRepository,
)
from gen_epix.commondb.repositories import (
    OrganizationSARepository as OrganizationSARepository,
)
from gen_epix.commondb.repositories.system_dict import (
    SystemDictRepository as SystemDictRepository,
)
from gen_epix.commondb.repositories.system_sa import (
    SystemSARepository as SystemSARepository,
)
from gen_epix.omopdb.repositories import sa_model as sa_model  # Initialize SA Models
from gen_epix.omopdb.repositories.abac_dict import (
    AbacDictRepository as AbacDictRepository,
)
from gen_epix.omopdb.repositories.abac_sa import AbacSARepository as AbacSARepository
from gen_epix.omopdb.repositories.omop_dict import (
    OmopDictRepository as OmopDictRepository,
)
from gen_epix.omopdb.repositories.omop_sa import OmopSARepository as OmopSARepository
from gen_epix.omopdb.repositories.organization_dict import (
    OrganizationDictRepository as OrganizationDictRepository,
)
from gen_epix.omopdb.repositories.organization_sa import (
    OrganizationSARepository as OrganizationSARepository,
)

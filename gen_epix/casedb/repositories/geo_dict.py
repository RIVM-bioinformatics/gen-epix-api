"""Provide dictionary-backed persistence for casedb geographic reference data.

GeoDictRepository combines the shared in-memory implementation with the
geographic repository contract used by casedb composition.
"""

from gen_epix.casedb.domain.repository import BaseGeoRepository
from gen_epix.fastapp.repositories import DictRepository


class GeoDictRepository(DictRepository, BaseGeoRepository):
    """Provide dictionary-backed persistence for casedb geographic data."""

    pass

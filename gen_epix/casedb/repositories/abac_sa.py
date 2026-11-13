"""Provide casedb's SQLAlchemy-backed ABAC repository adapter.

AbacSARepository combines shared SQLAlchemy persistence with the casedb ABAC
repository contract.
"""

from gen_epix.casedb.domain.repository import BaseAbacRepository
from gen_epix.fastapp.repositories import SARepository


class AbacSARepository(SARepository, BaseAbacRepository):
    """Provide SQLAlchemy-backed persistence for casedb ABAC policy data."""

    pass

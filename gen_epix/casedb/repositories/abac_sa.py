"""Provide casedb SQLAlchemy persistence behavior for ABAC policy data."""

from gen_epix.casedb.domain.repository import BaseAbacRepository
from gen_epix.fastapp.repositories import SARepository


class AbacSARepository(SARepository, BaseAbacRepository):
    """Provide SQLAlchemy-backed persistence for casedb ABAC policy data."""

    pass

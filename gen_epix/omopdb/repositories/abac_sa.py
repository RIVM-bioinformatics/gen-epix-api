"""SQLAlchemy-backed repository for OmopDB attribute-based access data."""

from gen_epix.fastapp.repositories import SARepository
from gen_epix.omopdb.domain.repository import BaseAbacRepository


class AbacSARepository(SARepository, BaseAbacRepository):
    """Encapsulates implementation of the OmopDB ABAC repository contract with SQLAlchemy storage."""

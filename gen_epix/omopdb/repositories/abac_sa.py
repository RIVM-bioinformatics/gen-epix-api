"""Provide the SQLAlchemy-backed OmopDB ABAC repository adapter."""

from gen_epix.fastapp.repositories import SARepository
from gen_epix.omopdb.domain.repository import BaseAbacRepository


class AbacSARepository(SARepository, BaseAbacRepository):
    """Encapsulates the OmopDB ABAC persistence contract using SQLAlchemy."""

"""Dictionary-backed repository for OmopDB attribute-based access data."""

from gen_epix.fastapp.repositories import DictRepository
from gen_epix.omopdb.domain.repository import BaseAbacRepository


class AbacDictRepository(DictRepository, BaseAbacRepository):
    """Implement the OmopDB ABAC repository contract with in-memory storage."""

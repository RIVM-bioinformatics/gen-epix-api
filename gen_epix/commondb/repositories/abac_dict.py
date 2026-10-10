"""Provide the in-memory repository implementation for commondb ABAC models.

`AbacDictRepository` combines FastApp's dictionary backend with commondb's ABAC
persistence contract.
"""

from gen_epix.commondb.domain.repository import BaseAbacRepository
from gen_epix.fastapp.repositories import DictRepository


class AbacDictRepository(DictRepository, BaseAbacRepository):
    """Encapsulates in-memory ABAC storage using FastApp's dictionary backend."""

    pass

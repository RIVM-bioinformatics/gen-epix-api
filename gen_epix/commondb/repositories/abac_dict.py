"""Provide the in-memory repository implementation for commondb ABAC models."""

from gen_epix.commondb.domain.repository import BaseAbacRepository
from gen_epix.fastapp.repositories import DictRepository


class AbacDictRepository(DictRepository, BaseAbacRepository):
    """Encapsulates storage of ABAC policy records using FastApp's dictionary repository backend."""

    pass

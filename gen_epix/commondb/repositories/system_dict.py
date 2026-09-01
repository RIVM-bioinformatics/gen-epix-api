"""Provide the in-memory repository implementation for commondb system models."""

from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp.repositories import DictRepository


class SystemDictRepository(DictRepository, BaseSystemRepository):
    """Store system records using FastApp's dictionary repository backend."""

    pass
